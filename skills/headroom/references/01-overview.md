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
