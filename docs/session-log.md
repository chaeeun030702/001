# 작업 기록 (Session Log)

- **저장소**: `chaeeun030702/001`
- **작업 브랜치**: `claude/loving-cori-aj8fvp`
- **문서 생성일**: 2026-11-18
- **작업자**: Claude Code (Opus 4.8) + chaeeun075@gmail.com

이 문서는 이 세션에서 진행한 전체 작업 내역과 생성/변경된 파일을 정리한 기록입니다.

---

## 1. 요청 요약 (시간순)

| # | 사용자 요청 | 처리 결과 |
|---|-------------|-----------|
| 1 | `claude-office-skills/skills`에서 **HR & Careers / Research & Intelligence / Visual & Creative** 3개 카테고리만 스킬 설치. 이력서·자기소개서·직무기술서 유사 요청 시 사용 | 15개 스킬을 `.claude/skills/`에 설치, HR 3종에 한국어 트리거 추가, 커밋·push |
| 2 | 사용자 지정 스킬에 추가 | 동일 15개 스킬을 사용자 레벨 `~/.claude/skills/`에도 복사 |
| 3 | '설정/스킬/내가만듦'에 올릴 수 있도록 skill 파일로 생성 | 업로드 규격에 맞춘 `.zip` 패키지 생성(`dist/uploadable-skills/`), 빌드 스크립트 추가, 커밋·push |
| 4 | 스킬에 맞춤법 추가 | `korean-proofreader` 맞춤법 교정 스킬 신규 작성·설치·패키징, 커밋·push |
| 5 | 전체 기록과 파일을 md 파일로 저장 | 본 문서 작성 |

---

## 2. 설치한 스킬 (총 16개)

출처: <https://github.com/claude-office-skills/skills> (16번째 `korean-proofreader`는 신규 자체 제작)

### HR & Careers (5)
| 스킬 | 설명 | 한국어 트리거 |
|------|------|---------------|
| `resume-tailor` | 이력서/CV 작성·최적화 | 이력서 |
| `cover-letter` | 자기소개서/커버레터 작성 | 자기소개서 |
| `job-description` | 직무기술서/채용공고 작성 | 직무기술서 |
| `offer-letter` | 채용 오퍼레터 | - |
| `applicant-screening` | 지원자 스크리닝·평가 | - |

### Research & Intelligence (5)
`deep-research`, `web-search`, `academic-search`, `competitive-analysis`, `news-monitor`

### Visual & Creative (5)
`image-generation`, `diagram-creator`, `chart-designer`, `infographic`, `ppt-visual`

### Writing & Proofreading (1, 신규)
| 스킬 | 설명 |
|------|------|
| `korean-proofreader` | 한국어 맞춤법·띄어쓰기·문법·표현 교정. 국립국어원 「한글 맞춤법」 기준, 교정문+교정내역표 출력. 이력서/자기소개서/직무기술서 등 결과물 교정에도 사용 |

---

## 3. 주요 기술 처리 내역

### 3.1 깨진 description 수정
원본 office-skills의 `resume-tailor`, `cover-letter`, `job-description` SKILL.md는
`description: ">"` (빈 플레이스홀더)로 되어 있어 자동 트리거가 불가능했습니다.
→ 세 스킬의 설명을 채우고 한국어 키워드(이력서/자기소개서/직무기술서)를 포함해
한국어 요청에도 활성화되도록 수정했습니다. 나머지 12개는 정상 설명이 있어 그대로 유지.

### 3.2 업로드용 패키지(.zip) 생성
claude.ai **설정 → 스킬 → 내가 만듦** 업로더는 프론트매터 규칙이 엄격합니다
(허용: `name`, `description`, `license` / `name`은 소문자·하이픈 슬러그).
원본에는 `category`, `tags`, `models`, `mcp`, `capabilities` 등 비표준 필드와
대문자 이름(`Applicant Screening` 등)이 있어 거부될 수 있었습니다.
→ 빌드 스크립트로 프론트매터를 정리하고 `name`을 폴더 슬러그로 통일한 뒤
스킬별 `.zip`(폴더 안 SKILL.md 구조)으로 패키징했습니다. 본문·부속 파일은 보존.

