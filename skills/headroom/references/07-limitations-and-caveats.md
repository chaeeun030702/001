# 07. 한계 · 주의 · 문서-코드 불일치

## 7.1 효과가 큰 곳 / 작은 곳 (저장소 `wiki/LIMITATIONS.md` 값, 직접 측정 아님)
| 콘텐츠 | 압축 | 지연 영향 |
|---|---|---|
| JSON 딕셔너리 배열(검색결과, API 응답, DB 행) | 86–100% | Sonnet/Opus에서 순이득 |
| JSON 문자열 배열(경로, 로그 줄) | 60–90% | 순이득 |
| JSON 숫자 배열(메트릭) | 70–85% | 순이득 |
| 혼합 타입 배열 | 50–70% | 순이득 |
| 구조화 로그(JSON) | 82–95% | 순이득 |
| 에이전트 대화(25–50턴) | 56–81% | 손익분기~순이득 |
| 일반 텍스트 | 43–46% | **지연 증가**(비용 절감용) |
| 코드 | 사실상 통과 | 최소 |
| RAG 문서(사용자 메시지 내 일반 텍스트) | 통과 | 최소 |

### README의 재현 가능한 벤치 (`uv run python benchmarks/index_proof_table.py --seed 20260902`)
| 시나리오 | 전 | 후 | 절감 |
|---|--:|--:|--:|
| 코드 검색(100건) | 17,199 | 13,597 | 21% |
| SRE 장애 디버깅 | 55,957 | 24,340 | 57% |
| 코드베이스 탐색 | 58,801 | 33,895 | 42% |
| GitHub 이슈 트리아지 | 46,067 | 32,429 | 30% |
- 압축 오버헤드: 10K 토큰 JSON에서 p50 0.21ms, 100K 토큰에서 1.4ms (ML 텍스트 압축은 제외 — 별도 지연).
- 정확도(`python -m headroom.evals suite --tier 1`, N=100): GSM8K 0.870→0.870, TruthfulQA 0.530→0.560(N=100에서 ±0.03은 신뢰구간 안이라 "개선"이 아니라 "차이 없음"), SQuAD v2 97%(19% 압축), BFCL 97%(32% 압축).
- **절감은 중복도에 비례**: 반복 JSON 배열·로그 줄은 90%+, 산문·이미 조밀한 출력은 거의 없음. `min_input_words` 미만은 바이트 동일.

## 7.2 "왜 압축이 안 되죠?" 체크리스트
1. **코드인가?** `protect_recent_code=4`, `protect_analysis_context=True`(analyze/review/explain/fix/debug/optimize/error/bug 키워드가 최근 사용자 메시지에 있으면 대화 전체 코드 보호) → 의도된 보호.
2. **임계 미만인가?** `min_tokens_to_compress`(compress() 기본 250, 라우터 기본 50), SmartCrusher는 ≥5항목·≥200토큰, 블록 압축 최소 500자, 라이브존 소스 2048/텍스트 5120.
3. **최근 4개 메시지인가?** `protect_recent=4` — 방금 온 도구 결과도 "최근"이면 보호될 수 있음(프록시는 라이브존 규칙 사용).
4. **JSON이 아닌 척하는가?** 깨진 JSON, 객체-only, 불리언 배열은 통과. 깊이 > 5 배열은 미검사.
5. **파이프라인이 열렸나(서킷)?** 연속 실패 3회 → 60초 `pipeline:circuit_open` 패스스루. 로그 확인.
6. **제외 도구/이미 압축됨/작은 MCP 결과**인가?
7. **ML(Kompress) 미설치?** `[ml]` 없으면 일반 텍스트는 통과(경고 로그). `kompress_model='disabled'`도 동일.
8. **네트워크로 모델 못 받음?** huggingface.co 차단 → `HF_HUB_OFFLINE=1`로 사전 다운로드 또는 `HF_ENDPOINT` 미러.
9. 확인 도구: `HEADROOM_DIAGNOSTICS=1` 또는 `CompressConfig(diagnostics=True)`로 **메시지별 결정(compressed/protected/skipped)** 확인, `headroom doctor`.

## 7.3 안전 설계 (실패해도 원문을 잃지 않게)
- 모든 압축기: 실패→원본 반환(예외 전파 안 함, WARNING 로그). 압축 후 더 커지면 원본.
- 로그엔 **프레임 위치만**(예외 메시지·로컬 변수·cause 체인 제외) → 페이로드 유출 방지.
- 검증 게이트: 블록 토큰 비교, `verify_lossless` 왕복 검증.
- 폴백이 아니라 **실패를 드러내는** 선택도 있음: SmartCrusher에 사용자 지정 `scorer`/`relevance_config`를 주면 조용히 무시하지 않고 `NotImplementedError`.
- 처음/끝 항목 + 에러 + 이상치는 K 예산과 무관하게 보존.

