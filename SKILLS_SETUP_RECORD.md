# 스킬 설치·설정 작업 기록

- 저장소: `chaeeun030702/001`
- 작업 브랜치: `claude/keen-noether-5k253h`
- 문서 생성일: 2026-11-18
- 작성: Claude Code (세션 요약)

---

## 1. 작업 개요

여러 외부 저장소/업로드 파일에서 Claude Code **스킬을 설치**하고, 요청 키워드에 따라
자동으로 알맞은 스킬이 선택되도록 **`CLAUDE.md` 라우팅 규칙**을 구성했다. 모든 변경은
위 브랜치에 커밋·푸시되었다.

설치 도메인: ① 한글 문서(HWPX) ② 프레젠테이션(PPTX/HTML) ③ 모바일 UI 디자인
④ 건설 안전(국내/해외).

---

## 2. 설치된 스킬 목록

| 스킬 | 출처 | 용도 | 규모 |
| --- | --- | --- | --- |
| `hwpx-jkf` | [jkf87/hwpx-skill](https://github.com/jkf87/hwpx-skill) | HWP/HWPX 변환·생성(공문/보고서/계획서/활동지) | 161파일 / 11M |
| `hwpx-kist` | [kist-aix/hwpx](https://github.com/kist-aix/hwpx) | HWPX 보고서 XML-first 생성/편집 | 36파일 / 612K |
| `pptx` | [anthropics/skills](https://github.com/anthropics/skills) | PowerPoint `.pptx` 생성/편집/읽기 | 56파일 / 1.3M |
| `ppt-master` | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | 고급 PPTX(브랜드/템플릿/내레이션/애니메이션/영상) | 12,993파일 / 121M |
| `html-ppt` | [lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) | 정적 HTML 슬라이드(reveal 스타일) | 239파일 / 12M |
| `design-mobile-apps` | [designed-by-ai/skills](https://github.com/designed-by-ai/skills) | Sleek 기반 모바일 앱/UI 디자인·코드 | 1파일 / 36K |
| `safety-inspection-kr` | **신규 작성(한국형)** | 국내 기준 점검표/산재·중대재해 판정/TBM(스크립트) | 4파일 / 48K |
| `construction-safety` | 사용자 업로드(한국형) | 국내 기준 컴플라이언스·부적합 판정·시정조치·보고 | 1파일 / 20K |
| `safety-inspection` | [DataDrivenConstruction](https://github.com/datadrivenconstruction/ddc_skills_for_ai_agents_in_construction) | (미국 OSHA) 현장 안전점검 시스템 | 3파일 / 40K |
| `safety-inspection-checklist` | DDC(동일) | (미국 OSHA) 디지털 안전점검 체크리스트 | 3파일 / 28K |
| `safety-compliance-checker` | DDC(동일) | (미국 OSHA) PPE·고소작업 규정준수 자동점검 | 3파일 / 44K |
| `incident-reporting` | DDC(동일) | (미국 OSHA) 사고 보고·조사·추세분석 | 3파일 / 28K |
| `toolbox-talk-generator` | DDC(동일) | (미국 OSHA) TBM 브리핑 생성(다국어) | 3파일 / 36K |

> 설치 위치: 프로젝트 스코프 `.claude/skills/<name>/`.
> `construction-safety`는 사용자 개인 스킬 영역(`~/.claude/skills/`)에도 복사하고,
> claude.ai '설정 → 스킬 → 내가 만듦' 업로드용 zip도 별도 제공함.

---

## 3. CLAUDE.md 라우팅 규칙 (요약)

### 3-1. 건설 안전 (최우선)
요청에 '안전' 또는 안전 관련 용어(안전점검·위험성평가·중대재해·PPE·추락·TBM·재해·사고·
safety·hazard·incident 등)가 있으면 **항상 안전 스킬 사용**. 다른 규칙보다 우선.

- **국내(한국) 기본값 — 용도별 분담**
  - 점검표 생성·산재/중대재해 자동 판정·TBM(스크립트) → `safety-inspection-kr`
  - 컴플라이언스·부적합 판정(심각도 4단계)·시정조치·보고문서 → `construction-safety`
  - 성격이 겹치면 함께 사용
- **미국 OSHA/해외 현장** → DDC 5종(`safety-inspection` 외)
- 특정 형식(hwpx 공문·pptx) 필요 시 형식 스킬과 병행

### 3-2. HWPX 문서
1. '공문'·'공공기관'·'공무원' 포함 → `hwpx-jkf`
2. 그 외 hwpx 생성/편집 → `hwpx-kist`

### 3-3. 프레젠테이션 (위에서부터 순서 적용)
1. "HTML" 언급(예: "HTML 파일을 ppt로") → `html-ppt` (정적 HTML 슬라이드)
2. 고급 연출("자세하게·화려하게·브랜드·내레이션·애니메이션·영상" 등) → `ppt-master`
3. 기본값 → `pptx`

### 3-4. 모바일 앱/웹 UI
"모바일웹/모바일 앱/앱 화면 디자인/Sleek" 등 → `design-mobile-apps`
(※ `SLEEK_API_KEY` 환경변수 + `https://sleek.design` 접근 필요)

### 공통
- 사용자가 특정 스킬을 명시하면 그 지정을 최우선으로 한다.

---

## 4. 신규 작성 스킬: `safety-inspection-kr`

미국 OSHA(29 CFR 1926) 기반 DDC 스킬과 달리 **대한민국 법령 기준**으로 신규 작성.

- **규정 근거**: 산업안전보건법, 산업안전보건기준에 관한 규칙(안전보건규칙),
  중대재해처벌법, KOSHA 기준
- **구성 파일**
  - `SKILL.md` — 스킬 정의·작업순서·국내 핵심기준 요약·법령 검증 고지
  - `references/regulations-kr.md` — 재해 정의·보고기준·재해유형별 조문 정리
  - `scripts/checklist_kr.py` — 공종별(공통·추락·비계·굴착·전기·밀폐공간·화기·양중)
    점검표 + TBM 생성 (파이썬 표준 라이브러리)
  - `scripts/incident_kr.py` — 사고 입력 → 중대재해(산안법)·중대산업재해(중처법)·
    일반 산재보고 해당 여부와 보고 기한·방법 판정
- **주요 국내 기준(요약)**
  - 중대재해(산안법 시행규칙 제3조): 사망 1명↑ / 3개월 이상 요양 부상 동시 2명↑ /
    부상·질병자 동시 10명↑ → 지체 없이 보고
  - 중대산업재해(중처법 제2조): 사망 1명↑ / 동일사고 6개월 이상 치료 2명↑ /
    동일 유해요인 직업성질병 1년내 3명↑
  - 일반 산재보고(산안법 제57조): 사망 또는 3일 이상 휴업 → 1개월 내 산업재해조사표
  - 안전난간: 상부난간대 90~120cm, 발끝막이판 10cm↑ (안전보건규칙 제13조)

> ⚠️ 조문·수치는 통용 기준 정리본이므로, 실제 사용 전 국가법령정보센터(law.go.kr)
> 최신 법령 및 KOSHA 지침으로 반드시 검증해야 함(스킬 내 고지 포함).

---

## 5. 안전 스킬 규정 기준 비교 (중요)

| 구분 | 국내 스킬 | DDC(미국) 스킬 |
| --- | --- | --- |
| 근거 법령 | 산안법·안전보건규칙·중대재해처벌법·KOSHA | OSHA **29 CFR 1926** |
| 사고 분류 | 중대재해/중대산업재해/산재조사표 | `osha_recordable` |
| 단위 | 미터법(m/cm) | 피트/인치(feet/inch) |
| 적용 현장 | 국내 | 미국/해외 |

→ 국내 현장 문서에는 **국내 스킬 기본 사용**, DDC 스킬은 미국/해외용 참고.

---

## 6. 작업 커밋 이력 (브랜치: claude/keen-noether-5k253h)

```
bb7658e Split domestic safety routing between the two Korean skills
c382008 Add construction-safety skill (user-provided, Korea-standard)
12a22a6 Add Korean-standard safety skill (safety-inspection-kr)
0a06513 Add DDC construction safety skills with safety-term routing rule
5f2775e Add design-mobile-apps skill and mobile UI routing rule
a034992 Reinstall ppt-master skill and track its .env.example
a09e92c Route HTML-to-PPT requests to html-ppt skill
bf6ae01 Add html-ppt to presentation routing rules
10ea805 Add html-ppt skill from lewislulu/html-ppt-skill
72984a7 Route presentation requests: pptx by default, ppt-master for advanced
0e7c909 Add ppt-master skill from hugohe3/ppt-master
68f1790 Add pptx skill from anthropics/skills
c9ba03e Route hwpx skill by keyword instead of prompting
3cd02f3 Add hwpx-kist skill and let user choose hwpx engine per request
41d6a8b Add hwpx skill for HWP/HWPX document generation
```

---

## 7. 참고/주의 사항

- **용량**: `ppt-master`(121M/약 1.3만 파일)로 저장소가 큼 — 클론·체크아웃이 무거울 수 있음.
- **실행 의존성**: 안전 스킬 스크립트·pptx·ppt-master 등은 실행 시 `python3`, 각
  `requirements*.txt` 설치가 필요할 수 있음.
- **design-mobile-apps**: `SLEEK_API_KEY` 및 `sleek.design` 네트워크 접근 필요.
- **안전 법령 고지**: 국내 안전 스킬의 조문·수치는 최신 법령으로 검증 후 사용.
- **개인 스킬 영구화**: `~/.claude/skills/`에 직접 둔 스킬은 컨테이너 재활용 시 사라짐.
  영구 적용은 claude.ai 개인 스킬 업로드 또는 저장소(.claude/skills) 커밋으로 유지.

---

## 8. 설치된 스킬 디렉터리 트리 (요약)

```
.claude/skills/
├── hwpx-jkf/                   # HWPX 생성(공문/보고서 등)
├── hwpx-kist/                  # HWPX XML-first
├── pptx/                       # PowerPoint 기본
├── ppt-master/                 # PowerPoint 고급
├── html-ppt/                   # HTML 슬라이드
├── design-mobile-apps/         # 모바일 UI(Sleek)
├── safety-inspection-kr/       # 국내 안전(신규)
│   ├── SKILL.md
│   ├── references/regulations-kr.md
│   └── scripts/{checklist_kr.py, incident_kr.py}
├── construction-safety/        # 국내 안전(업로드)
├── safety-inspection/          # 미국 OSHA
├── safety-inspection-checklist/
├── safety-compliance-checker/
├── incident-reporting/
└── toolbox-talk-generator/
```
