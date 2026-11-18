# Headroom 스킬 제작 — 전체 작업 기록

> 이 문서는 대화에서 진행한 요청·작업 과정·결과와, 산출물 파일 9개의 전문을 한곳에 모은 기록본이다.
> 대화 원문 그대로가 아니라 **요청과 작업 내용을 정리한 기록**이며, 도구 출력 원문은 포함하지 않는다.

## 1. 요청
| 순번 | 사용자 요청 | 처리 |
|---|---|---|
| 1 | `https://github.com/headroomlabs-ai/headroom` — 해당 스킬에 대해 **로직을 포함하여 설명**, **MD 파일을 넣어서 ZIP으로 제작** | 소스 조사 → 스킬 폴더(MD 9개) 작성 → `skills/headroom.zip` 생성 → 커밋·푸시 → 초안 PR |
| 2 | 전체 기록과 파일을 md 파일로 저장 | 본 문서(`docs/headroom_session_record.md`) |

## 2. 작업 타임라인
1. **저장소 접근**: Headroom은 세션 범위 밖이라 `add_repo`(읽기 전용, 공개 저장소)로 확인 후 `git clone --depth 1`.
   - 기준 커밋 `72302a3` (2026-10-12), Apache-2.0.
2. **조사한 자료** (소스·문서 대조)
   - `README.md`, `llms.txt`, `wiki/*.md`(ARCHITECTURE, ccr, transforms, LIMITATIONS, learn, mcp, memory, shared-context, configuration, cli)
   - Python: `headroom/compress.py`, `transforms/pipeline.py`, `transforms/content_router.py`, `transforms/smart_crusher.py`, `transforms/cache_aligner.py`, `transforms/lossless_compaction.py`, `proxy/output_shaper.py`, `proxy/output_steering.py`, `proxy/output_verbosity_policy.py`, `proxy/output_turn_policy.py`, `cli/proxy.py`
   - Rust: `crates/headroom-core/src/transforms/live_zone.rs`, `smart_crusher/{mod,config,planning}.rs`
3. **핵심 발견**
   - 파이프라인: (선택) ToolResultInterceptor → CacheAligner → ContentRouter. 메시지 삭제 단계(IntelligentContext/RollingWindow)는 PR-B1에서 제거.
   - **Live-zone 압축**: 캐시된 앞부분은 바이트 불변, 최신 user 블록만 바이트 범위 수술로 교체.
   - ContentRouter: 유형 감지 → 전략 매핑 → **무손실 접기 우선** → 손실 압축 → 더 커지면 원본.
   - SmartCrusher(Rust): 에러·이상치·변화점·처음/끝·질의 관련 항목 보존, adaptive K(Kneedle+SimHash+zlib), 버린 행은 CCR 센티널로 표시.
   - CCR: 원본 해시 보관 + `headroom_retrieve` 도구 주입 + 프록시가 호출 가로채기.
   - 출력 절감: 시스템 프롬프트 끝 조향(레벨 0–4) + 기계적 속행 턴에서만 effort 낮춤(구조 기반 분류).
   - **문서-코드 불일치 확인**: CacheAligner는 문서와 달리 코드상 *감지 전용*(PR-A2).
4. **산출물 작성**: `skills/headroom/`(SKILL.md, README.md, references 01~07).
5. **ZIP 생성**: `skills/headroom.zip` (11개 항목, 약 51.7KB 원본 크기).
6. **Git**: 브랜치 `claude/optimistic-pascal-onjqj9`에 커밋·푸시.
7. **PR**: 기본 브랜치가 `main`이 아니라 `claude/github-claude-code-connector-vbr24r`임을 확인 후 초안 PR 생성 — https://github.com/chaeeun030702/001/pull/53 (구독 시작, CI 체크 없음, 리뷰 없음).
8. 사용자에게 ZIP 파일 전달.

## 3. 에이전트 작업현황 (CLAUDE.md 규칙)
서브에이전트(Agent 도구)를 쓰지 않고 직접 조사했으므로 작업현황 아티팩트는 갱신하지 않았다.

| 에이전트 | 상태 | 결과 |
|---|---|---|
| (없음 — 메인 에이전트 단독 수행) | — | — |

## 4. 검증 범위와 한계
- Headroom을 **설치·실행하지 않았다.** 절감률·지연 수치는 저장소 문서 값이다.
- 저장소가 빠르게 변하므로(Phase B/C 진행 중) 세부는 `headroom doctor`와 최신 문서로 재확인 필요.
- 위키와 코드가 다른 항목은 `07-limitations-and-caveats.md` §7.4 표에 정리.

## 5. 산출물 목록
| 경로 | 설명 |
|---|---|
| `skills/headroom.zip` | 아래 폴더를 묶은 ZIP |
| `skills/headroom/SKILL.md` | 스킬 진입점 |
| `skills/headroom/README.md` | 패키지 소개 |
| `skills/headroom/references/01-overview.md` | 개요 |
| `skills/headroom/references/02-pipeline-logic.md` | 파이프라인 로직 |
| `skills/headroom/references/03-compressors.md` | 압축기·라우팅·SmartCrusher |
| `skills/headroom/references/04-ccr-reversible.md` | CCR 가역 압축 |
| `skills/headroom/references/05-output-and-learning.md` | 출력 절감·learn·메모리 |
| `skills/headroom/references/06-install-and-usage.md` | 설치·사용 |
| `skills/headroom/references/07-limitations-and-caveats.md` | 한계·불일치 |
| `docs/headroom_session_record.md` | 본 기록 |

---

# 6. 파일 전문


## 6.1 `skills/headroom/SKILL.md`

````markdown
---
name: headroom
description: Headroom(headroomlabs-ai/headroom) — AI 에이전트가 읽는 도구 출력·로그·RAG·파일·대화 이력을 LLM에 보내기 전에 로컬에서 압축해 토큰 비용을 줄이는 "컨텍스트 압축 레이어"의 동작 로직과 사용법을 설명한다. 사용자가 Headroom, 토큰 절감, 컨텍스트 압축, headroom wrap/proxy/learn/mcp, CCR(headroom_retrieve), SmartCrusher, ContentRouter, 출력 토큰 절감을 묻거나 도입·설정·튜닝·문제 해결을 요청할 때 사용한다.
---

