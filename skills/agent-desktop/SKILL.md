---
name: agent-desktop
description: vercel-labs/agent-desktop(데스크톱 앱을 OS 접근성 트리로 읽고 조작하는 AI 에이전트용 CLI·C 라이브러리) 사용 가이드. macOS·Windows·Linux 데스크톱 앱의 버튼 클릭, 폼 입력, UI 상태 읽기, 메뉴 탐색, 창 관리, 클립보드, 알림, 스크린샷, MCP 서버 연결, macOS 샌드박스를 다룰 때 사용한다. "agent-desktop", "computer use", "데스크톱 자동화", "접근성 트리", "앱 조작", "snapshot app" 요청에 쓴다.
---

# agent-desktop

AI 에이전트가 **스크린샷·픽셀 매칭 없이** 데스크톱 앱을 보고 조작하게 해 주는 CLI(+C 라이브러리).
앱의 접근성 트리(macOS AX · Windows UI Automation · Linux AT-SPI)를 JSON으로 돌려주고, 조작 가능한 요소마다 `ref`를 붙인다.
모델은 들어 있지 않다. **관찰 → 조작 → 검증 루프는 호출하는 에이전트가 돈다.**

원본: https://github.com/vercel-labs/agent-desktop (Apache-2.0, 기준 커밋 `ce2ddf0`, 2026-11-23)

> 개인정보 주의: snapshot·클립보드·스크린샷·출력에는 화면의 사적인 내용이 들어갈 수 있다. 공개 로그·업로드에 남기지 않는다.

## 1. 설치·첫 실행
```bash
npm install -g agent-desktop        # 또는 brew install agent-desktop (macOS/Linux)
agent-desktop status                # 플랫폼·권한·지원 화면(supported_surfaces)
agent-desktop permissions --guide   # macOS: 손쉬운 사용(Accessibility) 권한 안내
agent-desktop skills get desktop    # 버전에 맞는 공식 가이드(루프·ref·재시도 규칙)
agent-desktop skills get platform   # 현재 OS별 차이
```

## 2. 기본 루프
```bash
agent-desktop snapshot --skeleton --app "Notes" -i --compact   # 얕은 지도 (복잡한 앱)
agent-desktop snapshot --root @s8f3k2p9:e3 -i --compact        # 한 영역만 파고들기
agent-desktop click @s8f3k2p9:e12                              # ref로 조작
agent-desktop snapshot --root @s8f3k2p9:e3 -i --compact        # 같은 영역 다시 읽어 검증
```
- 작은 앱은 skeleton 없이 `snapshot -i` 한 번이면 된다. 아는 요소는 `find`.
- 메뉴·시트·알림창을 여는 동작은 결과의 `data.surfaces`에 그 화면을 알려 준다 → 다음 대상으로.
- 비동기 단계 뒤에는 `wait`. 고정 sleep은 경쟁 조건이다.

## 3. ref 규칙 (가장 많이 틀리는 곳)
- ref는 `@<snapshot_id>:e<N>` 형태로 **그 snapshot에만** 유효. 맨 `@e8`은 `INVALID_ARGS`.
- UI가 바뀌면 `STALE_REF` / `AMBIGUOUS_TARGET` → 새 snapshot의 ref를 쓴다.
- 창이 여러 개면 `AMBIGUOUS_TARGET` → `error.details`의 창 id를 `--window-id`로.
- Windows·Linux에서 똑같이 생긴 쌍둥이 요소(행마다 같은 버튼)는 ref로 구분 불가 → 창 안에서 유일한 컨트롤을 노린다.
- PowerShell에서는 ref를 따옴표로 감싼다(`'@s8f3k2p9:e8'`, `@`는 splatting 연산자).

## 4. 재시도 규칙
- 결과의 `disposition.retry`가 `safe`(= `delivery: not_delivered`)일 때**만** 재시도.
- 그 밖에는 이미 실행됐을 수 있다(두 번 클릭·두 번 제출, `toggle`은 원상복구). `get`/`is`/새 snapshot으로 실제 상태를 읽고 판단.
- 분기는 `error.code`와 `error.disposition`으로. 메시지 문구는 바뀔 수 있다.

## 5. Headless / Headed
- 기본은 headless: 포인터를 움직이거나 포커스를 뺏지 않고 접근성 API로만 동작. 의미 경로가 없으면 **실패로 닫힌다.**
- `--headed`(실제 마우스·키 입력)는 사용자가 명시적으로 허락했을 때만. headless 실패를 headed로 우회하지 않는다.
- 비밀 텍스트는 `type`/`set-value`/`clipboard-set --stdin`으로 넘겨 프로세스 인자에 남기지 않는다.

## 6. MCP 서버
```json
{ "mcpServers": { "agent-desktop": { "command": "agent-desktop", "args": ["mcp"] } } }
```
명령마다 `desktop_snapshot`, `desktop_click` 같은 MCP 도구로 노출되고, 같은 JSON envelope를 돌려준다.

## 7. 명령 그룹 (61개 이름, 57개 동작)
| 그룹 | 명령 |
|---|---|
| 관찰 | snapshot, find, get, is, screenshot, list-surfaces |
| ref 조작 | click, double/triple/right-click, type, set-value, clear, focus, select, toggle, check, uncheck, expand, collapse, scroll, scroll-to |
| 키보드·마우스 | press, hover, drag, mouse-move, mouse-click, mouse-wheel (key/mouse-down·up은 데몬 전까지 거부) |
| 앱·창 | launch, close-app, list-apps/windows/displays, focus/resize/move-window, minimize, maximize, restore, open-system-surface |
| 알림 | list-notifications, dismiss-notification, dismiss-all-notifications, notification-action |
| 클립보드 | clipboard-get, clipboard-set, clipboard-clear |
| 기타 | wait, session, trace, cursor-overlay, sandbox(macOS VM) |

## 8. 참고 문서 (references/)
저장소의 모든 `.md` 파일(77개)을 원래 경로 그대로 넣었다.
- `references/README.md`, `CONCEPTS.md`, `CHANGELOG.md`, `SECURITY.md` — 개요·개념·변경 이력·보안
- `references/skills/agent-desktop/` — 공식 스킬(SKILL.md + commands-observation/interaction/system, workflows)
- `references/skills/agent-desktop-{macos,windows,linux,ffi}/` — OS별·FFI 스킬과 트러블슈팅
- `references/docs/` — install, json-output, faq, releasing, solutions/(실전 오류·베스트 프랙티스)
- `references/probes/`, `references/tests/` — 플랫폼 조사 결과·테스트 안내
- `references/LICENSE` — Apache-2.0
