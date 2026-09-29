# 안전관리자 채용 일일 브리핑

매일 18:00 KST에 Routine이 `collect.py`를 실행해 아래 8개 사이트의 안전관리자
채용 공고를 수집·정리한다.

```bash
uv run safety_jobs/collect.py                  # 마크다운 표를 stdout으로
uv run safety_jobs/collect.py --json out.json  # 원자료(JSON)도 저장
```

## 규칙

- **우선순위**: `SOURCES` 순서(잡코리아 → 사람인 → 링커리어 → 워커 → 서울과기대 →
  충북대 → 인천대 → 부경대). 중복 공고는 위쪽 사이트 것을 남긴다.
- **대상**: 신입 / 경력무관 / 인턴만. 경력직 전용 공고는 제외.
- **표기**: 정규직·계약직은 업체명 앞에 `[정규직]`, `[계약직]`.
- **표 열**: 구분 · 업체명 · 지원 자격(학과, 자격, 영어) · 우대 사항 · 접수기한 · 출처 링크.

지원 자격·우대 사항은 상세 페이지 본문에서 정규식으로 뽑은 값이므로, Routine은
결과를 검토·보정해 브리핑을 작성한다.

## 네트워크

클라우드 환경의 Network access에서 아래 도메인이 허용돼 있어야 한다. 막힌 사이트는
브리핑 하단 '수집 실패'에 `ProxyError: 403`으로 표시된다.

`www.jobkorea.co.kr`, `www.saramin.co.kr`, `linkareer.com`, `www.worker.co.kr`,
`safety.seoultech.ac.kr`, `safety.chungbuk.ac.kr`, `www.inu.ac.kr`, `safety.pknu.ac.kr`