# Headroom — 컨텍스트 압축 레이어

> 기준: `headroomlabs-ai/headroom` 기본 브랜치 커밋 `72302a3` (2026-10-12) 소스 직접 확인. Apache-2.0.
> 한 줄 요약: **에이전트가 읽는 모든 것을 LLM에 닿기 전에 로컬에서 압축하고, 원본은 로컬에 캐시해 필요할 때 되살린다.**

## 1. 무엇인가
| 구분 | 내용 |
|---|---|
| 정체 | 에이전트 ↔ LLM 사이에 끼는 **로컬 압축 프록시/라이브러리/MCP 서버** (Python `headroom-ai`, TypeScript SDK, Rust 코어) |
| 압축 대상 | 도구 출력(JSON·로그·검색결과·diff), 코드, 텍스트, HTML, 이미지, 대화 이력 |
| 핵심 약속 | 같은 답을 더 적은 토큰으로. 압축은 **로컬**에서 수행(프롬프트가 압축용으로 외부 전송되지 않음) |
| 3가지 축 | ① 입력 압축 ② 출력 토큰 절감 ③ 학습/메모리(`learn`, cross-agent memory) |

## 2. 로직 한눈에 (자세한 건 `references/`)
```
요청(messages)
  │  ① Live-zone 판별: 캐시된 앞부분(frozen prefix)은 바이트 그대로 보존, 최신 블록만 후보
  ▼
  CacheAligner      → 시스템 프롬프트의 UUID/타임스탬프/JWT/해시 "감지·경고"만 (수정 안 함)
  ▼
  ContentRouter     → 내용 유형 감지 → 알맞은 압축기로 라우팅
  │     ├ JSON 배열  → SmartCrusher (통계 기반 행 선택, Rust)
  │     ├ 소스코드   → CodeCompressor (tree-sitter AST)
  │     ├ 검색결과   → SearchCompressor     ├ 로그/빌드 → LogCompressor
  │     ├ diff       → DiffCompressor       ├ HTML → 추출기
  │     ├ 표/설정    → Tabular/Config       └ 일반 텍스트 → Kompress-v2-base(ML, 선택)
  │   0단계로 항상 "무손실 접기(lossless-first)"를 먼저 시도
  ▼
  CCR               → 손실 압축분의 원본을 해시키로 로컬 저장 + <<ccr:HASH>> 마커 + headroom_retrieve 도구 주입
  ▼
압축된 요청 → LLM
  ▲ 모델이 headroom_retrieve(hash)를 부르면 프록시가 가로채 원본을 돌려줌(클라이언트는 모름)
```
핵심 불변식: **(a)** 대화 메시지를 *삭제하지 않는다* **(b)** 캐시 핫존(시스템 프롬프트·툴 정의·지난 턴)은 *바이트 불변* **(c)** 압축기가 실패하거나 더 커지면 *원본 반환(fail-open)*.

## 3. 언제 쓰나 / 쓰지 않나
- **쓰기 좋음**: 도구 출력이 큰 장시간 에이전트 세션(SRE 디버깅, 코드 탐색, 이슈 트리아지), 여러 에이전트 공유 메모리, "되돌릴 수 있는" 압축이 필요할 때.
- **효과 작음**: 짧은 대화, 이미 조밀한 산문, 코드(대부분 보호되어 통과), `min_input_words` 미만 블록(바이트 동일 반환).
- **건너뜀**: 한 공급자의 네이티브 컴팩션만 쓰고 메모리 공유가 불필요하거나, 로컬 프로세스를 못 띄우는 샌드박스.

## 4. 빠른 시작
```bash
pip install "headroom-ai[all]"            # CLI 포함 (npm 패키지는 SDK 전용, CLI 없음)
headroom wrap claude                      # 에이전트를 감싸 실행(프록시 자동 기동). 해제: headroom unwrap claude
headroom proxy --port 8787                # 코드 변경 없는 프록시 (ANTHROPIC_BASE_URL=http://127.0.0.1:8787)
headroom mcp install                      # MCP 도구: headroom_compress / headroom_retrieve / headroom_stats
headroom doctor ; headroom perf ; headroom dashboard   # 점검·성능·대시보드
headroom learn [--apply]                  # 실패 세션에서 교정 규칙 추출 → CLAUDE.local.md
export HEADROOM_OUTPUT_SHAPER=1           # 출력 토큰 절감(기본 꺼짐)
```
```python
from headroom import compress
r = compress(messages, model="gpt-4o")      # 같은 형식의 messages 반환
print(r.tokens_saved, r.compression_ratio)
```

## 5. 이 스킬을 쓰는 방법 (Claude용 지침)
1. 사용자가 **개념/원리**를 물으면 §2와 `references/02~05`를 근거로 설명한다.
2. **도입/설정**이면 `references/06`(설치·CLI·환경변수)을 따라 안내하고, 에이전트 종류별 `wrap` 가능 여부를 확인한다.
3. **효과가 안 나오는 이유**는 `references/07`(한계·보호 규칙)에서 찾는다 — 코드 보호, 최근 N개 보호, 임계값, 분석 의도 키워드가 대표 원인.
4. 수치(절감률 등)는 README의 **재현 가능한 벤치**(`benchmarks/index_proof_table.py --seed 20260902`)와 "내 트래픽에서 `headroom savings`로 측정" 원칙을 함께 전한다. 출력 토큰 절감은 **추정치**임을 밝힌다.
5. 문서와 코드가 어긋나는 곳(예: CacheAligner)은 **코드가 정답**임을 `references/07`의 "문서-코드 불일치"로 알린다.

