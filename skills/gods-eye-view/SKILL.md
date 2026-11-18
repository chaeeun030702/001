---
name: gods-eye-view
description: God's Eye View(bilawalsidhu/gods-eye-view) 3D 지구본 앱을 본인 PC에 설치하고 Claude Code에 MCP 서버로 등록한다. 사용자가 "gods-eye-view 설치", "God's Eye View 사용법", "지구본으로 항공기·위성·지진 보기", "gev MCP 연결"을 말할 때 사용한다.
---

# God's Eye View 설치·사용 (본인 PC용)

[God's Eye View](https://github.com/bilawalsidhu/gods-eye-view)는 항공기·선박·위성·지진·공공 카메라를 3D 지구본에 보여 주는 브라우저 앱이다.
이 스킬은 앱을 **본인 PC**에 설치하고 Claude Code에 MCP(`gods-eye-view`)로 등록한다.
클라우드 세션에서는 외부 데이터 사이트(USGS 등)가 막혀 있어 조회가 안 되므로 반드시 본인 PC에서 실행한다.

## 설치 (한 번만)
요구: git, Node.js 24.14 이상(24.x) 또는 26.x, Claude Code(`claude`).

- macOS / Linux / WSL: `bash scripts/install.sh`
- Windows(PowerShell): `powershell -ExecutionPolicy Bypass -File scripts\install.ps1`

스크립트가 하는 일
1. 필수 도구·Node 버전 확인 (부족하면 안내 후 중단)
2. `~/gods-eye-view`에 클론 (이미 있으면 `git pull`)
3. `npm ci` 로 의존성 설치
4. `claude mcp add --scope user gods-eye-view -- node <절대경로>/server/mcp/stdio.js --api-base http://localhost:4173` 로 MCP 등록
5. 다음 단계 안내 출력

환경변수: `GEV_DIR`(설치 위치, 기본 `~/gods-eye-view`), `GEV_PORT`(기본 4173), `GEV_SCOPE`(`user`|`local`|`project`, 기본 `user`).

## 사용 (매번)
1. 터미널 하나에서 앱을 켜 둔다: `cd ~/gods-eye-view && npm run dev` (끄지 말 것)
2. Claude Code를 **새로 시작**한다 (이미 열린 세션은 새 MCP를 모른다).
3. 자연어로 묻는다.
   - "Show San Diego in God's Eye View with military flights on."
   - "서울 근처 항공기 보여줘" · "지금 지구 위 지진 목록" · "ISS가 다음에 내 위를 지나가는 시간"
4. Claude Code는 데이터와 **링크**로 답한다. 지구본은 링크를 브라우저에서 열어 본다 (`http://localhost:4173`).

## 점검
- `claude mcp list` 에 `gods-eye-view … Connected` 가 보여야 한다.
- 도구가 `unavailable`이면 `npm run dev` 가 꺼졌거나 인터넷이 막힌 것이다.
- 서버 단독 점검: `node ~/gods-eye-view/server/mcp/stdio.js --api-base http://localhost:4173` → `God's Eye View MCP server reading http://localhost:4173` 출력 후 대기하면 정상.
- 제거: `claude mcp remove gods-eye-view` (앱 폴더는 직접 삭제).

## 선택: API 키로 기능 추가
키 없이도 항공기·군용기·위성·지진·공공 카메라·발사는 나온다. 앱 우측 하단 **POWER UP → Provider Settings** 에서 붙여 넣는다.
Cesium ion(포토리얼 3D) · OpenAI(음성) · AISStream(선박) · NASA FIRMS(화재) · TomTom(교통) · Mapillary(거리뷰).

## 도구 (30개, MCP)
`aircraft_in_area` `find_aircraft` `get_aircraft_track` `vessels_in_area` `satellites_overhead` `next_satellite_pass` `get_earthquakes` `get_active_fires` `get_recent_launches` `find_cctv_cameras` `get_cctv_snapshot` `get_weather_map` `get_cyclones` `situation_brief` `military_awareness` `show_in_gods_eye_view` 등.
위치 인자는 `place`(지명) · `bbox` · `lat/lon/radius_km` 중 하나로 준다.
