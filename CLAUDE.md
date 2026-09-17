# 프로젝트 지침

## 건설 안전(Safety) 관련 스킬 자동 사용 (필수·최우선)

요청에 **'안전'** 또는 안전 관련 용어가 하나라도 포함되면 → **안전 스킬을 항상 사용**한다.
(예: 안전, 안전점검, 안전관리, 재해, 사고, 위험, 위험성평가, 유해위험, PPE·보호구, 추락,
TBM·툴박스미팅, safety, hazard, incident, inspection 등)

### 국내/해외 분기 (중요)
1. **기본값 = 국내(한국) 기준** → **`safety-inspection-kr`** 스킬을 사용한다.
   한국어 요청, 국내 현장, '산안법·안전보건규칙·중대재해·중대재해처벌법·KOSHA·산재' 등
   국내 용어가 있으면 반드시 이 스킬을 쓴다. (규정 근거가 국내 법령임)
2. **미국(OSHA) 기준을 명시**하거나 해외 현장/영문 규정(OSHA, 29 CFR 1926 등)을 요구하면
   → 아래 DDC 스킬(미국 OSHA 기반)을 사용한다.
3. 요청 성격에 맞는 스킬을 고르고, 필요하면 여러 개를 함께 사용한다.
4. 이 규칙은 다른 스킬 규칙(HWPX·프레젠테이션·모바일)보다 **우선**한다. 단, 안전 문서를
   특정 형식(hwpx 공문·pptx 등)으로 산출해야 하면 해당 형식 스킬과 **함께** 사용한다.
5. 사용자가 특정 스킬을 명시하면 그 지정을 우선한다.

### 안전 스킬 정보
| 스킬 이름 | 기준 | 용도 | 디렉터리 |
| --- | --- | --- | --- |
| `safety-inspection-kr` | **국내(한국)** | 산안법·안전보건규칙·중대재해처벌법·KOSHA 기반 점검표/위험성평가/산재·중대재해 보고 판정/TBM (**국내 기본값**) | `.claude/skills/safety-inspection-kr` |
| `safety-inspection` | 미국 OSHA | 현장 안전점검 시스템(체크리스트·위험추적·사고보고·문서화) | `.claude/skills/safety-inspection` |
| `safety-inspection-checklist` | 미국 OSHA | 디지털 안전점검 체크리스트 생성·수행·추적 | `.claude/skills/safety-inspection-checklist` |
| `safety-compliance-checker` | 미국 OSHA | PPE·고소작업 등 안전규정 준수 자동 점검·보고 | `.claude/skills/safety-compliance-checker` |
| `incident-reporting` | 미국 OSHA | 안전사고 보고·조사·시정조치·추세분석 | `.claude/skills/incident-reporting` |
| `toolbox-talk-generator` | 미국 OSHA | TBM(툴박스미팅) 안전 브리핑 자동 생성(다국어) | `.claude/skills/toolbox-talk-generator` |

> DDC 스킬(미국 OSHA 29 CFR 1926 기반)은 국내 규정과 기준이 다르므로, 국내 현장 문서에는
> 기본적으로 `safety-inspection-kr`을 사용한다. 출처: [datadrivenconstruction/ddc_skills_for_ai_agents_in_construction](https://github.com/datadrivenconstruction/ddc_skills_for_ai_agents_in_construction)

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

## 모바일 앱/웹 UI 디자인 시 스킬 자동 선택 (필수)

**"모바일웹을 만들어줘"** 와 유사한 요청 — "모바일 앱", "모바일 UI", "앱 화면 디자인",
"모바일 화면", "mobile app/web", "앱 UI", "Sleek" 등 모바일 앱·웹 UI를 **디자인/구현**하는
요청을 받으면 → **`design-mobile-apps`** 스킬을 사용한다.

- 출력물: Sleek(sleek.design) 기반 모바일 앱/UI 디자인 및 코드(HTML, React Native, SwiftUI).
- 이 스킬은 `SLEEK_API_KEY` 환경변수와 `https://sleek.design` 네트워크 접근이 필요하다.
  키가 없으면 사용자에게 안내한다.
- 사용자가 특정 스킬을 명시하면 그 지정을 우선한다.

### 스킬 정보
| 스킬 이름 | 출처 | 디렉터리 |
| --- | --- | --- |
| `design-mobile-apps` | [designed-by-ai/skills](https://github.com/designed-by-ai/skills) | `.claude/skills/design-mobile-apps` |

## 프레젠테이션(PPT/PPTX/HTML) 생성 시 스킬 자동 선택 (필수)

프레젠테이션·슬라이드·PPT·PPTX·발표자료·HTML 덱을 **생성/편집/보정**하는 요청을 받으면
아래 규칙으로 **사용할 스킬을 자동으로 결정**한다.

### 분기 규칙 (위에서부터 순서대로 적용)
1. **HTML/웹 슬라이드** — 요청에 **"HTML"** 이 언급되면(예: "HTML 파일을 ppt로 만들어줘",
   "HTML로 발표자료 만들어줘", "웹 슬라이드", "reveal", "브라우저", "웹페이지 발표",
   "小红书 图文" 등) → **`html-ppt`** 스킬 사용. HTML 파일을 입력으로 주고 PPT/슬라이드로
   만들어 달라는 요청도 여기에 해당한다. (출력물은 `.pptx`가 아니라 정적 HTML 슬라이드)
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
