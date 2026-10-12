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
