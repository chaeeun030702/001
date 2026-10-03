# 작업 규칙

## 에이전트 작업현황 (항상)
- 서브에이전트(Agent 도구)·병렬 조사·GitHub Actions 수집 실행 등 에이전트 작업을 할 때는 **항상 에이전트 작업현황을 보여준다.**
  - 아티팩트 **에이전트 작업현황** https://claude.ai/artifact/ETZGZnQbEEFCZErq8QWxMS 을 같은 URL로 갱신한다
    (스킬: `skills/agent-status/` · `skills/agent-status.zip`, 원본: `docs/agent_status.html`, 아이콘은 주황 픽셀 캐릭터 `#clawd` 심볼 — 그대로 유지).
  - 메인 에이전트(발주) → 서브에이전트(하청) 구조로 그린다. 파일 아래 `JOB` 데이터만 고친다:
    `subs[]`에 하청마다 `status`(wait/run/done)·`progress`(0~100)·`task`·결과를 넣으면 메인 진행률은 평균으로 계산된다.
  - 에이전트를 시작할 때 카드를 `진행 중`으로 올리고, 끝나면 `완료`와 결과(건수·대상)로 바꾼다.
  - 답변에도 작업현황 표(에이전트 · 상태 · 결과)를 함께 적는다.
