# 안전관리자 신입 채용 브리핑 (매일 20시 예약 실행)

예약 작업이 매일 20:00 KST 근처에 이 문서를 읽고 아래 순서대로 실행한다.

## 파일
| 파일 | 내용 |
|---|---|
| `postings.json` | 브리핑에 싣는 공고 (url 기준 1건 1행). `first_seen`이 오늘이고 `baseline`이 아니면 **신규(파란 글씨)** |
| `excluded.json` | 조건 밖이라 뺀 공고 (사유별) |
| `build.py` | 브리핑 HTML 생성 → `docs/안전관리자_신입_채용_브리핑_YYYY-MM-DD.html` (마감 지난 공고 자동 제외) |
| `mail.py` | 메일 본문 HTML 생성 → `out/mail_YYYY-MM-DD.html` |
| `style.css` · `app.js` | 페이지 디자인·동작 (선택 삭제 → 제외 확정, 숫자 타일 → 목록 이동, D-n 계산) |

## 선별 조건
- 포함: 신입 · 경력무관 · 신입/경력 | 100대 그룹 계열사 | 외국계(한국 근무) | 공공기관·협회 | 종합건설 시평 50위 이내 정규직 · 10위 이내 계약직(`../construction_top100_2026.tsv`) | 설계사(엔지니어링) 10위 이내
- 제외: 경력직 전용(본문에 "경력 N년 이상"만 있는 공고 포함) | 감시단·감시원·순찰원 | 전기안전관리자 | 전문건설업체 | 안전이 주업무가 아닌 직종 | 교육·체험형 인턴 | 마감 지난 공고
- 표시: 파란 글씨 = 오늘 새로 찾은 공고 · 빨간 접수기한 = 3일 이내 · 주황 = 계약직(괄호로 정규직 전환 가능)

## 실행 순서
1. **작업현황**: `docs/agent_status.html`의 `JOB`를 이번 실행으로 바꿔 https://claude.ai/artifact/89otDQXoXzXKDG8U1kpkd7 에 게시하고 연다 (CLAUDE.md 규칙).
2. **ChatGPT 신규 공고 검색**: `mcp__openai__ask_chatgpt`(model `gpt-5-search-api`)로 위 조건의 "현재 접수 중인 안전관리자 신입" 공고를 대기업 계열 / 외국계 / 종합건설·설계사 / 공공기관·협회로 나눠 검색한다. 분당 한도(429)에 걸리면 웹 검색으로 대신 확인하고 다음 호출을 이어 간다.
3. **검증·추가**: `postings.json`에 없는 url만 후보로 보고, 본문에서 경력 요건·마감일·고용형태를 확인한다. 조건에 맞으면 아래 형식으로 추가하고 `first_seen`=오늘, `via`="ChatGPT 웹 검색"으로 둔다. 안 맞으면 `excluded.json`에 사유와 함께 적는다.
4. **내용 채우기 (신규 공고)**: ChatGPT로 신입 초봉(대졸 초임·연도·근거 URL), 전체 직원 수(사업보고서·알리오·국민연금·기업정보, 기준 시점·URL), 주요 복지(기숙사·사택·자녀학자금·주택대출·주거지원, 근거 URL)를 찾아 채운다. 못 찾은 값은 비워 둔다(브리핑에 "확인 못 함").
5. **생성**: `python3 safety_jobs/newgrad/build.py` · `python3 safety_jobs/newgrad/mail.py`
6. **게시**: 브리핑 HTML을 신입 브리핑 아티팩트 https://claude.ai/artifact/6o7keJV5TZ5rTWA77iKfpw 에 같은 URL로 게시(`url` 지정)하고 연다. SendUserFile(`display: "render"`)로도 보낸다.
7. **메일**: Gmail `send_message`로 사용자 메일(chaeeun075@gmail.com)에 보낸다. 제목 `[안전관리자 신입 브리핑] YYYY-MM-DD · 신규 N건 · 3일 내 마감 M건`, `htmlBody`는 `out/mail_YYYY-MM-DD.html` 내용.
8. **커밋·푸시**: `postings.json`·`excluded.json`·브리핑 HTML·작업현황을 커밋하고 브랜치에 푸시한다.
9. 작업현황을 완료로 바꿔 다시 게시하고, 답변에 작업현황 표와 신규·마감 임박 공고를 적는다.

## postings.json 한 건 형식
```json
{"url":"공고 URL","company":"회사명","company_url":"사람인 기업정보 또는 기업 검색 URL","title":"공고명",
 "group":"big|foreign|con|pub|etc","who":"그룹·구분 설명(예: SK그룹, 시평 8위)","note":"짧은 메모",
 "employment":"정규직|계약직|고용형태 확인 필요","conv":false,"level":"신입|경력무관|신입·경력",
 "qualification":"지원 자격 한 줄","deadline":"YYYY-MM-DD 또는 채용 시 마감","source":"사람인|잡코리아|…",
 "benefits":[{"label":"기숙사","kind":"post|web","url":"근거 URL","title":"근거 한 줄"}],
 "starter":{"pay":"4,100만원","basis":"2025 · 잡코리아","url":"…"},
 "employees":{"count":"1,230명","basis":"2025.12 · 잡코리아","url":"…"},
 "search_firm":false,"first_seen":"YYYY-MM-DD","via":"ChatGPT 웹 검색"}
```
