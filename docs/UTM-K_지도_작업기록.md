# UTM-K 좌표 지도 작업 기록

- 기간: 2026-11-08 ~ 2026-11-18
- 저장소·브랜치: `chaeeun030702/001` · `claude/tender-mayer-je4maf`
- PR: [PR #107](https://github.com/chaeeun030702/001/pull/107) (초안, 열림)
- 이 파일: `docs/UTM-K_지도_작업기록.md`
  - 앞부분: 대화 순서대로 요청과 처리 내용, 결과물 목록
  - 뒷부분(부록): 저장소에 넣은 파일 원문

## 결과물 한눈에 보기

| 결과물 | 아티팩트 | 저장소 파일 |
|---|---|---|
| UTM-K 좌표 지도 (도로명·지명 검색 포함) | https://claude.ai/artifact/PWDf1TAfB3pZUhWr2NDWhG | `docs/UTM-K_좌표지도.html` |
| 지번주소 위치 찾기 (방법 비교) | https://claude.ai/artifact/5FumKm76MNjT2sPksqGzSL | `docs/지번주소_위치표시_방법.html` |
| 이 작업 기록 | https://claude.ai/artifact/CRjmzMmXnh6Jhf3G7dTAEV | `docs/UTM-K_지도_작업기록.md`, `.html` |

## 대화 기록

### 1. PRJ 파일로 지도 홈페이지 만들기

**요청 (2026-11-08)**
> @GRS80_UTMK.prj 해당 파일을 분석해서 지도 기반 홈페이지를 만들고 싶어

**PRJ 분석 결과**
- 이 파일은 **EPSG:5179 (Korea 2000 / Unified CS, UTM-K)**와 같은 정의입니다.
- 서울시청(37.5665°N, 126.9780°E)을 넣으면 X 953,901.17, Y 1,952,032.08이 나옵니다. 파일 원문으로 계산해도, EPSG:5179 표준 정의로 계산해도 같은 값입니다.

| 항목 | 값 | 뜻 |
|---|---|---|
| 측지계 / 타원체 | ITRF2000 / GRS80 (a = 6,378,137 m, 1/f = 298.257222101) | 한국 측지계 2000. WGS84와 차이는 1 m 미만 |
| 투영 | 횡메르카토르(TM) | |
| 원점 | 38°N, 127.5°E | 한반도 전체를 원점 하나로 처리 |
| 원점의 X, Y | 1,000,000 / 2,000,000 m | 좌표가 음수가 되지 않도록 더하는 값 |
| 축척계수 | 0.9996 | |
| 단위 | m | |

**만든 것**
- **지도**: 아티팩트에서는 외부 지도 타일을 불러올 수 없습니다. 그래서 Natural Earth 해안선을 UTM-K로 투영해 캔버스에 직접 그렸습니다.
- **지도 위 표시**: UTM-K 격자, 휘어진 경위선, 중앙자오선, 원점, 주요 도시를 표시합니다.
- **지도 조작**: 클릭하면 핀이 찍히고 X·Y 좌표와 경위도가 나옵니다. 확대·축소와 이동이 되고, 화면 위치에 따라 축척 막대가 바뀝니다.
- **좌표 변환**: 경위도와 UTM-K를 서로 바꾸고, 여러 좌표를 한꺼번에 바꿔 엑셀용으로 복사할 수 있습니다.
- **PRJ 분석 탭**: EPSG 코드를 자동으로 식별하고 매개변수를 해석합니다. 다른 .prj를 열면 그 좌표계로 다시 그립니다.
- **GeoJSON**: 파일을 지도에 끌어다 놓으면 겹쳐 그립니다.
- **배포**: proj4js 2.9.0을 파일에 넣어 HTML 한 파일로 오프라인에서 동작합니다.
- **커밋**: `820d9dc` UTM-K(EPSG:5179) 좌표 지도 홈페이지 추가. 초안 PR #107을 열었습니다.

### 2. 결과물 게시 규칙

**요청**
> 결과물은 항상 아티팩트에 게시

**처리**
- `CLAUDE.md`에 두 가지를 넣었습니다.
  - "결과물은 예외 없이 항상 아티팩트에 게시한다. 파일 전송이나 커밋만으로 끝내지 않는다."는 규칙
  - 지금까지 게시한 결과 아티팩트 주소 목록
- 커밋: `f227423` 작업 규칙: 결과물은 항상 아티팩트에 게시

### 3. 국토지리정보원 1:120만 shp 반영

**요청**
> @kmap_2025_120_korean_shp.zip shp 파일로 올렸어

**shp 분석 결과**
- 파일은 국토지리정보원 대한민국 전도 1:120만(2025)이고, 12개 레이어입니다.
- 12개 레이어의 .prj가 모두 `Korea_2000_Korea_Unified_Coordinate_System`이고, 매개변수가 처음 올린 PRJ와 같습니다. 그래서 좌표를 변환 없이 그대로 썼습니다.
- 속성표(.dbf)는 CP949로 인코딩되어 있습니다.

| 레이어 | 형태 | 개수 | 내용 |
|---|---|---|---|
| KOR_ADMIN_AS | 면 | 9,922 | 행정경계. KG021 시도 42, KG022 시군구, KG023 읍면동. 중국·일본 일부 포함 |
| KOR_COAST_LS | 선 | 3,081 | 해안선 |
| KOR_ROAD_LS | 선 | 1,256 | 고속국도·국도·지방도 (노선명 155종) |
| KOR_RAILW_LS | 선 | 706 | 철도 (노선명 38종) |
| KOR_RIVER_LS | 선 | 1,265 | 하천 (이름 97종) |
| KOR_DZONE_LS | 선 | 1 | 군사분계선 (236.6 km) |
| KOR_LATLO_LS | 선 | 23 | 경위선 |
| KOR_PREMI_PS | 점 | 2,080 | 주요 지명 (시·군·읍·리) |
| KOR_NAME_PS | 점 | 1,361 | 일반 지명 (섬·항구·해수욕장 등) |
| KOR_MOUNT_PS | 점 | 182 | 산 (높이) |
| KOR_CULTU_PS | 점 | 57 | 국립공원·명소 |
| KOR_OCEAN_PS | 점 | 32 | 해양 지명 |

**데이터 정리**
- **단순화**: shapely `coverage_simplify`로 이웃 경계가 어긋나지 않게 줄였습니다. 행정경계는 150~300 m, 도로·철도·하천은 80 m 허용오차입니다.
- **압축**: 좌표를 10 m 정수의 차분값으로 저장했습니다. 데이터는 약 2.8 MB입니다.
- **같은 이름의 시군구 분리**: 원본은 영광군(전남·함남), 고성군(강원·경남)처럼 이름이 같은 시군구를 한 덩어리로 묶고 있었습니다. 상위 시도를 기준으로 나눴습니다.

### 4. 도로명으로 위치 찾기

**요청 (shp 작업 도중)**
> 도로명을 치면 위치를 확인할 수 있도록 만들고 싶어

**만든 것**
- **도로명·지명 검색**: 고속국도·국도·지방도·철도·하천·지명·산·국립공원·시도·시군구·읍면동을 찾습니다. 숫자만 넣으면(예: `77`) 국도 번호로 찾습니다.
- **검색 결과**:
  - 노선 전체를 강조합니다.
  - 구간 수와 길이(UTM-K 평면거리)를 보여 줍니다.
  - 노선 중앙의 좌표·경위도·행정구역과 지나가는 시도·시군구를 보여 줍니다.
- **노선 버튼**: 고속국도와 국도 번호를 버튼으로 고를 수 있습니다.
- **지도 클릭**: 시도·시군구·읍면동 주소와 가까운 도로 이름을 보여 줍니다.
- **레이어**: 레이어별로 켜고 끌 수 있고, 라이트·다크 테마를 지원합니다.
- **한계와 보완**: "세종대로" 같은 도로명주소의 거리 이름은 1:120만 데이터에 없습니다.
  - 그래서 shp(.shp + .dbf + .cpg/.prj)를 브라우저에서 직접 읽는 기능을 넣었습니다.
  - 도로명주소 전자지도의 도로구간 shp를 불러오면 그 도로명으로도 검색됩니다.
  - 시험용 shp(세종대로·테헤란로)로 확인했습니다.
- **확인**: Playwright로 1280px·400px 화면, 라이트·다크 테마에서 열어 봤습니다. 스크립트 오류는 없었고 가로 스크롤도 생기지 않았습니다.
- **커밋**: `39e9ad5` UTM-K 지도: 1:120만 shp 반영, 도로명·지명 검색 추가. 같은 아티팩트 주소에 갱신했습니다.

### 5. 지번주소로 위치 표시하는 방법

**요청**
> 지번주소를 치면 지도에서 위치는 표시하는 방법을 찾아줘

**결론**
- 정리한 문서는 `docs/지번주소_위치표시_방법.html`이고, 아티팩트도 따로 게시했습니다.
- 브이월드·행안부 공식 문서 사이트는 이 작업 환경에서 접속이 막혀 직접 확인하지 못했습니다. API 파라미터와 한도는 기억 기준이라 구현 전에 확인이 필요합니다.

| 방법 | 필요한 것 | 정확도 | 건물 없는 땅 | 아티팩트에서 바로 |
|---|---|---|---|---|
| **A. 연속지적도 shp** (추천) | 시군구별 shp (무료) | 필지 경계 | 찾음 | 됨 |
| B. 브이월드 지오코더 API | 인증키 | 필지 대표점 | 찾음 | 안 됨 (중계 필요) |
| C. 행안부 주소검색 + 좌표제공 API | 인증키 2종 | 건물 출입구 | 못 찾음 | 안 됨 (중계 필요) |
| D. 카카오 로컬 API | REST 키 | 대표점 | 대부분 찾음 | 안 됨 (중계 필요) |

- **방법 A의 원리**:
  - 연속지적도의 PNU(19자리)는 법정동코드 10자리 + 산 여부 1자리 + 본번 4자리 + 부번 4자리입니다.
  - 동·리 이름으로 찾으려면 법정동코드 목록이 필요합니다.
  - 연속지적도는 대개 EPSG:5186이지만, .prj를 읽어 UTM-K로 변환합니다.
- **API 방식(B~D)의 제약**: 아티팩트 페이지는 외부 주소로 요청을 보낼 수 없습니다. 이 세션, GitHub Actions, 작은 서버 중 하나가 API를 대신 불러야 합니다.
- **커밋**: `4e70fa1` 지번주소 위치 표시 방법 비교 문서 추가
- **남은 일**: 연속지적도 shp를 올려 주시거나 쓸 API와 인증키를 정해 주시면 지번 검색을 구현합니다.

### 6. PR #107 지켜보기

- PR 알림을 받도록 설정하고, 2026-11-08에 4번 다시 확인했습니다.
- 매번 상태가 같았습니다. 충돌 없이 합칠 수 있고, 이 저장소에는 PR CI가 없으며 리뷰 댓글도 없었습니다.
- PR 제목과 설명은 기능 추가에 맞게 고쳤습니다.
- 세 번 연속 바뀐 것이 없어서 정기 확인은 멈췄습니다. PR 알림은 계속 받습니다.

### 7. 작업 기록 저장

**요청 (2026-11-18)**
> 전체 기록과 파일을 md 파일로 저장

**처리**
- 이 파일을 만들었습니다.
- 같은 내용의 HTML 판도 만들어 아티팩트로 게시했습니다.

## 커밋 목록 (브랜치 `claude/tender-mayer-je4maf`)

| 커밋 | 내용 |
|---|---|
| `820d9dc` | UTM-K(EPSG:5179) 좌표 지도 홈페이지 추가 |
| `f227423` | 작업 규칙: 결과물은 항상 아티팩트에 게시 |
| `39e9ad5` | UTM-K 지도: 1:120만 shp 반영, 도로명·지명 검색 추가 |
| `4e70fa1` | 지번주소 위치 표시 방법 비교 문서 추가 |
| (이번) | 작업 기록 md·html 추가 |

## 파일 목록

| 파일 | 크기 | 설명 | 원문 수록 |
|---|---|---|---|
| `docs/UTM-K_좌표지도.html` | 2.8 MB | UTM-K 좌표 지도 완성본 (proj4js·지도 데이터 포함, 오프라인 동작) | 용량 때문에 생략 (템플릿+데이터로 다시 만들 수 있음) |
| `docs/지번주소_위치표시_방법.html` | 11.7 KB | 지번주소 위치 표시 방법 비교 문서 | 부록 수록 |
| `docs/utmk_map/README.md` | 0.7 KB | 지도 소스 폴더 설명 | 부록 수록 |
| `docs/utmk_map/GRS80_UTMK.prj` | 0.4 KB | 처음 올린 투영 정의 (EPSG:5179) | 부록 수록 |
| `docs/utmk_map/KOR_kmap120_UTMK.prj` | 0.4 KB | 1:120만 shp의 투영 정의 (같은 UTM-K) | 부록 수록 |
| `docs/utmk_map/build_kmap.py` | 4.4 KB | shp 12개 레이어 → 단순화한 kmap.json | 부록 수록 |
| `docs/utmk_map/build_html.js` | 1.1 KB | 템플릿 + proj4js + 데이터 → 완성본 HTML | 부록 수록 |
| `docs/utmk_map/template.html` | 63.3 KB | 지도 페이지 템플릿 (화면·검색·shp 읽기 코드) | 부록 수록 |
| `CLAUDE.md` | 3.8 KB | 작업 규칙 (아티팩트 게시 규칙·주소 목록 추가) | 부록 수록 |

### 저장소에 넣지 않은 파일
- **올린 원본 `kmap_2025_120_korean_shp.zip`** (29 MB): 용량 때문에 넣지 않았습니다.
  - 국토지리정보원에서 다시 받을 수 있습니다.
  - 압축 안 파일 이름은 `KOR_*_KO`(원래 이름은 `_국문`)입니다.
- **중간 산출물 `kmap.json`** (약 2.8 MB): 저장소에 따로 넣지 않았습니다. 완성본 HTML 안에 들어 있습니다.
- **빌드 스크립트의 경로 주의**: `build_kmap.py`와 `build_html.js`는 작업할 때의 임시 폴더 경로(`kmap/`, `template2.html`, 업로드 경로)를 그대로 가리킵니다.
  - 다시 빌드하려면 다음처럼 경로를 맞춰야 합니다.
    1. shp를 `kmap/` 폴더에 풀어 둡니다.
    2. `template.html`을 `template2.html`로 복사합니다.
    3. proj4js(`dl/proj4-2.9.0/package/dist/proj4.js`)를 받아 둡니다.

## 부록: 파일 원문

### `docs/지번주소_위치표시_방법.html`

지번주소 위치 표시 방법 비교 문서

````html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>지번주소 위치 찾기</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">
<style>
/* 레이아웃: 한 단 문서. 결론 → 방법 비교표 → 방법별 상세 → 지도에 붙이는 구조 → 확인 필요 항목 */
:root{
  --bg:#f4f7f8; --panel:#ffffff; --fg:#17242e; --muted:#5b6b77; --line:#d3dce2;
  --accent:#0b6e99; --accent-ink:#fff; --good:#1d7a4c; --warn:#a15c00; --bad:#b0273a; --chip:#e7eff3;
  --f-body:"IBM Plex Sans KR",system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0f171d; --panel:#151f27; --fg:#e3eaee; --muted:#93a3ae; --line:#2a3843;
  --accent:#4fb3dd; --accent-ink:#06141b; --good:#5fd39a; --warn:#f0b35a; --bad:#ff7d8c; --chip:#1f2c35; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0f171d; --panel:#151f27; --fg:#e3eaee; --muted:#93a3ae; --line:#2a3843;
  --accent:#4fb3dd; --accent-ink:#06141b; --good:#5fd39a; --warn:#f0b35a; --bad:#ff7d8c; --chip:#1f2c35; color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:15px;line-height:1.65}
.wrap{max-width:900px;margin:0 auto;padding-block:32px 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:28px}
h1{font-size:26px;line-height:1.3;margin:0;text-wrap:balance;letter-spacing:-.01em}
h2{font-size:18px;margin:0 0 10px;text-wrap:balance}
h3{font-size:15.5px;margin:0 0 6px}
p{margin:0 0 10px;max-width:68ch}
.lede{color:var(--muted);margin-top:6px}
.answer{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:8px;padding:16px 18px}
.answer p:last-child{margin-bottom:0}
.tbl{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--panel)}
table{border-collapse:collapse;width:100%;min-width:720px;font-size:13.5px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;color:var(--muted);font-weight:500;background:var(--chip)}
tr:last-child td{border-bottom:0}
.y{color:var(--good);font-weight:500}.m{color:var(--warn);font-weight:500}.n{color:var(--bad);font-weight:500}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px 18px;display:flex;flex-direction:column;gap:4px}
.card .tag{font-size:12px;color:var(--muted)}
.card.rec{border-color:var(--accent)}
.pill{display:inline-block;font-size:11.5px;padding:1px 8px;border-radius:999px;background:var(--accent);color:var(--accent-ink);font-weight:500;margin-left:6px;vertical-align:2px}
ul{margin:4px 0 8px;padding-left:20px}
li{margin:2px 0;max-width:66ch}
code,pre{font-family:var(--f-mono);font-size:12.5px}
code{background:var(--chip);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
pre{background:var(--chip);border-radius:6px;padding:10px 12px;overflow-x:auto;margin:6px 0 4px;line-height:1.5}
.flow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.flow div{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-size:13.5px}
.flow b{display:block;font-size:12px;color:var(--accent);margin-bottom:2px}
.note{font-size:13.5px;color:var(--muted)}
.check{background:var(--panel);border:1px dashed var(--warn);border-radius:8px;padding:14px 18px}
@media (max-width:640px){.flow{grid-template-columns:1fr 1fr}h1{font-size:22px}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>지번주소를 치면 지도에 위치 표시하기</h1>
    <p class="lede">UTM-K 좌표 지도(아티팩트)에 지번 검색을 붙이는 방법을 비교했습니다. 2026-11-08 작성.</p>
  </header>

  <section class="answer">
    <h2>결론</h2>
    <p><b>필지 경계까지 정확히 보려면 연속지적도 shp를 지도에 불러와 지번을 찾는 방법을 권합니다.</b> 인터넷 API 없이 지도 페이지 안에서 바로 동작하고, 아티팩트의 보안 제한에도 걸리지 않습니다. 시군구 단위로 내려받아 쓰면 됩니다.</p>
    <p>전국 어디든 지번 한 줄만 치면 나오게 하려면 <b>지오코딩 API(브이월드·행안부 주소·카카오)</b>가 필요합니다. 다만 아티팩트 페이지는 외부 API를 직접 부를 수 없으니, 중간에서 API를 대신 불러 줄 곳이 있어야 합니다. 이 Claude 세션이나 GitHub Actions, 작은 서버가 그 역할을 할 수 있습니다.</p>
  </section>

  <section>
    <h2>방법 비교</h2>
    <div class="tbl"><table>
      <tr><th>방법</th><th>필요한 것</th><th>정확도</th><th>건물 없는 땅</th><th>아티팩트에서 바로</th><th>좌표계</th></tr>
      <tr><td><b>A. 연속지적도 shp</b></td><td>시군구별 shp 파일 (무료)</td><td class="y">필지 경계</td><td class="y">됨</td><td class="y">됨</td><td>보통 EPSG:5186, .prj로 자동 변환</td></tr>
      <tr><td><b>B. 브이월드 지오코더</b></td><td>인증키 (무료)</td><td class="y">필지 대표점</td><td class="y">됨 (지번 검색 지원)</td><td class="n">안 됨 (중계 필요)</td><td>요청할 때 좌표계 지정</td></tr>
      <tr><td><b>C. 행안부 주소검색 + 좌표제공 API</b></td><td>인증키 2종 (무료)</td><td class="m">건물 출입구</td><td class="n">건물 없으면 못 찾음</td><td class="n">안 됨 (중계 필요)</td><td>UTM-K로 받음</td></tr>
      <tr><td><b>D. 카카오 로컬 API</b></td><td>REST 키 (무료 한도)</td><td class="m">대표점</td><td class="m">대부분 됨</td><td class="n">안 됨 (중계 필요)</td><td>WGS84 → UTM-K 변환</td></tr>
    </table></div>
    <p class="note" style="margin-top:8px">"중계 필요": 아티팩트 페이지는 보안 정책상 외부 주소로 요청을 보낼 수 없습니다. 페이지 대신 API를 불러 결과를 넘겨 주는 곳이 있어야 합니다.</p>
  </section>

  <section class="card rec">
    <div class="tag">방법 A</div>
    <h3>연속지적도 shp를 지도에 불러와 지번 검색<span class="pill">추천</span></h3>
    <ul>
      <li><b>받는 곳</b>: 브이월드 오픈마켓·국가공간정보포털의 "연속지적도". 시군구별 shp로 받습니다. 파일 이름은 보통 <code>LSMD_CONT_LDREG_시군구코드.shp</code>입니다.</li>
      <li><b>들어 있는 정보</b>: 필지 다각형과 <code>PNU</code>(19자리 필지고유번호), <code>JIBUN</code>(예: <code>123-4대</code>).</li>
      <li><b>PNU 구조</b>: 법정동코드 10자리, 산 여부 1자리(1=일반, 2=산), 본번 4자리, 부번 4자리로 되어 있습니다. 예를 들어 "와우리 123-4"는 <code>법정동코드 + 1 + 0123 + 0004</code>입니다.</li>
      <li><b>검색 방식</b>: 지번 숫자로 찾고, 같은 번지가 여러 동·리에 있으면 법정동코드 앞자리로 고르게 합니다.
        <ul>
          <li>동·리 이름으로 고르려면 법정동코드 목록(행정표준코드관리시스템의 법정동코드 전체자료)이 필요합니다.</li>
          <li>이 목록을 페이지에 넣어 두면 <code>봉담읍 와우리 123-4</code>처럼 이름으로 칠 수 있습니다.</li>
        </ul>
      </li>
      <li><b>좌표계</b>: 연속지적도는 대개 GRS80 중부원점(EPSG:5186)입니다. 지도가 함께 들어 있는 .prj를 읽어 UTM-K로 바꿔 겹칩니다. 이 변환 기능은 이미 만들어 둔 shp 불러오기에 들어 있습니다.</li>
      <li><b>장점</b>: 필지 경계를 강조하고 면적·지목까지 보여 줄 수 있습니다. 키나 인터넷이 필요 없습니다.</li>
      <li><b>한계</b>: 시군구 하나도 수십 MB가 될 수 있습니다. 전국 단위로는 무겁습니다.</li>
    </ul>
  </section>

  <section class="card">
    <div class="tag">방법 B</div>
    <h3>브이월드 지오코더 API (주소 → 좌표)</h3>
    <ul>
      <li>국토교통부 공간정보 오픈플랫폼의 API로, 지번주소(필지)와 도로명주소를 모두 좌표로 바꿉니다.</li>
      <li>요청 모양은 아래와 같습니다(기억 기준, 문서로 확인 필요).
        <pre>https://api.vworld.kr/req/address?service=address&amp;request=getcoord&amp;version=2.0
  &amp;type=parcel&amp;crs=epsg:5179&amp;format=json&amp;key=인증키
  &amp;address=경기도 화성시 봉담읍 와우리 123-4</pre></li>
      <li><code>type=parcel</code>이 지번, <code>type=road</code>가 도로명입니다. <code>crs</code>로 결과 좌표계를 고를 수 있어 UTM-K로 바로 받을 수 있습니다.</li>
      <li>인증키는 무료지만 발급할 때 사용할 도메인이나 서비스를 등록합니다. 일일 호출 한도가 있습니다.</li>
    </ul>
  </section>

  <section class="card">
    <div class="tag">방법 C</div>
    <h3>행정안전부 주소검색 API + 좌표제공 API</h3>
    <ul>
      <li>주소기반산업지원서비스(business.juso.go.kr)의 API입니다. 검색 API에 지번을 넣으면 도로명주소와 매칭된 결과를 줍니다.</li>
      <li>이 결과의 행정구역코드, 도로명코드, 지하여부, 건물본번·부번을 좌표제공 API에 넘기면 UTM-K 좌표(<code>entX</code>, <code>entY</code>, 건물 출입구 기준)를 줍니다.</li>
      <li>지도와 좌표계가 같아 변환이 필요 없습니다. 다만 <b>도로명주소가 부여된 건물이 있는 지번만</b> 찾을 수 있습니다. 논밭·임야 같은 빈 땅은 찾지 못합니다.</li>
    </ul>
  </section>

  <section class="card">
    <div class="tag">방법 D</div>
    <h3>카카오 로컬 API (주소 검색)</h3>
    <ul>
      <li><code>/v2/local/search/address.json?query=지번주소</code>로 경위도(WGS84)를 받아, 지도의 proj4로 UTM-K로 바꿉니다.</li>
      <li>주소를 덜 정확하게 쳐도 잘 찾습니다. 상용 서비스라 이용약관과 일일 한도를 따라야 합니다.</li>
    </ul>
  </section>

  <section>
    <h2>API를 쓸 때 지도에 붙이는 구조</h2>
    <div class="flow">
      <div><b>1. 입력</b>지도 페이지에 지번 입력</div>
      <div><b>2. 중계</b>이 Claude 세션·GitHub Actions·작은 서버가 API 호출</div>
      <div><b>3. 저장</b>결과 좌표를 아티팩트 데이터(db)에 기록</div>
      <div><b>4. 표시</b>페이지가 좌표를 받아 핀 표시</div>
    </div>
    <p class="note" style="margin-top:8px">한 번에 많은 지번을 처리할 때는 목록을 주시면 이 세션이 API로 일괄 변환해 지도 핀으로 넣는 방식이 가장 간단합니다. 이 경우 API 호스트를 이 작업 환경의 네트워크 허용 목록에 추가하고 인증키를 등록해야 합니다.</p>
  </section>

  <section class="check">
    <h2>확인이 필요한 부분</h2>
    <p>이 작업 환경에서는 vworld.kr과 juso.go.kr 문서에 접속할 수 없어, 아래 항목을 공식 문서로 직접 확인하지 못했습니다. 구현 전에 확인하겠습니다.</p>
    <ul>
      <li>브이월드 지오코더의 정확한 파라미터 이름, 받을 수 있는 좌표계 목록, 일일 한도, 브라우저에서 직접 부를 수 있는지(CORS)</li>
      <li>행안부 좌표제공 API의 요청 필드 이름과 좌표 기준(출입구인지 건물 중심인지)</li>
      <li>내려받은 연속지적도 shp의 실제 필드 구성과 .prj 좌표계(지역·배포처마다 다를 수 있음)</li>
    </ul>
  </section>
</div>
</body>
</html>
````

### `docs/utmk_map/README.md`

지도 소스 폴더 설명

````markdown
# UTM-K 좌표 지도 소스

- `../UTM-K_좌표지도.html` — 완성본(HTML 한 파일, 오프라인 동작). 아티팩트: https://claude.ai/artifact/PWDf1TAfB3pZUhWr2NDWhG
- `GRS80_UTMK.prj` — 처음 올린 투영 정의(EPSG:5179와 같음)
- `KOR_kmap120_UTMK.prj` — 국토지리정보원 대한민국 전도 1:120만(2025) shp의 투영 정의(같은 UTM-K)
- `build_kmap.py` — shp 12개 레이어를 화면용으로 단순화해 `kmap.json`으로 만든다(pyshp, shapely 2.1+). shp 원본은 용량(29 MB) 때문에 저장소에 넣지 않았다.
- `template.html`, `build_html.js` — 템플릿에 proj4js·WKT·kmap.json을 넣어 완성본을 만든다.
````

### `docs/utmk_map/GRS80_UTMK.prj`

처음 올린 투영 정의 (EPSG:5179)

````text
PROJCS["PCS_ITRF2000_TM",GEOGCS["GCS_ITRF_2000",DATUM["D_ITRF_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",1000000.0],PARAMETER["False_Northing",2000000.0],PARAMETER["Central_Meridian",127.5],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",38.0],UNIT["Meter",1.0]]
````

### `docs/utmk_map/KOR_kmap120_UTMK.prj`

1:120만 shp의 투영 정의 (같은 UTM-K)

````text
PROJCS["Korea_2000_Korea_Unified_Coordinate_System",GEOGCS["GCS_Korea_2000",DATUM["D_Korea_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",1000000.0],PARAMETER["False_Northing",2000000.0],PARAMETER["Central_Meridian",127.5],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",38.0],UNIT["Meter",1.0]]
````

### `docs/utmk_map/build_kmap.py`

shp 12개 레이어 → 단순화한 kmap.json

````python
import shapefile, json, collections as C, shapely, sys
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
D='kmap/'
def R(n): return shapefile.Reader(D+n,encoding='cp949')
Q=10.0; X0=595000; Y0=1333000
def enc_line(coords):
    out=[]; px=py=0
    for x,y in coords:
        ix=round((x-X0)/Q); iy=round((y-Y0)/Q)
        if out and ix==px and iy==py: continue
        out+= [ix-px, iy-py] if out else [ix,iy]; px,py=ix,iy
    return out
def polys(g):
    return list(g.geoms) if g.geom_type=='MultiPolygon' else ([g] if g.geom_type=='Polygon' else [p for p in getattr(g,'geoms',[]) if p.geom_type=='Polygon'])
def enc_poly(g, minarea):
    rings=[]
    for p in polys(g):
        if p.area<minarea: continue
        rings.append(enc_line(p.exterior.coords))
        for h in p.interiors:
            if shapely.Polygon(h).area>=minarea: rings.append(enc_line(h.coords))
    return [r for r in rings if len(r)>=6]
admin=C.defaultdict(lambda:C.defaultdict(list))
for sr in R('KOR_ADMIN_AS_KO').iterShapeRecords():
    g=shape(sr.shape.__geo_interface__)
    if not g.is_valid: g=g.buffer(0)
    admin[sr.record['FTR_CDE']][sr.record['MNG_NAM']].append(g)
def simp(geoms,tol):
    try: return shapely.coverage_simplify(geoms,tol)
    except Exception as e: print('cov fail',e,file=sys.stderr); return [g.simplify(tol) for g in geoms]
def grouped(code,parents):
    # parents: (names, geoms, tree) -> group raw polygons by (name, parent)
    pn,pg,pt=parents; groups=C.defaultdict(list)
    for n,gs in admin[code].items():
        for g in gs:
            p=g.representative_point(); par=''
            for i in pt.query(p):
                if pg[i].contains(p) and pn[i]: par=pn[i]; break
            groups[(n,par)].append(g)
    keys=list(groups); geoms=[unary_union(groups[k]) for k in keys]
    return keys,geoms
FOREIGN=set('랴오닝성 프리모르스키크라이 내이멍구자치구 지린성 히로시마현 야마구치현 시마네현 가고시마현 미야자키현 오이타현 후쿠오카현 사가현 나가사키현 구마모토현 에히메현'.split())
NORTH=set('황해남도 황해북도 평안북도 평안남도 자강도 양강도 함경남도 함경북도 강원도 평양직할시 남포특별시 라선특별시 개성특별시'.split())
sn=list(admin['KG021']); sg=[unary_union(admin['KG021'][n]) for n in sn]; ss=simp(sg,300)
gk,gg=grouped('KG022',(sn,sg,STRtree(sg))); gs=simp(gg,150)
gfull=[(k[1]+' '+k[0]).strip() for k in gk]
ek,eg=grouped('KG023',(gfull,gg,STRtree(gg))); es=simp(eg,150)
out={'q':Q,'x0':X0,'y0':Y0}
def kind(n): return 'f' if n in FOREIGN else ('n' if n in NORTH else ('?' if n=='' else 'k'))
def lab(g):
    p=max(polys(g),key=lambda q:q.area).representative_point() if polys(g) else g.representative_point()
    return [round((p.x-X0)/Q),round((p.y-Y0)/Q)]
out['sido']=[{'n':n,'k':kind(n),'l':lab(g),'r':enc_poly(s,150000)} for n,g,s in zip(sn,sg,ss)]
out['sgg']=[{'n':k[0],'p':k[1],'r':enc_poly(s,80000)} for k,s in zip(gk,gs) if k[0]]
out['emd']=[{'n':k[0],'p':k[1],'r':enc_poly(s,50000)} for k,s in zip(ek,es) if k[0]]
for k in ('sido','sgg','emd'): out[k]=[f for f in out[k] if f['r']]
def lines(name,fld,tol):
    res=[]
    for sr in R(name).iterShapeRecords():
        g=shape(sr.shape.__geo_interface__).simplify(tol)
        parts=list(g.geoms) if g.geom_type.startswith('Multi') else [g]
        nm=sr.record[fld] if fld else ''
        for p in parts:
            e=enc_line(p.coords)
            if len(e)>=4: res.append([nm,e])
    return res
out['river']=lines('KOR_RIVER_LS_KO','RIV_NAM',80)
out['road']=lines('KOR_ROAD_LS_KO','ROD_NAM',80)
out['rail']=lines('KOR_RAILW_LS_KO','RAL_NAM',80)
out['dmz']=lines('KOR_DZONE_LS_KO',None,40)
def pts(name,fld,extra=None):
    res=[]
    for sr in R(name).iterShapeRecords():
        x,y=sr.shape.points[0]; v=[sr.record[fld].strip(),round((x-X0)/Q),round((y-Y0)/Q)]
        if extra: v.append(sr.record[extra])
        if v[0]: res.append(v)
    return res
out['place']=pts('KOR_PREMI_PS_KO','MNG_NAM'); out['name']=pts('KOR_NAME_PS_KO','KOR_NAM')
out['mount']=pts('KOR_MOUNT_PS_KO','MOT_NAM','MOT_HIG'); out['cultu']=pts('KOR_CULTU_PS_KO','CUL_NAM'); out['ocean']=pts('KOR_OCEAN_PS_KO','OCN_NAM')
s=json.dumps(out,ensure_ascii=False,separators=(',',':'))
open('kmap.json','w').write(s)
for k,v in out.items():
    if isinstance(v,list): print(k,len(v),len(json.dumps(v,ensure_ascii=False,separators=(',',':'))))
print('total',len(s.encode()))
````

### `docs/utmk_map/build_html.js`

템플릿 + proj4js + 데이터 → 완성본 HTML

````javascript
const fs=require('fs');
const t=fs.readFileSync('template2.html','utf8');
const wkt=fs.readFileSync('/root/.claude/uploads/cfb0efa6-afac-5a01-9767-ff492ebaad56/19fe2d92-GRS80_UTMK.prj','utf8').trim();
const dprj=fs.readFileSync('kmap/KOR_ROAD_LS_KO.prj','utf8').trim();
const km=fs.readFileSync('kmap.json','utf8');
const fill=(s,p)=>s.replace('/*PROJ4*/',()=>p).replace('/*WKT*/',()=>JSON.stringify(wkt)).replace('/*DATAPRJ*/',()=>JSON.stringify(dprj)).replace('/*KMAP*/',()=>km);
fs.writeFileSync('utmk_map.html',fill(t,'<script src="https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.9.0/proj4.js"></script>'));
const lib=fs.readFileSync('dl/proj4-2.9.0/package/dist/proj4.js','utf8');
const full='<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>body{margin:0}[hidden]{display:none!important}</style>\n'+fill(t,'<script>/* proj4js 2.9.0 (MIT) */\n'+lib+'</script>').replace('<div class="app">','</head>\n<body>\n<div class="app">')+'\n</body>\n</html>\n';
fs.writeFileSync('/home/user/001/docs/UTM-K_좌표지도.html',full);
````

### `docs/utmk_map/template.html`

지도 페이지 템플릿 (화면·검색·shp 읽기 코드)

````html
<title>UTM-K 좌표 지도</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">
<style>
/* 레이아웃: 왼쪽은 국토지리정보원 1:120만 shp를 UTM-K 미터 좌표 그대로 그린 캔버스 지도, 오른쪽은 도로명 검색·좌표 변환·데이터 패널(좁은 화면에선 아래로) */
:root{
  --bg:#eef2f4; --panel:#ffffff; --fg:#17242e; --muted:#5b6b77; --line:#d3dce2;
  --sea:#d6e3ea; --land:#fbfbf9; --land-n:#f1f0ea; --land-f:#e6e9e8; --border:#8a9aa5; --border-s:#2f4a5c;
  --river:#3f8fc0; --road:#c9741a; --rail:#3b3f44; --dmz:#c0262d;
  --grid:#0b6e99; --grat:#8a7f6a; --cm:#b0127a; --pin:#b0127a; --hl:#e0108a; --accent:#0b6e99; --accent-ink:#ffffff;
  --chip:#e7eff3; --user:#7b3fd1;
  --f-body:"IBM Plex Sans KR",system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0f171d; --panel:#151f27; --fg:#e3eaee; --muted:#93a3ae; --line:#2a3843;
  --sea:#0c1820; --land:#1d2a33; --land-n:#1a252d; --land-f:#151e25; --border:#4b5f6d; --border-s:#9cc6dc;
  --river:#4ea3d6; --road:#e09a4a; --rail:#c9d1d7; --dmz:#ff6b6b;
  --grid:#4fb3dd; --grat:#a89a7c; --cm:#ef5fb8; --pin:#ef5fb8; --hl:#ff4fb0; --accent:#4fb3dd; --accent-ink:#06141b;
  --chip:#1f2c35; --user:#b48cff; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0f171d; --panel:#151f27; --fg:#e3eaee; --muted:#93a3ae; --line:#2a3843;
  --sea:#0c1820; --land:#1d2a33; --land-n:#1a252d; --land-f:#151e25; --border:#4b5f6d; --border-s:#9cc6dc;
  --river:#4ea3d6; --road:#e09a4a; --rail:#c9d1d7; --dmz:#ff6b6b;
  --grid:#4fb3dd; --grat:#a89a7c; --cm:#ef5fb8; --pin:#ef5fb8; --hl:#ff4fb0; --accent:#4fb3dd; --accent-ink:#06141b;
  --chip:#1f2c35; --user:#b48cff; color-scheme:dark}
html,body{height:100%}
body{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:14px;line-height:1.5}
.app{display:grid;grid-template-rows:auto 1fr;height:100%;min-height:600px}
header.top{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding-block:10px;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  border-bottom:1px solid var(--line);background:var(--panel)}
.brand{display:flex;align-items:baseline;gap:10px;min-width:0;flex-wrap:wrap}
.brand h1{font-size:17px;margin:0;font-weight:700;letter-spacing:-.01em}
.brand .epsg{font-family:var(--f-mono);font-size:12px;color:var(--muted)}
.prjname{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted);min-width:0;flex-wrap:wrap}
.prjname code{font-family:var(--f-mono);color:var(--fg);background:var(--chip);padding:2px 6px;border-radius:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:46vw}
.btn{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--panel);color:var(--fg);padding:6px 10px;border-radius:6px;cursor:pointer;display:inline-block}
.btn:hover{border-color:var(--accent)}
.btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.btn:focus-visible,input:focus-visible,textarea:focus-visible,[role=tab]:focus-visible,.res:focus-visible,.chip:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.main{display:grid;grid-template-columns:minmax(0,1fr) 400px;min-height:0}
.mapwrap{position:relative;min-height:0;overflow:hidden;background:var(--sea);touch-action:none}
canvas#map{display:block;width:100%;height:100%;cursor:crosshair}
.readout{position:absolute;left:max(10px,env(safe-area-inset-left,0px));bottom:10px;background:var(--panel);border:1px solid var(--line);border-radius:6px;
  padding:6px 10px;font-family:var(--f-mono);font-size:12px;font-variant-numeric:tabular-nums;line-height:1.45;pointer-events:none;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.readout b{font-weight:500;color:var(--muted);display:inline-block;width:52px;font-family:var(--f-body)}
.zoom{position:absolute;right:max(10px,env(safe-area-inset-right,0px));top:10px;display:flex;flex-direction:column;gap:4px}
.zoom .btn{width:34px;height:34px;padding:0;font-size:17px;line-height:1}
.mapsearch{position:absolute;left:max(10px,env(safe-area-inset-left,0px));top:10px;width:min(340px,calc(100% - 70px));display:flex;gap:6px}
.mapsearch input{flex:1;min-width:0;box-shadow:0 1px 3px rgba(0,0,0,.15)}
.drop{position:absolute;inset:0;border:3px dashed var(--accent);background:color-mix(in srgb,var(--accent) 10%,transparent);display:grid;place-items:center;font-weight:700;color:var(--accent);text-align:center;padding:20px}
aside{border-left:1px solid var(--line);background:var(--panel);display:flex;flex-direction:column;min-height:0}
.tabs{display:flex;border-bottom:1px solid var(--line);padding-inline:8px;overflow-x:auto}
.tabs [role=tab]{font:inherit;font-size:13px;background:none;border:0;border-bottom:2px solid transparent;color:var(--muted);padding:10px 10px;cursor:pointer;white-space:nowrap}
.tabs [role=tab][aria-selected=true]{color:var(--fg);border-bottom-color:var(--accent);font-weight:700}
.pane{overflow:auto;padding:16px;display:flex;flex-direction:column;gap:18px;min-height:0;flex:1}
.pane h2{font-size:13px;margin:0 0 8px;letter-spacing:.02em;color:var(--muted);font-weight:500}
.field-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
label.f{display:flex;flex-direction:column;gap:3px;font-size:12px;color:var(--muted)}
input[type=text],input[type=search],textarea{font-family:var(--f-body);font-size:14px;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:7px 9px;width:100%;box-sizing:border-box}
.mono,textarea,.field-row input{font-family:var(--f-mono)!important;font-size:13px!important;font-variant-numeric:tabular-nums}
.mapsearch input{background:var(--panel)}
textarea{min-height:92px;resize:vertical}
.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.result{font-family:var(--f-mono);font-size:12.5px;background:var(--chip);border-radius:6px;padding:8px 10px;font-variant-numeric:tabular-nums;word-break:break-all}
.small{font-size:12px;color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th,td{text-align:left;padding:6px 6px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:500;color:var(--muted);font-size:12px}
td.num{font-family:var(--f-mono);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.tblwrap{overflow-x:auto}
.reslist{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.res{font:inherit;text-align:left;background:var(--panel);color:var(--fg);border:0;border-bottom:1px solid var(--line);padding:8px 10px;cursor:pointer;display:grid;grid-template-columns:1fr auto;gap:2px 10px;align-items:baseline}
.res:last-child{border-bottom:0}
.res:hover,.res[aria-current=true]{background:var(--chip)}
.res .nm{font-weight:500;min-width:0;overflow-wrap:anywhere}
.res .meta{grid-column:1/-1;font-size:12px;color:var(--muted)}
.tag{font-size:11px;padding:1px 7px;border-radius:999px;border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.tag.road{border-color:var(--road);color:var(--road)} .tag.rail{border-color:var(--rail);color:var(--rail)} .tag.river{border-color:var(--river);color:var(--river)} .tag.user{border-color:var(--user);color:var(--user)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font:inherit;font-size:12px;border:1px solid var(--line);background:var(--panel);color:var(--fg);padding:3px 9px;border-radius:999px;cursor:pointer;font-variant-numeric:tabular-nums}
.chip:hover{border-color:var(--road)}
.detail{border:1px solid var(--line);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px}
.detail .big{font-size:17px;font-weight:700;line-height:1.3}
.kv{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;font-size:12.5px}
.kv dt{color:var(--muted)} .kv dd{margin:0;font-family:var(--f-mono);font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.kv dd.t{font-family:var(--f-body)}
.id-card{border:1px solid var(--line);border-radius:8px;padding:12px}
.id-card .big{font-size:16px;font-weight:700}
.pill{display:inline-block;font-size:11px;padding:1px 7px;border-radius:999px;background:var(--accent);color:var(--accent-ink);font-weight:500;vertical-align:2px}
.pill.warn{background:var(--chip);color:var(--fg);border:1px solid var(--line)}
pre.wkt{font-family:var(--f-mono);font-size:11.5px;background:var(--chip);border-radius:6px;padding:10px;white-space:pre-wrap;word-break:break-all;margin:0;line-height:1.55}
.pk{font-family:var(--f-mono);font-size:11px;color:var(--muted);letter-spacing:.02em}
.pv{font-family:var(--f-mono);font-size:13px;font-weight:500;word-break:break-all;margin:1px 0 2px}
.layer{display:grid;grid-template-columns:auto 22px 1fr auto;gap:8px;align-items:center;padding:6px 0;border-bottom:1px solid var(--line);font-size:13px}
.layer:last-child{border-bottom:0}
.layer i{display:block;width:22px;height:0;border-top:2px solid}
.layer code{font-family:var(--f-mono);font-size:11px;color:var(--muted);display:block}
.layer .n{font-family:var(--f-mono);font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.err{color:var(--cm);font-size:12px}
.note{font-size:12px;color:var(--muted);background:var(--chip);border-radius:6px;padding:8px 10px;margin:0}
@media (max-width:860px){
  .app{height:auto}
  .main{grid-template-columns:1fr}
  .mapwrap{height:64vh;min-height:380px}
  aside{border-left:0;border-top:1px solid var(--line)}
  .pane{overflow:visible}
  .prjname{margin-left:0;width:100%}
  .readout{font-size:11px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="app">
  <header class="top">
    <div class="brand"><h1>UTM-K 좌표 지도</h1><span class="epsg" id="epsgTag">EPSG:5179 · GRS80 · TM</span></div>
    <div class="prjname">
      <span>투영 정의</span><code id="prjFile">GRS80_UTMK.prj</code>
      <label class="btn" for="prjInput">다른 .prj 열기</label>
      <input id="prjInput" type="file" accept=".prj,.txt" hidden>
    </div>
  </header>
  <div class="main">
    <div class="mapwrap" id="mapwrap">
      <canvas id="map" aria-label="국토지리정보원 1:120만 지도를 UTM-K 좌표로 그린 지도. 클릭하면 주소와 좌표가 표시됩니다."></canvas>
      <form class="mapsearch" id="mapForm" role="search">
        <input id="mq" type="search" placeholder="도로명·지명 검색 (예: 경부고속국도, 국도 7)" aria-label="도로명·지명 검색" autocomplete="off">
      </form>
      <div class="zoom">
        <button class="btn" id="zin" aria-label="확대">+</button>
        <button class="btn" id="zout" aria-label="축소">−</button>
        <button class="btn" id="zhome" aria-label="처음 위치로" style="font-size:13px">⌂</button>
      </div>
      <div class="readout" id="readout"></div>
      <div class="drop" id="drop" hidden>.shp + .dbf (+ .prj) 파일을 함께 놓으면 도로명 검색에 추가됩니다<br>GeoJSON·.prj 파일도 놓을 수 있습니다</div>
    </div>
    <aside>
      <div class="tabs" role="tablist">
        <button role="tab" id="t-find" aria-selected="true" aria-controls="p-find">도로명 검색</button>
        <button role="tab" id="t-conv" aria-selected="false" aria-controls="p-conv">좌표 변환</button>
        <button role="tab" id="t-data" aria-selected="false" aria-controls="p-data">데이터·레이어</button>
        <button role="tab" id="t-prj" aria-selected="false" aria-controls="p-prj">PRJ 분석</button>
      </div>

      <div class="pane" id="p-find" role="tabpanel" aria-labelledby="t-find">
        <section>
          <h2>도로명·지명으로 위치 찾기</h2>
          <input id="q" type="search" placeholder="예: 국도 77, 서해안고속국도, 경부선, 설악산, 화성시" aria-label="검색어" autocomplete="off">
          <p class="small" style="margin:6px 0 0">숫자만 넣으면 국도 번호로 찾습니다. 도로·철도·하천은 노선 전체를 지도에 강조하고, 지나가는 시군구를 알려 줍니다.</p>
        </section>
        <section id="detailSec" hidden><div class="detail" id="detail"></div></section>
        <section>
          <h2 id="resHead">검색 결과</h2>
          <div class="reslist" id="results"></div>
        </section>
        <section id="chipSec">
          <h2>고속국도</h2><div class="chips" id="chipsHw"></div>
          <h2 style="margin-top:14px">국도 번호</h2><div class="chips" id="chipsNr"></div>
        </section>
        <section>
          <h2>도로명주소의 거리 이름으로 찾으려면</h2>
          <p class="note">이 지도(1:120만)에는 고속국도·국도·지방도 노선명만 있고 "세종대로", "테헤란로" 같은 도로명주소의 거리 이름은 없습니다. 도로명주소 전자지도의 <b>도로구간 shp</b>(.shp + .dbf, 필요하면 .prj)를 아래 버튼으로 함께 고르거나 지도 위에 끌어다 놓으면 그 도로명으로도 검색됩니다. 도로명주소 전자지도도 같은 UTM-K(EPSG:5179) 좌표계라서 변환 없이 바로 겹쳐집니다.</p>
          <div class="actions"><label class="btn primary" for="shpInput">도로 shp 불러오기</label><input id="shpInput" type="file" accept=".shp,.dbf,.prj,.cpg" multiple hidden><button class="btn" id="userClear">불러온 shp 지우기</button></div>
          <p class="small" id="userInfo" aria-live="polite" style="margin:6px 0 0"></p>
        </section>
      </div>

      <div class="pane" id="p-conv" role="tabpanel" aria-labelledby="t-conv" hidden>
        <section>
          <h2>경위도(WGS84) → UTM-K</h2>
          <div class="field-row">
            <label class="f" for="inLat">위도 φ (°N)<input id="inLat" type="text" inputmode="decimal" value="37.5665"></label>
            <label class="f" for="inLon">경도 λ (°E)<input id="inLon" type="text" inputmode="decimal" value="126.9780"></label>
          </div>
          <div class="actions"><button class="btn primary" id="goFwd">변환하고 지도에 표시</button></div>
          <div class="result" id="outFwd" style="margin-top:8px"></div>
        </section>
        <section>
          <h2>UTM-K → 경위도(WGS84)</h2>
          <div class="field-row">
            <label class="f" for="inX">X · 동향 E (m)<input id="inX" type="text" inputmode="decimal" value="1143467.38"></label>
            <label class="f" for="inY">Y · 북향 N (m)<input id="inY" type="text" inputmode="decimal" value="1688281.98"></label>
          </div>
          <div class="actions"><button class="btn primary" id="goInv">변환하고 지도에 표시</button></div>
          <div class="result" id="outInv" style="margin-top:8px"></div>
        </section>
        <section>
          <h2>여러 좌표 한꺼번에 변환</h2>
          <p class="small" style="margin:0 0 6px">한 줄에 한 점씩, 쉼표나 공백으로 구분. 값이 1,000보다 크면 UTM-K(X, Y), 작으면 위도, 경도로 읽습니다.</p>
          <textarea id="batch" aria-label="일괄 변환할 좌표">37.5665, 126.9780
35.1796 129.0756
1000000, 2000000
33.4996, 126.5312</textarea>
          <div class="actions">
            <button class="btn primary" id="goBatch">변환하고 지도에 찍기</button>
            <button class="btn" id="copyBatch">결과 복사</button>
            <button class="btn" id="clearPins">핀 지우기</button>
          </div>
          <div class="tblwrap" style="margin-top:8px"><table id="batchOut"></table></div>
          <p class="small" id="copyMsg" aria-live="polite"></p>
        </section>
      </div>

      <div class="pane" id="p-data" role="tabpanel" aria-labelledby="t-data" hidden>
        <section>
          <h2>올린 shp: 국토지리정보원 대한민국 전도 1:120만 (2025)</h2>
          <div id="layers"></div>
          <p class="small" style="margin:8px 0 0">12개 레이어의 .prj가 모두 같은 UTM-K 정의입니다(Korea_2000_Korea_Unified_Coordinate_System). 화면용으로 선을 단순화했습니다(행정경계 150~300 m, 도로·철도·하천 80 m 허용오차).</p>
        </section>
        <section>
          <h2>GeoJSON 겹쳐 보기</h2>
          <p class="small" id="gjInfo" style="margin:0">.geojson 파일을 지도 위에 끌어다 놓거나 아래 버튼으로 여세요. 좌표값 크기를 보고 경위도인지 UTM-K인지 자동으로 판단합니다.</p>
          <div class="actions"><label class="btn" for="gjInput">GeoJSON 열기</label><input id="gjInput" type="file" accept=".geojson,.json" hidden><button class="btn" id="gjClear">지우기</button></div>
        </section>
      </div>

      <div class="pane" id="p-prj" role="tabpanel" aria-labelledby="t-prj" hidden>
        <section class="id-card" id="idCard"></section>
        <section>
          <h2>매개변수 해석</h2>
          <div class="tblwrap"><table id="paramTbl"></table></div>
        </section>
        <section>
          <h2>원문 (WKT)</h2>
          <pre class="wkt" id="wktRaw"></pre>
          <p class="err" id="prjErr" aria-live="polite"></p>
        </section>
      </div>
    </aside>
  </div>
</div>

/*PROJ4*/
<script>
const PRJ_DEFAULT = /*WKT*/;
const DATA_PRJ = /*DATAPRJ*/;
const KMAP = /*KMAP*/;

const $ = id => document.getElementById(id);
const fmt = (v,d=2) => v.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const esc = s => String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let wkt = PRJ_DEFAULT, prjName = 'GRS80_UTMK.prj', P = null, params = null;
const BASE = proj4(DATA_PRJ);
let T = null; // 데이터(UTM-K) → 현재 투영

/* ---------- 데이터 풀기 ---------- */
function dec(a){ const o=new Float64Array(a.length); let x=0,y=0; for(let i=0;i<a.length;i+=2){ if(i===0){x=a[0];y=a[1];} else {x+=a[i];y+=a[i+1];} o[i]=KMAP.x0+x*KMAP.q; o[i+1]=KMAP.y0+y*KMAP.q; } return o; }
const ux = v => KMAP.x0+v*KMAP.q, uy = v => KMAP.y0+v*KMAP.q;
const L = {}; // 레이어별 base 좌표
L.sido = KMAP.sido.map(f=>({n:f.n,k:f.k,lab:[ux(f.l[0]),uy(f.l[1])],base:f.r.map(dec)}));
L.sgg  = KMAP.sgg.map(f=>({n:f.n,p:f.p,base:f.r.map(dec)}));
L.emd  = KMAP.emd.map(f=>({n:f.n,p:f.p,base:f.r.map(dec)}));
for (const k of ['road','rail','river','dmz']) L[k] = KMAP[k].map(r=>({n:r[0],base:[dec(r[1])]}));
const PT = [];
const METRO = new Set(['서울','부산','대구','인천','광주','대전','울산','세종','평양']);
function tierOf(n){ if(METRO.has(n)) return 0; if(/청$/.test(n)) return 9; if(/시$/.test(n)) return 1; if(/군$/.test(n)) return 2; if(/(구역|읍|구)$/.test(n)) return 3; return 4; }
KMAP.place.forEach(p=>{ const t=tierOf(p[0]); if(t<9) PT.push({n:p[0],t:'place',tier:t,bx:ux(p[1]),by:uy(p[2])}); });
KMAP.name.forEach(p=>PT.push({n:p[0],t:'name',tier:5,bx:ux(p[1]),by:uy(p[2])}));
KMAP.mount.forEach(p=>PT.push({n:p[0],t:'mount',tier:2.5,h:p[3],bx:ux(p[1]),by:uy(p[2])}));
KMAP.cultu.forEach(p=>PT.push({n:p[0],t:'cultu',tier:2.2,bx:ux(p[1]),by:uy(p[2])}));
KMAP.ocean.forEach(p=>PT.push({n:p[0],t:'ocean',tier:1.5,bx:ux(p[1]),by:uy(p[2])}));
let USER = []; // 불러온 shp 피처 {n, base:[F64], kind, bbox}
let userMeta = null;

function bboxOf(rings){ let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity; for(const r of rings) for(let i=0;i<r.length;i+=2){ const x=r[i],y=r[i+1]; if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; } return [x0,y0,x1,y1]; }
function projectArr(a){ if(!T) return a; const o=new Float64Array(a.length); for(let i=0;i<a.length;i+=2){ const t=T([a[i],a[i+1]]); o[i]=t[0]; o[i+1]=t[1]; } return o; }
const paths = {};
function projectAll(){
  for (const k of ['sido','sgg','emd','road','rail','river','dmz']) for (const f of L[k]){ f.g=f.base.map(projectArr); f.bb=bboxOf(f.g); }
  for (const f of L.sido){ const t=T?T(f.lab):f.lab; f.lx=t[0]; f.ly=t[1]; }
  for (const p of PT){ const t=T?T([p.bx,p.by]):[p.bx,p.by]; p.x=t[0]; p.y=t[1]; }
  for (const f of USER){ f.g=f.base.map(projectArr); f.bb=bboxOf(f.g); }
  buildPaths(); buildIndex();
  gj.forEach(f => f.proj = f.geoms.map(g => g.map(pt => gjXY(pt, f.isXY))));
  if (sel) select(sel.key, false);
}
function pathOf(list, closed){ const p=new Path2D(); for(const f of list) for(const r of f.g){ p.moveTo(r[0],r[1]); for(let i=2;i<r.length;i+=2) p.lineTo(r[i],r[i+1]); if(closed) p.closePath(); } return p; }
function buildPaths(){
  paths.sidoK = pathOf(L.sido.filter(f=>f.k==='k'),true); paths.sidoN = pathOf(L.sido.filter(f=>f.k==='n'),true); paths.sidoF = pathOf(L.sido.filter(f=>f.k==='f'||f.k==='?'),true);
  paths.sgg = pathOf(L.sgg,true); paths.emd = pathOf(L.emd,true);
  paths.road = pathOf(L.road.filter(f=>!/지방도/.test(f.n)),false); paths.local = pathOf(L.road.filter(f=>/지방도/.test(f.n)),false);
  paths.hw = pathOf(L.road.filter(f=>/고속/.test(f.n)),false);
  paths.rail = pathOf(L.rail,false); paths.river = pathOf(L.river,false); paths.dmz = pathOf(L.dmz,false);
  paths.user = pathOf(USER.filter(f=>f.kind!=='pt'),USER.some(f=>f.kind==='poly'));
}

/* ---------- 검색 색인 ---------- */
const TYPE = {road:'도로',rail:'철도',river:'하천',place:'지명',name:'지명',mount:'산',cultu:'국립공원·명소',ocean:'해양 지명',sido:'시도',sgg:'시군구',emd:'읍면동',user:'불러온 도로'};
let INDEX = [];
function lineLen(r){ let s=0; for(let i=2;i<r.length;i+=2) s+=Math.hypot(r[i]-r[i-2],r[i+1]-r[i-1]); return s; }
function buildIndex(){
  const m = new Map();
  const add=(type,n,f)=>{ if(!n) return; const key=type+'|'+n; if(!m.has(key)) m.set(key,{key,type,n,items:[]}); m.get(key).items.push(f); };
  for (const k of ['road','rail','river']) for (const f of L[k]) add(k,f.n,f);
  for (const f of USER) add('user',f.n,f);
  for (const f of L.sido) if(f.k!=='?') add('sido',f.n,f);
  for (const f of L.sgg) add('sgg',f.n+(f.p?' ('+f.p+')':''),f);
  for (const f of L.emd) add('emd',f.n+(f.p?' ('+f.p+')':''),f);
  for (const p of PT) add(p.t==='name'?'name':p.t,p.n,p);
  INDEX = [...m.values()];
  for (const e of INDEX){ if(['road','rail','river','user'].includes(e.type)){ e.len=e.items.reduce((s,f)=>s+f.base.reduce((a,r)=>a+lineLen(r),0),0); } }
}
const RANK = {road:0,user:0,rail:1,sgg:2,sido:2,place:3,emd:4,mount:4,cultu:4,river:5,ocean:6,name:7};
function search(q){
  q = q.replace(/\s+/g,'');
  if(!q) return [];
  let m = q.match(/^(?:국도)?제?(\d{1,4})(?:호선?|번)?$/);
  if (m){ const n=+m[1]; const hit=INDEX.filter(e=>e.type==='road'&&(e.n===`국도제${n}호선`||e.n===`지방도제${n}호선`)); const rest=INDEX.filter(e=>!hit.includes(e)&&e.n.replace(/\s/g,'').includes(q)); return hit.concat(rest).slice(0,60); }
  const nq = q.replace(/고속도로$/,'고속').replace(/고속국도$/,'고속');
  const res = INDEX.filter(e=>{ const s=e.n.replace(/\s/g,''); return s.includes(q) || (nq!==q && s.includes(nq)); });
  res.sort((a,b)=>{ const sa=a.n.replace(/\s/g,''), sb=b.n.replace(/\s/g,''); const ea=sa===q||sa.startsWith(q)?0:1, eb=sb===q||sb.startsWith(q)?0:1; return ea-eb || RANK[a.type]-RANK[b.type] || sa.length-sb.length || sa.localeCompare(sb,'ko'); });
  return res.slice(0,60);
}
function metaOf(e){
  if (e.len!=null) return `${e.items.length}개 구간 · 평면거리 약 ${fmt(e.len/1000,1)} km`;
  if (e.type==='mount') return `높이 ${fmt(e.items[0].h,0)} m`;
  if (e.items[0].x!=null) return `X ${fmt(e.items[0].x,0)} · Y ${fmt(e.items[0].y,0)}`;
  return '';
}
function renderResults(list,q){
  const box=$('results');
  if(!q){ $('resHead').textContent='검색 결과'; box.innerHTML='<div class="res" style="cursor:default"><span class="meta">검색어를 넣거나 아래 노선을 고르세요.</span></div>'; return; }
  $('resHead').textContent = list.length?`검색 결과 ${list.length}${list.length===60?'+':''}건`:'검색 결과';
  box.innerHTML = list.length ? list.map((e,i)=>`<button class="res" data-k="${esc(e.key)}" ${sel&&sel.key===e.key?'aria-current="true"':''}><span class="nm">${esc(e.n)}</span><span class="tag ${e.type}">${TYPE[e.type]}</span><span class="meta">${metaOf(e)}</span></button>`).join('')
    : `<div class="res" style="cursor:default"><span class="meta">"${esc(q)}"와 맞는 도로·지명이 없습니다. 도로명주소의 거리 이름이라면 아래에서 도로명주소 전자지도 shp를 불러오세요.</span></div>`;
  box.querySelectorAll('.res[data-k]').forEach(b=>b.addEventListener('click',()=>select(b.dataset.k,true)));
}
function renderChips(){
  const hw = INDEX.filter(e=>e.type==='road'&&/고속/.test(e.n)).sort((a,b)=>a.n.localeCompare(b.n,'ko'));
  const nr = INDEX.filter(e=>e.type==='road'&&/^국도제\d+호선$/.test(e.n)).sort((a,b)=>parseInt(a.n.slice(3))-parseInt(b.n.slice(3)));
  $('chipsHw').innerHTML = hw.map(e=>`<button class="chip" data-k="${esc(e.key)}">${esc(e.n.replace(/고속국도$/,'').replace(/고속도로$/,''))}</button>`).join('');
  $('chipsNr').innerHTML = nr.map(e=>`<button class="chip" data-k="${esc(e.key)}">${e.n.match(/\d+/)[0]}</button>`).join('');
  document.querySelectorAll('#chipSec .chip').forEach(b=>b.addEventListener('click',()=>{ select(b.dataset.k,true); $('q').value=INDEX.find(e=>e.key===b.dataset.k).n; renderResults(search($('q').value),$('q').value); }));
}

/* ---------- 선택·강조 ---------- */
let sel = null;
function pip(x,y,rings){ let inside=false; for(const r of rings){ for(let i=0,j=r.length-2;i<r.length;j=i,i+=2){ const xi=r[i],yi=r[i+1],xj=r[j],yj=r[j+1]; if(((yi>y)!==(yj>y)) && (x < (xj-xi)*(y-yi)/(yj-yi)+xi)) inside=!inside; } } return inside; }
function findIn(list,x,y){ for(const f of list){ const b=f.bb; if(x<b[0]||x>b[2]||y<b[1]||y>b[3]) continue; if(pip(x,y,f.g)) return f; } return null; }
function addrAt(x,y){
  const e=findIn(L.emd,x,y), g=findIn(L.sgg,x,y), s=findIn(L.sido,x,y);
  const parts=[]; if(s&&s.n) parts.push(s.n); if(g) parts.push(g.n); if(e) parts.push(e.n);
  return parts.join(' ');
}
function select(key, fly){
  const e = INDEX.find(v=>v.key===key); if(!e) return;
  sel = {key, e};
  const isLine = ['road','rail','river','user'].includes(e.type), isArea=['sido','sgg','emd'].includes(e.type);
  let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;
  if (isLine||isArea){ for(const f of e.items){ const b=f.bb; x0=Math.min(x0,b[0]);y0=Math.min(y0,b[1]);x1=Math.max(x1,b[2]);y1=Math.max(y1,b[3]); } sel.path = pathOf(e.items, isArea || (e.type==='user'&&e.items[0].kind==='poly')); sel.area=isArea; }
  else { const p=e.items[0]; x0=x1=p.x; y0=y1=p.y; sel.path=null; }
  sel.bb=[x0,y0,x1,y1];
  // 경유 시군구
  let via=[];
  if (isLine){ const seen=new Map(); for(const f of e.items) for(const r of f.g){ const step=Math.max(2,Math.floor(r.length/2/400)*2); for(let i=0;i<r.length;i+=step){ const g=findIn(L.sgg,r[i],r[i+1]); if(g){ const k=(g.p?g.p+' ':'')+g.n; if(!seen.has(k)) seen.set(k,[r[i],r[i+1]]); } } } via=[...seen.keys()]; }
  const cx=(x0+x1)/2, cy=(y0+y1)/2;
  let px=cx,py=cy;
  if (isLine){ let best=Infinity; for(const f of e.items) for(const r of f.g) for(let i=0;i<r.length;i+=2){ const d=Math.hypot(r[i]-cx,r[i+1]-cy); if(d<best){best=d;px=r[i];py=r[i+1];} } }
  const [lo,la]=P.inverse([px,py]);
  const addr = addrAt(px,py);
  for (let i=pins.length-1;i>=0;i--) if(pins[i].sel) pins.splice(i,1);
  pins.push({x:px,y:py,lat:la,lon:lo,label:e.n,sub:addr,sel:true});
  $('detailSec').hidden=false;
  const sorted = [...new Set(via.map(v=>v.split(' ')[0]))];
  $('detail').innerHTML = `<div class="small">${TYPE[e.type]}</div><div class="big">${esc(e.n)}</div>
    <dl class="kv">
      ${e.len!=null?`<dt>구간 수</dt><dd>${e.items.length}</dd><dt>길이</dt><dd>약 ${fmt(e.len/1000,1)} km (UTM-K 평면거리)</dd>`:''}
      ${e.type==='mount'?`<dt>높이</dt><dd>${fmt(e.items[0].h,0)} m</dd>`:''}
      <dt>${isLine?'노선 중앙':'위치'}</dt><dd>X ${fmt(px)}<br>Y ${fmt(py)}</dd>
      <dt>경위도</dt><dd>${la.toFixed(6)}°N<br>${lo.toFixed(6)}°E</dd>
      ${addr?`<dt>행정구역</dt><dd class="t">${esc(addr)}</dd>`:''}
      ${isLine?`<dt>범위</dt><dd>X ${fmt(x0,0)} ~ ${fmt(x1,0)}<br>Y ${fmt(y0,0)} ~ ${fmt(y1,0)}</dd>`:''}
    </dl>
    ${isLine&&via.length?`<div><div class="small" style="margin-bottom:4px">지나가는 시도 (${sorted.length}) · 시군구 (${via.length})</div><div class="chips">${via.map(v=>`<span class="chip" style="cursor:default">${esc(v)}</span>`).join('')}</div></div>`:''}`;
  if (fly){ if(isLine||isArea) flyTo(cx,cy,Math.max(30,Math.max((x1-x0)/W,(y1-y0)/H)*1.25)); else flyTo(px,py,Math.min(view.s,60)); }
  document.querySelectorAll('.res').forEach(b=>b.toggleAttribute('aria-current',b.dataset.k===key));
  draw();
}

/* ---------- WKT 해석 ---------- */
function parseWkt(s){
  const g = (re) => { const m = s.match(re); return m ? m[1] : null; };
  const p = {};
  p.projcs = g(/PROJCS\["([^"]+)"/); p.geogcs = g(/GEOGCS\["([^"]+)"/); p.datum = g(/DATUM\["([^"]+)"/);
  const sph = s.match(/SPHEROID\["([^"]+)",\s*([\d.eE+-]+),\s*([\d.eE+-]+)/);
  if (sph){ p.spheroid = sph[1]; p.a = +sph[2]; p.rf = +sph[3]; }
  p.primem = g(/PRIMEM\["[^"]+",\s*([\d.eE+-]+)/);
  p.projection = g(/PROJECTION\["([^"]+)"/);
  const par = {}; for (const m of s.matchAll(/PARAMETER\["([^"]+)",\s*([\d.eE+-]+)\]/g)) par[m[1].toLowerCase()] = +m[2];
  p.par = par;
  const units = [...s.matchAll(/UNIT\["([^"]+)",\s*([\d.eE+-]+)\]/g)]; p.unit = units.length ? units[units.length-1][1] : null;
  return p;
}
const KNOWN = [
  {code:'EPSG:5179',name:'Korea 2000 / Unified CS (UTM-K)',lon:127.5,lat:38,fe:1000000,fn:2000000,k:0.9996,use:'전국을 원점 하나로 덮는 통합 좌표계. 도로명주소 전자지도, 국토지리정보원 소축척 지도, 네이버 지도 등이 씁니다.'},
  {code:'EPSG:5186',name:'Korea 2000 / Central Belt 2010 (중부원점)',lon:127,lat:38,fe:200000,fn:600000,k:1,use:'지적·측량 성과에 쓰는 중부 원점 좌표계.'},
  {code:'EPSG:5185',name:'Korea 2000 / West Belt 2010 (서부원점)',lon:125,lat:38,fe:200000,fn:600000,k:1,use:'서부 지역 측량용 원점.'},
  {code:'EPSG:5187',name:'Korea 2000 / East Belt 2010 (동부원점)',lon:129,lat:38,fe:200000,fn:600000,k:1,use:'동부 지역 측량용 원점.'},
  {code:'EPSG:5188',name:'Korea 2000 / East Sea Belt 2010 (동해원점)',lon:131,lat:38,fe:200000,fn:600000,k:1,use:'울릉도·독도 지역 측량용 원점.'},
  {code:'EPSG:5181',name:'Korea 2000 / Central Belt (카카오맵)',lon:127,lat:38,fe:200000,fn:500000,k:1,use:'카카오맵 등에서 쓰는 중부원점(가산값 50만).'},
  {code:'EPSG:32652',name:'WGS 84 / UTM zone 52N',lon:129,lat:0,fe:500000,fn:0,k:0.9996,use:'세계 UTM 52구역.'}
];
function identify(p){
  const q = p.par, near=(a,b,t=1e-6)=>a!=null&&Math.abs(a-b)<=t;
  return KNOWN.find(k => near(q.central_meridian,k.lon) && near(q.latitude_of_origin ?? 0,k.lat) && near(q.false_easting,k.fe,0.01) && near(q.false_northing,k.fn,0.01) && near(q.scale_factor,k.k));
}
function loadPrj(text, name){
  let proj;
  if (!/PROJCS\[/.test(text)) throw new Error('PROJCS(투영 좌표계)가 없는 파일입니다. 경위도 좌표계(.prj에 GEOGCS만 있는 경우)는 지도의 미터 격자를 만들 수 없습니다.');
  try { proj = proj4(text); } catch(e){ throw new Error('proj4가 이 WKT를 읽지 못했습니다: '+e.message); }
  const t = proj.forward([127.5,37]); if (!isFinite(t[0])||!isFinite(t[1])) throw new Error('한반도 좌표를 이 투영으로 계산할 수 없습니다.');
  wkt = text; prjName = name; P = proj; params = parseWkt(text);
  const same = [[124,33],[131,43],[127.5,38]].every(ll=>{ const a=P.forward(ll), b=BASE.forward(ll); return Math.abs(a[0]-b[0])<1e-3&&Math.abs(a[1]-b[1])<1e-3; });
  T = same ? null : (xy => P.forward(BASE.inverse(xy)));
  projectAll(); renderPrj(); runFwd(false); runInv(false);
  pins.forEach(pp => { [pp.x,pp.y] = P.forward([pp.lon,pp.lat]); });
  computeBounds(); home(); draw();
}

/* ---------- PRJ 패널 ---------- */
function renderPrj(){
  const p = params, q = p.par, id = identify(p);
  $('prjFile').textContent = prjName;
  $('epsgTag').textContent = (id ? id.code : '사용자 정의') + ' · ' + (p.spheroid||'') + ' · ' + (p.projection||'').replace(/_/g,' ');
  const inv = p.rf ? 1/p.rf : null, b = p.a && inv ? p.a*(1-inv) : null;
  $('idCard').innerHTML = (id
    ? `<div class="small">식별 결과 <span class="pill">일치</span></div><div class="big">${id.code} ${id.name}</div><p class="small" style="margin:6px 0 0">${id.use} 측지계 이름은 ${p.datum}로 적혀 있지만, 한국 측지계 2000(Korea 2000)은 ITRF2000에 GRS80 타원체를 쓰므로 같은 좌표계입니다. WGS84 경위도와의 차이는 1 m 미만입니다.</p>`
    : `<div class="small">식별 결과 <span class="pill warn">목록에 없음</span></div><div class="big">${p.projcs||'이름 없는 투영'}</div><p class="small" style="margin:6px 0 0">알려진 한국 좌표계와 매개변수가 다릅니다. shp 데이터(UTM-K)를 이 투영으로 다시 계산해 그렸습니다.</p>`)
    + `<p class="small" style="margin:6px 0 0">${T?'올린 shp의 .prj와 투영이 달라 경위도를 거쳐 다시 계산했습니다.':'올린 shp 12개 레이어의 .prj(Korea_2000_Korea_Unified_Coordinate_System)와 매개변수가 같아 좌표를 변환 없이 그대로 씁니다.'}</p>`;
  const rows = [
    ['PROJCS', p.projcs, '투영 좌표계 이름. ESRI 형식이라 EPSG 번호는 따로 적혀 있지 않습니다.'],
    ['GEOGCS / DATUM', `${p.geogcs} / ${p.datum}`, '기준이 되는 지리 좌표계와 측지계.'],
    ['SPHEROID', p.spheroid, `타원체. 장반경 a = ${p.a?fmt(p.a,1):'?'} m, 역편평률 1/f = ${p.rf??'?'}${b?`, 단반경 b ≈ ${fmt(b,3)} m`:''}.`],
    ['PRIMEM', p.primem!=null?p.primem+'°':'', '본초자오선(그리니치 = 0°).'],
    ['PROJECTION', p.projection, '횡메르카토르(TM). 원통을 옆으로 눕혀 남북으로 긴 지역을 왜곡 적게 펼칩니다.'],
    ['Central_Meridian', q.central_meridian!=null?q.central_meridian+'°E':'', '중앙자오선. 한반도 한가운데를 지나 왜곡이 가장 작은 선입니다.'],
    ['Latitude_Of_Origin', (q.latitude_of_origin??0)+'°N', '원점 위도. 원점은 이 위도와 중앙자오선이 만나는 점입니다.'],
    ['Scale_Factor', q.scale_factor, `중앙자오선 축척계수. 1보다 조금 작게 잡아 동서로 멀어져도 왜곡이 고르게 퍼집니다(중앙에서 ${q.scale_factor<1?fmt((1-q.scale_factor)*1e5,0)+' cm/km 짧게':'왜곡 없음'}).`],
    ['False_Easting', q.false_easting!=null?fmt(q.false_easting,0)+' m':'', '가산 동향(X). 원점의 X값으로, 서쪽 좌표가 음수가 되지 않게 더합니다.'],
    ['False_Northing', q.false_northing!=null?fmt(q.false_northing,0)+' m':'', '가산 북향(Y). 원점의 Y값으로, 남쪽 좌표가 음수가 되지 않게 더합니다.'],
    ['UNIT', p.unit, '좌표 단위.']
  ];
  $('paramTbl').innerHTML = rows.map(r=>`<tr><td><div class="pk">${r[0]}</div><div class="pv">${r[1]??''}</div><div class="small">${r[2]}</div></td></tr>`).join('');
  $('wktRaw').textContent = wkt.replace(/,(?=[A-Z]+\[)/g, ',\n ');
}

/* ---------- 레이어 패널 ---------- */
const LAYERS = [
  {id:'admin',file:'KOR_ADMIN_AS',nm:'행정경계 (시도·시군구·읍면동)',n:'9,922',sw:'--border-s',on:true},
  {id:'road',file:'KOR_ROAD_LS',nm:'도로 (고속국도·국도·지방도)',n:'1,256',sw:'--road',on:true},
  {id:'rail',file:'KOR_RAILW_LS',nm:'철도',n:'706',sw:'--rail',on:true},
  {id:'river',file:'KOR_RIVER_LS',nm:'하천',n:'1,265',sw:'--river',on:true},
  {id:'dmz',file:'KOR_DZONE_LS',nm:'군사분계선',n:'1',sw:'--dmz',on:true},
  {id:'place',file:'KOR_PREMI_PS',nm:'주요 지명 (시·군·읍·리)',n:'2,080',sw:'--fg',on:true},
  {id:'name',file:'KOR_NAME_PS',nm:'일반 지명 (섬·항구·해수욕장 등)',n:'1,361',sw:'--muted',on:true},
  {id:'mount',file:'KOR_MOUNT_PS',nm:'산 (높이)',n:'182',sw:'--grat',on:true},
  {id:'cultu',file:'KOR_CULTU_PS',nm:'국립공원·명소',n:'57',sw:'--accent',on:true},
  {id:'ocean',file:'KOR_OCEAN_PS',nm:'해양 지명',n:'32',sw:'--river',on:true},
  {id:'coast',file:'KOR_COAST_LS',nm:'해안선 (행정경계 외곽선으로 표시)',n:'3,081',sw:'--border',fixed:true},
  {id:'latlo',file:'KOR_LATLO_LS',nm:'경위선 (정밀 계산한 경위선으로 표시)',n:'23',sw:'--grat',fixed:true},
  {id:'grid',file:'—',nm:'UTM-K 격자 · 중앙자오선',n:'',sw:'--grid',on:true}
];
const SHOW = Object.fromEntries(LAYERS.map(l=>[l.id,l.fixed?true:l.on]));
function renderLayers(){
  $('layers').innerHTML = LAYERS.map(l=>`<label class="layer"><input type="checkbox" id="ly-${l.id}" ${SHOW[l.id]?'checked':''} ${l.fixed?'disabled':''}><i style="border-color:var(${l.sw})"></i><span>${l.nm}<code>${l.file}</code></span><span class="n">${l.n}</span></label>`).join('');
  LAYERS.forEach(l=>{ if(!l.fixed) $('ly-'+l.id).addEventListener('change',e=>{ SHOW[l.id]=e.target.checked; draw(); }); });
}

/* ---------- 지도 그리기 ---------- */
const cv = $('map'), ctx = cv.getContext('2d');
let W=0,H=0,DPR=1, view = {cx:1000000, cy:1900000, s:1500};
const pins = [];
let hover = null, bounds=null, gj = [];
function computeBounds(){ const ks=L.sido.filter(f=>f.k==='k'||f.k==='n'); bounds=[Math.min(...ks.map(f=>f.bb[0])),Math.min(...ks.map(f=>f.bb[1])),Math.max(...ks.map(f=>f.bb[2])),Math.max(...ks.map(f=>f.bb[3]))]; }
function resize(){ const r = cv.getBoundingClientRect(); DPR = window.devicePixelRatio||1; W=r.width; H=r.height; cv.width=Math.round(W*DPR); cv.height=Math.round(H*DPR); draw(); }
const sx = x => (x-view.cx)/view.s + W/2, sy = y => H/2 - (y-view.cy)/view.s;
const wx = px => view.cx + (px-W/2)*view.s, wy = py => view.cy - (py-H/2)*view.s;
function home(){ if(!bounds||!W) return; const [x0,y0,x1,y1]=bounds; const nar=W<600; view.cx=(x0+x1)/2+(nar?60000:30000); view.cy=nar?(y0+y1)/2-220000:(y0+y1)/2-120000; view.s=nar?Math.max((x1-x0-200000)/W,(y1-y0)/H*0.62):Math.max((x1-x0)/W,(y1-y0)/H)*0.62; }
function css(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
let C = {};
function readColors(){ ['sea','land','land-n','land-f','border','border-s','river','road','rail','dmz','grid','grat','cm','pin','hl','fg','muted','panel','user','accent'].forEach(k=>C[k]=css('--'+k)); C.mono=css('--f-mono'); C.body=css('--f-body'); }
function worldTx(){ ctx.setTransform(DPR/view.s,0,0,-DPR/view.s,DPR*(W/2-view.cx/view.s),DPR*(H/2+view.cy/view.s)); }
function strokeW(path,color,px,dash,alpha=1){ ctx.strokeStyle=color; ctx.lineWidth=px*view.s; ctx.setLineDash(dash?dash.map(d=>d*view.s):[]); ctx.globalAlpha=alpha; ctx.stroke(path); ctx.globalAlpha=1; }
let rafPending=false;
function draw(){ if(rafPending) return; rafPending=true; requestAnimationFrame(()=>{ rafPending=false; drawNow(); }); }
function drawNow(){
  if(!P||!W) return;
  const s=view.s;
  ctx.setTransform(DPR,0,0,DPR,0,0); ctx.fillStyle=C.sea; ctx.fillRect(0,0,W,H);
  worldTx(); ctx.lineJoin='round'; ctx.lineCap='round';
  ctx.fillStyle=C['land-f']; ctx.fill(paths.sidoF,'evenodd');
  ctx.fillStyle=C['land-n']; ctx.fill(paths.sidoN,'evenodd');
  ctx.fillStyle=C.land; ctx.fill(paths.sidoK,'evenodd');
  if(SHOW.admin){
    if(s<110) strokeW(paths.emd,C.border,.5,[3,2],.7);
    if(s<900) strokeW(paths.sgg,C.border,s<300?.9:.6,null,.9);
  }
  if(SHOW.river) strokeW(paths.river,C.river,s<200?1.3:.8,null,.85);
  if(SHOW.admin){ ctx.strokeStyle=C['border-s']; strokeW(paths.sidoK,C['border-s'],s<300?1.4:1); strokeW(paths.sidoN,C['border-s'],s<300?1.2:.8,null,.8); strokeW(paths.sidoF,C.border,.6); }
  if(SHOW.road){ if(s<500) strokeW(paths.local,C.road,.8,null,.6); strokeW(paths.road,C.road,s<200?1.5:1,null,.85); strokeW(paths.hw,C.road,s<200?2.6:1.8); }
  if(SHOW.rail){ strokeW(paths.rail,C.rail,s<200?2:1.4,null,.9); if(s<400){ strokeW(paths.rail,C.land,s<200?1:.7,[6,6]); } }
  if(SHOW.dmz) strokeW(paths.dmz,C.dmz,2,[8,5]);
  if(USER.length) strokeW(paths.user,C.user,s<50?2.2:1.4,null,.95);
  if(sel&&sel.path){ if(sel.area){ ctx.fillStyle=C.hl; ctx.globalAlpha=.14; ctx.fill(sel.path,'evenodd'); ctx.globalAlpha=1; strokeW(sel.path,C.hl,2.2); } else { strokeW(sel.path,C.panel,7,null,.9); strokeW(sel.path,C.hl,4); } }
  ctx.setLineDash([]); ctx.setTransform(DPR,0,0,DPR,0,0);
  if(SHOW.grid) drawGrid();
  if(USER.length){ ctx.fillStyle=C.user; for(const f of USER) if(f.kind==='pt'){ const r=f.g[0]; const px=sx(r[0]),py=sy(r[1]); if(px>-5&&px<W+5&&py>-5&&py<H+5){ ctx.beginPath(); ctx.arc(px,py,2.5,0,7); ctx.fill(); } } }
  drawLabels();
  // GeoJSON
  for(const f of gj){ ctx.strokeStyle=C.cm; ctx.fillStyle=C.cm; ctx.lineWidth=1.6;
    f.proj.forEach((g,gi)=>{ const kind=f.kinds[gi];
      if(kind==='pt'){ const [x,y]=g[0]; ctx.beginPath(); ctx.arc(sx(x),sy(y),3.5,0,7); ctx.fill(); }
      else { ctx.beginPath(); g.forEach(([x,y],i)=> i?ctx.lineTo(sx(x),sy(y)):ctx.moveTo(sx(x),sy(y))); if(kind==='poly'){ ctx.closePath(); ctx.globalAlpha=.15; ctx.fill(); ctx.globalAlpha=1; } ctx.stroke(); } }); }
  drawPins(); drawScale(); updateReadout();
}
function drawGrid(){
  const steps=[100,500,1000,5000,10000,50000,100000,500000]; const st=steps.find(v=>v/view.s>=90)||1e6;
  const x0=wx(0),x1=wx(W),y0=wy(H),y1=wy(0);
  ctx.save(); ctx.strokeStyle=C.grid; ctx.globalAlpha=.35; ctx.lineWidth=.8; ctx.beginPath();
  for(let x=Math.ceil(x0/st)*st;x<=x1;x+=st){ const p=Math.round(sx(x))+.5; ctx.moveTo(p,0); ctx.lineTo(p,H); }
  for(let y=Math.ceil(y0/st)*st;y<=y1;y+=st){ const p=Math.round(sy(y))+.5; ctx.moveTo(0,p); ctx.lineTo(W,p); }
  ctx.stroke(); ctx.restore();
  ctx.font='500 10.5px '+C.mono; ctx.fillStyle=C.grid; ctx.textBaseline='bottom';
  for(let x=Math.ceil(x0/st)*st;x<=x1;x+=st){ const p=sx(x); if(p>40&&p<W-70) ctx.fillText(fmt(x,0),p+3,H-4); }
  for(let y=Math.ceil(y0/st)*st;y<=y1;y+=st){ const p=sy(y); if(p>60&&p<H-90) ctx.fillText(fmt(y,0),W-ctx.measureText(fmt(y,0)).width-52,p-2); }
  // 경위선
  const degStep = view.s>600?1:view.s>60?0.25:view.s>8?0.05:0.01;
  const corners=[[0,0],[W,0],[0,H],[W,H],[W/2,0],[W/2,H]].map(([a,b])=>P.inverse([wx(a),wy(b)]));
  const lonA=Math.floor(Math.min(...corners.map(c=>c[0]))/degStep)*degStep, lonB=Math.max(...corners.map(c=>c[0]));
  const latA=Math.floor(Math.min(...corners.map(c=>c[1]))/degStep)*degStep, latB=Math.max(...corners.map(c=>c[1]));
  if((lonB-lonA)/degStep<80 && (latB-latA)/degStep<80){
    ctx.save(); ctx.strokeStyle=C.grat; ctx.setLineDash([4,4]); ctx.lineWidth=.8; ctx.globalAlpha=.7;
    const n=40;
    for(let lo=lonA;lo<=lonB+1e-9;lo+=degStep){ ctx.beginPath(); for(let i=0;i<=n;i++){ const la=latA+(latB-latA)*i/n; const t=P.forward([lo,la]); i?ctx.lineTo(sx(t[0]),sy(t[1])):ctx.moveTo(sx(t[0]),sy(t[1])); } ctx.stroke(); }
    for(let la=latA;la<=latB+1e-9;la+=degStep){ ctx.beginPath(); for(let i=0;i<=n;i++){ const lo=lonA+(lonB-lonA)*i/n; const t=P.forward([lo,la]); i?ctx.lineTo(sx(t[0]),sy(t[1])):ctx.moveTo(sx(t[0]),sy(t[1])); } ctx.stroke(); }
    ctx.restore();
    ctx.font='11px '+C.body; ctx.fillStyle=C.grat; ctx.textBaseline='top';
    const dd = degStep<1?2:0;
    for(let lo=lonA;lo<=lonB+1e-9;lo+=degStep){ const la=P.inverse([wx(W/2),wy(52)])[1]; const t=P.forward([lo,la]); const p=sx(t[0]); if(p>360&&p<W-60) ctx.fillText(lo.toFixed(dd)+'°E',p+3,52); }
    for(let la=latA;la<=latB+1e-9;la+=degStep){ const lo=P.inverse([wx(8),wy(H/2)])[0]; const t=P.forward([lo,la]); const p=sy(t[1]); if(p>60&&p<H-80) ctx.fillText(la.toFixed(dd)+'°N',6,p+2); }
  }
  const cm = params.par.central_meridian, lo0 = params.par.latitude_of_origin??0;
  ctx.save(); ctx.strokeStyle=C.cm; ctx.lineWidth=1.2; ctx.globalAlpha=.8; ctx.beginPath();
  for(let i=0;i<=60;i++){ const la=30+i*0.25; const t=P.forward([cm,la]); i?ctx.lineTo(sx(t[0]),sy(t[1])):ctx.moveTo(sx(t[0]),sy(t[1])); } ctx.stroke(); ctx.globalAlpha=1;
  const o=P.forward([cm,lo0]), ox=sx(o[0]), oy=sy(o[1]);
  ctx.fillStyle=C.cm; ctx.font='500 11px '+C.body;
  if(ox>-20&&ox<W+20&&oy>-20&&oy<H+20){
    ctx.lineWidth=1.6; ctx.beginPath(); ctx.arc(ox,oy,7,0,7); ctx.stroke(); ctx.beginPath(); ctx.moveTo(ox-11,oy);ctx.lineTo(ox+11,oy);ctx.moveTo(ox,oy-11);ctx.lineTo(ox,oy+11);ctx.stroke();
    ctx.textBaseline='top'; const ol='UTM-K 원점 ('+fmt(o[0],0)+', '+fmt(o[1],0)+')'; const lw=ctx.measureText(ol).width;
    ctx.lineWidth=3; ctx.strokeStyle=C.panel; ctx.strokeText(ol,ox-10-lw,oy+8); ctx.fillText(ol,ox-10-lw,oy+8);
  }
  ctx.restore();
}
function drawLabels(){
  const s=view.s, boxes=[];
  const free=(x,y,w,h)=>{ for(const b of boxes) if(x<b[0]+b[2]&&x+w>b[0]&&y<b[1]+b[3]&&y+h>b[1]) return false; boxes.push([x,y,w,h]); return true; };
  const halo=(t,x,y)=>{ ctx.lineWidth=3; ctx.strokeStyle=C.panel; ctx.globalAlpha=.85; ctx.strokeText(t,x,y); ctx.globalAlpha=1; ctx.fillText(t,x,y); };
  ctx.textBaseline='middle';
  for (const p of pins){ const px=sx(p.x),py=sy(p.y); boxes.push([px-8,py-26,16,26]); }
  // 시도 이름 (축소 시)
  if (s>220 && SHOW.admin){ ctx.font='700 13px '+C.body; ctx.fillStyle=C.muted;
    for(const f of L.sido){ if(f.k!=='k'&&f.k!=='n') continue; const px=sx(f.lx),py=sy(f.ly); const nm=f.n.replace(/(특별자치도|특별자치시|광역시|특별시|직할시)$/,'').replace(/^(.{2}).*도$/,(m,a)=>f.n.length<=4?f.n:a+'도'); const w=ctx.measureText(nm).width; if(px<0||px>W||py<0||py>H) continue; if(free(px-w/2-2,py-9,w+4,18)) halo(nm,px-w/2,py); } }
  const lim = {0:1e9,1:s>1400?0:1,1.5:1,2:s<650?1:0,2.2:s<450?1:0,2.5:s<330?1:0,3:s<220?1:0,4:s<80?1:0,5:s<55?1:0};
  const cand = PT.filter(p=>SHOW[p.t]!==false && lim[p.tier]).sort((a,b)=>a.tier-b.tier);
  for(const p of cand){ const px=sx(p.x),py=sy(p.y); if(px<-40||px>W+40||py<-20||py>H+20) continue;
    let txt=p.n, font, col;
    if(p.t==='ocean'){ font='italic 12px '+C.body; col=C.river; }
    else if(p.t==='mount'){ txt='▲ '+p.n+(s<160?' '+fmt(p.h,0):''); font='11px '+C.body; col=C.grat; }
    else if(p.t==='cultu'){ font='500 11.5px '+C.body; col=C.accent; }
    else if(p.tier===0){ font='700 13.5px '+C.body; col=C.fg; }
    else if(p.tier===1){ font='500 12.5px '+C.body; col=C.fg; }
    else if(p.tier<=3){ font='12px '+C.body; col=C.fg; }
    else { font='11px '+C.body; col=C.muted; }
    ctx.font=font; const w=ctx.measureText(txt).width;
    const dot = (p.t==='place'||p.t==='name');
    const lx = dot?px+5:px-w/2, ly=py;
    if(!free(lx-2,ly-8,w+4,16)) continue;
    if(dot){ ctx.fillStyle=col; ctx.beginPath(); ctx.arc(px,py,p.tier<=1?3:2.2,0,7); ctx.fill(); }
    ctx.fillStyle=col; halo(txt,lx,ly);
  }
}
function drawPins(){
  pins.forEach((p,i)=>{ const px=sx(p.x),py=sy(p.y); ctx.fillStyle=p.sel?C.hl:C.pin; ctx.beginPath(); ctx.moveTo(px,py); ctx.arc(px,py-16,7,Math.PI*0.75,Math.PI*0.25); ctx.closePath(); ctx.fill();
    ctx.fillStyle=C.panel; ctx.beginPath(); ctx.arc(px,py-16,2.8,0,7); ctx.fill();
    if(i===pins.length-1){ const lines=[[p.label||'선택한 지점','500 12.5px '+C.body,C.fg]]; if(p.sub) lines.push([p.sub,'12px '+C.body,C.fg]); lines.push(['X '+fmt(p.x)+'  Y '+fmt(p.y),'12px '+C.mono,C.fg],[p.lat.toFixed(6)+'°N  '+p.lon.toFixed(6)+'°E','12px '+C.mono,C.muted]); if(p.road) lines.push(['가까운 도로 '+p.road,'12px '+C.body,C.road]);
      let w=0; lines.forEach(l=>{ ctx.font=l[1]; w=Math.max(w,ctx.measureText(l[0]).width); }); w+=16; const h=lines.length*17+10;
      let bx=px+12,by=py-h-4; if(bx+w>W-50) bx=px-12-w; bx=Math.max(4,Math.min(bx,W-w-4)); if(by<56) by=py+8;
      ctx.fillStyle=C.panel; ctx.strokeStyle=C.border; ctx.lineWidth=1; ctx.beginPath(); ctx.roundRect?ctx.roundRect(bx,by,w,h,6):ctx.rect(bx,by,w,h); ctx.fill(); ctx.stroke();
      ctx.textBaseline='top'; lines.forEach((l,j)=>{ ctx.font=l[1]; ctx.fillStyle=l[2]; ctx.fillText(l[0],bx+8,by+6+j*17); }); } });
}
function drawScale(){
  const target=view.s*120, nice=[1,2,5].flatMap(m=>[1,10,100,1000,1e4,1e5,1e6].map(e=>m*e)).sort((a,b)=>a-b).filter(v=>v<=target).pop()||1;
  const narrow=W<600, bw=nice/view.s, bx0=narrow?W-bw-56:W-bw-56, by0=narrow?H-24:H-24;
  ctx.strokeStyle=C.fg; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(bx0,by0-5);ctx.lineTo(bx0,by0);ctx.lineTo(bx0+bw,by0);ctx.lineTo(bx0+bw,by0-5); ctx.stroke();
  ctx.fillStyle=C.fg; ctx.font='11px '+C.mono; ctx.textBaseline='bottom'; const sl=nice>=1000?(nice/1000)+' km':nice+' m'; ctx.fillText(sl,bx0+bw/2-ctx.measureText(sl).width/2,by0-6);
}
function updateReadout(){
  const pt = hover || [W/2,H/2]; const x=wx(pt[0]), y=wy(pt[1]); const [lo,la]=P.inverse([x,y]);
  $('readout').innerHTML = `<div><b>${hover?'커서':'화면 중심'}</b>X ${fmt(x)} · Y ${fmt(y)}</div><div><b>경위도</b>${la.toFixed(6)}°N · ${lo.toFixed(6)}°E</div><div><b>축척</b>1 px ≈ ${view.s>=1000?fmt(view.s/1000,2)+' km':fmt(view.s,1)+' m'}</div>`;
}
function nearestRoad(x,y,tol){
  let best=tol, name=null;
  for(const f of L.road.concat(USER.filter(u=>u.kind==='line'))){ if(!f.n) continue; const b=f.bb; if(x<b[0]-tol||x>b[2]+tol||y<b[1]-tol||y>b[3]+tol) continue;
    for(const r of f.g) for(let i=2;i<r.length;i+=2){ const ax=r[i-2],ay=r[i-1],bx=r[i],by=r[i+1]; const dx=bx-ax,dy=by-ay; const t=Math.max(0,Math.min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy||1))); const d=Math.hypot(ax+t*dx-x,ay+t*dy-y); if(d<best){best=d;name=f.n;} } }
  return name;
}

/* ---------- 상호작용 ---------- */
const ptrs = new Map(); let moved=0, pinch=null;
cv.addEventListener('pointerdown',e=>{ cv.setPointerCapture(e.pointerId); ptrs.set(e.pointerId,[e.offsetX,e.offsetY]); moved=0;
  if(ptrs.size===2){ const [a,b]=[...ptrs.values()]; pinch={d:Math.hypot(a[0]-b[0],a[1]-b[1]),s:view.s}; } });
cv.addEventListener('pointermove',e=>{ const prev=ptrs.get(e.pointerId); hover=[e.offsetX,e.offsetY];
  if(prev){ const dx=e.offsetX-prev[0], dy=e.offsetY-prev[1]; ptrs.set(e.pointerId,[e.offsetX,e.offsetY]);
    if(ptrs.size===2&&pinch){ const [a,b]=[...ptrs.values()]; const d=Math.hypot(a[0]-b[0],a[1]-b[1]); const m=[(a[0]+b[0])/2,(a[1]+b[1])/2]; zoomAt(m[0],m[1],pinch.s*pinch.d/d/view.s); moved+=10; }
    else if(ptrs.size===1){ view.cx-=dx*view.s; view.cy+=dy*view.s; moved+=Math.abs(dx)+Math.abs(dy); }
    draw(); } else updateReadout(); });
const up=e=>{ if(ptrs.has(e.pointerId)&&ptrs.size===1&&moved<5&&e.type==='pointerup'){ const x=wx(e.offsetX),y=wy(e.offsetY); const [lo,la]=P.inverse([x,y]);
    pins.push({x,y,lat:la,lon:lo,label:'선택한 지점',sub:addrAt(x,y)||'행정구역 밖(바다)',road:nearestRoad(x,y,view.s*8)}); if(pins.length>200) pins.shift(); draw(); }
  ptrs.delete(e.pointerId); if(ptrs.size<2) pinch=null; };
cv.addEventListener('pointerup',up); cv.addEventListener('pointercancel',up);
cv.addEventListener('pointerleave',()=>{ hover=null; updateReadout(); });
cv.addEventListener('wheel',e=>{ e.preventDefault(); zoomAt(e.offsetX,e.offsetY,Math.exp(e.deltaY*0.0015)); draw(); },{passive:false});
function zoomAt(px,py,f){ const ns=Math.min(6000,Math.max(0.5,view.s*f)); const x=wx(px),y=wy(py); view.s=ns; view.cx=x-(px-W/2)*ns; view.cy=y+(py-H/2)*ns; }
$('zin').onclick=()=>{ zoomAt(W/2,H/2,1/1.8); draw(); }; $('zout').onclick=()=>{ zoomAt(W/2,H/2,1.8); draw(); }; $('zhome').onclick=()=>{ home(); draw(); };
function flyTo(x,y,s){ const a={...view}, t0=performance.now(), dur=matchMedia('(prefers-reduced-motion: reduce)').matches?0:650;
  const step=now=>{ const k=dur?Math.min(1,(now-t0)/dur):1, e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2; view.cx=a.cx+(x-a.cx)*e; view.cy=a.cy+(y-a.cy)*e; view.s=Math.exp(Math.log(a.s)+(Math.log(s)-Math.log(a.s))*e); drawNow(); if(k<1) requestAnimationFrame(step); }; requestAnimationFrame(step); }

/* ---------- 검색 입력 ---------- */
let qTimer=null;
function onQuery(v,from){ if(from!=='q') $('q').value=v; if(from!=='mq') $('mq').value=v; clearTimeout(qTimer); qTimer=setTimeout(()=>renderResults(search(v),v.trim()),120); }
$('q').addEventListener('input',e=>onQuery(e.target.value,'q'));
$('mq').addEventListener('input',e=>onQuery(e.target.value,'mq'));
function pickFirst(v){ const r=search(v); renderResults(r,v.trim()); if(r.length) select(r[0].key,true); }
$('q').addEventListener('keydown',e=>{ if(e.key==='Enter'){ e.preventDefault(); pickFirst(e.target.value); } });
$('mapForm').addEventListener('submit',e=>{ e.preventDefault(); tabs[0].click(); pickFirst($('mq').value); });

/* ---------- 변환 패널 ---------- */
const num = s => parseFloat(String(s).replace(/,/g,'').trim());
function runFwd(show){ const la=num($('inLat').value), lo=num($('inLon').value);
  if(!isFinite(la)||!isFinite(lo)||Math.abs(la)>90||Math.abs(lo)>180){ $('outFwd').textContent='위도는 -90~90, 경도는 -180~180 사이 숫자로 넣어 주세요.'; return; }
  const [x,y]=P.forward([lo,la]); $('outFwd').innerHTML=`X = ${fmt(x,3)} m<br>Y = ${fmt(y,3)} m`;
  if(show){ pins.push({lat:la,lon:lo,x,y,label:'입력한 경위도',sub:addrAt(x,y)}); flyTo(x,y,Math.min(view.s,120)); } }
function runInv(show){ const x=num($('inX').value), y=num($('inY').value);
  if(!isFinite(x)||!isFinite(y)){ $('outInv').textContent='X, Y를 미터 단위 숫자로 넣어 주세요.'; return; }
  const [lo,la]=P.inverse([x,y]); const ad=addrAt(x,y); $('outInv').innerHTML=`위도 = ${la.toFixed(8)}°N<br>경도 = ${lo.toFixed(8)}°E<br><span class="small">${dms(la,'N')}  ${dms(lo,'E')}</span>${ad?`<br><span class="small">${esc(ad)}</span>`:''}`;
  if(show){ pins.push({lat:la,lon:lo,x,y,label:'입력한 UTM-K',sub:ad}); flyTo(x,y,Math.min(view.s,120)); } }
function dms(v,h){ const a=Math.abs(v), d=Math.floor(a), m=Math.floor((a-d)*60), s=((a-d)*60-m)*60; return `${d}°${String(m).padStart(2,'0')}′${s.toFixed(3).padStart(6,'0')}″${h}`; }
$('goFwd').onclick=()=>runFwd(true); $('goInv').onclick=()=>runInv(true);
['inLat','inLon'].forEach(i=>$(i).addEventListener('keydown',e=>{ if(e.key==='Enter') runFwd(true); }));
['inX','inY'].forEach(i=>$(i).addEventListener('keydown',e=>{ if(e.key==='Enter') runInv(true); }));
let batchRows=[];
$('goBatch').onclick=()=>{
  batchRows=[]; const lines=$('batch').value.split(/\n/).map(s=>s.trim()).filter(Boolean);
  for(const l of lines){ const v=l.split(/[\s,;\t]+/).map(num).filter(isFinite); if(v.length<2){ batchRows.push({src:l,err:'숫자 2개가 필요합니다'}); continue; }
    if(Math.abs(v[0])>1000||Math.abs(v[1])>1000){ const [lo,la]=P.inverse([v[0],v[1]]); batchRows.push({src:l,lat:la,lon:lo,x:v[0],y:v[1],dir:'XY→경위도'}); }
    else { const [x,y]=P.forward([v[1],v[0]]); batchRows.push({src:l,lat:v[0],lon:v[1],x,y,dir:'경위도→XY'}); } }
  batchRows.forEach(r=>{ if(!r.err) r.addr=addrAt(r.x,r.y); });
  $('batchOut').innerHTML='<tr><th>입력</th><th style="text-align:right">X / Y (m)</th><th style="text-align:right">위도 / 경도</th></tr>'+batchRows.map(r=>r.err?`<tr><td>${esc(r.src)}</td><td colspan="2" class="err">${r.err}</td></tr>`:`<tr><td><span class="mono">${esc(r.src)}</span><div class="small">${r.dir}${r.addr?' · '+esc(r.addr):''}</div></td><td class="num">${fmt(r.x)}<br>${fmt(r.y)}</td><td class="num">${r.lat.toFixed(6)}<br>${r.lon.toFixed(6)}</td></tr>`).join('');
  const ok=batchRows.filter(r=>!r.err); ok.forEach((r,i)=>pins.push({lat:r.lat,lon:r.lon,x:r.x,y:r.y,label:'일괄 '+(i+1),sub:r.addr}));
  if(ok.length){ let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity; ok.forEach(r=>{x0=Math.min(x0,r.x);x1=Math.max(x1,r.x);y0=Math.min(y0,r.y);y1=Math.max(y1,r.y);});
    flyTo((x0+x1)/2,(y0+y1)/2,Math.max(50,Math.max((x1-x0)/W,(y1-y0)/H)*1.4)); }
};
$('copyBatch').onclick=()=>{ if(!batchRows.length){ $('copyMsg').textContent='먼저 변환을 눌러 주세요.'; return; }
  const txt='input\tX\tY\tlat\tlon\taddress\n'+batchRows.filter(r=>!r.err).map(r=>[r.src,r.x.toFixed(3),r.y.toFixed(3),r.lat.toFixed(8),r.lon.toFixed(8),r.addr||''].join('\t')).join('\n');
  navigator.clipboard.writeText(txt).then(()=>{ $('copyMsg').textContent='탭으로 구분된 표로 복사했습니다. 엑셀에 붙여 넣으면 됩니다.'; },()=>{ $('batch').value=txt; $('batch').select(); $('copyMsg').textContent='자동 복사가 막혀 있어 입력칸에 결과를 넣고 선택해 두었습니다. Ctrl+C로 복사하세요.'; }); };
$('clearPins').onclick=()=>{ pins.length=0; draw(); };

/* ---------- 탭 ---------- */
const tabs=[...document.querySelectorAll('[role=tab]')];
tabs.forEach(t=>t.addEventListener('click',()=>{ tabs.forEach(o=>{ const on=o===t; o.setAttribute('aria-selected',on); $(o.getAttribute('aria-controls')).hidden=!on; }); }));

/* ---------- shp 읽기 (도로명주소 전자지도 등) ---------- */
function parseShp(buf){
  const dv=new DataView(buf), out=[]; let o=100;
  while(o+8<=buf.byteLength){ const len=dv.getInt32(o+4,false)*2; const s=o+8; const t=len>=4?dv.getInt32(s,true):0; let rec=null;
    if(t===1||t===11||t===21){ rec={kind:'pt',parts:[new Float64Array([dv.getFloat64(s+4,true),dv.getFloat64(s+12,true)])]}; }
    else if(t===8||t===18||t===28){ const n=dv.getInt32(s+36,true); rec={kind:'pt',parts:[]}; for(let i=0;i<n;i++) rec.parts.push(new Float64Array([dv.getFloat64(s+40+16*i,true),dv.getFloat64(s+48+16*i,true)])); }
    else if([3,5,13,15,23,25].includes(t)){ const np=dv.getInt32(s+36,true), n=dv.getInt32(s+40,true); const idx=[]; for(let i=0;i<np;i++) idx.push(dv.getInt32(s+44+4*i,true)); idx.push(n); const pb=s+44+4*np; rec={kind:(t%10===5)?'poly':'line',parts:[]};
      for(let k=0;k<np;k++){ const a=new Float64Array((idx[k+1]-idx[k])*2); for(let i=idx[k],j=0;i<idx[k+1];i++,j+=2){ a[j]=dv.getFloat64(pb+16*i,true); a[j+1]=dv.getFloat64(pb+16*i+8,true); } rec.parts.push(a); } }
    out.push(rec); o=s+len; }
  return out;
}
function parseDbf(buf,enc){
  const dv=new DataView(buf), u8=new Uint8Array(buf); const n=dv.getUint32(4,true), hl=dv.getUint16(8,true), rl=dv.getUint16(10,true);
  let td; try{ td=new TextDecoder(enc); }catch(e){ td=new TextDecoder('euc-kr'); }
  const fields=[]; for(let p=32;p<hl-1&&u8[p]!==0x0D;p+=32){ let e=p; while(e<p+11&&u8[e]) e++; fields.push({name:td.decode(u8.subarray(p,e)),type:String.fromCharCode(u8[p+11]),len:u8[p+16]}); }
  const rows=[]; for(let i=0;i<n;i++){ const b=hl+i*rl; if(b+rl>u8.length) break; let p=b+1; const r={}; for(const f of fields){ r[f.name]=td.decode(u8.subarray(p,p+f.len)).trim(); p+=f.len; } rows.push(r); }
  return {fields,rows};
}
const NAME_FIELDS=['RN','ROAD_NM','RD_NM','ROAD_NAME','RDNM','RN_NM','NAME','NM','KOR_NAM','ROD_NAM'];
async function loadShpSet(files){
  const by={}; for(const f of files){ const m=f.name.match(/^(.*)\.(shp|dbf|prj|cpg)$/i); if(m) (by[m[1]]=by[m[1]]||{})[m[2].toLowerCase()]=f; }
  const sets=Object.entries(by).filter(([k,v])=>v.shp&&v.dbf);
  if(!sets.length){ $('userInfo').textContent='.shp와 같은 이름의 .dbf를 함께 골라 주세요. (.prj, .cpg도 있으면 같이)'; return; }
  let added=0, msgs=[];
  for(const [base,v] of sets){
    const shp=parseShp(await v.shp.arrayBuffer());
    let enc='euc-kr'; if(v.cpg){ const c=(await v.cpg.text()).trim().toLowerCase(); enc=/utf/.test(c)?'utf-8':'euc-kr'; }
    const dbf=parseDbf(await v.dbf.arrayBuffer(),enc);
    let src=null; if(v.prj){ try{ src=proj4((await v.prj.text()).trim()); }catch(e){ msgs.push(base+'.prj를 읽지 못해 UTM-K로 가정했습니다'); } }
    const fnames=dbf.fields.map(f=>f.name);
    let nf=NAME_FIELDS.find(n=>fnames.includes(n)) || fnames.find(n=>/(RN|NM|NAM|NAME|명)/i.test(n)) || dbf.fields.find(f=>f.type==='C')?.name;
    let sample=null; for(const r of shp) if(r&&r.parts.length&&r.parts[0].length){ sample=r.parts[0]; break; }
    const isLL = !src && sample && Math.abs(sample[0])<1000;
    const toBase = src ? (xy=>BASE.forward(src.inverse(xy))) : isLL ? (xy=>BASE.forward(xy)) : null;
    shp.forEach((r,i)=>{ if(!r) return; const parts=toBase?r.parts.map(a=>{ const o=new Float64Array(a.length); for(let j=0;j<a.length;j+=2){ const t=toBase([a[j],a[j+1]]); o[j]=t[0]; o[j+1]=t[1]; } return o; }):r.parts;
      const nm=(dbf.rows[i]&&dbf.rows[i][nf])||''; USER.push({n:nm,kind:r.kind,base:parts,src:base}); added++; });
    msgs.push(`${base}: ${shp.length.toLocaleString()}개 피처, 이름 필드 ${nf||'없음'}${src?' · .prj 변환':isLL?' · 경위도로 판단해 변환':' · UTM-K로 가정'}`);
  }
  userMeta = msgs; projectAll(); renderChips(); draw();
  $('userInfo').textContent = msgs.join(' / ') + ` — 이제 검색창에서 도로명을 찾을 수 있습니다.`;
  const b=bboxOf(USER.flatMap(f=>f.g)); if(isFinite(b[0])) flyTo((b[0]+b[2])/2,(b[1]+b[3])/2,Math.max(2,Math.max((b[2]-b[0])/W,(b[3]-b[1])/H)*1.2));
  tabs[0].click();
}
$('shpInput').onchange=e=>{ loadShpSet([...e.target.files]); e.target.value=''; };
$('userClear').onclick=()=>{ USER=[]; if(sel&&sel.e.type==='user') sel=null; projectAll(); draw(); $('userInfo').textContent='불러온 shp를 지웠습니다.'; renderResults(search($('q').value),$('q').value.trim()); };

/* ---------- GeoJSON·드래그 ---------- */
const gjXY = (pt,isXY) => isXY ? (T?T(pt):pt) : P.forward(pt);
function loadGeojson(text,name){
  let d; try{ d=JSON.parse(text); }catch(e){ $('gjInfo').textContent='JSON으로 읽을 수 없습니다: '+e.message; return; }
  const feats = d.type==='FeatureCollection'?d.features:d.type==='Feature'?[d]:[{geometry:d}];
  const f={name,geoms:[],kinds:[]}; let maxAbs=0;
  const add=(g)=>{ if(!g) return; const c=g.coordinates;
    if(g.type==='Point'){ f.geoms.push([c]); f.kinds.push('pt'); }
    else if(g.type==='MultiPoint'){ c.forEach(p=>{f.geoms.push([p]);f.kinds.push('pt');}); }
    else if(g.type==='LineString'){ f.geoms.push(c); f.kinds.push('line'); }
    else if(g.type==='MultiLineString'){ c.forEach(l=>{f.geoms.push(l);f.kinds.push('line');}); }
    else if(g.type==='Polygon'){ c.forEach(r=>{f.geoms.push(r);f.kinds.push('poly');}); }
    else if(g.type==='MultiPolygon'){ c.forEach(p=>p.forEach(r=>{f.geoms.push(r);f.kinds.push('poly');})); }
    else if(g.type==='GeometryCollection'){ g.geometries.forEach(add); } };
  feats.forEach(ft=>add(ft.geometry));
  f.geoms.forEach(g=>g.forEach(p=>{ maxAbs=Math.max(maxAbs,Math.abs(p[0]),Math.abs(p[1])); }));
  f.isXY = maxAbs>1000; f.proj = f.geoms.map(g=>g.map(pt=>gjXY(pt,f.isXY))); gj.push(f);
  $('gjInfo').textContent = `${name}: 도형 ${f.geoms.length.toLocaleString()}개, ${f.isXY?'UTM-K 미터 좌표로 판단':'경위도(WGS84)로 판단해 UTM-K로 변환'}했습니다.`;
  let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity; f.proj.forEach(g=>g.forEach(([x,y])=>{x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}));
  if(isFinite(x0)) flyTo((x0+x1)/2,(y0+y1)/2,Math.max(5,Math.max((x1-x0)/W,(y1-y0)/H)*1.25));
}
$('gjInput').onchange=e=>{ const f=e.target.files[0]; if(f) f.text().then(t=>{ loadGeojson(t,f.name); tabs[2].click(); }); e.target.value=''; };
$('gjClear').onclick=()=>{ gj.length=0; $('gjInfo').textContent='지웠습니다.'; draw(); };
$('prjInput').onchange=e=>{ const f=e.target.files[0]; if(!f) return; f.text().then(t=>{ try{ loadPrj(t.trim(),f.name); $('prjErr').textContent=''; }catch(err){ $('prjErr').textContent=err.message; tabs[3].click(); } }); e.target.value=''; };
const mw=$('mapwrap');
mw.addEventListener('dragover',e=>{ e.preventDefault(); $('drop').hidden=false; });
mw.addEventListener('dragleave',e=>{ if(e.target===$('drop')) $('drop').hidden=true; });
mw.addEventListener('drop',e=>{ e.preventDefault(); $('drop').hidden=true; const fs=[...e.dataTransfer.files]; if(!fs.length) return;
  if(fs.some(f=>/\.shp$/i.test(f.name))){ loadShpSet(fs); return; }
  const f=fs[0];
  f.text().then(t=>{ if(/\.prj$/i.test(f.name)||/^\s*(PROJCS|GEOGCS)\[/.test(t)){ try{ loadPrj(t.trim(),f.name); }catch(err){ $('prjErr').textContent=err.message; tabs[3].click(); } } else { loadGeojson(t,f.name); tabs[2].click(); } }); });

/* ---------- 시작 ---------- */
readColors();
const recolor=()=>{ readColors(); draw(); };
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',recolor);
new MutationObserver(recolor).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
try { loadPrj(PRJ_DEFAULT,'GRS80_UTMK.prj'); } catch(e){ $('prjErr').textContent=e.message; }
renderLayers(); renderChips();
new ResizeObserver(()=>{ const first=!W; resize(); if(first){ home(); const k=INDEX.find(e=>e.key==='road|경부고속국도'); $('q').value=$('mq').value='경부고속국도'; renderResults(search('경부고속국도'),'경부고속국도'); if(k) select(k.key,false); drawNow(); } }).observe(cv);
if(document.fonts) document.fonts.ready.then(()=>{ readColors(); draw(); });
</script>
````

### `CLAUDE.md`

작업 규칙 (아티팩트 게시 규칙·주소 목록 추가)

````markdown
# 작업 규칙

## 에이전트 작업현황 (항상)
- 서브에이전트(Agent 도구)·병렬 조사·GitHub Actions 수집 실행 등 에이전트 작업을 할 때는 **항상 에이전트 작업현황을 보여준다.**
  - 아티팩트 **에이전트 작업현황** https://claude.ai/artifact/89otDQXoXzXKDG8U1kpkd7 을 같은 URL로 갱신한다
    (스킬: `skills/agent-status/` · `skills/agent-status.zip`, 원본: `docs/agent_status.html`, 아이콘은 주황 픽셀 캐릭터 `#clawd` 심볼 — 그대로 유지).
  - 메인 에이전트(발주) → 서브에이전트(하청) 구조로 그린다. 파일 아래 `JOB` 데이터만 고친다:
    `subs[]`에 하청마다 `status`(wait/run/done)·`progress`(0~100)·`task`·결과를 넣으면 메인 진행률은 평균으로 계산된다.
  - 에이전트를 시작할 때 카드를 `진행 중`으로 올리고, 끝나면 `완료`와 결과(건수·대상)로 바꾼다.
  - 갱신할 때마다 Artifact 도구 `action: "open"`으로 작업현황 페이지를 **항상 열어** 보여준다.
  - 답변에도 작업현황 표(에이전트 · 상태 · 결과)를 함께 적는다.

## 결과 바로 열어 보기 (항상)
- 결과가 나오면 **바로** 최종 결과물을 **HTML 한 파일**로 이 세션에 게시한다: SendUserFile(`display: "render"`)로 완성된 HTML 한 파일을 보낸다.
  (작업 중간 산출물이 아니라 최종본만, 결과가 나올 때마다 매번)
  - 브리핑: 기본 브랜치 `briefings/latest_edit.html`(완전한 HTML 한 파일, 편집·A4 인쇄 가능)을
    `docs/안전관리자_채용_브리핑_YYYY-MM-DD.html`로 복사해 render로 보낸다.
  - 그 밖의 결과(문서·표·보고서)도 HTML 한 파일로 만들어 render로 보낸다.
- 브리핑을 게시(갱신)한 뒤에는 Artifact 도구 `action: "open"`으로 브리핑 아티팩트
  https://claude.ai/artifact/8vwqioKkr5ADyBJnbVDQZA 도 연다 (작업현황 페이지와 함께).

## 작업이 끝나면 아티팩트로도 게시 (항상)
- 작업이 끝나면 결과를 **이 세션에서 아티팩트로도 게시**하고 링크를 답변에 적는다.
  - 브리핑 → **항상** 기본 브랜치 `briefings/latest.html`(+ `briefings/archive/briefing_*.html` 날짜별 사본)을
    브리핑 아티팩트(위 URL)에 같은 URL로 게시하고, 최종 결과물 `briefings/latest_edit.html`을
    `docs/안전관리자_채용_브리핑_YYYY-MM-DD.html`로 복사해 이 세션에 render로 보낸다.
  - 규칙·자료 정리 → [안전관리자 브리핑 운영 규칙](https://claude.ai/artifact/6VvRGcg4ETB48WhnAWBCcr)
    (원본 `docs/rules_and_materials/규칙_자료_모음.html`)을 같은 URL로 갱신.
  - 채용 달력 → 브리핑을 게시할 때마다 **항상** 기본 브랜치 `briefings/calendar.html`(채용 달력만 담은 HTML 한 파일)을
    [안전관리자 채용 달력](https://claude.ai/artifact/1pvKKJpGMY9Wc4cqH3AaAk)에 같은 URL로 게시하고,
    `docs/안전관리자_채용_달력_YYYY-MM-DD.html`로 복사해 render로도 보낸다.
  - 그 밖의 결과 → 결과 HTML 한 파일을 새 아티팩트로 게시(같은 주제를 다시 하면 그 URL을 갱신).
    - **결과물은 예외 없이 항상 아티팩트에 게시한다.** 파일 전송(SendUserFile)이나 저장소 커밋만으로 끝내지 않는다.
    - 지금까지 게시한 결과 아티팩트(같은 주제는 이 URL을 갱신):
      - UTM-K 좌표 지도 → https://claude.ai/artifact/PWDf1TAfB3pZUhWr2NDWhG (원본 `docs/UTM-K_좌표지도.html`)
      - 지번주소 위치 찾기(방법 비교) → https://claude.ai/artifact/5FumKm76MNjT2sPksqGzSL (원본 `docs/지번주소_위치표시_방법.html`)
      - UTM-K 지도 작업 기록 → https://claude.ai/artifact/CRjmzMmXnh6Jhf3G7dTAEV (원본 `docs/UTM-K_지도_작업기록.md`, `.html`)
- 게시한 아티팩트는 `action: "open"`으로 연다.
````