## 6. 참고 파일
| 파일 | 내용 |
|---|---|
| `references/01-overview.md` | 문제 정의, 구성요소 지도, 진입 방식 4가지 |
| `references/02-pipeline-logic.md` | 요청 수명주기, live-zone, 파이프라인·서킷브레이커, `compress()` 옵션/모드 |
| `references/03-compressors.md` | ContentRouter 라우팅·무손실 우선·net-cost 게이트, SmartCrusher 알고리즘, 각 압축기 |
| `references/04-ccr-reversible.md` | CCR 마커·센티널·도구 주입·응답 가로채기·TTL |
| `references/05-output-and-learning.md` | 출력 토큰 절감(verbosity/effort), `learn`, 메모리, SharedContext |
| `references/06-install-and-usage.md` | 설치, wrap 대상 표, 프록시/MCP/SDK 연동, 환경변수, 진단 |
| `references/07-limitations-and-caveats.md` | 한계, 보호 규칙, 문서-코드 불일치, 텔레메트리 |
| `README.md` | 이 패키지 소개 |

````


## 6.2 `skills/headroom/README.md`

````markdown
# headroom 스킬 패키지

`https://github.com/headroomlabs-ai/headroom` 를 소스 코드까지 읽고 정리한 **설명 + 로직 해설** 스킬입니다.

- 기준 커밋: `72302a3` (2026-10-12), 라이선스 Apache-2.0
- 대상 독자: Headroom을 도입·튜닝하거나 원리를 설명해야 하는 개발자/에이전트
- 구성: `SKILL.md`(진입점) + `references/01~07`(상세 MD)

## 설치(스킬로 쓰기)
1. 압축을 풀어 `headroom/` 폴더를 Claude 스킬 디렉터리(예: `~/.claude/skills/` 또는 프로젝트 `skills/`)에 둔다.
2. "Headroom 토큰 절감 어떻게 동작해?" 같은 질문에서 `SKILL.md`가 트리거된다.

## 읽는 순서
`SKILL.md` → `01-overview` → `02-pipeline-logic` → `03-compressors` → `04-ccr-reversible` → `05-output-and-learning` → `06-install-and-usage` → `07-limitations-and-caveats`

## 근거와 한계
- 설명은 README·wiki·`headroom/`(Python)·`crates/headroom-core`(Rust) 소스 주석과 코드를 대조해 작성했다.
- 이 패키지를 만든 환경에서는 **Headroom을 실제로 설치·실행해 보지 않았다.** 수치는 저장소 문서의 값이며 직접 측정한 값이 아니다.
- 저장소는 빠르게 바뀐다(Phase B/C 리얼라인먼트 진행 중). 세부 동작은 `headroom doctor`와 최신 문서(`https://docs.headroomlabs.ai/llms.txt`)로 재확인할 것.

````


## 6.3 `skills/headroom/references/01-overview.md`

````markdown
# 01. 개요

## 풀려는 문제
LLM 에이전트의 입력 토큰 대부분은 **도구 출력**이다. 검색 결과 JSON 100건, 반복되는 로그 수천 줄, 거의 같은 메트릭 60개처럼 *중복이 많은* 덩어리가 매 턴 컨텍스트에 쌓이고,
① 비용 ② 지연 ③ 컨텍스트 창 소진 ④ (긴 맥락에서의) 정확도 저하를 부른다.
Headroom은 이 덩어리를 **모델이 읽기 전에** 줄이되, 중요한 줄(에러·이상치·처음/끝·질의와 관련된 줄)은 남기고, 나머지는 원본을 로컬에 보관해 **필요하면 되살리게** 한다.

README의 데모: 10,144 토큰 로그 → 1,260 토큰, `FATAL` 줄은 그대로 생존.

