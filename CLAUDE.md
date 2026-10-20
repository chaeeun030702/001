# 작업 규칙

## 에이전트 작업현황 (항상)
- 서브에이전트(Agent 도구)·병렬 조사·GitHub Actions 수집 실행 등 에이전트 작업을 할 때는 **항상 에이전트 작업현황을 보여준다.**
  - 아티팩트 **에이전트 작업현황** https://claude.ai/artifact/ETZGZnQbEEFCZErq8QWxMS 을 같은 URL로 갱신한다
    (스킬: `skills/agent-status/` · `skills/agent-status.zip`, 원본: `docs/agent_status.html`, 아이콘은 주황 픽셀 캐릭터 `#clawd` 심볼 — 그대로 유지).
  - 메인 에이전트(발주) → 서브에이전트(하청) 구조로 그린다. 파일 아래 `JOB` 데이터만 고친다:
    `subs[]`에 하청마다 `status`(wait/run/done)·`progress`(0~100)·`task`·결과를 넣으면 메인 진행률은 평균으로 계산된다.
  - 에이전트를 시작할 때 카드를 `진행 중`으로 올리고, 끝나면 `완료`와 결과(건수·대상)로 바꾼다.
  - 갱신할 때마다 Artifact 도구 `action: "open"`으로 작업현황 페이지를 **항상 열어** 보여준다.
  - 답변에도 작업현황 표(에이전트 · 상태 · 결과)를 함께 적는다.

## 결과 바로 열어 보기 (항상)
- 결과가 나오면 **바로** 결과물을 **한 파일**로 열어 보여준다: SendUserFile(`display: "render"`)로 완성된 HTML 한 파일을 보낸다.
  - 브리핑: 기본 브랜치 `briefings/latest_edit.html`(완전한 HTML 한 파일, 편집·A4 인쇄 가능)을
    `docs/안전관리자_채용_브리핑_YYYY-MM-DD.html`로 복사해 render로 보낸다.
  - 그 밖의 결과(문서·표·보고서)도 HTML 한 파일로 만들어 render로 보낸다.
- 브리핑을 게시(갱신)한 뒤에는 Artifact 도구 `action: "open"`으로 브리핑 아티팩트
  https://claude.ai/artifact/8vwqioKkr5ADyBJnbVDQZA 도 연다 (작업현황 페이지와 함께).
