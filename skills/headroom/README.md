# headroom 스킬 패키지

`https://github.com/headroomlabs-ai/headroom` 를 소스 코드까지 읽고 정리한 **설명 + 로직 해설** 스킬입니다.

- 기준 커밋: `72302a3` (2026-10-12), 라이선스 Apache-2.0
- 대상 독자: Headroom을 도입·튜닝하거나 원리를 설명해야 하는 개발자/에이전트
- 구성: `SKILL.md`(진입점) + `references/01~07`(상세 MD)

## 설치(스킬로 쓰기)
1. 압축을 풀어 `headroom/` 폴더를 Claude 스킬 디렉터리(예: `~/.claude/skills/` 또는 프로젝트 `skills/`)에 둔다.
2. "Headroom 토큰 절감 어떻게 동작해?" 같은 질문에서 `SKILL.md`가 트리거된다.

## 읽는 순서
`SKILL.md` → `01-overview` → `02-pipeline-logic` → `03-compressors` → `04-ccr-reversible` → `05-output-and-learning` → `06-install-and-usage` → `07-limitations-and-caveats`

## 근거와 한계
- 설명은 README·wiki·`headroom/`(Python)·`crates/headroom-core`(Rust) 소스 주석과 코드를 대조해 작성했다.
- 이 패키지를 만든 환경에서는 **Headroom을 실제로 설치·실행해 보지 않았다.** 수치는 저장소 문서의 값이며 직접 측정한 값이 아니다.
- 저장소는 빠르게 바뀐다(Phase B/C 리얼라인먼트 진행 중). 세부 동작은 `headroom doctor`와 최신 문서(`https://docs.headroomlabs.ai/llms.txt`)로 재확인할 것.