## 구성요소 지도
| 영역 | 위치 | 역할 |
|---|---|---|
| 공개 API | `headroom/compress.py` | 한 함수 `compress(messages, model=…)` |
| 파이프라인 | `headroom/transforms/pipeline.py` | 변환 순서 실행, 서킷브레이커, 지표 |
| 라우터 | `headroom/transforms/content_router.py` (~7.9k줄) | 내용 유형 감지 → 압축기 선택 → 조립 |
| JSON 압축 | `transforms/smart_crusher.py` → Rust `crates/headroom-core/.../smart_crusher/` | 통계 기반 행 선택 (Python 구현은 제거됨, Rust 필수) |
| 코드 | `transforms/code_compressor.py` | tree-sitter AST (Python/JS/TS/Go/Rust/Java/C/C++/C#/PHP) |
| 텍스트(ML) | `transforms/kompress_compressor.py` | HF 모델 `chopratejas/kompress-v2-base` (선택, `[ml]`) |
| 무손실 접기 | `transforms/lossless_compaction.py` | grep/로그/diff 형식을 유지한 채 바이트만 줄임 |
| 캐시 | `transforms/cache_aligner.py`, `headroom/cache/` | 프리픽스 불안정 요소 감지, 공급자별 캐시 정책 |
| CCR | `headroom/ccr/` | 원본 보관·마커·검색 도구·응답 가로채기 |
| 프록시 | `headroom/proxy/` | OpenAI/Anthropic/Gemini 호환 HTTP 프록시, 출력 절감, 메모리 주입 |
| 학습/메모리 | `headroom/learn/`, `headroom/memory/` | 실패 세션 → 교정 규칙, 에이전트 간 공유 메모리 |
| MCP | `headroom/ccr/mcp_server.py` | `headroom_compress/retrieve/stats` |
| Rust 코어 | `crates/headroom-core`, `headroom-proxy`, `headroom-py` | 라이브존 디스패처, SmartCrusher, 토크나이저 |

## 진입 방식 4가지 (같은 파이프라인을 공유)
| 방식 | 사용법 | 코드 변경 |
|---|---|---|
| 라이브러리 | `compress(messages, model=…)` / TS `await compress(messages,{model})` | 필요 |
| 프록시 | `headroom proxy --port 8787` → 클라이언트 base URL만 교체 | 불필요 |
| 에이전트 래핑 | `headroom wrap claude|codex|…` (프록시 기동 + 설정 주입 + 실행) | 불필요 |
| MCP 서버 | `headroom mcp install` | 불필요 |

프레임워크 어댑터: Anthropic/OpenAI SDK `withHeadroom()`, Vercel AI SDK 미들웨어, LiteLLM 콜백, LangChain `HeadroomChatModel`, Agno, Strands, ASGI `CompressionMiddleware`, 멀티에이전트 `SharedContext`.

## 경쟁/대안과의 위치
README 비교표 기준: Headroom은 *로컬 실행·모든 콘텐츠 유형·가역(reversible)*. 호스팅 API 방식(Compresr 등)은 텍스트를 외부로 보내며 비가역, OpenAI Compaction은 대화 이력만 대상이며 비가역.

````


## 6.4 `skills/headroom/references/02-pipeline-logic.md`

````markdown
# 02. 파이프라인 로직

## 2.1 요청 수명주기
`Setup → Pre-Start → Post-Start → Input Received → Input Cached → Input Routed → Input Compressed → Input Remembered → Pre-Send → Post-Send → Response Received`
(`headroom/pipeline.py`의 `PipelineStage`; 확장은 `on_pipeline_event(...)`로 각 단계를 관찰/수정). `compress()`·SDK·프록시가 이 수명주기를 공유한다.

## 2.2 변환 순서 (`TransformPipeline._build_default_transforms`)
```
0. ToolResultInterceptor  (롤아웃 플래그 tool_result_interceptors — 예: ast-grep Read 개요화; 먼저 줄여서 뒤 단계가 이득)
1. CacheAligner           (config.cache_aligner.enabled — 감지·경고 전용)
2. ContentRouter          (모든 유형을 감지해 알맞은 압축기로)
```
과거의 `IntelligentContextManager`/`RollingWindow`(메시지를 *버리는* 단계)는 **Phase B PR-B1에서 제거**되었다. 지금은 *live-zone-only* 압축이 유일한 전략이다.

### `apply()` 의사코드
```python
def apply(messages, model, model_limit, **kw):
    if breaker_is_open():                      # 연속 실패 3회 → 60초간 패스스루
        return passthrough(messages)           # transforms_applied=["pipeline:circuit_open"]
    tokens_before = tokenizer.count_messages(messages)
    cur = deep_copy(messages)                  # 입력 불변
    for t in transforms:
        if not t.should_apply(cur, tokenizer, **kw): continue
        try:  res = t.apply(cur, tokenizer, **kw)
        except Exception: breaker_record_failure(); raise   # 로그엔 프레임 위치만(페이로드 비노출)
        cur = res.messages                     # 변환기가 보고한 토큰 수 재사용(재카운트 안 함)
    breaker_record_success()
    # 절감이 100토큰 초과일 때만, 그리고 입력이 100k 토큰 이하일 때만 waste-signal 진단(텔레메트리 전용)
    return TransformResult(cur, tokens_before, tokens_after, transforms_applied, warnings, timing)
```
- 서킷브레이커: `HEADROOM_PIPELINE_BREAKER_THRESHOLD`(기본 3), `HEADROOM_PIPELINE_BREAKER_COOLDOWN_S`(기본 60). 잘못된 값은 경고 후 기본값.
- 토크나이저: OpenAI=tiktoken(정확), Anthropic=보정된 추정(~3.5자/토큰), 오픈모델=HF(설치 시), 미상=문자 기반 추정.

## 2.3 Live-zone: "무엇을 건드려도 되는가"
캐시 적중(0.1× 읽기 요금)을 지키기 위해 **프리픽스는 바이트 단위로 불변**이어야 한다. 그래서:
- **바닥(floor)**: `frozen_message_count` — 명시적 `cache_control` 마커로 계산(Rust `compute_frozen_count`). 이 인덱스 미만은 절대 변경 금지.
- **천장(ceiling)**: 최신 user 메시지. 직전 assistant 메시지는 "다음 응답이 이어받는 핫존"이라 건드리지 않음.
- **후보**: 최신 user 메시지 안의 블록. 가장 흔한 것은 `tool_result`, `text`(사용자가 붙여넣은 긴 로그)도 가능.
- **변경 방식**: JSON을 파싱→수정→재직렬화하지 않고 **바이트 범위 수술**(`out = body[..start] || 교체문 || body[end..]`). 압축 안 한 구간의 SHA-256이 입력과 동일함을 CI 테스트(`byte_fidelity_outside_compressed_block`)로 고정.
- **토크나이저 검증 게이트**: 블록별로 `compressed.tokens >= original.tokens`면 원본으로 되돌림.
- **유형별 임계값**(코드 주석 기준): 소스코드 2048, 일반 텍스트 5120(바이트), HTML은 현재 no-op.
- 디스패처는 현재 Anthropic `/v1/messages`용이 먼저 구현되고, OpenAI Chat/Responses·Gemini는 각자 walker 필요(Phase C에서 확장 — 요청 형태가 다르기 때문: OpenAI는 `role:"tool"`, Responses는 `input`+`function_call_output`, Gemini는 `contents/parts/function_response`).

## 2.4 `compress()` 옵션과 모드
| 옵션 | 기본 | 의미 |
|---|---|---|
| `compress_user_messages` | False | 사용자 메시지도 압축(문서/RAG는 True) |
| `compress_system_messages` | True | 시스템 프롬프트 압축 여부(음성 에이전트는 False) |
| `protect_recent` | 4 | 마지막 N개 메시지는 압축 안 함(0이면 전부) |
| `protect_analysis_context` | True | "analyze/review/…" 의도가 보이면 코드 보호 |
| `frozen_message_count` | 0 | 이미 공급자 캐시에 앵커된 앞부분 수(프록시가 자동 계산) |
| `target_ratio` | None | Kompress 보존 비율(None=모델 결정 ~15% 보존, 0.5/0.7=보수적). SmartCrusher에는 영향 없음 |
| `min_tokens_to_compress` | 250 | 이보다 짧은 메시지는 유지 |
| `kompress_model` | None | `'disabled'`면 ML 텍스트 압축 끔(SmartCrusher+CacheAligner만) |
| `savings_profile` | None | 예: `'agent-90'` 고절감 프로파일 |
| `diagnostics` | False | 메시지별 결정(`MessageDecision`) 반환. `HEADROOM_DIAGNOSTICS=1`도 가능 |
| `mode` | None | `None`=기본(CCR 제거+검색 허용), `"agent"`=**무손실 치밀화만**(CCR·ML 없음, 결정적이라 캐시 안전, `verify_lossless` 강제) |
| `verify_lossless` | False | 메시지별 왕복 검증, 증명 못 하면 원본으로 되돌림 → `CompressResult.lossless`, `reverted_messages` |

`densify()`는 `mode="agent"`의 약칭. 훅(`CompressionHooks`)으로 메시지별 **bias(소프트 가중)** 와 **protect(하드 거부권)** 를 줄 수 있다.

### 사용 패턴
```python
compress(messages, model="gpt-4o")                                   # 코딩 에이전트 기본
compress(messages, model="claude-opus-4-20250514",
         compress_user_messages=True, target_ratio=0.5, protect_recent=0)  # 금융 문서
compress(messages, model="gpt-4o", target_ratio=0.2)                 # 로그/검색결과 공격적
compress(messages, model="…", mode="agent")                          # 라이브 에이전트: 무손실만
```

````


## 6.5 `skills/headroom/references/03-compressors.md`

````markdown
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

````


## 6.6 `skills/headroom/references/04-ccr-reversible.md`

````markdown
# 04. CCR — Compress · Cache · Retrieve (가역 압축)

전통적 압축은 "중요한 걸 잘못 짚으면 영원히 손실"이라 공격성과 안전성이 상충한다. CCR은 **손실 압축한 부분의 원본을 로컬에 두고, 모델이 요청하면 돌려주는** 방식으로 이 상충을 없앤다.

## 4.1 흐름
```
도구 출력 1000행
  └ SmartCrusher: 20행만 남김
  └ 원본을 해시(abc123)로 LRU 저장소에 보관
  └ 남긴 배열 끝에 센티널 추가 + headroom_retrieve 도구를 요청의 tools에 주입
        ▼ LLM
   A) 20행으로 충분 → 끝 (큰 절감)
   B) headroom_retrieve(hash=abc123) 호출
        → 프록시 Response Handler가 도구 호출을 가로채 ~1ms에 로컬에서 조회
        → 결과를 대화에 붙여 API 호출을 자동 속행 (클라이언트에는 보이지 않음)
```

## 4.2 마커/센티널 형태
| 형태 | 예 | 쓰임 |
|---|---|---|
| dict 센티널 | `{"_ccr_dropped": "<<ccr:HASH N_rows_offloaded>>"}` | dict 배열의 드롭 행 자리 (`CCR_SENTINEL_KEY`) |
| 문자열 센티널 | `"… N more items <<ccr:HASH N_items_offloaded>>"` | 문자열/숫자/혼합 배열 (원소 타입 균일 유지) |
| 텍스트 마커 | `[1000 items compressed to 20. Retrieve more: hash=abc123]` | 문서상의 설명용 형태 |
- 균일 스키마를 가정하는 소비 코드는 `strip_ccr_sentinels(items)`로 센티널을 걸러야 한다(`is_ccr_sentinel`).
- `ccr_config.enabled=False` 또는 `inject_retrieval_marker=False`면 행 드롭 경로에서 **마커와 저장 둘 다** 생략.

## 4.3 4단계 구성
1. **Compression Store** — 해시키 → 원본, LRU/TTL (`headroom/cache/compression_store.py`)
2. **Tool Injection** — `headroom_retrieve` 툴 정의 주입 (`ccr/tool_injection.py`, 이름 상수 `CCR_TOOL_NAME`)
3. **Response Handler** — 모델의 retrieve 호출 가로채기·속행 (`ccr/response_handler.py`, 버퍼링 응답 `buffered_ccr_response.py`)
4. **Context Tracker** — 이전 턴에 압축된 것을 기억하고, 새 질의가 그 내용과 관련 있어 보이면 **모델이 묻기 전에 선제 확장** (예: 5턴째 "auth 미들웨어는?" → 500개 파일 목록 원본 확장). `--no-ccr-proactive-expansion`으로 끔.

## 4.4 가역성의 범위
- CCR은 **메시지를 지우는 게 아니라 콘텐츠 블록**(최신 tool_result 등)을 대상으로 한다. 시스템 프롬프트·툴 정의·지난 턴은 불변.
- **무손실 접기**(03 문서 §3.2)로 해결되는 건 CCR 마커 없이 끝난다. SmartCrusher도 무손실 컴팩션 절감률 ≥ 15%면 손실/CCR 경로를 타지 않는다.
- `mode="agent"`는 CCR 자체를 쓰지 않는다(무손실만).
- 검색(`query`)을 함께 주면 원본 안에서 일치 항목만 반환 가능(MCP `headroom_retrieve`).

## 4.5 TOIN 피드백
사용자가(모델이) 압축된 내용을 *다시 가져온* 패턴은 "그 필드/패턴이 중요했다"는 신호로 학습되어, 이후 같은 도구 출력의 압축에서 더 보존된다. 교차 세션 학습은 `TelemetryConfig.storage_path` 영속화가 필요.

## 4.6 설정
```bash
headroom proxy --port 8787                          # CCR 기본 켜짐
headroom proxy --no-ccr                             # 마커·headroom_retrieve 도구 모두 끔
headroom proxy --no-ccr-proactive-expansion         # 선제 확장만 끔
```
주의: 전체 compress→retrieve 루프(응답 가로채기·선제 확장)는 **프록시 안에서만** 돈다. SDK `compress()` 단독 호출은 임계값을 못 넘으면 마커 자체가 없을 수 있다(`examples/test_ccr.py` 결과가 "No CCR markers").
MCP 경로의 `headroom_compress` 원본 보관은 세션 단위 **1시간 TTL**.

````


## 6.7 `skills/headroom/references/05-output-and-learning.md`

````markdown
# 05. 출력 토큰 절감 · 학습 · 메모리

## 5.1 출력 토큰 절감 (프록시, 기본 꺼짐)
입력 압축은 *보내는* 토큰을 줄인다. 출력은 모델이 *쓰는* 토큰이고 Opus급에선 입력의 약 5배 단가다. 프록시는 출력을 직접 생성하지 않으므로 **요청을 재구성하는 두 가지 레버**만 쓴다.

```bash
export HEADROOM_OUTPUT_SHAPER=1      # 켜기 (1/true/yes)
export HEADROOM_VERBOSITY_LEVEL=2    # 0~4 (기본 2)
headroom proxy --port 8787
```
적용 대상: Anthropic `/v1/messages`, OpenAI `/v1/chat/completions`, `/v1/responses`.

### 레버 ① 장황함 조향 (verbosity steering)
- 시스템 프롬프트 **맨 끝**에 `<headroom_output_shaping> … </headroom_output_shaping>` 블록을 덧붙임 → 앞쪽 `cache_control` 중단점이 유지되어 프롬프트 캐시가 계속 적중.
- 블록은 **레벨별 바이트 고정**이고 **멱등**(센티널로 이미 있으면 교체/무시) → 반복 요청도 프리픽스가 동일. 문구 수정은 곧 캐시 무효화이므로 릴리스 간에도 고정.
- 레벨은 누적: 1=서두/맺음말 생략 · 2=+이미 대화에 있는 코드/출력 재인용 금지(경로·줄로 참조), 도구 성공 후 서술 생략 · 3=+결론만, 근거 생략, 최소 수정, **부정어(not/never/no/only/except) 삭제 금지**, 파괴적/보안/다단계는 풀 문장 · 4=최소 토큰(조각 문장 허용).
- 설계 근거(코드 주석): SWE-bench 완주 실험에서 "위치 불명확"이 후속 질문을 낳았고, "정확한 파일 경로와 줄을 *의무적으로* 인용"하도록 조항을 조여 3→0으로 해결. 교훈: **내용 억제는 안전하지만 *내용을 가리키는 포인터* 억제는 한 턴 값을 치른다.** (표본 n=9, Claude만 — 크기보다 메커니즘이 근거가 더 강하다고 스스로 밝힘)
- `--mode cache`(기본)에서는 조향이 꺼질 수 있다(`steering_allowed_for`): 조향은 프리픽스 캐시 키에 쓰는 유일한 레버라서.

### 레버 ② 노력 라우팅 (effort routing)
에이전트 루프의 대부분은 기계적 속행(파일 읽기, 테스트 통과)이지만 하네스는 매 턴 `output_config.effort`를 최고로 고정하곤 한다. 사고(thinking)는 출력 토큰으로 청구된다.
```
classify_turn(messages)  ← 구조만 본다(블록 타입·role·is_error). 내용 정규식/키워드 없음
  NEW_USER_ASK            마지막 user가 text/image/document 포함        → effort 유지
  MECHANICAL_CONTINUATION 마지막 user가 tool_result만, 오류 없음        → effort 낮춤
  ERROR_CONTINUATION      tool_result 중 is_error=true                  → effort 유지
  UNKNOWN                 판단 불가                                     → 건드리지 않음
```
- 공급자별: OpenAI는 `reasoning_effort`, Anthropic은 `output_config.effort` 또는 `thinking.budget_tokens`(레거시 모델은 API 하한까지만 clamp). 두 경로 모두 "**낮추기만** 하는 clamp-only 불변식"과 동일한 `output_shaper:*` 라벨.
- 안전 규칙: ⑴ 클라이언트가 보내지 않은 `output_config.effort`는 **주입하지 않음**(미지원 모델은 400) ⑵ `thinking.type`은 **토글하지 않음**(이력에 thinking 블록이 있으면 400 + 메시지 캐시 계층 무효화).

### 측정과 자동 튜닝
- `headroom output-savings` → `Reduction: 31.7% (95% CI 27.7% … 35.7%) [estimated]`. 모델이 *쓰지 않은* 토큰은 볼 수 없어 **반사실적 추정**이며 그렇게 표기.
- 실측: `HEADROOM_OUTPUT_HOLDOUT=0.1` → 대화 10%를 대조군(미조향)으로 두면 대시보드 "Output Tokens Saved"가 `measured`로 바뀌고 밴드 표시.
- `headroom learn --verbosity` (드라이런) / `--apply`: 과거 세션에서 사용자가 긴 답변을 **끊거나 읽기 전에 넘어간** 행동으로 레벨을 추정. 캐시 모드 프록시는 중간 변경이 캐시를 깨므로 학습 레벨을 재읽지 않음 → `--apply`가 `HEADROOM_VERBOSITY_LEVEL`을 고정(재시작 후 유지는 직접 설정).
- 이미 떠 있는 프록시: 이 스위치들은 요청마다 라이브로 읽히며, `headroom wrap`이 재사용한 프록시에는 루프백 `POST /admin/runtime-env`로 핫싱크(전역 적용, 마지막 설정 승리).

## 5.2 `headroom learn` — 실패 학습
```
과거 세션 → Plugin(에이전트별 로그 읽기) → Analyzer(LLM 분석) → Writer(마커 구획 갱신) → 에이전트 네이티브 컨텍스트 파일
  Claude: ~/.claude/projects/*.jsonl · Codex: ~/.codex/sessions/*.json · Gemini: ~/.gemini/tmp/*/chats/session-*.json
```
- **성공 상관(핵심)**: 실패 목록이 아니라 *그 실패를 어떻게 고쳤는지*를 찾는다. 예) `Read axion-formats/.../X.java` 실패 → `Read axion-scala-common/.../X.scala` 성공 ⇒ "X는 `axion-scala-common/`에 있음".
- 학습 항목: 환경 사실(`uv run python`), 파일 경로 교정, 검색 범위, 명령 패턴(사용자가 18번 거부 → 실행 말고 명령만 제시), 큰 파일(offset/limit), 재시도 방지, 권한 메모.
- 출력: Claude → `CLAUDE.local.md`(기본, gitignore) / `--target CLAUDE.md`(팀 공유), Codex → `AGENTS.md`, Gemini → `GEMINI.md`, Grok → `GROK.md`. 재실행 시 중복 없이 교체:
  ```
  <!-- headroom:learn:start --> … <!-- headroom:learn:end -->
  ```
