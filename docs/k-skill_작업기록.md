# k-skill 용량·파일 수 줄이기 작업 기록

- 작업일: 2026-11-05 (기록 저장: 2026-11-18)
- 원본: `k-skill-110-R1.zip` (2,563,850바이트 · 2.56MB · 파일 936개 · 스킬 110개)
- 최종본: `docs/k-skill-110-R1-200files.zip` (575,780바이트 · 0.55MB · 파일 112개 · SKILL.md 1개 · 스킬 110개)
- 브랜치: `claude/elegant-edison-ofhyii` · PR: https://github.com/chaeeun030702/001/pull/106 (초안)
- 선택 도구 아티팩트: https://claude.ai/artifact/UGkCfUM7GMTFQpJyR1icLp

## 1. 대화 흐름

| 순서 | 요청 / 오류 | 한 일 | 결과 |
| --- | --- | --- | --- |
| 1 | "스킬을 2MB 이내로 줄이고 싶어. 리스트 보고 선택해 삭제할 수 있도록 해줘" | zip을 풀어 항목별 압축 크기를 계산하고, 체크하면 예상 크기가 계산되는 HTML 선택 도구를 만듦 | `docs/k-skill_용량정리.html` + 아티팩트 게시 |
| 2 | "CLI 테스트 스냅샷 전체 삭제" | `k-skill/packages/k-skill-cli/test/` 220개 파일 삭제 | `docs/k-skill-110-R1-2MB.zip` · 1.52MB · 716개 파일 |
| 3 | 오류 `Zip contains too many files (maximum 200)` | 파일 구성을 분석함. 사본·문서를 다 빼도 스킬 폴더만 220개(SKILL.md 110 + instruction.md 110)라서 200개를 넘음 | 방법 세 가지를 제시하고 사용자가 "스킬당 한 파일로 합치기"를 선택 |
| 4 | (선택 반영) | 스킬마다 SKILL.md + instruction.md + references를 한 파일로 합치고, 110개 목록을 담은 루트 SKILL.md를 새로 만들고, packages/docs를 뺌 | 0.55MB · 112개 파일 |
| 5 | 오류 `Zip must contain exactly one SKILL.md file. Currently there are 111.` | 스킬별 파일을 `skills/<이름>.md`로 옮겨 SKILL.md를 루트 1개만 남김 | 최종본 · 업로드 성공 (`k-skill` 스킬로 등록 확인) |
| 6 | PR 안전망 점검 3회 | 충돌·리뷰·CI 모두 없음 | 점검 중단 |

## 2. 원본 분석 결과

### 압축 크기 (2MB 기준)

| 항목 | 압축 크기 | 비고 |
| --- | --- | --- |
| `packages/k-skill-cli/test/` (테스트 스냅샷) | 약 943KB | 스킬 설명서의 테스트용 중복 사본. 스킬 사용에 불필요 |
| `packages/k-skill-cli/skills/` | 약 496KB | 루트 스킬 폴더 instruction.md와 110개 모두 내용 동일 |
| `docs/features/` | 약 229KB | 스킬별 기능 설명서 |
| `docs/` 나머지 | 약 88KB | 설치·배포·로드맵 문서 |
| 스킬 폴더 110개 | 나머지 | 스킬당 4~69KB (가장 큰 것: korean-humanizer) |

### 파일 수 (200개 기준, 테스트 스냅샷 삭제 후 716개)

| 묶음 | 파일 수 |
| --- | --- |
| 스킬 폴더 | 318 (SKILL.md 110 · instruction.md 110 · references 98, 이 중 72개는 DISCLAIMER/TRADEMARK 법적고지) |
| `packages/k-skill-cli/skills/` | 200 |
| `docs/features/` | 110 |
| `docs/` 나머지 | 21 |
| `packages/k-skill-cli/templates/` | 13 |
| 기타 packages (README·CHANGELOG) | 45 |
| 루트 파일 | 9 |

참고: 원본 각 스킬의 SKILL.md는 `npx -y @nomadamas/k-skill@0 instruct <이름>`을 실행하라는 안내문(stub)이고, 실제 지침은 instruction.md에 있음.

## 3. 만든 파일

| 파일 | 내용 |
| --- | --- |
| `docs/k-skill_용량정리.html` | 스킬 110개 + 부가 자료 6개의 체크 목록. 예상 zip 크기와 삭제 목록 복사 기능 (예상치와 실제 크기 일치 확인) |
| `docs/k-skill-110-R1-2MB.zip` | 테스트 스냅샷만 삭제한 판. 1.52MB · 716개 파일 (파일 수 제한 때문에 업로드 불가) |
| `docs/k-skill-110-R1-200files.zip` | 최종 업로드본. 0.55MB · 112개 파일 |
| `docs/k-skill_작업기록.md` | 이 문서 |

