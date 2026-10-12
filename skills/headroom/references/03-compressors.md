# 03. 압축기와 라우팅 로직

## 3.1 ContentRouter 결정 순서
`content_router.py` 모듈 docstring 기준:
1. **소스 힌트**(어떤 도구의 출력인지) — 가장 신뢰도 높음
2. **혼합 콘텐츠?** (`is_mixed_content`) → 섹션으로 쪼개 각각 라우팅 후 재조립
3. **유형 감지** (`_detect_content`: Rust/Magika 네이티브 + 정규식 휴리스틱, 타임아웃 워치독)
4. 유형 → 전략 매핑 → 압축 → 라우팅 메타데이터(`routing_log`, `strategy_used`)와 함께 반환

### 유형 → 전략 매핑 (`_strategy_from_detection`)
| 감지 유형 | 전략 | 압축기 |
|---|---|---|
| `JSON_ARRAY` | `SMART_CRUSHER` | SmartCrusher |
| `SOURCE_CODE` | `CODE_AWARE` | CodeCompressor (끄면 `PASSTHROUGH`) |
| `SEARCH_RESULTS` | `SEARCH` | grep/ripgrep 결과 압축 |
| `BUILD_OUTPUT` | `LOG` | 빌드/테스트 로그 |
| `GIT_DIFF` | `DIFF` | diff 압축(헝크 보존) |
| `HTML` | `HTML` | 본문 추출 |
| `TABULAR` / git status | `TABULAR` | 표 압축 |
| `STRUCTURED_CONFIG` | `CONFIG` | 설정 파일 |
| `PLAIN_TEXT` | `TEXT`→`KOMPRESS` | Kompress-v2-base (ML, 선택) |
| 그 외 | `fallback_strategy` | — |

### 오분류 방지 규칙 (코드 주석에서 확인)
- **파이썬 소스가 MIXED로 오분류**되는 문제: dict/list 리터럴 → `has_json_blocks`, docstring → `has_prose`로 걸림. 네이티브 감지기가 `SOURCE_CODE` & `confidence ≥ 0.8`이면 **휴리스틱보다 네이티브를 신뢰**.
- `prefer_code_aware_for_code=False`면 코드는 ML(Kompress)로 보내지 않고 **`PASSTHROUGH`**. (45K 토큰 파이썬을 912토큰으로 줄였더니 사실 재현율 11%였던 사례 때문)

## 3.2 무손실 우선 (lossless-first, STAGE 0)
손실 압축 전에 항상 **형식을 유지한 채 바이트만 줄이는 접기**를 먼저 시도한다 (`_lossless_first` → `lossless_compaction.compact_lossless`).
| 종류 | 동작 |
|---|---|
| `search` | grep `path:line:content` → ripgrep `--heading` 형태로 경로 반복 제거 |
| `paths` | 디렉터리 헤딩화 |
| `log` | ANSI 색상 제거 + 연속 동일 줄 `... (repeated N times)` + 반복 블록 `... (repeats L lines from D lines back)` (3~64줄, 최대 2만 줄 스캔) |
| `diff` | `index <hex>..<hex>` 부기 줄 제거 (diff일 때만; 역변환 검증이 없는 유일한 접기라 비-diff엔 금지) |
| `text` | 빈 줄 연속 접기 |
- **자기검증**: 각 접기는 정확한 역함수가 있고 실행 시 왕복 검증. 원본과 다르거나 더 작아지지 않으면 **원본 그대로** 반환. 예외는 던지지 않음.
- 마커(`<<ccr:…>>`/`Retrieve …`)를 **전혀 넣지 않음** → no-CCR 프록시에서도 복구 가능.
- 가능한 모든 접기를 시도해 **가장 많이 줄인 하나**를 채택. 외부 무손실 provider(`headroom.transforms.lossless_provider`)도 경쟁(더 작을 때만 채택, **diff엔 제공 금지**).
- 메모이제이션: `(hash, len, strategy, provider_generation)` 키로 동일 요청 내 중복 계산 방지.