```bash
headroom learn                 # 드라이런
headroom learn --apply         # CLAUDE.local.md 기록
headroom learn --apply --target CLAUDE.md
headroom learn --project ~/my-project --apply
headroom learn --all --apply
```

## 5.3 크로스 에이전트 메모리
`headroom proxy --memory` 또는 `headroom wrap claude|codex|aider --memory` — 프록시를 지나는 **모든 에이전트가 한 저장소 공유**(Claude가 저장 → Codex가 읽음).
```
요청 → 1.메모리 DB 검색 → 2.공급자 네이티브 형식으로 시스템 컨텍스트 주입 → 3.memory_save/search/update/delete 도구 추가
     → 4.업스트림 전달 → 5.응답의 메모리 도구 호출 처리 → 6.비동기 백그라운드 dedup(코사인 >92% 자동 제거)
```
- 저장: 프로젝트별 `{cwd}/.headroom/memory.db`(SQLite + HNSW/FTS5). 프로젝트 간 오염 없음. `--memory-db-path`로 변경.
- 특징: 에이전트 출처(provenance) 기록, 계층 스코프(User→Session→Agent→Turn), 시간적 버전(supersession 체인), 시맨틱+전문검색, 중요 메모리 자동 승격(bubbling), LLM 기반 중복 병합(사용자 자신의 LLM에 편승, 추가 호출 비용 없음).
- 캐시 상호작용: Anthropic `/v1/messages`에서 `--mode cache`는 프리픽스를 지키려 **자동 메모리 주입을 건너뜀**; OpenAI chat/responses·Gemini는 라이브존 꼬리에 덧붙임. Anthropic에서 자동 주입이 필요하면 `--mode token`.
- `headroom memory list|show|stats|edit|delete|prune|purge|export|import`.