### 최종본 구조

```
k-skill/
├── SKILL.md      ← 유일한 SKILL.md (110개 스킬 카테고리별 목록)
├── LICENSE       ← MIT
└── skills/
    └── <스킬 이름>.md × 110   (원본 SKILL.md + instruction.md + references를 차례로 이어 붙임)
```

### 최종본 파일 목록 (압축 전 바이트 · 경로)

<details><summary>112개 펼치기</summary>

```
   18994  k-skill/skills/danawa-price-search.md
   14110  k-skill/skills/bunjang-search.md
    5860  k-skill/skills/g2b-sanctioned-supplier.md
    6560  k-skill/skills/gongsijiga-search.md
   16848  k-skill/skills/sharenuri-facility-search.md
    4995  k-skill/skills/localdata-business-status.md
    8541  k-skill/skills/lotto-results.md
    6773  k-skill/skills/household-waste-info.md
    5534  k-skill/skills/korean-holiday-calendar.md
   42890  k-skill/skills/corporate-registration-consulting.md
   10495  k-skill/skills/k-skill-setup.md
    6215  k-skill/skills/bok-ecos-stats.md
   17060  k-skill/skills/flight-ticket-search.md
    5350  k-skill/skills/assembly-bill-vote-search.md
   13192  k-skill/skills/korean-privacy-terms.md
    9614  k-skill/skills/kopis-performance-search.md
   14245  k-skill/skills/korean-cinema-search.md
   16533  k-skill/skills/iros-registry-automation.md
   14199  k-skill/skills/korean-jangbu-for.md
    5222  k-skill/skills/subway-lost-property.md
    9991  k-skill/skills/housing-official-price.md
   17665  k-skill/skills/k-dart.md
    4932  k-skill/skills/joseon-sillok-search.md
   13047  k-skill/skills/kakao-bar-nearby.md
    7254  k-skill/skills/building-register-search.md
    4834  k-skill/skills/emergency-room-beds.md
   20947  k-skill/skills/korean-scholarship-search.md
    5687  k-skill/skills/railway-timetable.md
   14264  k-skill/skills/ohou-today-deal.md
    5957  k-skill/skills/korean-spell-check.md
    4627  k-skill/skills/fsc-corporate-info.md
    9836  k-skill/skills/ev-subsidy-status.md
   13167  k-skill/skills/rhwp-edit.md
   10665  k-skill/skills/seoul-weather-risk.md
   16651  k-skill/skills/court-auction-notice-search.md
   11111  k-skill/skills/keris-academic-search.md
    7256  k-skill/skills/nts-business-registration.md
    6991  k-skill/skills/korean-marathon-schedule.md
    7483  k-skill/skills/donation-place-search.md
    7980  k-skill/skills/court-payment-order-assistant.md
    6046  k-skill/skills/cheap-gas-nearby.md
    5992  k-skill/skills/mfds-drug-safety.md
   11823  k-skill/skills/korean-transit-route.md
   14780  k-skill/skills/daishin-report-search.md
    7460  k-skill/skills/government-support-survey.md
    9192  k-skill/skills/real-estate-search.md
    5258  k-skill/skills/korean-character-count.md
   12434  k-skill/skills/daangn-cars-search.md
   42978  k-skill/skills/korean-humanizer.md
    6259  k-skill/skills/k-skill-cleaner.md
   20518  k-skill/skills/intercity-bus-booking.md
    5380  k-skill/skills/parking-lot-search.md
    8694  k-skill/skills/store-longevity-radar.md
    7386  k-skill/skills/korean-law-search.md
   14811  k-skill/skills/job-posting-match.md
    6205  k-skill/skills/seoul-density.md
   18753  k-skill/skills/korean-bond-search.md
    7109  k-skill/skills/biz-health-check.md
    5006  k-skill/skills/korean-patent-search.md
   13757  k-skill/skills/popbill.md
   10068  k-skill/skills/hankookilbo-news.md
    6928  k-skill/skills/zipcode-search.md
    6489  k-skill/skills/korean-heritage-search.md
   26321  k-skill/skills/kosis-stats.md
   12577  k-skill/skills/daangn-jobs-search.md
   10177  k-skill/skills/g2b-order-plan-search.md
    4623  k-skill/skills/fine-dust-location.md
    5852  k-skill/skills/public-restroom-nearby.md
   12426  k-skill/skills/daangn-used-goods-search.md
   43016  k-skill/skills/multi-asset-morning-briefing.md
    7206  k-skill/skills/nhis-care-checkup-search.md
    4395  k-skill/skills/nts-tax-delinquency.md
   20375  k-skill/skills/delivery-tracking.md
   10190  k-skill/skills/toss-investment.md
   10673  k-skill/skills/lh-notice-search.md
    9215  k-skill/skills/rhwp-advanced.md
   17256  k-skill/skills/myrealtrip-search.md
   35482  k-skill/skills/market-event-impact.md
   10872  k-skill/skills/religious-facility-search.md
    3792  k-skill/skills/geeknews-search.md
   14584  k-skill/skills/kakao-map.md
   11729  k-skill/skills/saramin-talent-search.md
   20026  k-skill/skills/express-bus-booking.md
   14138  k-skill/skills/daangn-realty-search.md
   12917  k-skill/skills/ticket-availability.md
    7725  k-skill/skills/sh-notice-search.md
    6975  k-skill/skills/kr-whois-lookup.md
    7691  k-skill/skills/library-book-search.md
   11438  k-skill/skills/naver-shopping-search.md
    4494  k-skill/skills/komsa-ferry-info.md
    5640  k-skill/skills/national-pension-workplace.md
    4972  k-skill/skills/korea-weather.md
   12176  k-skill/skills/korean-stock-search.md
   30200  k-skill/skills/gov-overseas-trip-report.md
    9560  k-skill/skills/mfds-food-safety.md
   17858  k-skill/skills/bccard-eatpl-search.md
   12208  k-skill/skills/coupang-product-search.md
    9246  k-skill/skills/hwp.md
   10413  k-skill/skills/korean-slang-writing.md
   15956  k-skill/skills/daiso-product-search.md
   11017  k-skill/skills/naver-blog-research.md
    6399  k-skill/skills/ev-charger-nearby.md
    8400  k-skill/skills/saju-fortune.md
   12663  k-skill/skills/naver-news-search.md
   28670  k-skill/skills/company-analysis.md
    4783  k-skill/skills/kamis-food-price.md
   13282  k-skill/skills/jobkorea-talent-search.md
    6533  k-skill/skills/highway-traffic-status.md
    8205  k-skill/skills/naming-house.md
   16096  k-skill/skills/foresttrip-vacancy.md
   14566  k-skill/SKILL.md
    1056  k-skill/LICENSE
```

