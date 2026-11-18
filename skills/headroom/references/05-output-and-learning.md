# 05. 출력 토큰 절감 · 학습 · 메모리

## 5.1 출력 토큰 절감 (프록시, 기본 꺼짐)
입력 압축은 *보내는* 토큰을 줄인다. 출력은 모델이 *쓰는* 토큰이고 Opus급에선 입력의 약 5배 단가다. 프록시는 출력을 직접 생성하지 않으므로 **요청을 재구성하는 두 가지 레버**만 쓴다.

```bash
export HEADROOM_OUTPUT_SHAPER=1      # 켜기 (1/true/yes)
export HEADROOM_VERBOSITY_LEVEL=2    # 0~4 (기본 2)
headroom proxy --port 8787
```
적용 대상: Anthropic `/v1/messages`, OpenAI `/v1/chat/completions`, `/v1/responses`.

### 레버 ① 장황함 조향 (verbosity steering)
- 시스템 프롬프트 **맨 끝**에 `<headroom_output_shaping> … </headroom_output_shaping>` 블록을 덧붙임 → 앞쪽 `cache_control` 중단점이 유지되어 프롬프트 캐시가 계속 적중.
- 블록은 **레벨별 바이트 고정**이고 **멱등**(센티널로 이미 있으면 교체/무시) → 반복 요청도 프리픽스가 동일. 문구 수정은 곧 캐시 무효화이므로 릴리스 간에도 고정.
- 레벨은 누적: 1=서두/맺음말 생략 · 2=+이미 대화에 있는 코드/출력 재인용 금지(경로·줄로 참조), 도구 성공 후 서술 생략 · 3=+결론만, 근거 생략, 최소 수정, **부정어(not/never/no/only/except) 삭제 금지**, 파괴적/보안/다단계는 풀 문장 · 4=최소 토큰(조각 문장 허용).
- 설계 근거(코드 주석): SWE-bench 완주 실험에서 "위치 불명확"이 후속 질문을 낳았고, "정확한 파일 경로와 줄을 *의무적으로* 인용"하도록 조항을 조여 3→0으로 해결. 교훈: **내용 억제는 안전하지만 *내용을 가리키는 포인터* 억제는 한 턴 값을 치른다.** (표본 n=9, Claude만 — 크기보다 메커니즘이 근거가 더 강하다고 스스로 밝힘)
- `--mode cache`(기본)에서는 조향이 꺼질 수 있다(`steering_allowed_for`): 조향은 프리픽스 캐시 키에 쓰는 유일한 레버라서.

### 레버 ② 노력 라우팅 (effort routing)
에이전트 루프의 대부분은 기계적 속행(파일 읽기, 테스트 통과)이지만 하네스는 매 턴 `output_config.effort`를 최고로 고정하곤 한다. 사고(thinking)는 출력 토큰으로 청구된다.
```
classify_turn(messages)  ← 구조만 본다(블록 타입·role·is_error). 내용 정규식/키워드 없음
  NEW_USER_ASK            마지막 user가 text/image/document 포함        → effort 유지
  MECHANICAL_CONTINUATION 마지막 user가 tool_result만, 오류 없음        → effort 낮춤
  ERROR_CONTINUATION      tool_result 중 is_error=true                  → effort 유지
  UNKNOWN                 판단 불가                                     → 건드리지 않음
```
- 공급자별: OpenAI는 `reasoning_effort`, Anthropic은 `output_config.effort` 또는 `thinking.budget_tokens`(레거시 모델은 API 하한까지만 clamp). 두 경로 모두 "**낮추기만** 하는 clamp-only 불변식"과 동일한 `output_shaper:*` 라벨.
- 안전 규칙: ⑴ 클라이언트가 보내지 않은 `output_config.effort`는 **주입하지 않음**(미지원 모델은 400) ⑵ `thinking.type`은 **토글하지 않음**(이력에 thinking 블록이 있으면 400 + 메시지 캐시 계층 무효화).