## 5.4 SharedContext — 에이전트 간 인계 압축
```python
ctx = SharedContext()
ctx.put("research", big_output, agent="researcher")   # 전체 파이프라인으로 자동 압축 (≈80% 절감 예)
ctx.get("research")                                   # 압축본
ctx.get("research", full=True)                        # 원본
ctx.get_entry("research").savings_percent
```

````


## 6.8 `skills/headroom/references/06-install-and-usage.md`

````markdown
# 06. 설치 · 사용 · 설정

## 6.1 설치
```bash
uv tool install --python 3.13 "headroom-ai[all]"   # 권장: 격리된 CLI 환경
pip install "headroom-ai[all]"                     # Python (CLI 포함)
npm install headroom-ai                            # TypeScript SDK 전용 — headroom 명령 없음
docker pull ghcr.io/headroomlabs-ai/headroom:latest
```
- 요구: Python ≥ 3.10. 세분화 extras: `[proxy] [mcp] [ml](Kompress) [code](tree-sitter) [memory] [vector](HNSW, C++ 툴체인 필요, [all] 제외) [relevance] [image] [agno] [langchain] [evals] [pytorch-mps]`. 어댑터(`langchain/agno/strands/anyllm/bedrock`)는 `[all]`에 미포함.
- 네이티브 휠: macOS Apple Silicon, Linux, Windows(`win_amd64`) 등. Intel macOS는 Docker 권장(ONNX Runtime 문제; `ORT_STRATEGY=system` 우회 가능).
- x86에서 AVX2 없으면 ONNX 기능(Magika 감지, 임베딩 관련성)이 **BM25/휴리스틱으로 폴백**(크래시 없음).
- Codex 등 PATH를 상속 못 하는 MCP 클라이언트는 `command -v headroom` 절대경로를 설정(`args = ["mcp","serve"]`).
- 업데이트: `headroom update [--check] [--pre]` (pip/pipx/uv tool 자동 판별).

