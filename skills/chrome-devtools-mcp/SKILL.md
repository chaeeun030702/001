---
name: chrome-devtools-mcp
description: Google 공식 Chrome DevTools MCP(ChromeDevTools/chrome-devtools-mcp)를 Claude Code에 설치하고, 실제 Chrome으로 웹 페이지를 자동화·디버깅·성능 분석한다. 사용자가 "chrome devtools mcp 설치", "브라우저로 페이지 확인", "페이지 성능/LCP 분석", "콘솔 에러·네트워크 요청 확인", "메모리 누수 찾기", "폼 자동 입력 테스트"를 말할 때 사용한다.
---

# Chrome DevTools MCP (설치 · 사용)

[chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) (기준 v1.14.0, 2026-11)는
에이전트가 실제 Chrome을 조작하고 DevTools 수준으로 계측하게 해 주는 MCP 서버다.
도구 63개(13개 카테고리), `--slim` 모드는 3개(navigate · evaluate · screenshot).
요구: Node.js 20.19+ / 22.12+ / 23+, Chrome stable 이상, npm.

## 1. 설치 (본인 PC, 한 번만)

MCP만 (권장 기본값: 임시 프로필 + 통계 끔):
```bash
claude mcp add chrome-devtools --scope user -- npx chrome-devtools-mcp@latest --isolated --no-usage-statistics
```

MCP + 공식 스킬 8개(플러그인):
```
/plugin marketplace add ChromeDevTools/chrome-devtools-mcp
/plugin install chrome-devtools-mcp@chrome-devtools-plugins
```
설치 뒤 Claude Code를 **새로 시작**한다. 확인 프롬프트: `Check the performance of https://developers.chrome.com`

클라우드 세션(이 컨테이너)에서 쓸 때: Chromium이 `/opt/pw-browsers/chromium`에 있으므로
`--headless --executablePath /opt/pw-browsers/chromium` 을 붙인다. 외부 사이트는 환경 네트워크 허용 목록에 따라 막힐 수 있다.

## 2. 플래그 고르기

| 목적 | 플래그 |
|---|---|
| 기존 Chrome(144+)에 붙기 | `--autoConnect` (chrome://inspect/#remote-debugging 에서 원격 디버깅 켜기) 또는 `--browserUrl http://127.0.0.1:9222` |
| 화면 없이 | `--headless` |
| 깨끗한 프로필 | `--isolated` / 로그인 유지용 전용 프로필 `--userDataDir <경로>` |
| 네트워크 목(mock) | `--categoryNetworkMocks` (재시작 필요) |
| 확장 프로그램 테스트 | `--categoryExtensions` (재시작 필요) |
| 힙 스냅샷·메모리 | `--memoryDebugging` |
| PWA / WebAuthn / WebMCP | `--categoryPwa` / `--categoryWebauthn` / `--categoryExperimentalWebmcp` |
| 자동화만, 토큰 절약 | `--slim` |
| 프라이버시 | `--no-usage-statistics`, `--no-performance-crux`, `--redactNetworkHeaders`, `--allowedUrlPattern`, `--javascriptEvaluation=false` |

도구가 목록에 없으면 지어내지 말고, 필요한 플래그와 재시작을 사용자에게 안내한다.

## 3. 핵심 규칙

- 페이지 도구는 `pageId`가 필요하다: `list_pages` 또는 `new_page`의 반환값을 쓴다.
- 요소는 `take_snapshot`의 `uid`로 다룬다(텍스트 기반, 빠르고 결정적). 못 찾으면 스냅샷을 새로 뜬다.
  좌표 클릭(`click_at`)과 스크린샷은 시각 확인이 필요할 때만.
- 순서: `navigate_page`/`new_page` → `wait_for` → `take_snapshot` → `click`/`fill`. 독립 조회만 병렬로.
- 큰 결과는 `filePath`로 파일에 저장하고, `pageSize`·`pageIdx`·`types`로 거른다. 입력 도구는 `includeSnapshot: false`.
- 소스 수정 없이 값 보기: `set_logpoints` → `list_console_messages`.
- 스타일 판단은 `get_css_styles` 결과를 신뢰한다. 그 밖의 런타임 값은 `evaluate_script`.

## 4. 작업별 도구 체인

- **성능/LCP**: `emulate`(CPU 4x, Slow 4G 등 조건 고정) → `performance_start_trace`(reload) →
  `performance_stop_trace` → 인사이트 이름으로 `performance_analyze_insight` → `list_network_requests`로 리소스 타이밍 확인.
  Lighthouse(`lighthouse_audit`)는 보조 지표로만. 전후 비교는 같은 조건에서.
- **콘솔 에러**: `list_console_messages`(types로 error만) → `get_console_message`(소스맵 스택) → 필요하면 `set_logpoints`.
- **네트워크/API**: `list_network_requests`(resourceTypes 필터) → `get_network_request`(헤더·본문) →
  가설 검증은 `mock_network`로 응답 바꿔 재현, 끝나면 `remove_network_mock`.
- **폼·흐름 테스트**: `take_snapshot` → `fill_form`(여러 필드 한 번에) → `click` → `wait_for`(결과 텍스트) → `take_screenshot`(증빙).
- **메모리 누수**: `take_heapsnapshot`(기준) → 동작 반복 → 다시 스냅샷 → `compare_heapsnapshots` → `get_heapsnapshot_retaining_paths`.
- **반응형/디바이스**: `emulate`(viewport·userAgent·네트워크) 또는 `resize_page` → `take_screenshot`.

전체 도구 목록: `references/tools.md`.

## 5. 보안

- 브라우저 내용 전체가 MCP 클라이언트에 노출된다. 평소 로그인된 개인 프로필로 연결하지 않는다.
- 사용 통계는 기본 켜짐(`CI` 또는 `CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS` 환경변수가 있으면 꺼짐).
- 성능 도구는 URL을 CrUX API로 보낼 수 있다(`--no-performance-crux`).

## 6. 흔한 문제

- 도구가 안 보임 → MCP 등록 후 Claude Code 재시작, `claude mcp list`로 확인.
- 플러그인 설치 `Failed to clone repository` → CLI 설치(1번 첫 명령)로 대신한다.
- Chrome 실행 실패 → `--executablePath`로 Chrome 경로 지정, 또는 `--headless`.
- 스킬과 서버 버전 불일치 → `@latest` 갱신 시 스킬도 다시 받는다(도구 이름·파라미터가 바뀜).
- 자세히: https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/troubleshooting.md

## 7. 시각화 분석
아키텍처·도구 분포·초보/숙련 비교: `docs/chrome-devtools-mcp_분석_2026-11-27.html`
