# 안전관리자 채용 일일 브리핑

매일 **19:07·19:27 KST** GitHub Actions(`.github/workflows/safety-jobs-briefing.yml`)가
`collect.py`로 아래 사이트의 안전관리자 채용 공고를 수집해 `briefings/`에 커밋하고,
**20:00 KST** Routine이 `briefings/latest.*`를 읽어 브리핑을 전달한다.

```bash
uv run safety_jobs/collect.py --out briefings   # latest.md / latest.html / latest.json / YYYY-MM-DD.md
```

## 수집 대상 (순서 = 중복 시 우선순위)

| # | 사이트 | 수집 방법 |
|---|---|---|
| 1 | 잡코리아 신입·인턴 채용관 | 채용관 목록 API에서 `안전관리자` 검색 |
| 2 | 사람인 | 지정 검색 URL + 신입/경력무관 필터 100건 |
| 3 | 링커리어 | 검색 결과 `__NEXT_DATA__` |
| 4 | 건설워커 | `안전/품질/재료/CAD` 부문 목록 3쪽 |
| 5–8 | 서울과기대·충북대·인천대·부경대 안전공학과 | 취업/채용 게시판 (최근 75일, 안전 직무 포함 글) |
| 9 | 피플앤잡 (외국계) | 제목 검색(안전·보건·HSE·EHS·Safety·SHE) + 전체 검색(HSE·EHS·NEBOSH·산업안전기사·ISO 45001) |
| 10 | 기업 채용 페이지 | Workday 공개 API: 3M·Applied Materials·Micron·Equinix·Air Liquide·Air Products (+ Lam Research·Linde·ASML·Corning·Dow·Honeywell은 채용 홈에서 Workday 주소 탐색), BASF(SuccessFactors). 한국 근무 HSE/EHS/Safety 공고만, 영문 `N+ years of experience` 2년 이상은 경력직으로 제외 |
| 11 | 원티드 | 공개 API — 현재 GitHub Actions 접속을 403 차단 |
| 12 | 캐치 | 검색 결과 — 현재 GitHub Actions 접속을 403 차단 |

## 이전 수집 정보 유지

- 접수기한이 남은 공고는 다음 수집에서 목록에 안 보여도 `latest.json`에서 이어받는다(마감일 없는 공고는 14일).
- 실행마다 원격 최신 `briefings/`를 이어받아 수집하고, 결과는 `briefings/history/YYYY-MM-DD.json.gz`에 날짜별로 보관한다.

## 규칙

- **대상**: 안전 직무(안전·보건·HSE/EHS·소방·방재) 공고 중 신입 / 경력무관 / 신입·경력 / 인턴. 경력직 전용·마감 공고 제외.
- **직급**: 대리급 이상(제목·직급·본문·우대 표기 포함, 영문 Senior/Manager/Director 등)이 명시된 공고는 제외. 산업안전기사·건설안전기술사 등 기술사 우대 공고는 포함.
- **계약직**: 관심 기업(대기업 계열·외국계·코스피/코스닥·데이터센터/반도체) + 도급순위 15위 이내 건설사만.
- **중복**: 업체명 + 제목 유사도로 판단, 위쪽 사이트 것을 남긴다.
- **표기**: `[정규직]`, `[계약직]`, `[인턴]`, `[고용형태 미표기]` 문단으로 나눈다.
- **표 열**: 구분 · 업체명 · 공고명 · 지원 자격(학과·자격·영어·학력) · 우대 사항 · 접수기한 · 출처.
- **강조**: 🔴 데이터센터·하이테크·삼성·하이닉스 관련 / 🔵 대기업군·외국계 (둘 다면 🔴).
  HTML(`latest.html`)은 행 배경색으로 구분한다.

지원 자격·우대 사항은 상세 페이지 본문에서 자동 추출한 요약이므로 지원 전 원문 확인이 필요하다.