## 7.4 문서-코드 불일치 (코드를 정답으로 볼 것)
| 항목 | 일부 문서 | 코드/최신 README |
|---|---|---|
| **CacheAligner** | `wiki/ARCHITECTURE.md`·`transforms.md`·`LIMITATIONS.md`: 날짜 등을 시스템 프롬프트에서 꺼내 끝으로 옮겨 안정화, `[Dynamic Context]` 마커 추가 | `cache_aligner.py` 머리 주석(PR-A2/P2-23): **감지 전용**. 재작성 경로는 불변식 I2(캐시 핫존 불변) 위반이라 제거됨. UUID/ISO8601/JWT/hex-hash를 구조적 파서로 감지해 **경고 로그·지표만**, `apply`는 메시지 no-op |
| **Context Manager / RollingWindow** | ARCHITECTURE 다이어그램에 "Context Manager(토큰 한도 맞춤, 점수 기반)" | PR-B1에서 **제거**. 메시지는 삭제되지 않음 |
| **SmartCrusher 구현** | 문서의 `crusher.crush(tool_output, query=…)` 예시·Python 로직 서술 | Python 구현 제거(2026-04-27), `headroom._core` Rust **하드 의존** — `scripts/build_rust_extension.sh` 또는 휠 필요 |
| **LLMLingua** | 일부 과거 문구 | 제거, **Kompress**로 대체 (`[llmlingua]` extra 설치 불가) |
| **TOIN 신뢰도 임계** | `headroom.config.SmartCrusherConfig` 기본 0.3 | 라우터가 실제 쓰는 transforms 쪽 `SmartCrusherConfig`는 **0.5** |
| **max_items_after_crush** | `transforms.md` 예시 50 | 기본값 **15** (Rust config) |
| **CCR 데모** | `examples/ccr_demo.py` | 삭제됨 → `examples/test_ccr.py` |

## 7.5 알려진 제약
- **Live-zone 디스패처 범위**: 현재 Anthropic `/v1/messages`가 선행 구현. OpenAI Chat/Responses, Gemini, Bedrock 네이티브는 각 walker가 필요(Phase C, `REALIGNMENT/`). 공급자별 효과 차이가 있을 수 있음.
- **캐시와의 긴장**: 프리픽스 중간을 바꾸면 이후 캐시가 깨진다 → 라이브존 한정 + net-cost 게이트(플래그). `--mode cache`가 보수적, `--mode token`이 공격적.
- **출력 절감은 추정치**(홀드아웃 없이는), 조향은 캐시 모드에서 꺼질 수 있음, 표본이 작은 실험 근거(n=9, Claude).
- **프록시 공유 시 런타임 오버라이드는 전역**(마지막 설정 승리).
- **TOIN 콜드스타트**: 새 도구 유형은 통계 휴리스틱만. 교차 세션 학습은 저장 경로 필요.
- **Kompress**: 첫 호출 모델 로딩, 전역 락으로 동시성 직렬화, 마감 초과 시 포기.
- **Intel macOS**: `ort-sys` 사전빌드 없음(이슈 #941) → 시스템 ORT 지정 필요.
- **Enterprise 전용**(OSS 아님): 모든 모델에 도구 검색, 하네스 튜닝, 자동 모델 라우팅, 프롬프트 인젝션/위험 도구 호출 제거, SSO/VPC, 조직 대시보드. OSS의 모델 라우팅은 규칙 기반·옵트인.

## 7.6 프라이버시 · 텔레메트리
- 압축은 **로컬**. 프롬프트·파일 내용은 압축 목적으로 외부로 가지 않음.
- 그러나 **익명 비콘이 기본 켜짐**: 압축 비율·카운터·공급자/모델 ID·OS/아키텍처만 전송, 프롬프트/응답/코드/파일 경로는 불포함. 끄기: `HEADROOM_BEACON=off` / `DO_NOT_TRACK=1` / `HEADROOM_OFFLINE=1`.
- 업데이트 확인(PyPI, 하루 1회, 비차단): `HEADROOM_UPDATE_CHECK=off`, `--stateless`/CI에선 생략.
- 기업 도입 시: 비콘 정책 결정, `headroom doctor --network`로 TLS/게이트웨이 점검, 허용 도메인(IT용 목록은 docs "Corporate networks").

## 7.7 이 문서의 신뢰 범위
소스·문서를 읽고 정리했을 뿐 **설치·실행 검증은 하지 않았다.** 절감률/지연 수치는 저장소 문서가 출처다. 도입 판단은 `headroom savings`(입력)·`headroom output-savings`(출력)로 **자기 트래픽에서** 재측정할 것.
