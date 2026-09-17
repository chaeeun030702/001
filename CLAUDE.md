# 프로젝트 지침

## HWPX 문서 생성 시 스킬 자동 선택 (필수)

`.hwpx` 파일(한글 문서)을 **생성/변환/편집**하는 요청을 받으면, 요청 내용에 따라
아래 규칙으로 **사용할 스킬을 자동으로 결정**한다. 사용자에게 다시 묻지 않는다.

### 분기 규칙
1. 요청에 **'공문', '공공기관', '공무원'** 중 하나라도 포함되면 → **`hwpx-jkf`** 스킬 사용.
2. 그 외의 모든 hwpx 생성/편집 요청 → **`hwpx-kist`** 스킬 사용.
3. 사용자가 특정 스킬을 명시하면("kist로 만들어줘", "jkf로 해줘" 등) 위 규칙보다
   사용자의 명시적 지정을 우선한다.

### 스킬 정보
| 스킬 이름 | 출처 | 디렉터리 |
| --- | --- | --- |
| `hwpx-jkf` | [jkf87/hwpx-skill](https://github.com/jkf87/hwpx-skill) | `.claude/skills/hwpx-jkf` |
| `hwpx-kist` | [kist-aix/hwpx](https://github.com/kist-aix/hwpx) | `.claude/skills/hwpx-kist` |
