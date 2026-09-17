# Uploadable Skills (설정 → 스킬 → 내가 만든 스킬)

These `.zip` files are packaged for upload to Claude via
**Settings → Skills → Created by me** (설정 → 스킬 → 내가 만듦).

Each zip contains a single skill folder with a `SKILL.md` whose frontmatter
has been cleaned to the fields the uploader accepts (`name`, `description`,
`license`). One zip = one skill; upload them one at a time.

## Skills (15)

**HR & Careers**
- `resume-tailor.zip` — 이력서(resume) 작성/최적화
- `cover-letter.zip` — 자기소개서(cover letter) 작성
- `job-description.zip` — 직무기술서(job description) 작성
- `offer-letter.zip` — 채용 오퍼레터
- `applicant-screening.zip` — 지원자 스크리닝

**Research & Intelligence**
- `deep-research.zip`, `web-search.zip`, `academic-search.zip`,
  `competitive-analysis.zip`, `news-monitor.zip`

**Visual & Creative**
- `image-generation.zip`, `diagram-creator.zip`, `chart-designer.zip`,
  `infographic.zip`, `ppt-visual.zip`

The three HR skills (resume-tailor, cover-letter, job-description) include
Korean trigger keywords (이력서 / 자기소개서 / 직무기술서) in their descriptions
so they activate on Korean requests.

## Rebuild

Regenerate from `.claude/skills/` with `scripts/build_uploadable_skills.py`.
