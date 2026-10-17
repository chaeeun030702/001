# 매칭 브리핑 빌더 (코드만)

`safety_jobs/match/` 는 수집 결과(`briefings/latest.json`, `briefings/broad/latest.json`)를 공고별 매칭도로 채점해 HTML 브리핑을 만드는 **코드**입니다.
개인 프로필·채점(`scores.json`)·기업분석 카드(`cr_cards.json`)·화면 템플릿(`body.tpl.html`)은 개인 정보라 이 공개 저장소에 두지 않고 비공개 아티팩트에서 받아 같은 폴더에 놓고 실행합니다.

```
sh run_all.sh <main latest.json> <broad latest.json>   # 결과: matching_briefing.html
python3 unscored.py [순번...]                          # 채점 안 된 공고 목록(순번을 주면 본문)
python3 verify.py                                       # 회사명·gap이 같은 행에 있는지 검증
```