</details>

## 4. 최종본 루트 SKILL.md 전문

````markdown
---
name: k-skill
description: 한국 특화 검색·조회·자동화 스킬 110개 모음. 쇼핑 가격비교, 부동산·경매, 교통·예매, 공공·행정·법률, 금융·주식, 날씨·생활, 한국어 글쓰기 등 한국 서비스와 공공데이터를 다루는 요청에 사용한다. 아래 목록에서 맞는 스킬을 찾아 skills 폴더의 해당 파일을 읽고 따른다.
license: MIT
---

# k-skill (110개 스킬 묶음)

요청에 맞는 스킬을 아래 목록에서 고른 뒤 `skills/<스킬 이름>.md`를 읽고 그 지침을 따른다.
각 skills/*.md에는 원본 SKILL.md, instruction.md, references 자료가 한 파일에 합쳐져 있다.

## 쇼핑 · 커머스

- [`coupang-product-search`](skills/coupang-product-search.md) — 쿠팡 Partners API로 상품 검색·로켓배송·가격 후보 비교
- [`naver-shopping-search`](skills/naver-shopping-search.md) — 네이버 쇼핑 BFF로 상품 후보·최저가·판매처 가격비교
- [`danawa-price-search`](skills/danawa-price-search.md) — 다나와 가격비교로 실구매가·카드할인·무이자할부 비교
- [`daiso-product-search`](skills/daiso-product-search.md) — 다이소몰 매장별 상품 재고 조회
- [`ohou-today-deal`](skills/ohou-today-deal.md) — 오늘의집 오늘의딜 특가·할인율·리뷰·링크 조회
- [`bunjang-search`](skills/bunjang-search.md) — 번개장터 검색·상세·찜·채팅·대량수집·AI TOON export
- [`daangn-used-goods-search`](skills/daangn-used-goods-search.md) — 당근 중고거래 키워드·지역 매물 검색/상세

## 부동산 · 경매 · 차량

- [`real-estate-search`](skills/real-estate-search.md) — 아파트/오피스텔/빌라 실거래가·전월세 조회 (MOLIT)
- [`daangn-realty-search`](skills/daangn-realty-search.md) — 당근부동산 지역 기반 매물 검색/상세
- [`gongsijiga-search`](skills/gongsijiga-search.md) — 개별공시지가(원/㎡) 조회 (세금 산정용, 시세 아님)
- [`housing-official-price`](skills/housing-official-price.md) — 공동주택 공시가격 조회
- [`building-register-search`](skills/building-register-search.md) — 건축물대장 표제부 조회 (주소·PNU 기준)
- [`court-auction-notice-search`](skills/court-auction-notice-search.md) — 대법원경매정보 부동산 매각공고·사건 조회
- [`daangn-cars-search`](skills/daangn-cars-search.md) — 당근중고차 지역·가격 조건 차량 검색/상세
- [`iros-registry-automation`](skills/iros-registry-automation.md) — 인터넷등기소 등기사항증명서 발급 준비·브라우저 핸드오프

## 교통 · 예매 · 여행

- [`express-bus-booking`](skills/express-bus-booking.md) — 고속버스(KOBUS) 예매·시간표·좌석·임시선점
- [`intercity-bus-booking`](skills/intercity-bus-booking.md) — 시외버스(Tmoney) 예매·시간표·좌석/요금
- [`railway-timetable`](skills/railway-timetable.md) — Korail 통합 철도 시간표 조회 (KTX 계열, 조회 전용)
- [`flight-ticket-search`](skills/flight-ticket-search.md) — Google Flights 항공권 후보·최저가/평균가 비교
- [`myrealtrip-search`](skills/myrealtrip-search.md) — 마이리얼트립 항공권·숙소·투어/티켓/액티비티 검색
- [`korean-transit-route`](skills/korean-transit-route.md) — 지하철+버스+도보 door-to-door 대중교통 경로 (ODsay)
- [`komsa-ferry-info`](skills/komsa-ferry-info.md) — 연안여객선 운항 일정·선박·항로 정보 (KOMSA MTIS)
- [`highway-traffic-status`](skills/highway-traffic-status.md) — 고속도로 실시간 소통·정체등급·CCTV 메타데이터
- [`foresttrip-vacancy`](skills/foresttrip-vacancy.md) — 국립자연휴양림 숙박·야영 빈자리 조회
- [`subway-lost-property`](skills/subway-lost-property.md) — 지하철 분실물/유실물 조회 안내 (LOST112)

## 공공 · 행정 · 법률

- [`korean-law-search`](skills/korean-law-search.md) — 법령·조문·판례·법령해석·자치법규 검색
- [`assembly-bill-vote-search`](skills/assembly-bill-vote-search.md) — 의안 검색/상세·국회의원 본회의 표결정보
- [`court-payment-order-assistant`](skills/court-payment-order-assistant.md) — 전자소송 지급명령 인터뷰·신청서 초안·입력 핸드오프
- [`corporate-registration-consulting`](skills/corporate-registration-consulting.md) — 주식회사 발기설립 절차·정관 HWP 작성·등록면허세 안내
- [`korean-privacy-terms`](skills/korean-privacy-terms.md) — Next.js 프로젝트에 한국 법령 기반 약관·개인정보처리방침 설치
- [`korean-patent-search`](skills/korean-patent-search.md) — KIPRIS Plus 특허·실용신안 공보 검색
- [`kr-whois-lookup`](skills/kr-whois-lookup.md) — .kr/한국 도메인·IP·AS 번호 공개 등록정보 조회
- [`zipcode-search`](skills/zipcode-search.md) — 우편번호·공식 영문주소 조회
- [`korean-holiday-calendar`](skills/korean-holiday-calendar.md) — 공휴일·국경일·기념일·24절기·잡절 조회 (KASI)
- [`household-waste-info`](skills/household-waste-info.md) — 시군구별 생활쓰레기 배출 요일·시간·장소
- [`gov-overseas-trip-report`](skills/gov-overseas-trip-report.md) — 공무국외출장·국외훈련 보고서 조회 및 원문 사실 확인
- [`sharenuri-facility-search`](skills/sharenuri-facility-search.md) — 공유누리 공공개방자원(회의실·체육·숙소·물품) 검색·예약정보
- [`lh-notice-search`](skills/lh-notice-search.md) — LH 청약(청년/행복/영구/국민/매입/전세임대) 공고
- [`sh-notice-search`](skills/sh-notice-search.md) — SH공사 청약·주택 공고 목록·본문·첨부
- [`donation-place-search`](skills/donation-place-search.md) — 지역별 기부처 조회·추천
- [`religious-facility-search`](skills/religious-facility-search.md) — 근처 교회·성당·사찰 등 종교시설 조회
- [`public-restroom-nearby`](skills/public-restroom-nearby.md) — 근처 개방 화장실 조회

## 조달 · 입찰 · 기업조회

- [`g2b-order-plan-search`](skills/g2b-order-plan-search.md) — 나라장터 물품·공사·용역·외자 발주계획 검색
- [`g2b-sanctioned-supplier`](skills/g2b-sanctioned-supplier.md) — 나라장터 부정당제재업체(입찰참가자격 제한) 조회
- [`nts-business-registration`](skills/nts-business-registration.md) — 국세청 사업자등록 진위확인·상태조회
- [`nts-tax-delinquency`](skills/nts-tax-delinquency.md) — 국세청 고액·상습체납자 명단 조회
- [`fsc-corporate-info`](skills/fsc-corporate-info.md) — 금융위 기업기본정보(대표자·설립일·업종) 조회
- [`national-pension-workplace`](skills/national-pension-workplace.md) — 국민연금 가입 사업장 가입자수·고지금액·취득/상실 추이
- [`biz-health-check`](skills/biz-health-check.md) — 사업자번호 하나로 등록상태·연금·체납·법인개요·제재 통합 점검
- [`localdata-business-status`](skills/localdata-business-status.md) — 인허가 208종 사업장의 영업/휴업/폐업 상태·업력 조회

## 금융 · 투자 · 통계

- [`multi-asset-morning-briefing`](skills/multi-asset-morning-briefing.md) — 글로벌 주식·금리·외환·원자재·변동성과 한국시장 전달 경로 7섹션 브리핑
- [`market-event-impact`](skills/market-event-impact.md) — 정례 발표·비정형 사건의 교차자산 전달경로·시장 해석 정리
- [`korean-bond-search`](skills/korean-bond-search.md) — 한국 채권 발행조건·잔액·CALL/PUT·CB/EB/BW 검색·비교
- [`company-analysis`](skills/company-analysis.md) — 국내·해외 상장기업 공시·실적 대조 6섹션 분석
- [`k-dart`](skills/k-dart.md) — DART 공시검색·기업개황·재무제표·주요사항보고서
- [`korean-stock-search`](skills/korean-stock-search.md) — 상장종목 검색·KRX 기본정보·시세 조회
- [`toss-investment`](skills/toss-investment.md) — 토스증권 Open API 계좌·보유주식·시세·주문조회 (read-only)
- [`bok-ecos-stats`](skills/bok-ecos-stats.md) — 한국은행 ECOS 기준금리·환율·물가·통화량 시계열
- [`kosis-stats`](skills/kosis-stats.md) — KOSIS 국가통계포털 통계표 검색·메타데이터·데이터 조회
- [`kamis-food-price`](skills/kamis-food-price.md) — KAMIS 농수축산물 도소매 가격·기간별 비교
- [`popbill`](skills/popbill.md) — 팝빌 전자세금계산서·현금영수증·문자·팩스·휴폐업 조회
- [`korean-jangbu-for`](skills/korean-jangbu-for.md) — 1인 법인·프리랜서·개인사업자 장부 자동화

## 의료 · 안전 · 환경

- [`emergency-room-beds`](skills/emergency-room-beds.md) — 근처 응급실 위치·실시간 병상 현황
- [`nhis-care-checkup-search`](skills/nhis-care-checkup-search.md) — 건보공단 장기요양기관·건강검진기관 조회
- [`mfds-drug-safety`](skills/mfds-drug-safety.md) — 인터뷰형 의약품 안전 체크 (식약처)
- [`mfds-food-safety`](skills/mfds-food-safety.md) — 인터뷰형 식품 안전 체크 (식품안전나라)
- [`korea-weather`](skills/korea-weather.md) — 기상청 단기예보 기반 한국 날씨 요약
- [`seoul-weather-risk`](skills/seoul-weather-risk.md) — 서울 행정동별 기상 위험 예상 시간대
- [`fine-dust-location`](skills/fine-dust-location.md) — 에어코리아 미세먼지/초미세먼지 지역별 조회
- [`ev-charger-nearby`](skills/ev-charger-nearby.md) — 전기차 충전소 위치·충전기 타입·실시간 상태
- [`ev-subsidy-status`](skills/ev-subsidy-status.md) — 지자체별 전기차 보조금 공고·접수·출고잔여 대수

## 지역 · 장소

- [`kakao-map`](skills/kakao-map.md) — 카카오 장소검색·주소↔좌표 변환·자동차 길찾기
- [`bccard-eatpl-search`](skills/bccard-eatpl-search.md) — 지역·역·동네 기준 맛집·카페·회식 장소 추천
- [`kakao-bar-nearby`](skills/kakao-bar-nearby.md) — 근처 술집 검색
- [`cheap-gas-nearby`](skills/cheap-gas-nearby.md) — 근처 최저가 주유소 조회
- [`parking-lot-search`](skills/parking-lot-search.md) — 근처 주차장·공영주차장 조회
- [`seoul-density`](skills/seoul-density.md) — 서울 주요 121개 핫스팟 실시간 혼잡도·인구 현황

## 채용 · 창업 · 지원사업

- [`job-posting-match`](skills/job-posting-match.md) — 이력서 기반 잡코리아·사람인 공고 검색·적합도 분석
- [`jobkorea-talent-search`](skills/jobkorea-talent-search.md) — 잡코리아 인재 이력서 검색·shortlist (기업회원)
- [`saramin-talent-search`](skills/saramin-talent-search.md) — 사람인 인재풀 후보 검색·shortlist (기업회원)
- [`daangn-jobs-search`](skills/daangn-jobs-search.md) — 당근알바 키워드·지역 알바 공고 검색/상세
- [`government-support-survey`](skills/government-support-survey.md) — K-Startup·기업마당·NIPA·KOCCA·SMTECH 공고 전수조사·적합성 분류
- [`store-longevity-radar`](skills/store-longevity-radar.md) — 상권정보 공개파일로 장수 점포(N년 이상 영업) 선별
- [`korean-scholarship-search`](skills/korean-scholarship-search.md) — 한국 장학금 공고 검색·금액/자격 추출·필터

## 문서 · 한국어 텍스트

- [`hwp`](skills/hwp.md) — kordoc 기반 HWP/HWPX 파싱·JSON 추출·diff·양식 채우기
- [`rhwp-edit`](skills/rhwp-edit.md) — HWP 텍스트 삽입/삭제/치환·표 생성·셀 편집
- [`rhwp-advanced`](skills/rhwp-advanced.md) — HWP 레이아웃 디버깅·IR 덤프·버전 비교·썸네일 추출
- [`korean-spell-check`](skills/korean-spell-check.md) — 한국어 맞춤법 교정 (나라/PNU)
- [`korean-humanizer`](skills/korean-humanizer.md) — AI 티 나는 한국어를 자연스러운 사람 글로 재작성
- [`korean-character-count`](skills/korean-character-count.md) — 한국어 글자/줄/바이트 정확 카운트
- [`korean-slang-writing`](skills/korean-slang-writing.md) — 최신 유행어로 위트있는 한국어 작성
- [`naver-blog-research`](skills/naver-blog-research.md) — 네이버 블로그 검색·본문 전체 읽기·이미지 다운로드

## 미디어 · 뉴스 · 콘텐츠

- [`naver-news-search`](skills/naver-news-search.md) — 네이버 뉴스 검색 (제목·발행시각·링크·요약)
- [`hankookilbo-news`](skills/hankookilbo-news.md) — 한국일보 공식 MCP로 헤드라인·인기·섹션별 기사
- [`geeknews-search`](skills/geeknews-search.md) — 긱뉴스 RSS/Atom 게시물 조회·검색·상세
- [`daishin-report-search`](skills/daishin-report-search.md) — 대신증권 리포트 미러에서 최신 리포트 목록·원문
- [`korean-cinema-search`](skills/korean-cinema-search.md) — CGV·메가박스·롯데시네마 상영작·시간표·잔여석
- [`kopis-performance-search`](skills/kopis-performance-search.md) — KOPIS 공연 목록·상세·공연시설 조회
- [`ticket-availability`](skills/ticket-availability.md) — YES24·인터파크 공연 일정·등급별 잔여석 (조회 전용)
- [`library-book-search`](skills/library-book-search.md) — 한국 도서관 도서·소장정보 검색 (Data4Library)
- [`keris-academic-search`](skills/keris-academic-search.md) — 한국 학위논문·학술논문·연구보고서 검색 (RISS)

## 스포츠 · 엔터 · 운세

- [`korean-marathon-schedule`](skills/korean-marathon-schedule.md) — 마라톤·철인3종 일정·장소·신청 마감일
- [`saju-fortune`](skills/saju-fortune.md) — 사주팔자 연애/재물/직업/건강/궁합 대화형 풀이
- [`naming-house`](skills/naming-house.md) — 생년월일시·성씨 기반 사주 오행·성명학 이름 추천

## 생활 · 기타

- [`delivery-tracking`](skills/delivery-tracking.md) — CJ대한통운·우체국 택배 송장 추적
- [`lotto-results`](skills/lotto-results.md) — 로또 회차별 당첨번호·내 번호 매칭
- [`joseon-sillok-search`](skills/joseon-sillok-search.md) — 조선왕조실록 원문 키워드 검색
- [`korean-heritage-search`](skills/korean-heritage-search.md) — 국가유산 기록·상세·위치·월별 행사 검색

## k-skill 관리

- [`k-skill-setup`](skills/k-skill-setup.md) — 번들 설치·통합 CLI 사용·크리덴셜 해결·런타임 검증
- [`k-skill-cleaner`](skills/k-skill-cleaner.md) — 미사용 스킬 트리거 분석·제거 추천
````

## 5. 사용한 스크립트

### 5-1. 항목별 크기 데이터 생성 (`gen2.py`)

선택 도구 HTML에 넣을 데이터(파일별 압축 크기, 스킬별 관련 파일)를 만든다.

```python
import zipfile, json, re, sys
S=sys.argv[1]; R='k-skill/'
z=zipfile.ZipFile(S+'/orig.zip')
inf=[i for i in z.infolist() if not i.is_dir()]
names=[i.filename for i in inf]
sizes=[i.compress_size+76+2*len(i.filename.encode()) for i in inf]
dirs=[i for i in z.infolist() if i.is_dir()]
base=22+sum(76+2*len(d.filename.encode()) for d in dirs)
skills=sorted({n.split('/')[1] for n in names if n.count('/')==2 and n.endswith('/SKILL.md')})
lst=z.read(R+'k-skills-list.md').decode(); cat='기타'; info={}
for line in lst.splitlines():
    m=re.match(r'## (.+)',line)
    if m: cat=m.group(1).strip(); continue
    m=re.match(r'- \*\*(.+?)\*\* — (.+)',line)
    if m: info[m.group(1)]=(cat,m.group(2).strip())
items=[]
for s in skills:
    pf=[R+s+'/',R+'packages/'+s+'/',R+'packages/k-skill-cli/skills/'+s+'/',R+'packages/k-skill-cli/test/snapshots/'+s+'.',R+'docs/features/'+s+'.md']
    idx=[i for i,n in enumerate(names) if any(n.startswith(p) for p in pf)]
    c,d=info.get(s,('기타',''))
    items.append(dict(id=s,cat=c,desc=d,idx=idx))
cats=[]
for it in items:
    if it['cat'] not in cats: cats.append(it['cat'])
ex=[('CLI 테스트 스냅샷 전체','packages/k-skill-cli/test/','스킬 설명서의 테스트용 중복 사본. 스킬 사용에는 필요 없음'),
    ('CLI 내장 스킬 사본 전체','packages/k-skill-cli/skills/','루트 스킬 폴더와 같은 내용의 CLI용 사본'),
    ('기능 설명서 전체 (docs/features)','docs/features/','README 표에서 링크하는 스킬별 설명 문서'),
    ('운영 문서 (docs 나머지)','docs/','설치·배포·로드맵 등 저장소 운영 문서'),
    ('k-skill-proxy 서버 소스','packages/k-skill-proxy/','프록시 서버 코드 (직접 운영하지 않으면 불필요)'),
    ('infra 설정','infra/','배포 인프라 설정 파일')]
extras=[]
for t,p,d in ex:
    idx=[i for i,n in enumerate(names) if n.startswith(R+p) and not (p=='docs/' and n.startswith(R+'docs/features/'))]
    extras.append(dict(id='x:'+p,title=t,path=p,desc=d,idx=idx))
data=dict(base=base,sizes=sizes,items=items,extras=extras,cats=cats,orig=2563850)
open(S+'/tools/data.js','w').write('const DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
print(base+sum(sizes), len(items), [ (e['title'],sum(sizes[i] for i in e['idx'])) for e in extras])
```

### 5-2. 스킬당 한 파일로 합치기 (`merge.py`)

```python
import os, re, sys, shutil
src, out = sys.argv[1], sys.argv[2]
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
skills = sorted(d for d in os.listdir(src) if os.path.isfile(os.path.join(src, d, 'SKILL.md')))
for s in skills:
    d = os.path.join(src, s)
    body = open(os.path.join(d, 'SKILL.md'), encoding='utf-8').read().rstrip() + '\n'
    ins = os.path.join(d, 'instruction.md')
    if os.path.isfile(ins):
        body += '\n---\n\n<!-- 원본 instruction.md 내용 (한 파일로 합침) -->\n\n' + open(ins, encoding='utf-8').read().strip() + '\n'
    extra = []
    for root, _, files in os.walk(d):
        for f in sorted(files):
            p = os.path.join(root, f); rel = os.path.relpath(p, d)
            if rel in ('SKILL.md', 'instruction.md'): continue
            extra.append((rel, open(p, encoding='utf-8').read().strip()))
    for rel, txt in sorted(extra):
        body += f'\n---\n\n<!-- 원본 {rel} 내용 (한 파일로 합침) -->\n\n{txt}\n'
    os.makedirs(os.path.join(out, s)); open(os.path.join(out, s, 'SKILL.md'), 'w', encoding='utf-8').write(body)
# root index
lst = open(os.path.join(src, 'k-skills-list.md'), encoding='utf-8').read()
cat, groups, seen = None, {}, set()
for line in lst.splitlines():
    m = re.match(r'## (.+)', line)
    if m: cat = m.group(1).strip(); groups.setdefault(cat, []); continue
    m = re.match(r'- \*\*(.+?)\*\* — (.+)', line)
    if m and m.group(1) in skills: groups[cat].append((m.group(1), m.group(2))); seen.add(m.group(1))
rest = [s for s in skills if s not in seen]
if rest: groups['기타'] = [(s, '') for s in rest]
md = ['---', 'name: k-skill',
      'description: 한국 특화 검색·조회·자동화 스킬 110개 모음. 쇼핑 가격비교, 부동산·경매, 교통·예매, 공공·행정·법률, 금융·주식, 날씨·생활, 한국어 글쓰기 등 한국 서비스와 공공데이터를 다루는 요청에 사용한다. 아래 목록에서 맞는 스킬을 찾아 그 폴더의 SKILL.md를 읽고 따른다.',
      'license: MIT', '---', '', '# k-skill (110개 스킬 묶음)', '',
      '요청에 맞는 스킬을 아래 목록에서 고른 뒤 `<스킬 이름>/SKILL.md`를 읽고 그 지침을 따른다.',
      '각 SKILL.md에는 원본 SKILL.md, instruction.md, references 자료가 한 파일에 합쳐져 있다.', '']
for c, items in groups.items():
    if not items: continue
    md += [f'## {c}', '']
    md += [f'- [`{n}`]({n}/SKILL.md) — {d}' if d else f'- [`{n}`]({n}/SKILL.md)' for n, d in items]
    md.append('')
open(os.path.join(out, 'SKILL.md'), 'w', encoding='utf-8').write('\n'.join(md))
shutil.copy(os.path.join(src, 'LICENSE'), os.path.join(out, 'LICENSE'))
print(len(skills), 'skills', len(rest), 'uncategorized')
```

### 5-3. SKILL.md를 하나만 남기는 후처리 (셸)

```bash
B=build/k-skill
mkdir -p $B/skills
for d in $B/*/; do n=$(basename $d); [ "$n" = skills ] && continue
  mv $d/SKILL.md $B/skills/$n.md && rmdir $d; done
# 루트 SKILL.md 링크 (<이름>/SKILL.md) → (skills/<이름>.md) 로 치환
zip -qr -D -9 k-skill-110-R1-200files.zip k-skill
```

### 5-4. 테스트 스냅샷 삭제판 만들기 (셸)

```bash
cp k-skill-110-R1.zip k-skill-110-R1-2MB.zip
zip -q -d k-skill-110-R1-2MB.zip 'k-skill/packages/k-skill-cli/test/*'
```

## 6. 참고

- 최종본의 각 `skills/<이름>.md` 맨 앞에는 원본 SKILL.md의 frontmatter(name, description)가 그대로 남아 있다. 내용 손실은 없다.
- 원본의 `packages/`, `docs/`, README·CONTRIBUTING 등 루트 안내 문서는 최종본에서 뺐다. 필요하면 `docs/k-skill-110-R1-2MB.zip`에 그대로 있다.