### 측정과 자동 튜닝
- `headroom output-savings` → `Reduction: 31.7% (95% CI 27.7% … 35.7%) [estimated]`. 모델이 *쓰지 않은* 토큰은 볼 수 없어 **반사실적 추정**이며 그렇게 표기.
- 실측: `HEADROOM_OUTPUT_HOLDOUT=0.1` → 대화 10%를 대조군(미조향)으로 두면 대시보드 "Output Tokens Saved"가 `measured`로 바뀌고 밴드 표시.
- `headroom learn --verbosity` (드라이런) / `--apply`: 과거 세션에서 사용자가 긴 답변을 **끊거나 읽기 전에 넘어간** 행동으로 레벨을 추정. 캐시 모드 프록시는 중간 변경이 캐시를 깨므로 학습 레벨을 재읽지 않음 → `--apply`가 `HEADROOM_VERBOSITY_LEVEL`을 고정(재시작 후 유지는 직접 설정).
- 이미 떠 있는 프록시: 이 스위치들은 요청마다 라이브로 읽히며, `headroom wrap`이 재사용한 프록시에는 루프백 `POST /admin/runtime-env`로 핫싱크(전역 적용, 마지막 설정 승리).

## 5.2 `headroom learn` — 실패 학습
```
과거 세션 → Plugin(에이전트별 로그 읽기) → Analyzer(LLM 분석) → Writer(마커 구획 갱신) → 에이전트 네이티브 컨텍스트 파일
  Claude: ~/.claude/projects/*.jsonl · Codex: ~/.codex/sessions/*.json · Gemini: ~/.gemini/tmp/*/chats/session-*.json
```
- **성공 상관(핵심)**: 실패 목록이 아니라 *그 실패를 어떻게 고쳤는지*를 찾는다. 예) `Read axion-formats/.../X.java` 실패 → `Read axion-scala-common/.../X.scala` 성공 ⇒ "X는 `axion-scala-common/`에 있음".
- 학습 항목: 환경 사실(`uv run python`), 파일 경로 교정, 검색 범위, 명령 패턴(사용자가 18번 거부 → 실행 말고 명령만 제시), 큰 파일(offset/limit), 재시도 방지, 권한 메모.
- 출력: Claude → `CLAUDE.local.md`(기본, gitignore) / `--target CLAUDE.md`(팀 공유), Codex → `AGENTS.md`, Gemini → `GEMINI.md`, Grok → `GROK.md`. 재실행 시 중복 없이 교체:
  ```
  <!-- headroom:learn:start --> … <!-- headroom:learn:end -->
  ```
```bash
headroom learn                 # 드라이런
headroom learn --apply         # CLAUDE.local.md 기록
headroom learn --apply --target CLAUDE.md
headroom learn --project ~/my-project --apply
headroom learn --all --apply
```

## 5.3 크로스 에이전트 메모리
`headroom proxy --memory` 또는 `headroom wrap claude|codex|aider --memory` — 프록시를 지나는 **모든 에이전트가 한 저장소 공유**(Claude가 저장 → Codex가 읽음).
```
요청 → 1.메모리 DB 검색 → 2.공급자 네이티브 형식으로 시스템 컨텍스트 주입 → 3.memory_save/search/update/delete 도구 추가
     → 4.업스트림 전달 → 5.응답의 메모리 도구 호출 처리 → 6.비동기 백그라운드 dedup(코사인 >92% 자동 제거)
```
- 저장: 프로젝트별 `{cwd}/.headroom/memory.db`(SQLite + HNSW/FTS5). 프로젝트 간 오염 없음. `--memory-db-path`로 변경.
- 특징: 에이전트 출처(provenance) 기록, 계층 스코프(User→Session→Agent→Turn), 시간적 버전(supersession 체인), 시맨틱+전문검색, 중요 메모리 자동 승격(bubbling), LLM 기반 중복 병합(사용자 자신의 LLM에 편승, 추가 호출 비용 없음).
- 캐시 상호작용: Anthropic `/v1/messages`에서 `--mode cache`는 프리픽스를 지키려 **자동 메모리 주입을 건너뜀**; OpenAI chat/responses·Gemini는 라이브존 꼬리에 덧붙임. Anthropic에서 자동 주입이 필요하면 `--mode token`.
- `headroom memory list|show|stats|edit|delete|prune|purge|export|import`.

## 5.4 SharedContext — 에이전트 간 인계 압축
```python
ctx = SharedContext()
ctx.put("research", big_output, agent="researcher")   # 전체 파이프라인으로 자동 압축 (≈80% 절감 예)
ctx.get("research")                                   # 압축본
ctx.get("research", full=True)                        # 원본
ctx.get_entry("research").savings_percent
```