## 6.2 에이전트 래핑 (`headroom wrap <tool>`)
| 에이전트 | wrap | 비고 |
|---|:-:|---|
| Claude Code | ✅ | `--memory` `--code-graph` `--1m` `--tool-search` |
| Codex | ✅ | Claude와 메모리 공유 |
| Grok CLI | ✅ | `GROK_MODELS_BASE_URL` 경유 |
| Cursor | 수동 | 프록시 기동 + base URL 출력 |
| Aider / Copilot CLI / Goose / OpenHands / Vibe | ✅ | 프록시 + 실행 |
| VS Code Copilot | ✅ | `wrap vscode` (모델 선택기 유지) |
| Claude Code (VS Code) | ✅ | `wrap vscode-claude [--1m]` |
| OpenClaw | ✅ | ContextEngine 플러그인 |
| OpenCode / Oh My Pi / Cline / Continue | ✅ | 설정 주입 + 프록시 |
| Kimi CLI, ZCode | ✅ | OAuth 전달 / base URL 출력 |
| Cortex Code | 라이브러리만 | 60–65% 절감(라이브러리 모드) |
- `headroom wrap`은 로컬 프록시를 띄우고 **Serena**(시맨틱 코드 탐색 MCP)를 설치/등록(Claude는 `local` 스코프). `--code-memory-scope user`로 전역, `--code-memory none`로 생략.
- 해제: `headroom unwrap <claude|copilot|codex|grok|kimi|omp|opencode|openclaw|zcode|vscode-claude>`.
- 서드파티 OpenAI 호환 공급자(DeepSeek 등)는 `--openai-api-url https://api.deepseek.com/v1` 또는 `OPENAI_TARGET_API_URL` — 아니면 키가 OpenAI로 가서 `401`.
- Copilot 구독 모드: `headroom copilot-auth login` → `headroom wrap copilot --subscription -- --model gpt-4o`.