## 3.3 보호 규칙 (압축하지 않는 것)
| 규칙 | 기본 | 설명 |
|---|---|---|
| `protect_recent_code` | 4 | 마지막 4개 메시지 안의 코드는 압축 금지 (도구 결과는 항상 "최근"이라 사실상 코드 통과) |
| `protect_analysis_context` | True | 최근 사용자 메시지에 analyze/review/explain/fix/debug/optimize/error/bug 등이 있으면 **대화 전체의 코드 보호** |
| Read 보호 | 켜짐 | 파일 읽기(`cat`, Read 도구 등 `_is_read_command`) 출력은 보호/수명주기 관리(`read_lifecycle`, `read_maturation`) |
| 제외 도구 | `DEFAULT_EXCLUDE_TOOLS` 등 | 바이트 정확/원문 유지 도구는 건너뜀 (`is_tool_excluded`) |
| 작은 MCP 결과 | 임계 미만 | `_is_small_mcp_result`면 그대로 |
| 이미 압축됨 | — | `_is_already_compressed`면 재압축 안 함 |
| 사용자 메시지 | 건너뜀 | `skip_user_messages=True` |
- 이유(문서): 코드는 *작업하려고* 가져온 것이므로 함수 본문을 지우면 필요한 걸 잃는다. Claude 같은 모델은 큰 파일 탐색에 능하다.
- 해제: `ContentRouterConfig(protect_analysis_context=False)` (+ tree-sitter `[code]`).

