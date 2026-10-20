# 작업 규칙

환경마다 쓸 수 있는 도구가 다르다. 아래 규칙은 **도구가 있을 때만** 적용하고, 없으면 대체 방법을 쓴다.
(Claude Code 웹에는 Artifact 도구가 있지만 Notion AI·CLI·다른 에이전트에는 없다.)

## 에이전트 작업현황
- 서브에이전트·병렬 조사·GitHub Actions 수집처럼 오래 걸리는 작업을 할 때 작업현황을 보여준다.
  - 원본은 `docs/agent_status.html`의 `JOB` 블록이다. 하청마다 `status`(wait/run/done/fail)·`progress`(0~100)·`task`·결과를 넣는다.
  - 시작할 때 `진행 중`, 끝나면 `완료`와 결과(건수·대상)로 바꾼다.
  - Artifact 도구가 있으면 작업현황 아티팩트(https://claude.ai/artifact/ETZGZnQbEEFCZErq8QWxMS)를 같은 URL로 갱신해 연다. 없으면 건너뛴다.
  - 어느 환경이든 답변에 작업현황 표(에이전트 · 상태 · 결과)를 적는다.
- **세션이 여럿일 때 (충돌 방지)**
  - `docs/agent_status.html`을 고치기 전에 `git pull --rebase`로 최신을 받는다.
  - 자기 세션 카드만 고치고, 다른 세션 카드는 지우거나 덮어쓰지 않는다. 카드 `name`에 `(세션 A)`처럼 구분을 붙인다.
  - push가 거절되면 다시 pull → 자기 카드만 다시 반영 → push 한다.

## 브리핑 게시 후 표시
- 브리핑을 게시(갱신)한 뒤 Artifact 도구가 있으면 브리핑 아티팩트(https://claude.ai/artifact/8vwqioKkr5ADyBJnbVDQZA)를 연다.
- 없으면 `briefings/latest.html` 경로와 웹 주소(`SITE_URL`)를 답변에 적는다.

## 제외 규칙을 고칠 때
- `safety_jobs/collect.py`의 규칙을 추가·수정하면 `tests/rule_cases.json`에 빠져야 할 사례(exclude)와 남아야 할 사례(keep)를 함께 넣는다.
- PR에서 `safety-jobs-test` 워크플로가 통과해야 병합한다. 로컬 확인: `uv run --no-project --with pytest pytest -q tests`(collect.py 의존성 포함).
- `safety_jobs/README.md` 규칙 줄의 날짜는 **병합한 날(KST)**로 적는다.
- 작업 브랜치에 push해도 수집이 돌지 않는다. 결과를 바로 보려면 병합 후 `safety-jobs-briefing`을 수동 실행한다.