### 3.3 설치 위치
| 위치 | 범위 | 영속성 |
|------|------|--------|
| `.claude/skills/` (프로젝트) | 이 저장소 세션 | git 커밋됨 → 영구 |
| `~/.claude/skills/` (사용자) | 모든 프로젝트 | 임시 컨테이너 → 세션 종료 시 소멸 |
| `dist/uploadable-skills/*.zip` | 업로드용 | git 커밋됨 → 영구 |

> ⚠️ 이 세션은 클라우드 임시 환경이라 `~/.claude/skills/`(=`/root/.claude/skills`)
> 사본은 세션 종료 시 사라집니다. 로컬 PC에서 항상 쓰려면 브랜치를 받아
> `cp -r 001/.claude/skills/* ~/.claude/skills/` 하면 됩니다.

---

## 4. 생성·변경 파일

```
.claude/skills/
├── resume-tailor/            (SKILL.md, README.md) — description 수정 + 한국어 트리거
├── cover-letter/             (SKILL.md)            — description 수정 + 한국어 트리거
├── job-description/          (SKILL.md)            — description 수정 + 한국어 트리거
├── offer-letter/             (SKILL.md)
├── applicant-screening/      (SKILL.md)
├── deep-research/            (SKILL.md)
├── web-search/               (SKILL.md)
├── academic-search/          (SKILL.md)
├── competitive-analysis/     (SKILL.md)
├── news-monitor/             (SKILL.md)
├── image-generation/         (SKILL.md)
├── diagram-creator/          (SKILL.md)
├── chart-designer/           (SKILL.md)
├── infographic/              (SKILL.md)
├── ppt-visual/               (SKILL.md)
└── korean-proofreader/       (SKILL.md)            — 신규 작성

dist/uploadable-skills/
├── README.md                 — 업로드 방법 안내
└── <16개 스킬>.zip           — '내가 만듦' 업로드용 패키지

scripts/
└── build_uploadable_skills.py — .claude/skills → dist zip 재생성 스크립트

docs/
└── session-log.md            — 본 문서

.gitignore                    — dist/.skill-build/ 추가
```

---

## 5. 커밋 이력 (브랜치: claude/loving-cori-aj8fvp)

```
1b1496c Add korean-proofreader skill (맞춤법 교정)
7e753c1 Add uploadable skill packages for claude.ai custom skills
ad3be16 Install office skills: HR & Careers, Research & Intelligence, Visual & Creative
06dd06a Add openai_mcp server to call ChatGPT from Claude Code   (이전 작업, 기준점)
```

---

## 6. 사용 방법

### 업로드 (claude.ai 웹)
`dist/uploadable-skills/`의 각 `.zip`을 **설정 → 스킬 → 내가 만듦**에서 스킬별로 업로드.

### 패키지 재생성
```bash
python3 scripts/build_uploadable_skills.py
# → dist/uploadable-skills/*.zip 갱신
```

### 트리거 예시
- "이력서 작성해줘" → `resume-tailor`
- "자기소개서 써줘" → `cover-letter`
- "직무기술서 만들어줘" → `job-description`
- "맞춤법 검사해줘 / 교정해줘" → `korean-proofreader`

---

## 7. 참고 / 미결 사항
- 일부 office 스킬은 `office-mcp` MCP 서버 툴(`create_docx`, `extract_text_from_pdf` 등)을
  참조합니다. 현재 프로젝트 `.mcp.json`에는 `openai` 서버만 등록되어 있어, 문서 생성/추출까지
  온전히 쓰려면 office-mcp 등록이 별도로 필요할 수 있습니다.
- PR은 요청이 없어 생성하지 않았습니다. 필요 시
  <https://github.com/chaeeun030702/001/pull/new/claude/loving-cori-aj8fvp> 에서 생성 가능합니다.