## 3.4 net-cost 게이트 (선택, 플래그)
캐시 프리픽스 중간을 바꾸면 **그 뒤 접미부 전체의 캐시가 깨져** 재작성 비용(쓰기 1.25×)이 든다. 그래서 변형이 이득인지 손익분기로 판정:
- ΔT = 후보의 정확한 토큰 절감, S = 해당 슬롯 뒤 토큰 합, R = 기대 재읽기 횟수(`HEADROOM_NET_COST_EXPECTED_READS`, 기본 10), P_alive = 캐시 생존 확률(`HEADROOM_NET_COST_P_ALIVE`, 기본 1.0 = 보수적).
- **P3a 배치**: 더 얕은 슬롯이 이미 허용되었다면 그보다 깊은 후보는 이미 같은 무효화에 편승 → S=0으로 계산.
- **P3b 유휴 타이머**: 세션이 오래 쉬면 `P_alive = max(0, 1 − idle/TTL)`로 감소(TTL 기본 300초, `HEADROOM_NET_COST_CACHE_TTL_SECONDS`) → 곧 캐시가 식으니 편집이 공짜에 가까워짐.
- 결정마다 `netcost:skip:<band>` 마커·카운터를 남김 (#856, 플래그 기본 꺼짐).

## 3.5 SmartCrusher — JSON 배열의 핵심 로직
Rust(`smart_crusher/`)가 실구현, Python은 얇은 shim(`headroom._core` 하드 임포트, 폴백 없음). 출력은 **스키마 보존형**: 원본 배열에 있던 항목만 남기고 래퍼/생성 텍스트를 넣지 않는다(예외: CCR 센티널).

### 입구 게이트
배열 ≥ 5개(`min_items_to_analyze`) · 콘텐츠 ≥ 200토큰(`min_tokens_to_crush`) · 잘못된 JSON/숫자 외 불리언 배열/배열 없는 객체는 통과. 중첩은 깊이 5까지 재귀.

### 처리 흐름
```
1. normalize_concatenated_json  (이어붙은 JSON 정규화)
2. classify_array → dict[] / string[] / number[] / mixed (mixed는 타입별 그룹으로 나눠 각각 압축)
3. SmartAnalyzer 필드 통계: 상수 필드, unique_ratio(<0.1이면 거의 상수), 분산, 변화점, 순차 ID(제로패딩 보존), 점수 필드 자동 탐지
4. 무손실 컴팩션 시도 (csv-schema / json / markdown-kv 렌더링)
      └ 절감률 ≥ lossless_min_savings_ratio(0.15)이면 채택 → CCR 왕복 불필요
5. 아니면 손실 경로: 계획 수립(Planner)
      a) adaptive K 결정
      b) 앵커(처음/끝) + 전략별 신호 + 제약(constraints) + 질의 신호로 유지 인덱스 선택
      c) 중복 제거(dedup_identical_items) → 빈 슬롯 채움 → 예산 초과 시 가지치기(prioritize_indices)
6. 버린 행은 CCR 저장소에 원본 저장, 배열 끝에 센티널 추가
```

### Adaptive K (정보이론적 크기 결정)
- **Kneedle**: 바이그램 커버리지 곡선에서 "항목을 더 넣어도 새 정보가 안 늘어나는 무릎점"을 K로
- **SimHash**: 근사 중복 항목 탐지 / **zlib 검증**: 선택 부분집합이 전체 다양성을 담는지 확인
- K 배분: **앞 30% · 뒤 15% · 중요도 점수 55%** (`first_fraction`, `last_fraction`), 상한 `max_items_after_crush`(기본 15)

### 항상 유지되는 것 (K 예산 초과해도 *추가*됨)
| 범주 | 판정 |
|---|---|
| 에러 항목 | 필드 분산 통계 + 에러 키워드(`error`, `exception`, `failed`, `critical` …) — 키워드 *목록만*에 의존하지 않음 |
| 수치 이상치 | 평균에서 > 2σ (`variance_threshold` 2.0) |
| 문자열 길이 이상치 | 길이가 > 2σ |
| 변화점 | 누적값의 급변 (`preserve_change_points`) |
| 희귀 상태값 | `detect_rare_status_values` (>10개 고유값에서도 단락하지 않도록 수정됨) |
| 질의 앵커 | 사용자 질의의 정확 일치(결정적) |
| 관련도 | BM25/임베딩 점수 ≥ `relevance_threshold` 0.3 |
| TOIN 선호 필드 | 학습된 중요 필드 값에 질의 토큰이 맞는 항목 |

### 전략 4종
`TIME_SERIES`(변화점 보존) · `CLUSTER`(유사 로그 메시지 군집당 1–2개) · `TOP_N`(점수 상위, 검색결과) · `SMART_SAMPLE`(통계적 샘플 + 상수 추출)

### 숫자/문자열 배열
- 숫자: 통계 요약 + 이상치·변화점 보존 (`crush_number_array`)
- 문자열: 중복 제거 + 적응 샘플링 + 에러 보존 (`crush_string_array`); 드롭 시 `"… N more items <<ccr:HASH N_items_offloaded>>"` 문자열 센티널(균일한 원소 타입 유지)

### 이식 중 고쳐진 버그 4건 (Rust 주석)
k-split 과다(K=1일 때 2개 유지) · 제로패딩 문자열 ID가 순차 숫자로 오인 · 희귀상태 탐지가 10개 초과에서 조기 종료 · 퍼센타일 off-by-one(디버그 문자열만).

## 3.6 그 외 압축기
- **CodeCompressor**: tree-sitter AST로 시그니처·임포트·타입은 유지하고 본문을 축약. 파싱 실패 시 원본. (Live-zone에서는 코드 컴프레서가 입력을 그대로 돌려주면 캐시된 Kompress로 폴백)
- **Kompress-v2-base**: 에이전트 트레이스로 학습한 토큰 분류 모델(ModernBERT 계열, HF). 첫 호출은 모델 로딩 지연, 전역 단일 인스턴스+락. **속도보다 비용 절감용**. ML 단계는 `_ml_stage_deadline_seconds`·전체 `_compression_deadline_seconds` 마감을 가지며 초과 시 포기.
- **이미지**: 학습된 ML 라우터로 40–90% 축소(`[image]`).
- **TOIN(Tool Output Intelligence Network)**: 도구 출력 구조 해시로 압축 패턴·검색(retrieve) 이력을 학습해 이후 압축 결정에 반영(신뢰도 < 0.5면 무시, 콜드스타트는 통계 휴리스틱).
- **병렬화**: 블록 압축은 워커 풀(`HEADROOM_COMPRESS_WORKERS`)에서 병렬.