## 6.3 프록시
```bash
headroom proxy --port 8787
ANTHROPIC_BASE_URL=http://127.0.0.1:8787 claude          # 또는 OpenAI 호환 클라이언트 base URL
headroom proxy --no-optimize | --no-cache | --no-ccr | --no-ccr-proactive-expansion | --memory | --mode cache|token
```
- `--mode cache`(기본): 프리픽스 안정 우선(자동 메모리 주입 생략 등). `--mode token`: 토큰 절감 우선.
- 개발 중 영향 예측: **simulate 모드**(실제 호출 없이 압축 결과 시뮬레이션). 감사만 하려면 SDK `audit` 모드(변경 없이 기록).

## 6.4 SDK
```python
from headroom import compress, CompressConfig
r = compress(messages, model="claude-sonnet-4-5-20250929", config=CompressConfig(protect_recent=2))
```
```ts
import { compress, withHeadroom } from 'headroom-ai'
const msgs = await compress(messages, { model })
const client = withHeadroom(new Anthropic())     // 또는 new OpenAI()
```
LiteLLM `litellm.callbacks=[HeadroomCallback()]` · LangChain `HeadroomChatModel(llm)` · Agno `HeadroomAgnoModel(model)` · ASGI `app.add_middleware(CompressionMiddleware)` · Vercel `wrapLanguageModel({model, middleware: headroomMiddleware()})`.

## 6.5 MCP 도구
| 도구 | 입력 | 출력 |
|---|---|---|
| `headroom_compress` | `content` | `compressed`, `hash`, `original/compressed_tokens`, `savings_percent`, `transforms` |
| `headroom_retrieve` | `hash`, 선택 `query` | `original_content` 또는 검색 `results`, `source: local|proxy` (로컬 저장소 먼저, 없으면 프록시 저장소) |
| `headroom_stats` | — | 압축/검색 횟수, 절감 토큰·%, 추정 절감 USD, 최근 이벤트 10개, 서브에이전트 통계 |
`headroom mcp install|uninstall|status|serve`. 프록시 없이도 온디맨드 압축 가능(자동 전체 압축은 프록시 필요).

## 6.6 점검과 가시화
| 명령 | 용도 |
|---|---|
| `headroom doctor [--network]` | 라우팅 건강검진, `--network`는 업스트림 인증서 서명자·게이트웨이 차단 페이지 진단 |
| `headroom perf` / `headroom dashboard` | 성능, 실시간 절감 대시보드(프록시 필요) |
| `headroom savings` / `headroom output-savings` | 내 트래픽 기준 절감(입력/출력) |
| `headroom inspect` / `headroom evals` | 요청 검사, 평가(`python -m headroom.evals suite --tier 1`) |
| `headroom install apply/status/start/stop/restart/remove` | 영속 서비스 설치 |
- Prometheus 지표·OTel 스팬(`headroom.compression.pipeline/transform`, `gen_ai.request.model`) 제공.

## 6.7 주요 환경변수
| 변수 | 의미 |
|---|---|
| `HEADROOM_OUTPUT_SHAPER`, `HEADROOM_VERBOSITY_LEVEL`, `HEADROOM_OUTPUT_HOLDOUT` | 출력 절감 켜기 / 레벨 0–4 / 대조군 비율 |
| `HEADROOM_DIAGNOSTICS=1` | 메시지별 결정 로그 |
| `HEADROOM_PIPELINE_BREAKER_THRESHOLD`, `…_COOLDOWN_S` | 서킷브레이커 (3 / 60s) |
| `HEADROOM_NET_COST_EXPECTED_READS`, `…_P_ALIVE`, `…_CACHE_TTL_SECONDS` | net-cost 게이트 (10 / 1.0 / 300) |
| `HEADROOM_COMPRESS_WORKERS` | 병렬 압축 워커 수 |
| `HEADROOM_WORKSPACE_DIR`, `HEADROOM_CONFIG_DIR` | 상태/설정 루트 (`~/.headroom`, `~/.headroom/config`) |
| `HEADROOM_BETA_HEADER_STICKY` | 세션 내 `anthropic-beta` 토큰 합집합 재주입(캐시 안정, 기본 enabled) |
| `HEADROOM_BEACON=off`, `DO_NOT_TRACK=1`, `HEADROOM_OFFLINE=1` | 텔레메트리/외부 통신 끄기 |
| `HEADROOM_CA_BUNDLE`, `NODE_EXTRA_CA_CERTS`, `HEADROOM_TLS_STRICT=0` | 사내 SSL 인스펙션 환경 TLS |
| `HEADROOM_UPDATE_CHECK=off` | 업데이트 알림 끄기 |
| `HEADROOM_MODEL_ROUTER_ENABLED=1`, `HEADROOM_MODEL_ROUTES` | 규칙 기반 모델 라우팅(OSS, 옵트인) |
| `HF_HUB_OFFLINE=1`, `HF_ENDPOINT`, `ORT_STRATEGY`, `ORT_LIB_LOCATION` | 모델/ONNX 에어갭·미러 |

## 6.8 사내망 / SSL 인스펙션
- 런타임 TLS는 **OS 인증서 저장소 + certifi**를 사용 → Zscaler/Netskope 루트가 OS에 있으면 보통 무설정.
- 없으면 PEM으로 내보내 `HEADROOM_CA_BUNDLE`. `Basic Constraints of CA cert not marked critical`은 Python 3.13/OpenSSL 3의 `VERIFY_X509_STRICT` 때문 → `HEADROOM_TLS_STRICT=0`(체인·서명·만료·호스트명 검증은 유지).
- 설치 단계 `CERTIFICATE_VERIFY_FAILED`는 maturin이 rustup을 받을 때 발생 → Rust 선설치 또는 `pip install --only-binary headroom-ai headroom-ai`.

````


## 6.9 `skills/headroom/references/07-limitations-and-caveats.md`

````markdown
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

````
