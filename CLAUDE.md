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

## 프레젠테이션(PPT/PPTX/HTML) 생성 시 스킬 자동 선택 (필수)

프레젠테이션·슬라이드·PPT·PPTX·발표자료·HTML 덱을 **생성/편집/보정**하는 요청을 받으면
아래 규칙으로 **사용할 스킬을 자동으로 결정**한다.

### 분기 규칙 (위에서부터 순서대로 적용)
1. **HTML/웹 슬라이드** — "HTML", "웹 슬라이드", "reveal", "브라우저", "웹페이지 발표",
   "小红书 图文" 등 **HTML 형식**을 원하는 표현이 있으면 → **`html-ppt`** 스킬 사용.
   (출력물은 `.pptx`가 아니라 정적 HTML 슬라이드)
2. **고급 PPTX 요청** — (HTML 요청이 아닌 경우) "자세하게", "화려하게", "멋지게",
   "디자인 강화", "브랜드/템플릿", "재구성", "beautify/미화", "내레이션",
   "애니메이션", "영상" 등 정교함·고급 연출을 요구하는 표현이 있으면
   → **`ppt-master`** 스킬 사용.
3. **기본값** — 위 어디에도 해당하지 않으면 → **`pptx`** 스킬 사용.
4. 사용자가 특정 스킬을 명시하면("ppt-master로 만들어줘", "html-ppt로 해줘",
   "pptx로 해줘" 등) 위 규칙보다 사용자의 명시적 지정을 우선한다.

### 스킬 정보
| 스킬 이름 | 출처 | 출력물 | 디렉터리 |
| --- | --- | --- | --- |
| `pptx` | [anthropics/skills](https://github.com/anthropics/skills) | PowerPoint `.pptx` | `.claude/skills/pptx` |
| `ppt-master` | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | PowerPoint `.pptx` (고급) | `.claude/skills/ppt-master` |
| `html-ppt` | [lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) | 정적 HTML 슬라이드 | `.claude/skills/html-ppt` |
