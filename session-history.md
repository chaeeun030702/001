# 세션 기록 · 파일 보관본

- 저장소: `chaeeun030702/001`
- 작업 브랜치: `claude/loving-johnson-oixt6n` (PR 머지 후)
- 관련 PR: [chaeeun030702/001#19](https://github.com/chaeeun030702/001/pull/19) — 스쿼시 머지, 머지 커밋 `c3d2ac6`
- 이 문서는 (1) 대화 기록 (2) 작업 결과 (3) 저장소 소스 파일 전문으로 구성됩니다.
- 도구 호출의 원시 출력과 시스템 알림은 길이 때문에 요약했고, 사용자 요청과 응답 내용은 빠짐없이 옮겼습니다.

---

## 1. 대화 기록

### 1-1. 첫 메시지 (작업 요청 아님)

**사용자**

> 새 세션에서 sources에 저장소를 넣고 한 줄만 요청하는 방법이 있어요. 그쪽은 제가 전부 해 드리지만, 새 대화를 열어야 해요.

**Claude**

보낸 메시지에 이 저장소에서 처리할 작업이 없다고 답했습니다. 이 세션에는 이미 `chaeeun030702/001`이 연결돼 있고 작업 브랜치는 `claude/loving-johnson-oixt6n`이라, 새 대화 없이 여기서 바로 요청하면 된다고 안내했습니다. 작업이 끝나면 커밋·푸시 후 드래프트 PR까지 만든다고 덧붙였습니다.

### 1-2. 회사명 제외 요청

**사용자**

> 회사명에 아래 용어가 있는 경우 제외
> 소방, 조경, 구조엔지니어링, 감시단, 재해예방, 구조안전, 세이프티, 안전관리, 학원, 소방기술단, 교육원, 안전시스템, 방재, 무사퇴근, 보건안전, 호남산업,

**Claude의 작업**

1. 저장소 구조를 확인했습니다. 안전관리자 채용 공고를 수집해 `briefings/`에 브리핑을 만드는 프로젝트였습니다(`safety_jobs/collect.py`, GitHub Actions 일일 실행).
2. 공고 필터링 위치를 찾았습니다.
   - `keep()` — 수집한 공고를 남길지 판정 (영업직·감시단·건설사 100위 밖·경력직·마감 등 제외)
   - 직전 브리핑에서 접수 중 공고를 이어받는 반복문 (제외 규칙을 다시 적용)
3. `collect.py`에 제외 용어 목록과 판정 함수를 추가하고 두 곳에 적용했습니다.
   - `EXCLUDE_CORP_TERMS`, `EXCLUDE_CORP_RE`
   - `excluded_corp()` — 회사명에서 공백을 뺀 뒤 용어 포함 여부 확인
   - `keep()`의 맨 앞에서 `return False, "제외 업체명"`
   - 이어받기 반복문에서 `continue`
4. `safety_jobs/README.md` 규칙 목록에 "제외 업체명" 항목을 추가했습니다.
5. 검증: `py_compile` 통과. 현재 `briefings/latest.json` 343건 중 22건이 걸렸습니다(사람인 대부분, 링커리어 1건, 인천대 게시판 1건).
6. 커밋 `eeda4a9` → 브랜치 푸시 → 드래프트 PR #19 생성. 처음 `main`을 base로 지정했다가 실패했고, 저장소 기본 브랜치가 `claude/github-claude-code-connector-vbr24r`임을 확인해 그쪽으로 다시 만들었습니다. PR 활동 구독도 걸었습니다.

**Claude (결과 보고)**

- 비교 방식: 회사명에서 공백을 뺀 뒤 용어가 들어 있는지 확인 (`(주)대한 안전보건 교육원`도 `교육원`에 걸림)
- 적용 위치: 새로 수집한 공고 + 직전 브리핑 이어받기 단계
- 현재 `latest.json` 기준 22건 해당. 브리핑 파일은 건드리지 않았고 다음 Actions 실행부터 반영
- 주의: `한국소방산업기술원` 같은 공공기관도 이름에 `소방`이 있으면 함께 제외됨. 남겨야 하면 예외 목록을 추가하겠다고 안내

제외 대상으로 걸린 22건은 다음과 같습니다.

| 출처 | 회사명 | 공고명 |
|---|---|---|
| 사람인 | 대한재해예방기술(주) | 산업안전관리자(신입,경력우대) |
| 사람인 | (주)무사퇴근 | [무사퇴근] 안전보건교육 안전파트 강사 모집 |
| 사람인 | 창조보건안전주식회사 | 창조보건안전(주) 보건관리전문기관 간호사 모집 |
| 사람인 | (주)대한 안전보건 교육원 | [(주)대한안전보건교육원] PHP 개발자 신입/경력 모집 |
| 사람인 | 에이치케이안전시스템(주) | [에이치케이안전시스템] 본사 안전지원팀 - 팀원 채용 |
| 사람인 | (주)호남산업안전본부 | 안전관리전문기관 산업안전기사 채용 |
| 사람인 | 에듀스카이항공승무원학원 | [훈련강사] 산업안전기사 훈련강사 모집 |
| 사람인 | 광주컴퓨터기술학원 | [직업훈련교사] 산업안전기사 교사 (정규,시간 강의 가능) |
| 사람인 | (주)정구조엔지니어링 | 건축 구조 안전진단 신입 및 경력직 채용 |
| 링커리어 | 모아소방전기학원 | [27년 1회대비] 과정평가형 산업안전기사 자격증 취득과정 |
| 인천대 안전공학과 | 한국소방산업기술원 | 한국소방산업기술원 2026년 정규직 채용 안내 |
| 사람인 | 바이킹소방 | [소방점검] 소방점검 인력채용 |
| 사람인 | 그린소방기술단 | 그린소방기술단 소방설비점검 신입 모집 |
| 사람인 | (주)에이탑소방 | 소방/방재 정규직 채용 - 신입&경력 |
| 사람인 | 대한안전관리(주) | 산업안전관리자 채용합니다. |
| 사람인 | (주)이에이치소방 | 소방점검, 공사, 안전관리 직원모집합니다.. |
| 사람인 | (주)나래구조안전기술 | (주)나래구조안전기술 건설안전점검 및 안전진단 담당 신입 채용 |
| 사람인 | (주)세이프티온솔루션 | 신입/경력 안전 컨설턴트 채용 |
| 사람인 | (주)부경방재 | 소방점검,안전관리 신입 / 경력 모집합니다 |
| 사람인 | 세이프티 프로 컨설팅 | PSM/산업안전/고압가스 컨설팅 신입·경력 채용 |
| 사람인 | (주)한울구조안전진단 | 안전점검전문기관(토목분야) 신입 및 경력직 모집 |
| 사람인 | 라온구조안전기술(주) | 시설물 안전진단(건축) 직원채용 공고[신입/경력] |

### 1-3. 시스템 알림 (구독 시작)

PR 구독 시작 알림 2건이 왔고, 확인 결과 CI 체크는 아직 등록되지 않았고(`pending`) 리뷰 코멘트도 없었습니다. 처리할 일이 없다고 보고했습니다.

### 1-4. 공공기관 예외 + 머지 요청

**사용자**

> 공공기관은 남기고 PR 머지해줘

**Claude의 작업**

1. `latest.json`의 `company_type` 값은 `''`(310건), `외국계`, `중견기업`, `중소기업`, `대기업`, `비영리법인`뿐이라 "공공" 표기가 거의 없다는 것을 확인했습니다. 이름 끝말로 판별하기로 했습니다.
2. `PUBLIC_CORP_RE`(공단·공사·진흥원·기술원·연구원·안전원·재단으로 끝나는 이름)를 추가하고, `excluded_corp()`가 공고 객체를 받아 `company_type`에 "공공"이 있거나 이 패턴에 맞으면 제외하지 않도록 바꿨습니다. 호출부 2곳도 함께 수정했습니다.
3. 검증: 문법 통과, 제외 대상 22건 → 21건, `한국소방산업기술원`은 남음.
4. README 문구를 갱신하고 커밋 `049c215`를 푸시했습니다.
5. PR이 드래프트라서 리뷰 가능 상태로 바꾸고 설명을 현재 동작에 맞게 고친 뒤, **스쿼시 머지**했습니다(`c3d2ac6`). PR 구독은 해제했습니다.

**Claude (결과 보고)**

- 공공기관 판별: 회사 유형이 공공이거나 이름이 위 끝말로 끝나면 제외 용어가 있어도 남김. 제외 대상은 22건에서 21건으로 감소
- 한계: 사이트가 공공 여부를 거의 표기하지 않아 이름 끝말로 판별함. 위 끝말이 아닌 공공기관(`…협회`, `…센터` 등)은 제외될 수 있음
- 이 저장소에는 CI 체크가 따로 없어서 로컬 문법 검사와 `latest.json` 대상 확인만 거침
- `briefings/` 파일은 다음 Actions 실행부터 반영

### 1-5. 시스템 알림 (머지 완료)

PR이 리뷰 가능 상태로 바뀌었다는 알림과 머지 완료 알림 2건이 왔고, 이미 처리가 끝난 일이라 추가 작업이 없다고 보고했습니다.

### 1-6. 저장 요청

**사용자**

> 전체 기록과 파일을 md 파일로 저장

**Claude**

이 문서를 만들었습니다.

---

## 2. 작업 결과 요약

### 변경 파일

| 파일 | 변경 |
|---|---|
| `safety_jobs/collect.py` | 제외 용어 목록(`EXCLUDE_CORP_TERMS`), 공공기관 패턴(`PUBLIC_CORP_RE`), 판정 함수 `excluded_corp()` 추가. `keep()` 맨 앞과 직전 브리핑 이어받기 반복문에 적용 |
| `safety_jobs/README.md` | 규칙 목록에 "제외 업체명" 항목 추가 (공공기관 예외 포함) |

### 커밋

| 커밋 | 내용 |
|---|---|
| `eeda4a9` | 회사명에 특정 용어가 있는 공고 제외 |
| `049c215` | 제외 업체명 규칙에서 공공기관 예외 처리 |
| `c3d2ac6` | PR #19 스쿼시 머지 |

### 추가된 코드 (`safety_jobs/collect.py`)

```python
# 회사명에 이 용어가 있으면 제외 (안전·소방 전문 용역사, 학원·교육기관 등). 공백은 무시하고 비교한다
EXCLUDE_CORP_TERMS = ("소방", "조경", "구조엔지니어링", "감시단", "재해예방", "구조안전", "세이프티", "안전관리", "학원",
                      "소방기술단", "교육원", "안전시스템", "방재", "무사퇴근", "보건안전", "호남산업")
EXCLUDE_CORP_RE = re.compile("|".join(map(re.escape, EXCLUDE_CORP_TERMS)))

PUBLIC_CORP_RE = re.compile(r"(?:공단|공사|진흥원|기술원|연구원|안전원|재단)(?:\(.*?\))?$")  # 공공기관은 제외하지 않는다


def excluded_corp(p: Posting) -> bool:
    """회사명에 제외 용어(EXCLUDE_CORP_TERMS)가 있는 민간 업체인가. 공공기관은 제외하지 않는다."""
    name = re.sub(r"\s|\(주\)|㈜|주식회사", "", p.company or "")
    if not EXCLUDE_CORP_RE.search(name):
        return False
    return not ("공공" in p.company_type or PUBLIC_CORP_RE.search(name))
```

`keep()` 맨 앞:

```python
    if excluded_corp(p):
        return False, "제외 업체명"
```

직전 브리핑 이어받기 반복문:

```python
        if excluded_corp(p):  # 제외 업체명 재적용
            continue
```

### 알려진 한계

- 공공기관 판별은 이름 끝말 기준이라 `…협회`, `…센터` 같은 공공기관은 제외될 수 있습니다.
- `briefings/`의 기존 결과 파일은 수정하지 않았고, 다음 Actions 실행부터 반영됩니다.

---

## 3. 저장소 소스 파일 전문

`briefings/`의 결과 파일(`latest.*`, 날짜별 `.md`, `history/*.json.gz`, `krx_listed.json`)은 용량이 커서 이 문서에서 뺐고, 목록만 아래에 적었습니다.


### 제외한 파일 (`briefings/`)

- `briefings/2026-09-29.md` (133,865 bytes)
- `briefings/2026-09-30.md` (155,735 bytes)
- `briefings/2026-10-01.md` (141,939 bytes)
- `briefings/2026-10-02.md` (155,863 bytes)
- `briefings/2026-10-03.md` (157,735 bytes)
- `briefings/history/2026-09-30.json.gz` (174,503 bytes)
- `briefings/history/2026-10-01.json.gz` (158,325 bytes)
- `briefings/history/2026-10-02.json.gz` (167,111 bytes)
- `briefings/history/2026-10-03.json.gz` (171,733 bytes)
- `briefings/krx_listed.json` (84,868 bytes)
- `briefings/latest.html` (406,358 bytes)
- `briefings/latest.json` (1,009,343 bytes)
- `briefings/latest.md` (157,735 bytes)
- `briefings/latest_edit.html` (406,522 bytes)


### 3-1. `README.md`

````markdown
# openai_mcp — Call ChatGPT from Claude Code

An MCP (Model Context Protocol) server that lets **Claude Code** call
**OpenAI's ChatGPT** models to delegate work. Register it once and Claude
gains two tools:

| Tool | What it does |
| --- | --- |
| `ask_chatgpt` | Send a prompt to a ChatGPT model and get its reply (draft, summarize, translate, second opinion, …). |
| `list_openai_models` | List the model ids your API key can use. |

The whole server is a single file, `server.py`, with its dependencies declared
inline (PEP 723), so [`uv`](https://docs.astral.sh/uv/) runs it with **no
manual install or build step**.

---

## 1. Prerequisites

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed
  (`uv --version` to check).
- An **OpenAI API key** from <https://platform.openai.com/api-keys>.
  > This uses the paid OpenAI API and is billed separately from a ChatGPT
  > subscription. You need API credits on your OpenAI account.

## 2. Provide your API key

The server reads the key from the `OPENAI_API_KEY` environment variable — it is
**never** written into any file in this repo. Export it in your shell:

```bash
export OPENAI_API_KEY="sk-...your key..."
# optional: point at a compatible endpoint (Azure OpenAI, a proxy, etc.)
# export OPENAI_BASE_URL="https://api.openai.com/v1"
```

Put the `export` line in your `~/.zshrc` / `~/.bashrc` to make it persistent.

## 3. Register with Claude Code

This repo already includes a project-scoped [`.mcp.json`](./.mcp.json) pointing
at `server.py`. When you open Claude Code in this directory it will detect the
server and ask you to approve it — accept, and the `ask_chatgpt` /
`list_openai_models` tools become available.

Prefer a global registration (works in any directory)? Run:

```bash
claude mcp add openai --env OPENAI_API_KEY="$OPENAI_API_KEY" -- uv run /full/path/to/server.py
```

Verify it's connected from inside Claude Code with `/mcp`.

## 4. Try it

Ask Claude Code things like:

- "Use ask_chatgpt to summarize this text: …"
- "Ask gpt-4o-mini to write a limerick about MCP."
- "List the OpenAI models I can use."

## Notes & troubleshooting

- **`OPENAI_API_KEY is not set`** → the variable isn't exported in the
  environment Claude Code launched from. Re-export it and restart Claude Code.
- **401 / authentication failed** → the key is wrong, revoked, or lacks access.
- **429 / quota exceeded** → out of credits or hitting rate limits; check
  <https://platform.openai.com/usage>.
- **Wrong model id (404)** → run `list_openai_models` to see valid ids; the
  default is `gpt-4o`.
- ChatGPT called this way has **no access** to your files, terminal, or the
  Claude conversation. Put everything it needs directly in the prompt.

## Run manually (debugging)

```bash
# starts a stdio MCP server; use the MCP Inspector to poke at it
uv run server.py
# or:
npx @modelcontextprotocol/inspector uv run server.py
```
````


### 3-2. `.gitignore`

```
# Secrets — never commit API keys
.env
.env.*
*.key

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# uv
.uv/

# OS / editor
.DS_Store
.idea/
.vscode/
```


### 3-3. `.mcp.json`

```json
{
  "mcpServers": {
    "openai": {
      "command": "uv",
      "args": ["run", "server.py"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "OPENAI_BASE_URL": "${OPENAI_BASE_URL:-https://api.openai.com/v1}"
      }
    }
  }
}
```


### 3-4. `.github/workflows/safety-jobs-briefing.yml`

```yaml
# 안전관리자 채용 일일 브리핑 — 12개 사이트 수집 후 briefings/ 에 커밋
# 20:00 KST Routine이 briefings/latest.* 를 읽어 브리핑 전달.
# GitHub 예약 실행은 지연·누락될 수 있어 19:07 / 19:27 KST 두 번 잡아 둔다(늦게 끝난 쪽이 최신).
name: safety-jobs-briefing
on:
  schedule:
    - cron: "7 10 * * *"  # 19:07 KST
    - cron: "27 10 * * *" # 19:27 KST
  workflow_dispatch:
  push:
    branches: [claude/safety-manager-job-openings-ab59yi]
    paths: [safety_jobs/**, .github/workflows/safety-jobs-briefing.yml]
permissions:
  contents: write
concurrency:
  group: safety-jobs-briefing-${{ github.ref }}
  cancel-in-progress: false
jobs:
  collect:
    runs-on: ${{ vars.COLLECT_RUNNER || 'ubuntu-latest' }}
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Use latest briefings (이전 수집 정보 유지)
        # push로 시작된 실행은 트리거 커밋을 체크아웃하므로, 그 뒤에 올라온 최신 브리핑을 이어받는다
        run: |
          git fetch -q origin "${GITHUB_REF_NAME}" && git checkout "origin/${GITHUB_REF_NAME}" -- briefings || true
      - name: Collect
        run: uv run safety_jobs/collect.py --out briefings
      - name: Commit briefing
        run: |
          git config user.name github-actions
          git config user.email github-actions@users.noreply.github.com
          # 결과를 보관한 뒤 원격 최신 커밋 위에 그대로 덮어쓴다 (JSON을 git이 줄 단위로 합치면 공고가 중복됨)
          out=$(mktemp -d); cp -r briefings/. "$out"/
          for i in 1 2 3 4; do
            git fetch -q origin "${GITHUB_REF_NAME}"
            git reset -q --hard "origin/${GITHUB_REF_NAME}"
            mkdir -p briefings && cp -r "$out"/. briefings/
            git add briefings
            if git diff --cached --quiet; then echo "no changes"; exit 0; fi
            git commit -q -m "briefing: $(TZ=Asia/Seoul date +%F)"
            if git push -q origin "HEAD:${GITHUB_REF_NAME}"; then echo "pushed"; exit 0; fi
            sleep $((i * 5))
          done
          echo "::error::briefing push failed"; exit 1
```


### 3-5. `safety_jobs/README.md`

````markdown
# 안전관리자 채용 일일 브리핑

매일 **19:07·19:27 KST** GitHub Actions(`.github/workflows/safety-jobs-briefing.yml`)가
`collect.py`로 아래 사이트의 안전관리자 채용 공고를 수집해 `briefings/`에 커밋하고,
**이틀에 한 번(짝수 날, 2·4·…·30일) 20:00 KST** Routine이 `briefings/latest.*`를 읽어 브리핑을 전달한다.
지난 보고일 이후 처음 수집된 공고는 **신규**(🆕, 초록 라벨·`N` 태그·신규 공고 표·필터)로 따로 표시한다.

```bash
uv run safety_jobs/collect.py --out briefings   # latest.md / latest.html / latest.json / YYYY-MM-DD.md
```

## 수집 대상 (순서 = 중복 시 우선순위)

| # | 사이트 | 수집 방법 |
|---|---|---|
| 1 | 잡코리아 신입·인턴 채용관 | 채용관 목록 API에서 `안전관리자` 검색 |
| 2 | 사람인 | 지정 검색 URL + 신입/경력무관 필터 100건 |
| 3 | 링커리어 | 검색 결과 `__NEXT_DATA__` |
| 4 | 건설워커 | `안전/품질/재료/CAD` 부문 목록 3쪽 |
| 5–8 | 서울과기대·충북대·인천대·부경대 안전공학과 | 취업/채용 게시판 (최근 75일, 안전 직무 포함 글) |
| 9 | 피플앤잡 (외국계) | 제목 검색(안전·보건·HSE·EHS·Safety·SHE) + 전체 검색(HSE·EHS·NEBOSH·산업안전기사·ISO 45001) |
| 10 | 기업 채용 페이지 | Workday 공개 API: 3M·Applied Materials·Micron·Equinix·Air Liquide·Air Products (+ Lam Research·Linde·ASML·Corning·Dow·Honeywell은 채용 홈에서 Workday 주소 탐색), BASF(SuccessFactors). 한국 근무 HSE/EHS/Safety 공고만, 영문 `N+ years of experience` 2년 이상은 경력직으로 제외 |
| 11 | 원티드 | 공개 API — 현재 GitHub Actions 접속을 403 차단 |
| 12 | 캐치 | 검색 결과 — 현재 GitHub Actions 접속을 403 차단 |

## 이전 수집 정보 유지

- 접수기한이 남은 공고는 다음 수집에서 목록에 안 보여도 `latest.json`에서 이어받는다(마감일 없는 공고는 14일).
- 실행마다 원격 최신 `briefings/`를 이어받아 수집하고, 결과는 `briefings/history/YYYY-MM-DD.json.gz`에 날짜별로 보관한다.

## 규칙

- **대상**: 안전 직무(안전·보건·HSE/EHS·소방·방재) 공고 중 신입 / 경력무관 / 신입·경력 / 인턴. 경력직 전용·마감 공고 제외.
- **직급**: 대리급 이상(제목·직급·본문·우대 표기 포함, 영문 Senior/Manager/Director 등)이 명시된 공고는 제외. 산업안전기사·건설안전기술사 등 기술사 우대 공고는 포함.
- **계약직**: 관심 기업(대기업 계열·외국계·코스피/코스닥·데이터센터/반도체) + 도급순위 15위 이내 건설사만.
- **제외 업체명**: 회사명(공백 무시)에 소방·조경·구조엔지니어링·감시단·재해예방·구조안전·세이프티·안전관리·학원·소방기술단·교육원·안전시스템·방재·무사퇴근·보건안전·호남산업이 있으면 제외(공공기관, 그리고 공단·공사·진흥원·기술원·연구원·안전원·재단으로 끝나는 이름은 제외하지 않음). 목록은 `collect.py`의 `EXCLUDE_CORP_TERMS`.
- **중복**: 업체명 + 제목 유사도로 판단, 위쪽 사이트 것을 남긴다.
- **표기**: `[정규직]`, `[계약직]`, `[인턴]`, `[고용형태 미표기]` 문단으로 나눈다.
- **표 열**: 구분 · 업체명 · 공고명 · 지원 자격(학과·자격·영어·학력) · 우대 사항 · 접수기한 · 출처.
- **강조**: 🔴 데이터센터·하이테크·삼성·하이닉스 관련 / 🔵 대기업군·외국계 (둘 다면 🔴).
  HTML(`latest.html`)은 행 배경색으로 구분한다.

지원 자격·우대 사항은 상세 페이지 본문에서 자동 추출한 요약이므로 지원 전 원문 확인이 필요하다.
````


### 3-6. `safety_jobs/collect.py`

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx>=0.27.0",
#     "beautifulsoup4>=4.12.0",
# ]
# ///
#!/usr/bin/env python3
"""안전관리자 채용 공고 수집·정리 (일일 브리핑용).

SOURCES 순서가 곧 우선순위다. 같은 공고가 여러 곳에 있으면 목록에서 위에 있는
사이트의 것을 남긴다. 경력직 전용 공고와 마감된 공고는 제외한다.

    uv run safety_jobs/collect.py --out briefings   # md/html/json 브리핑 생성

GitHub Actions(.github/workflows/safety-jobs-briefing.yml)가 매일 실행한다.
"""

import argparse
import collections
import datetime as dt
import difflib
import gzip
import html
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup

KST = dt.timezone(dt.timedelta(hours=9))
Q = quote("안전관리자")
# 검색어: 안전관리자 + 업종 무관 HSE/EHS 직무 + 자격증 명시 공고
KEYWORDS = ["안전관리자", "HSE", "EHS", "안전보건", "산업안전기사", "건설안전기사", "NEBOSH", "IOSH", "ISO45001", "안전공학"]
# 우대 강조(보라색): 외국어·영어 능통 / NEBOSH / IOSH / CSP
LANG_RE = re.compile(r"(?:영어|외국어|어학|English|중국어|일본어|베트남어|스페인어)\s*(?:회화\s*)?(?:능통|능숙|우수|가능|원활|비즈니스|원어민|fluent|business)"
                     r"|(?:TOEIC|토익|OPIc|오픽|TEPS|텝스|TOEIC\s*Speaking|토익\s*스피킹)\s*[:：]?\s*(?:\d{2,3}|IM|IH|AL|Lv|Level)"
                     r"|(?:어학|영어)\s*(?:성적|점수)\s*(?:우대|보유|필수)", re.I)
NEBOSH_RE = re.compile(r"NEBOSH", re.I)
IOSH_RE = re.compile(r"(?<![A-Za-z])IOSH(?![A-Za-z])", re.I)
HSE_ROLE_RE = re.compile(r"(?<![A-Za-z])(?:HSE|EHS|EH&S|SHE|HSEQ|QHSE)(?![A-Za-z])\s*(?:팀|파트|그룹|부문|담당|직무|업무|관리|엔지니어|매니저|"
                         r"Engineer|Specialist|Manager|Analyst|Officer|Coordinator|Supervisor|Leader|Assistant|Staff)", re.I)
CSP_RE = re.compile(r"(?<![A-Za-z])CSP(?![A-Za-z])|Certified\s+Safety\s+Professional", re.I)
CERT_KEY_RE = re.compile(r"(산업|건설)안전(?:산업)?기사")
ISO45001_RE = re.compile(r"ISO\s*[-_]?\s*45001|KOSHA[-\s]*MS", re.I)
# 공고 본문에 이 중 하나라도 있으면 안전 직무 공고로 싣는다
INCLUDE_RE = re.compile(r"산업안전(?:산업)?기사|(?:산업|건설)안전기술사|ISO\s*[-_]?\s*45001|안전\s*공학", re.I)
# '안전관리'는 흔한 말이라 직무로 쓰였거나 자격·우대·담당업무 항목에 있을 때만
SAFETY_DUTY_RE = re.compile(r"안전\s*관리\s*(?:자|업무|담당|선임|병행|직|팀|계획|체계)|안전\s*관리\s*(?:및|/|·)")
DUTY_HEAD = r"담당\s*업무|주요\s*업무|업무\s*내용|직무\s*내용|모집\s*분야"
PREF_IN_TITLE_RE = re.compile(r"[\(\[【][^\)\]】]*우대[^\)\]】]*[\)\]】]|[^\s/,]*\s*우대")
NON_HSE_SAFETY_RE = re.compile(r"Functional\s*Safety|안전\s*인증|Drug\s*Safety|Pharmacovigilance|Patient\s*Safety|Food\s*Safety|Product\s*Safety|Clinical|"
                               r"약물\s*감시|의약품\s*안전|식품\s*안전|안전성\s*(?:평가|정보)", re.I)
WATCH_RE = re.compile(r"감시\s*단")  # 안전감시단 등 감시 인력 모집은 제외
# 회사명에 이 용어가 있으면 제외 (안전·소방 전문 용역사, 학원·교육기관 등). 공백은 무시하고 비교한다
EXCLUDE_CORP_TERMS = ("소방", "조경", "구조엔지니어링", "감시단", "재해예방", "구조안전", "세이프티", "안전관리", "학원",
                      "소방기술단", "교육원", "안전시스템", "방재", "무사퇴근", "보건안전", "호남산업")
EXCLUDE_CORP_RE = re.compile("|".join(map(re.escape, EXCLUDE_CORP_TERMS)))
SALES_RE = re.compile(r"영업|세일즈|(?<![A-Za-z])Sales(?![A-Za-z])|판매\s*(?:사원|직|원)|텔레\s*마케|TM\s*상담", re.I)
HSE_RE = re.compile(r"(?<![A-Za-z])(?:HSE|EHS|SHE|HSEQ|QHSE)(?![A-Za-z])|환경\s*안전|안전\s*환경|안전\s*보건|안전\s*관리")
# 업체명으로 건설사 여부 판단 (제목의 '현장' 등은 공장 현장과 헷갈리므로 쓰지 않음)
CONSTR_NAME_RE = re.compile(r"건설|건축|토건|토목|이앤씨|이엔씨|E&C|ENC|씨엠|(?<![A-Za-z])CM(?![A-Za-z])|종합개발|주택|건영|중공업\s*건설부문|건설부문")

# 건설사는 2026년 시공능력평가 상위 100개사(토목건축)만 싣는다 — construction_top100_2026.tsv
_LATIN = {"A": "에이", "B": "비", "C": "씨", "D": "디", "E": "이", "F": "에프", "G": "지", "H": "에이치", "I": "아이", "J": "제이",
          "K": "케이", "L": "엘", "M": "엠", "N": "엔", "O": "오", "P": "피", "Q": "큐", "R": "알", "S": "에스", "T": "티",
          "U": "유", "V": "브이", "W": "더블유", "X": "엑스", "Y": "와이", "Z": "지"}
_ALIAS = {"아이파크현대산업개발": ["에이치디씨현대산업개발", "현대산업개발", "아이파크현대산업개발"],
          "삼성이앤에이": ["삼성엔지니어링"], "한화": ["한화건설부문", "한화건설"],
          "씨제이대한통운": ["씨제이대한통운건설부문"], "에스엠상선": ["에스엠상선건설부문"]}


def norm_corp(name):
    """업체명 정규화: 법인 표기·공백·괄호 제거, 영문 약칭은 한글 발음으로 (GS건설 → 지에스건설)."""
    n = re.sub(r"\(.*?\)|㈜|주식회사|유한회사|\s", "", name or "")
    n = n.upper().replace("E&C", "이앤씨").replace("E&A", "이앤에이").replace("S&D", "에스앤디").replace("D&I", "디앤아이")
    n = n.replace("IPARK", "아이파크").replace("POSCO", "포스코")
    n = re.sub(r"[A-Z]", lambda m: _LATIN[m.group(0)], n)
    return n.replace("이엔씨", "이앤씨")


def _load_top100():
    table = {}
    path = Path(__file__).with_name("construction_top100_2026.tsv")
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        rank, name = line.split("\t")
        key = norm_corp(name)
        table[key] = (int(rank), name)
        for a in _ALIAS.get(key, []):
            table[a] = (int(rank), name)
    return table


TOP100 = _load_top100()
MIXED_TOP100 = {norm_corp(n) for n in ("두산에너빌리티(주)", "효성중공업(주)", "(주)한화", "씨제이대한통운(주)", "에스엠상선(주)",
                                       "(주)농협네트웍스", "삼성물산(주)", "(주)동양", "(주)대림")}


def top100_rank(company):
    n = norm_corp(company)
    if n in TOP100:
        return TOP100[n][0]
    # '현대건설(주) 건설부문', '한화 건설부문' 처럼 뒤에 부문명이 붙은 경우
    m = re.match(r"(.+?)(?:건설부문|플랜트부문|인프라부문)$", n)
    return TOP100[m.group(1)][0] if m and m.group(1) in TOP100 else None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

SAFETY_RE = re.compile(r"안전|보건관리|(?<![A-Za-z])(?:HSE|EHS|EH&S|SHE|HSEQ|QHSE|HSSE|[Ss]afety|SAFETY)(?![A-Za-z])|산업위생|Industrial\s*Hygien|소방|방재")
CAREER_ONLY_RE = re.compile(r"경력\s*\d+\s*년\s*(이상|↑)?|경력직|경력\s*사원|경력\s*채용|^경력$")
NEWBIE_RE = re.compile(r"신입|인턴|경력\s*무관|졸업\s*예정|전체|무관")

# 강조 규칙 — A가 B보다 우선
HILITE_A_RE = re.compile(r"데이터\s*센터|IDC|하이테크|삼성|하이닉스")
BIG_GROUPS = (
    "삼성 SK 현대 HD현대 LG 롯데 포스코 POSCO 한화 GS 신세계 이마트 CJ 한진 대한항공 KT 두산 LS "
    "DL 대림 HDC 효성 코오롱 OCI KCC 한국타이어 고려아연 영풍 아모레 카카오 네이버 NAVER 쿠팡 "
    "대우건설 금호 태영 호반 부영 중흥 하림 HMM 셀트리온 미래에셋 농협 NH 한국전력 한전 "
    "한국수력원자력 한수원 한국가스공사 에코프로 SGC 동국제강 세아 한솔 대상 오리온 농심 "
    "KCC 현대건설 현대엔지니어링 GS건설 DL이앤씨 롯데건설 SK에코플랜트 포스코이앤씨 삼성물산"
).split()
FOREIGN_NAMES = (
    "3M 쓰리엠 필립모리스 바스프 BASF 듀폰 DuPont 에어리퀴드 린데 Linde 지멘스 Siemens 슈나이더 "
    "ABB 인텔 Intel 마이크론 Micron ASML 램리서치 Lam 어플라이드 Applied 도쿄일렉트론 TEL "
    "에쓰오일 S-OIL 유니레버 P&G 로레알 네슬레 코카콜라 아마존 Amazon AWS 구글 Google "
    "마이크로소프트 Microsoft 에퀴닉스 Equinix 디지털리얼티 다우 Dow 머크 Merck 에보닉 솔베이 "
    "아우모비오 보쉬 Bosch 콘티넨탈 BMW 벤츠 볼보 Volvo GE 하니웰 Honeywell 에머슨 존슨콘트롤즈 "
    "쉘 Shell 엑손 셰브론 토탈 한국알콘 Tesla 테슬라 Air Products 에어프로덕츠 SGS UL DNV 뷰로베리타스"
).split()

CERT_RE = re.compile(
    r"(?:산업|건설|가스|전기|소방|화공|기계|인간공학|화재감식)?안전(?:관리)?(?:기사|산업기사|기술사|지도사)"
    r"|산업위생관리(?:산업)?기사|산업보건지도사|소방(?:설비|시설)?(?:산업)?기사|소방시설관리사|소방안전관리자\s*\d급"
    r"|위험물(?:산업기사|기능장|기능사)|(?:대기|수질)?환경기사|전기(?:산업)?기사|가스(?:산업)?기사|건축(?:산업)?기사"
    r"|토목(?:산업)?기사|화약류(?:관리|제조)?(?:산업)?기사|간호사|보건관리자|운전면허"
)
ENG_RE = re.compile(r"(?:TOEIC\s*Speaking|TOEIC|토익\s*스피킹|토익|OPIc|오픽|TEPS|텝스|영어\s*(?:회화|능통|가능|우수|면접))(?:\s*[\d.]+\s*점?\s*(?:이상|↑)?|\s*(?:IM|IH|AL|Level)\s*\d?\s*(?:이상)?)?", re.I)
MAJOR_RE = re.compile(r"(?:산업|건설|화학|화공|기계|전기|전자|환경|소방|방재|토목|건축|안전|보건|원자력|재료|신소재|산업보건|간호)[가-힣·/]{0,6}(?:공학|학과|학|계열|전공)")
EDU_RE = re.compile(r"(?:학력\s*[:：]?\s*)?(대졸\s*(?:\(4년\))?\s*(?:이상|↑)?|초대졸\s*(?:이상|↑)?|고졸\s*(?:이상|↑)?|학력\s*무관|4년제[^,\n]{0,10}|석사[^,\n]{0,6})")

QUAL_HEAD = r"자격\s*요건|지원\s*자격|응시\s*자격|자격\s*조건|필수\s*(?:요건|사항)|공통\s*자격|Qualifications|Requirements|What\s+you\s+(?:need|bring)|Who\s+you\s+are"
PREF_HEAD = r"우대\s*(?:사항|조건|요건)|우대\s*[:：]|Preferred\s+(?:Qualifications|Skills|Experience)|Nice\s+to\s+have|Desired\s+(?:Qualifications|Skills)"
# 우대 조건에 AI 관련 역량이 있으면 강조(주황)
AI_TERM = r"(?<![A-Za-z])AI(?![A-Za-z])(?!\s*추천)|인공\s*지능|머신\s*러닝|딥\s*러닝|생성형|ChatGPT|(?<![A-Za-z])LLM(?![A-Za-z])|Machine\s*Learning"
AI_NEAR_PREF_RE = re.compile(rf"(?:{AI_TERM})[^.\n]{{0,40}}우대|우대[^.\n]{{0,60}}(?:{AI_TERM})", re.I)
AI_RE = re.compile(AI_TERM, re.I)
STOP = r"Preferred\s+Qualifications|Nice\s+to\s+have|Benefits|What\s+we\s+offer|이\s*기업과\s*나의|로그인\s*하고|적합도|TOP\s*궁금해요|스킬\s*핵심역량|핵심\s*역량|우대|근무\s*조건|근무\s*형태|근무지|근무\s*시간|전형|접수|복리|급여|제출\s*서류|유의\s*사항|기타\s*사항|채용\s*절차|모집\s*인원|기업\s*정보"


@dataclass
class Posting:
    source: str
    title: str
    company: str
    url: str
    listing_text: str = ""
    detail_text: str = ""
    employment: str = ""   # 정규직 / 계약직 / 인턴 / 기타
    level: str = ""        # 신입 / 경력무관 / 신입·경력 / 인턴 / 경력
    deadline: str = ""     # 표시용
    deadline_date: str = ""  # YYYY-MM-DD (정렬·만료 판단)
    qualification: str = ""
    preferred: str = ""
    company_type: str = ""  # 대기업 / 외국계 / 중견 / 공공 ... (사이트 표기)
    hilite: str = ""        # A / B / ""
    industry: str = ""      # 건설 / 일반 산업
    certs: list = field(default_factory=list)  # 공고에 명시된 산업안전기사·건설안전기사
    prefs: list = field(default_factory=list)  # 외국어·영어 능통 / NEBOSH / IOSH / CSP (보라색 강조)
    extra: dict = field(default_factory=dict)


def clean(s) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def text_of(node) -> str:
    return clean(node.get_text(" ")) if node else ""


def soup_text(html_: str) -> str:
    s = BeautifulSoup(html_, "html.parser")
    for t in s(["script", "style", "nav", "header", "footer", "noscript"]):
        t.decompose()
    return clean(s.get_text(" "))


class Fetcher:
    def __init__(self):
        self.c = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=40)

    def get(self, url, encoding=None, tries=3):
        last = None
        for i in range(tries):
            try:
                r = self.c.get(url, headers={"Referer": url})
                r.raise_for_status()
                if encoding:
                    return r.content.decode(encoding, errors="ignore")
                return r.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500:  # 404 등은 재시도해도 같다
                    raise
                last = e
            except Exception as e:  # 타임아웃 등 일시 오류는 재시도
                last = e
            time.sleep(3 + i * 5)
        raise last


# ---------------------------------------------------------------- 날짜
def parse_deadline(text: str, today: dt.date):
    """문자열에서 마감일을 찾아 (표시 문자열, date|None)을 돌려준다."""
    t = clean(text)
    rel = re.search(r"오늘\s*마감|\d{1,2}\s*시\s*마감|내일\s*마감|모레\s*마감|D\s*-\s*(\d+)", t)
    if rel:
        days = int(rel.group(1)) if rel.group(1) else 1 if "내일" in rel.group(0) else 2 if "모레" in rel.group(0) else 0
        d = today + dt.timedelta(days=days)
        return f"{d:%Y-%m-%d}", d
    m = re.search(r"(20\d{2})\s*[.\-/년]\s*(\d{1,2})\s*[.\-/월]\s*(\d{1,2})", t)
    if m:
        d = safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if d:
            return f"{d:%Y-%m-%d}", d
    m = re.search(r"~\s*(\d{1,2})\s*[/.월]\s*(\d{1,2})", t) or re.search(r"\((\d{1,2})/(\d{1,2})\)", t) \
        or re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", t) or re.fullmatch(r"(\d{1,2})/(\d{1,2})", t)
    if m:
        mo, da = int(m.group(1)), int(m.group(2))
        d = safe_date(today.year, mo, da)
        if d and (today - d).days > 60:  # 연말→연초 넘김 (today = 기준일: 게시판은 작성일)
            d = safe_date(today.year + 1, mo, da)
        if d:
            return f"{d:%Y-%m-%d}", d
    if re.search(r"상시|채용\s*시|수시", t):
        return "채용 시 마감", None
    return "", None


def safe_date(y, m, d):
    try:
        return dt.date(y, m, d)
    except ValueError:
        return None


# ---------------------------------------------------------------- 목록 파서
def src_jobkorea(f: Fetcher):
    """잡코리아 신입·인턴 채용관(entry-level-internship)에서 KEYWORDS 검색."""
    out, seen = [], set()
    for kw in KEYWORDS:
        for page in (1, 2, 3):
            url = ("https://www.jobkorea.co.kr/Theme/TemplateFreeGnoList/entry-level-internship?"
                   f"rSearchText={quote(kw)}&themeNo=169&tabNo=0&jobFilter=1&psTab=40&FreePageNo={page}&MainPageNo=1&GIOpenTypeCode=0")
            s = BeautifulSoup(f.get(url), "html.parser")
            items = s.select("li.dmpItem")
            for li in items:
                a = li.select_one(".rTit a")
                if not a:
                    continue
                link = urljoin("https://www.jobkorea.co.kr", a["href"].split("&rPageCode")[0])
                if link in seen:
                    continue
                seen.add(link)
                p = Posting("잡코리아", text_of(a), text_of(li.select_one(".corNm")), link, text_of(li))
                p.deadline = text_of(li.select_one(".rPeriod"))
                p.extra = {"query": kw}
                out.append(p)
            if len(items) < 40:
                break
    return out


def src_saramin(f: Fetcher):
    out, seen = [], set()
    # 사용자 지정 검색 URL + 검색어별 신입/경력무관 필터 100건
    urls = [("안전관리자", f"https://www.saramin.co.kr/zf_user/search?searchword={Q}&go=&flag=n&searchMode=1&searchType=search&search_done=y&search_optional_item=n")]
    urls += [(kw, f"https://www.saramin.co.kr/zf_user/search?searchword={quote(kw)}&searchType=search&exp_cd=1&exp_none=y"
                  "&recruitPageCount=100&recruitSort=relation") for kw in KEYWORDS]
    for kw, url in urls:
        s = BeautifulSoup(f.get(url), "html.parser")
        for it in s.select("div.item_recruit"):
            a = it.select_one("h2.job_tit a")
            if not a:
                continue
            rec = re.search(r"rec_idx=(\d+)", a.get("href", ""))
            if not rec or rec.group(1) in seen:
                continue
            seen.add(rec.group(1))
            cond = [text_of(x) for x in it.select(".job_condition > span")]
            p = Posting("사람인", clean(a.get("title") or a.get_text()),
                        text_of(it.select_one(".corp_name a")),
                        f"https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx={rec.group(1)}",
                        text_of(it))
            bold = " ".join(text_of(b) for b in it.select(".job_sector b"))
            p.extra = {"rec_idx": rec.group(1), "cond": cond, "sector": bold, "query": kw}
            p.level = cond[1] if len(cond) > 1 else ""
            p.employment = cond[3] if len(cond) > 3 else ""
            p.deadline = text_of(it.select_one(".job_date .date"))
            out.append(p)
    return out


def src_linkareer(f: Fetcher):
    acts = {}
    for kw in ("안전관리자", "HSE", "EHS", "산업안전기사"):
        url = f"https://linkareer.com/search?direction=DESC&page=1&q={quote(kw)}&sort=RELEVANCE&tab=open-activity"
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', f.get(url), re.S)
        if not m:
            raise RuntimeError("__NEXT_DATA__ 없음")
        _walk_activities(json.loads(m.group(1)), acts, kw)
    return _linkareer_postings(acts)


def _walk_activities(data, acts, kw):

    def walk(o):
        if isinstance(o, dict):
            if o.get("__typename") == "Activity" and o.get("title") and o.get("id") and o["id"] not in acts:
                acts[o["id"]] = dict(o, _kw=kw)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)


def _linkareer_postings(acts):
    out = []
    for a in acts.values():
        p = Posting("링커리어", clean(a["title"]), clean(a.get("organizationName")),
                    f"https://linkareer.com/activity/{a['id']}", "")
        jt = a.get("jobTypes") or []
        p.extra = {"jobTypes": jt, "query": a.get("_kw", "")}
        names = {"NEW": "신입", "INTERN": "인턴", "EXPERIENCED": "경력", "CONTRACT": "계약직", "REGULAR": "정규직"}
        p.listing_text = " ".join(names.get(x, x) for x in jt)
        if a.get("recruitCloseAt"):
            d = dt.datetime.fromtimestamp(a["recruitCloseAt"] / 1000, KST).date()
            p.deadline = f"{d:%Y-%m-%d}"
        else:
            p.deadline = "채용 시 마감"
        out.append(p)
    return out


def src_worker(f: Fetcher):
    """건설워커 '안전/품질/재료/CAD' 부문 목록(40건 × 3쪽)."""
    out, seen = [], set()
    for page in (1, 2, 3):
        url = f"https://www.worker.co.kr/job/list.asp?jobid=all&key=jkind&bkw=si&list_ea=40&p={page}"
        s = BeautifulSoup(f.get(url, encoding="cp949"), "html.parser")
        for tr in s.find_all("tr"):
            tds = tr.find_all("td", recursive=False)
            if len(tds) < 11:
                continue
            a = tds[4].find("a", href=re.compile(r"view\.asp"))
            if not a:
                continue
            no = re.search(r"no=(\d+)", a["href"])
            if not no or no.group(1) in seen:
                continue
            seen.add(no.group(1))
            full = text_of(tds[4])  # "제목 지역 | 채용구분 | 급여"
            title = text_of(a)
            if "|" in title:
                title = title.split("|")[0].strip()
            head, _, rest = full.partition("|")
            region = head.replace(title, "").strip() if title in head else ""
            if not region and " " in title:  # 제목 끝의 지역명 분리
                t0, _, last = title.rpartition(" ")
                if re.fullmatch(r"[가-힣/·,]{2,12}", last) and re.search(r"서울|경기|인천|세종|강원|충|대전|부산|울산|대구|경|전|광주|제주|해외|전국|기타", last):
                    title, region = t0, last
            parts = [region] + [clean(x) for x in rest.split("|")]
            title, rest = clean(title), " | ".join(parts)
            p = Posting("워커", title, text_of(tds[2]), urljoin("https://www.worker.co.kr/job/", a["href"]),
                        f"{title} {rest} {text_of(tds[6])}")
            p.employment = parts[1] if len(parts) > 1 else ""
            p.level = text_of(tds[6]).split(" ")[0]  # 경력 / 신입 / 무관 / 전체
            p.extra = {"exp_edu": text_of(tds[6]), "region": parts[0] if parts else ""}
            p.deadline = text_of(tds[10])
            out.append(p)
    return out


def board_rows(soup, base, link_fn):
    """학과 게시판(표) → (제목, 링크, 작성일)."""
    rows = []
    for tr in soup.select("tbody tr, table tr"):
        a = tr.find("a")
        tds = tr.find_all("td")
        if not a or len(tds) < 3:
            continue
        title = clean(text_of(a.find("strong")) or a.get("title") or text_of(a))
        title = re.sub(r"^\[\s*일반공지\s*\]\s*", "", title)
        link = link_fn(a)
        date = ""
        for td in tds:
            m = re.search(r"20\d{2}[.\-]\d{2}[.\-]\d{2}", text_of(td))
            if m:
                date = m.group(0).replace(".", "-")
        if title and link and date:  # 작성일 없는 행 = 메뉴/레이아웃 표
            rows.append((title, urljoin(base, link), date))
    return rows


def make_board_source(name, url, link_fn, encoding=None):
    def _src(f: Fetcher):
        s = BeautifulSoup(f.get(url, encoding=encoding), "html.parser")
        out = []
        for title, link, date in board_rows(s, url, link_fn):
            p = Posting(name, title, "", link, f"{title} 작성일 {date}")
            p.extra = {"posted": date}
            out.append(p)
        if not out:
            raise RuntimeError("게시글 목록을 찾지 못함")
        return out
    return _src


def _href(a):
    h = a.get("href", "")
    return None if h.startswith(("#", "javascript")) else h


def _inu(a):
    seq, fnct = a.get("data-bbs-artcl-seq"), a.get("data-fnct-no")
    return f"https://www.inu.ac.kr/bbs/safety/{fnct}/{seq}/artclView.do" if seq and fnct else _href(a)


# ---------------------------------------------------------------- 외국계 채용 사이트 · 기업 채용 페이지
EN_SAFETY_TITLE_RE = re.compile(r"(?<![A-Za-z])(?:HSE|EHS|EH&S|SHE|HSEQ|QHSE|HSSE|Safety|Industrial\s*Hygien\w*)(?![A-Za-z])|안전|보건", re.I)
KOREA_LOC_RE = re.compile(r"Korea|,\s*KOR(?![A-Za-z])|Bundang|Seoul|Pyeongtaek|Hwaseong|Icheon|Cheongju|Gumi|Ulsan|Yeosu|Pohang|Incheon|Suwon|Yongin|"
                          r"Giheung|Asan|Cheonan|Onyang|Busan|Daegu|Gwangju|Daejeon|Pangyo|Seongnam|Anseong|Osan|Paju|"
                          r"서울|경기|평택|화성|이천|청주|구미|울산|여수|포항|인천|수원|용인|기흥|아산|천안|부산|판교|파주|한국", re.I)


def src_peoplenjob(f: Fetcher):
    """피플앤잡(외국계 전문) — 제목 검색 + HSE/EHS 전체 검색."""
    out, seen = [], set()
    queries = [("jobs.title", q) for q in ("안전", "보건", "HSE", "EHS", "Safety", "SHE")]
    queries += [("all", q) for q in ("HSE", "EHS", "NEBOSH", "산업안전기사", "ISO 45001")]
    for fld, q in queries:
        for page in (1, 2, 3):
            url = f"https://www.peoplenjob.com/jobs?field={fld}&q={quote(q)}&page={page}"
            s = BeautifulSoup(f.get(url), "html.parser")
            cards = s.select(".jd-card")
            for c in cards:
                a = c.select_one(".jd-card-title a")
                if not a:
                    continue
                link = a.get("href", "").split("?")[0]
                link = urljoin("https://www.peoplenjob.com", link)
                if link in seen:
                    continue
                seen.add(link)
                for b in a.select(".jd-card-meta-urgent"):  # 'U'(긴급) 배지
                    b.decompose()
                title = text_of(a)
                p = Posting("피플앤잡", title, text_of(c.select_one(".jd-card-company")), link, text_of(c))
                career = text_of(c.select_one(".jd-card-meta-career-text"))
                # 직급: 인턴.신입 포함 → 신입, 사원 → 상세 확인, 대리 이상만 → 경력
                p.level = "신입" if "신입" in career else "" if "사원" in career else "경력"
                p.deadline = re.sub(r"^(\d{1,2})\.(\d{1,2})$", r"\1/\2", text_of(c.select_one(".job-fin-date")))
                p.company_type = "외국계"
                p.extra = {"query": q, "career": career,
                           "loc": text_of(c.select_one(".jd-card-meta-location-text"))}
                out.append(p)
            if len(cards) < 30:
                break
            time.sleep(0.5)
    return out


# (표시 이름, tenant, wd 번호, site, 업종) — Workday 공개 채용 API
WORKDAY = [
    ("3M", "3m", "wd1", "Search", ""),
    ("Applied Materials", "amat", "wd1", "External", "하이테크·반도체"),
    ("Micron", "micron", "wd1", "External", "하이테크·반도체"),
    ("Equinix", "equinix", "wd1", "External", "데이터센터"),
    ("Air Liquide", "airliquidehr", "wd3", "AirLiquideExternalCareer", "반도체 산업가스"),
    ("Air Products", "airproducts", "wd5", "AP0001", "반도체 산업가스"),
]
# Workday 주소를 모르는 회사: 채용 홈에서 myworkdayjobs 링크를 찾아 쓴다 (못 찾으면 건너뜀)
WORKDAY_DISCOVER = [
    ("Lam Research", "https://careers.lamresearch.com/", "하이테크·반도체"),
    ("Linde", "https://www.linde.com/careers", "반도체 산업가스"),
    ("ASML", "https://www.asml.com/en/careers", "하이테크·반도체"),
    ("Corning", "https://www.corning.com/worldwide/en/careers.html", "하이테크"),
    ("Dow", "https://corporate.dow.com/en-us/careers.html", ""),
    ("Honeywell", "https://careers.honeywell.com/", ""),
]
WD_LINK_RE = re.compile(r"https://([a-z0-9-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([A-Za-z0-9_-]+)")
CAREER_STATUS = {}  # 회사별 수집 결과 (사이트 현황표에 표시)
PREV_SEEN = {}      # 직전 브리핑의 URL/업체+공고명 → 처음 수집일 (신규 판정)
REPORT_EVERY = 2    # 보고 주기: 짝수 날(2·4·…·30일) 20:00 — Routine cron '2-30/2'


def last_report_date(today):
    """오늘 이전의 마지막 보고일 (짝수 날, 30일까지). 그 뒤에 처음 수집된 공고가 '신규'."""
    d = today - dt.timedelta(days=1)
    while not (d.day % 2 == 0 and d.day <= 30):
        d -= dt.timedelta(days=1)
    return d


def is_new(p, today):
    fs = p.extra.get("first_seen")
    return bool(fs) and fs > last_report_date(today).isoformat()
PREV_TOTAL = None   # 직전 브리핑 공고 수 (KPI 변화량)


def _html_text(h):
    return clean(BeautifulSoup(h or "", "html.parser").get_text(" "))


def _workday(f: Fetcher, name, tenant, wd, site, sector):
    base = f"https://{tenant}.{wd}.myworkdayjobs.com"
    api = f"{base}/wday/cxs/{tenant}/{site}/jobs"
    found = {}
    for q in ("Korea", "EHS", "HSE", "Safety", "Environmental Health Safety", "안전"):
        for off in range(0, 200, 20):
            r = f.c.post(api, json={"appliedFacets": {}, "limit": 20, "offset": off, "searchText": q},
                         headers={"Accept": "application/json", "Content-Type": "application/json"})
            r.raise_for_status()
            d = r.json()
            posts = d.get("jobPostings") or []
            for jp in posts:
                path = jp.get("externalPath", "")
                if path and path not in found:
                    found[path] = jp
            if len(posts) < 20 or (q != "Korea" and off >= 40):
                break
            time.sleep(0.3)
    out = []
    for path, jp in found.items():
        title = clean(jp.get("title", ""))
        loc = clean(jp.get("locationsText", ""))
        if not EN_SAFETY_TITLE_RE.search(title):
            continue
        multi = re.search(r"\d+\s*(?:Locations|개\s*근무지)", loc)
        if not (KOREA_LOC_RE.search(f"{loc} {title}") or multi):
            continue
        p = Posting("기업 채용 페이지", title, name, f"{base}/{site}{path}", f"{title} {loc} {jp.get('postedOn', '')}")
        p.company_type = "외국계"
        p.deadline = "채용 시 마감"  # Workday 공고에는 마감일이 없다
        p.extra = {"query": "Workday", "sector": sector, "loc": loc,
                   "detail_api": f"{base}/wday/cxs/{tenant}/{site}{path}", "need_korea": bool(multi and not KOREA_LOC_RE.search(loc))}
        out.append(p)
    return out


def _rmk_basf(f: Fetcher):
    """BASF (SAP SuccessFactors 채용 사이트) — 한국 근무 공고."""
    page = f.get("https://basf.jobs/search/?q=&locationsearch=Korea")
    tok = re.search(r'CSRFToken\s*=\s*"([^"]+)"', page)
    out = []
    for pn in range(0, 5):
        r = f.c.post("https://basf.jobs/services/recruiting/v1/jobs",
                     json={"locale": "en_US", "pageNumber": pn, "sortBy": "", "keywords": "", "location": "Korea",
                           "facetFilters": {}, "brand": "", "skills": [], "categoryId": 0, "alertId": "", "rcmCandidateId": ""},
                     headers={"Accept": "application/json", "Content-Type": "application/json",
                              "X-CSRF-Token": tok.group(1) if tok else ""})
        r.raise_for_status()
        rows = r.json().get("jobSearchResult") or []
        for row in rows:
            j = row.get("response", row)
            title = clean(j.get("unifiedStandardTitle") or j.get("title") or "")
            locs = " ".join(j.get("jobLocationShort") or [])
            if not EN_SAFETY_TITLE_RE.search(title):
                continue
            url = f"https://basf.jobs/job/{j.get('urlTitle', 'job')}/{j.get('id')}-en_US/"
            p = Posting("기업 채용 페이지", title, "BASF", url, f"{title} {locs}")
            p.company_type = "외국계"
            p.deadline = "채용 시 마감"
            p.extra = {"query": "RMK", "sector": "화학", "loc": locs}
            out.append(p)
        if len(rows) < 10:
            break
    return out


def src_company_careers(f: Fetcher):
    """외국계 기업 채용 페이지(Workday 등)에서 한국 근무 HSE/EHS/Safety 공고."""
    out = []
    targets = list(WORKDAY)
    for name, home, sector in WORKDAY_DISCOVER:
        try:
            m = WD_LINK_RE.search(f.get(home, tries=1))
        except Exception as e:
            CAREER_STATUS[name] = f"채용 홈 접속 실패({type(e).__name__})"
            continue
        if not m:
            CAREER_STATUS[name] = "Workday 등 공개 API 없음 — 자체 검색(스크립트 렌더링)이라 수집 불가"
            continue
        targets.append((name, m.group(1), m.group(2), m.group(3), sector))
    for name, tenant, wd, site, sector in targets:
        try:
            got = _workday(f, name, tenant, wd, site, sector)
            CAREER_STATUS[name] = f"한국 HSE {len(got)}건"
            out += got
        except Exception as e:
            CAREER_STATUS[name] = f"실패({type(e).__name__})"
    try:
        got = _rmk_basf(f)
        CAREER_STATUS["BASF"] = f"한국 HSE {len(got)}건"
        out += got
    except Exception as e:
        CAREER_STATUS["BASF"] = f"실패({type(e).__name__})"
    if not any(v.startswith("한국") for v in CAREER_STATUS.values()):
        raise RuntimeError("기업 채용 페이지 전부 접속 실패: " + ", ".join(f"{k} {v}" for k, v in CAREER_STATUS.items()))
    return out


def src_wanted(f: Fetcher):
    """원티드 — 공개 API (GitHub Actions에서는 403 차단 중)."""
    out = []
    for q in ("안전관리자", "HSE", "EHS"):
        d = json.loads(f.get(f"https://www.wanted.co.kr/api/v4/jobs?country=kr&query={quote(q)}&years=0&limit=50&offset=0&job_sort=job.latest_order"))
        for j in d.get("data", []):
            p = Posting("원티드", clean(j.get("position", "")), clean((j.get("company") or {}).get("name", "")),
                        f"https://www.wanted.co.kr/wd/{j.get('id')}", clean(j.get("position", "")))
            p.deadline = j.get("due_time") or "채용 시 마감"
            p.extra = {"query": q}
            out.append(p)
    return out


def src_catch(f: Fetcher):
    """캐치 — 검색 결과 (GitHub Actions에서는 403 차단 중)."""
    out, seen = [], set()
    for q in ("안전관리자", "HSE", "EHS"):
        s = BeautifulSoup(f.get(f"https://www.catch.co.kr/NCS/RecruitSearch?Keyword={quote(q)}"), "html.parser")
        for a in s.select('a[href*="RecruitInfoDetails"]'):
            link = urljoin("https://www.catch.co.kr", a["href"])
            if link in seen or not text_of(a):
                continue
            seen.add(link)
            p = Posting("캐치", text_of(a), "", link, text_of(a.parent))
            p.extra = {"query": q}
            out.append(p)
    return out


def fetch_detail(f: Fetcher, p: Posting) -> str:
    if p.extra.get("detail_api"):  # Workday: JSON 상세
        r = f.c.get(p.extra["detail_api"], headers={"Accept": "application/json"})
        r.raise_for_status()
        info = r.json().get("jobPostingInfo", {})
        locs = " ".join([info.get("location", "")] + (info.get("additionalLocations") or []))
        p.extra["loc"] = clean(locs) or p.extra.get("loc", "")
        p.extra["time_type"] = info.get("timeType", "")
        return clean(f"{info.get('title', '')} 근무지 {locs} {info.get('timeType', '')} "
                     f"{_html_text(info.get('jobDescription'))}")
    url = p.url
    if p.source == "사람인":
        url = f"https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx={p.extra['rec_idx']}&rec_seq=0"
    return soup_text(f.get(url, encoding="cp949" if p.source == "워커" else None))


EN_YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:or\s+more\s+|\+\s*)?years?(?:'|’)?\s*(?:of\s+)?(?:\w+\s+){0,4}?(?:experience|exp\.)", re.I)
EN_ENTRY_RE = re.compile(r"new\s*grad|recent\s*graduate|entry[\s-]*level|(?<![A-Za-z])intern(?:ship)?(?![A-Za-z])|no\s+(?:prior\s+)?experience\s+(?:is\s+)?required|0\s*[-~]\s*\d\s*years?|신입", re.I)


def foreign_level(p: Posting):
    """외국계 채용 페이지·피플앤잡 공고의 경력 요건 (영문 'N+ years of experience' 포함)."""
    t = p.detail_text
    if p.source == "피플앤잡" and p.level == "경력":
        return
    if EN_ENTRY_RE.search(f"{p.title} {t[:6000]}") or re.search(r"신입\s*(?:가능|지원|포함)|경력\s*무관", t):
        p.level = p.level or "신입"
        return
    years = [int(m.group(1)) for m in EN_YEARS_RE.finditer(t)]
    years += [int(m.group(1)) for m in re.finditer(r"경력\s*(\d{1,2})\s*년\s*(?:이상|↑)", t)]
    if years and min(years) >= 2:
        p.level = "경력"
    elif years:
        p.level = "신입·경력"
    elif p.source == "피플앤잡" and not p.level:
        p.level = "신입·경력" if "사원" in p.extra.get("career", "") else ""


# (이름, 수집 함수, 게시판 여부) — 순서 = 중복 시 우선순위
SOURCES = [
    ("잡코리아", src_jobkorea, False),
    ("사람인", src_saramin, False),
    ("링커리어", src_linkareer, False),
    ("워커", src_worker, False),
    ("서울과기대 안전공학과", make_board_source(
        "서울과기대 안전공학과", "https://safety.seoultech.ac.kr/b_information/job_info/", _href), True),
    ("충북대 안전공학과", make_board_source(
        "충북대 안전공학과", "https://safety.chungbuk.ac.kr/safety5_2", _href), True),
    ("인천대 안전공학과", make_board_source(
        "인천대 안전공학과", "https://www.inu.ac.kr/safety/3207/subview.do", _inu), True),
    ("부경대 안전공학과", make_board_source(
        "부경대 안전공학과", "https://safety.pknu.ac.kr/safety/2080", _href), True),
    ("피플앤잡", src_peoplenjob, False),
    ("기업 채용 페이지", src_company_careers, False),
    ("원티드", src_wanted, False),
    ("캐치", src_catch, False),
]


# ---------------------------------------------------------------- 상세 분석
def section(text, head_re, max_len=260):
    m = re.search(rf"(?:{head_re})\s*[:：]?", text)
    if not m:
        return ""
    body = text[m.end():m.end() + 1200]
    stop = re.search(STOP if "우대" not in head_re else STOP.replace("|우대", ""), body[5:])
    if stop:
        body = body[:stop.start() + 5]
    return clean(body)[:max_len]


def uniq(seq, limit=4):
    out = []
    for x in seq:
        x = clean(x)
        if x and not any(x in y or y in x for y in out):
            out.append(x)
    return out[:limit]


def summarize_qual(qual_txt, whole):
    src = qual_txt or whole
    majors = uniq(m.group(0) for m in MAJOR_RE.finditer(src))
    certs = uniq((m.group(0) for m in CERT_RE.finditer(src)), 4)
    eng = uniq((m.group(0) for m in ENG_RE.finditer(whole)), 2)
    edu = uniq((m.group(1) for m in EDU_RE.finditer(src)), 1)
    parts = []
    if majors:
        parts.append("학과: " + ", ".join(majors))
    if certs:
        parts.append("자격: " + ", ".join(certs))
    if eng:
        parts.append("영어: " + ", ".join(eng))
    if edu:
        parts.append("학력: " + edu[0])
    if not parts and qual_txt:
        parts.append(qual_txt[:110])
    return " / ".join(parts)


def detail_fields(p: Posting):
    t = p.detail_text
    if p.source == "잡코리아":
        m = re.search(r"고용형태\s*([가-힣·,/ ]{2,20}?)\s*(?:직급|급여|근무)", t)
        if m:
            p.employment = clean(m.group(1))
        m = re.search(r"지원자격\s*경력\s*([가-힣·↑0-9 ]{2,15}?)\s*학력", t)
        if m:
            p.level = clean(m.group(1))
        m = re.search(r"마감일\s*(20\d{2}\.\d{2}\.\d{2})", t)
        if m:
            p.deadline = m.group(1)
        m = re.search(r"지원자격\s*경력\s*[가-힣·↑0-9 ]{2,15}?\s*학력\s*([가-힣0-9()↑ ]{2,15}?)\s*(?:스킬|우대|핵심|자격증|$)", t)
        if m:
            p.extra["edu"] = clean(m.group(1))
        m = re.search(r"산업\s*\(업종\)\s*([가-힣·,/ ]{2,30}?)\s*(?:지도보기|위치|설립|대표|$)", t)
        if m:
            p.extra["biz"] = clean(m.group(1))
        m = re.search(r"기업구분\s*([가-힣]+)", t)
        if m:
            p.company_type = m.group(1)
    elif p.source == "링커리어":
        m = re.search(r"기업형태\s*([가-힣]+)", t)
        if m:
            p.company_type = m.group(1)
        m = re.search(r"마감일\s*(20\d{2}\.\d{2}\.\d{2})", t)
        if m:
            p.deadline = m.group(1)
    elif p.source == "워커":
        if p.deadline in ("", "채용시"):
            m = re.search(r"마감일\s*(20\d{2}년\s*\d{1,2}월\s*\d{1,2}일|채용시)", t)
            if m:
                p.deadline = m.group(1)
    elif p.extra.get("posted") is not None:  # 학과 게시판
        m = re.search(r"(?:접수\s*기간|마감|지원서\s*접수)[^~]{0,30}~\s*([^)\]]{3,25})", t)
        p.deadline = m.group(1) if m else ""


def employment_of(p: Posting, text):
    e = p.employment
    if p.source == "링커리어":
        jt = p.extra.get("jobTypes", [])
        e = "계약직" if "CONTRACT" in jt else "인턴" if "INTERN" in jt else "정규직" if "NEW" in jt else ""
    if not e:
        if re.search(r"인턴", p.title):
            e = "인턴"
        elif re.search(r"계약직|기간제|촉탁|PJT|프로젝트\s*계약", f"{p.title} {text}"):
            e = "계약직"
        elif re.search(r"(?<![A-Za-z])(?:Contract(?:or)?|Temporary|Fixed[\s-]*term)(?![A-Za-z])", f"{p.title} {p.extra.get('time_type', '')}", re.I):
            e = "계약직"
        elif re.search(r"정규직", text) or re.search(r"Full[\s_-]*time|Regular|Permanent", p.extra.get("time_type", ""), re.I):
            e = "정규직"
    if re.search(r"계약|기간제|파견|현장채용", e):
        return "계약직"
    if "정규" in e:
        return "정규직"
    if "인턴" in e:
        return "인턴"
    return "기타/미표기"


# 대리급 이상(대리·과장·차장·부장·팀장·임원, 영문 Senior/Manager/Director 등) 공고는 경력직으로 보고 제외
SENIOR_RANK_RE = re.compile(r"대리|과장|차장|부장|팀장|실장|임원|책임|수석|매니저|디렉터|"
                            r"(?<![A-Za-z])(?:Senior|Sr\.?|Director|Head|Principal|Lead|Manager|Supervisor|VP|Chief)(?![A-Za-z])", re.I)
JUNIOR_RANK_RE = re.compile(r"사원|주임|신입|인턴|졸업|(?<![A-Za-z])(?:Junior|Jr\.?|Associate|Entry|Intern|Graduate|Trainee)(?![A-Za-z])", re.I)
RANK_FIELD_RE = re.compile(r"직급\s*(?:/\s*직책)?\s*[:：]?\s*([가-힣·,/.~\- ]{2,24}?)(?=\s*(?:급여|근무|직책|연봉|모집|$))")


# 본문에 명시된 대리급 이상 요건(우대 포함)
BODY_SENIOR_RE = re.compile(r"(?:대리|과장|차장|부장|책임|수석)\s*급|(?:대리|과장|차장|부장)\s*(?:이상|~|-)")


TITLE_YEARS_RE = re.compile(r"(\d{1,2})\s*(?:[-~]\s*\d{1,2}\s*)?년\s*(?:이상|↑|차|경력|\))|경력\s*(\d{1,2})\s*[-~]")


def senior_rank(p: Posting) -> bool:
    """대리급 이상이 명시된 공고인가 (제목·직급 표기·본문, 우대 표기 포함). 기술사 우대는 제외하지 않는다.
    직급 표기에 사원·신입을 함께 뽑는다고 되어 있으면 제외하지 않는다."""
    title = p.title
    if SENIOR_RANK_RE.search(title) and not JUNIOR_RANK_RE.search(title):
        return True
    for m in BODY_SENIOR_RE.finditer(p.detail_text or ""):
        near = p.detail_text[max(0, m.start() - 12):m.end() + 4]
        if not JUNIOR_RANK_RE.search(near):
            return True
    m = RANK_FIELD_RE.search(p.detail_text or "")
    field_ = m.group(1) if m else ""
    if p.source == "피플앤잡":
        field_ = p.extra.get("career", "") or field_
    return bool(SENIOR_RANK_RE.search(field_) and not JUNIOR_RANK_RE.search(field_))


def level_of(p: Posting, text):
    lv = p.level
    if senior_rank(p):
        p.extra["senior"] = True
        return "경력"
    # 제목의 '3년 이상', '2-5년 경력', '(10~20년)' 등 2년 이상 경력 요건
    yrs = [int(m.group(1) or m.group(2)) for m in TITLE_YEARS_RE.finditer(p.title)]
    if yrs and min(yrs) >= 2 and not NEWBIE_RE.search(p.title):
        return "경력"
    if re.search(r"신입\s*[Xx×]|신입\s*불가", p.title) or (
            CAREER_ONLY_RE.search(p.title) and not NEWBIE_RE.search(p.title)):
        return "경력"
    if p.source == "링커리어":
        jt = set(p.extra.get("jobTypes", []))
        if jt and jt <= {"EXPERIENCED", "CONTRACT"} and "EXPERIENCED" in jt:
            return "경력"
        return "인턴" if "INTERN" in jt else "신입"
    if lv in ("전체", "무관", "경력무관") or re.search(r"경력\s*무관", lv):
        return "경력무관"
    if "신입" in lv and "경력" in lv:
        return "신입·경력"
    if "신입" in lv:
        return "신입"
    if "인턴" in lv:
        return "인턴"
    if "경력" in lv:
        # 목록엔 '경력'이어도 본문에 '신입 가능'이면 살린다
        return "신입·경력" if re.search(r"신입\s*(가능|지원\s*가능)", text) else "경력"
    head = f"{p.title} {p.listing_text}"
    if re.search(r"신입|인턴|졸업\s*예정|채용연계|채용형", head):
        return "인턴" if "인턴" in head else "신입"
    if CAREER_ONLY_RE.search(p.title):
        return "경력"
    return "신입" if p.extra.get("posted") is not None else "확인 필요"


def _name_hit(name, words):
    return any(re.search(rf"(?<![가-힣A-Za-z]){re.escape(w)}", name) for w in words)


def _group_tag(title):
    """제목 머리의 [GS계열사], [DB월드/DB그룹] 같은 계열 표기 (외국계 표기가 함께면 제외)."""
    if re.search(r"대기업\s*계열", title):
        return True
    for tag in re.findall(r"\[([^\]]+)\]", title):
        parts = [x.strip() for x in tag.split("/")]
        if "외국계" not in parts and any(re.search(r"(?:계열사?|그룹)$", x) for x in parts):
            return True
    return False


def company_groups(p: Posting, text):
    """['대기업 계열', '외국계'] 중 해당하는 것 (둘 다일 수 있음)."""
    name = re.sub(r"\(주\)|㈜|주식회사|\s", "", p.company)
    groups = []
    if (p.company_type == "대기업" or re.search(r"기업\s*(?:구분|형태)\s*대기업", text)
            or _group_tag(p.title) or _name_hit(name, BIG_GROUPS)):
        groups.append("대기업 계열")
    if (p.company_type == "외국계" or re.search(r"기업\s*(?:구분|형태)\s*외국계|외국인\s*투자\s*기업", text)
            or re.search(r"외국계|외투기업", p.title) or _name_hit(name, FOREIGN_NAMES)
            or re.search(r"코리아.*(?:\(유\)|유한)|(?:\(유\)|유한회사).*코리아|(?<![가-힣])(?:Korea|Inc\.?|Ltd\.?|GmbH|LLC)(?![A-Za-z])", p.company)):
        groups.append("외국계")
    return groups


def classify_company(p: Posting, text):
    """행 강조 색: A(데이터센터·하이테크·삼성·하이닉스) > B(대기업 계열) > F(외국계)."""
    p.extra["groups"] = company_groups(p, text)
    if HILITE_A_RE.search(f"{p.company} {p.title} {p.listing_text} {p.extra.get('sector', '')}"):
        return "A"
    if "대기업 계열" in p.extra["groups"]:
        return "B"
    if "외국계" in p.extra["groups"]:
        return "F"
    return ""


def guess_company(title):
    title = re.sub(r"^\s*(?:\[\s*(?:채용|모집|인턴|공채|일반공지)\s*\]\s*)+", "", title)
    title = re.sub(r"^\s*(?:20)?\d{2}\s*년(?:도)?\s*(?:[상하]반기)?\s*", "", title)
    m = re.match(r"^\s*[\[\(【]([^\]\)】]{2,30})[\]\)】]", title)
    if m:
        first = clean(re.split(r"[/,]", m.group(1))[0])
        if not re.search(r"채용|모집|공고|정규|계약|인턴|신입|대외|일반공지", first):
            return first
    m = re.match(r"^\s*((?:\(주\)|㈜|주식회사)?\s*[가-힣A-Za-z&][가-힣A-Za-z0-9&]{1,14}(?:\(주\)|㈜)?)\s", title)
    if m and not re.match(r"제\s*\d", m.group(1).strip()):
        return clean(m.group(1))
    return ""


def analyze(p: Posting, today):
    text = p.detail_text
    detail_fields(p)
    if p.source in ("피플앤잡", "기업 채용 페이지"):
        foreign_level(p)
    if not p.company:
        p.company = guess_company(p.title)
    p.employment = employment_of(p, f"{p.listing_text} {text[:4000]}")
    p.level = level_of(p, text)
    qual = section(text, QUAL_HEAD)
    pref = section(text, PREF_HEAD, 180)
    p.qualification = summarize_qual(qual, text[:6000])
    if p.source == "사람인" and p.extra.get("cond"):
        edu = p.extra["cond"][2] if len(p.extra["cond"]) > 2 else ""
        if edu and "학력" not in p.qualification:
            p.qualification = " / ".join(filter(None, [p.qualification, f"학력: {edu}"]))
    if p.extra.get("edu") and "학력" not in p.qualification:
        p.qualification = " / ".join(filter(None, [re.sub(r"^경력\s*\S+\s*", "", p.qualification), f"학력: {p.extra['edu']}"]))
    if p.source == "워커" and "학력" not in p.qualification:
        edu = p.extra.get("exp_edu", "").split(" ", 1)[-1]
        p.qualification = " / ".join(filter(None, [p.qualification, f"학력: {edu}"]))
    if pref:
        certs = uniq(m.group(0) for m in CERT_RE.finditer(pref))
        p.preferred = (", ".join(certs) + " · " if certs else "") + pref[:110]
    ref = safe_date(*map(int, p.extra["posted"].split("-"))) if p.extra.get("posted") else today
    disp, d = parse_deadline(p.deadline, ref)
    if not disp and p.extra.get("posted") is not None:
        disp, d = parse_deadline(p.title, ref)
    p.deadline = disp or p.deadline or "확인 필요"
    p.deadline_date = d.isoformat() if d else ""
    p.hilite = classify_company(p, text)
    p.extra["listed"] = listed_market(p)
    p.certs = sorted({f"{m.group(1)}안전기사" for m in CERT_KEY_RE.finditer(f"{p.title} {p.listing_text} {text}")})
    if ISO45001_RE.search(f"{p.title} {text}"):
        p.certs.append("ISO 45001")
    blob = f"{p.title} {p.listing_text} {text}"
    p.prefs = [lab for lab, rx in (("외국어·영어", LANG_RE), ("NEBOSH", NEBOSH_RE), ("IOSH", IOSH_RE), ("CSP", CSP_RE)) if rx.search(blob)]
    pref_sec = section(text, PREF_HEAD, 600)
    p.extra["ai"] = bool(AI_RE.search(pref_sec) or AI_NEAR_PREF_RE.search(text))
    rank = top100_rank(p.company)
    p.extra["top100"] = rank
    sector = f"{p.listing_text[:12]} {p.extra.get('biz', '')}"
    mixed = norm_corp(p.company) in MIXED_TOP100  # 건설 외 주력 사업이 있는 시평 100위 업체
    by_name = rank and not mixed or re.search(r"건설\s*부문|건설사업", f"{p.company} {p.title}")
    p.industry = "건설" if (by_name or p.source == "워커" or CONSTR_NAME_RE.search(p.company)
                            or re.search(r"건설·건축|건설업|건축|토목|공사업", sector)) else "일반 산업"


OTHER_TRADE_RE = re.compile(r"공무|시공|공사\s*관리|현장\s*소장|현장\s*대리인|품질|설계|전기|기계|설비|토목|건축|조경|감리|생산|용접|정비|"
                            r"배관|도장|측량|구매|총무|사무|회계|인사|물류|운전|시설\s*관리|CAD", re.I)


def other_trade(p: Posting) -> bool:
    """안전이 아닌 공종·직무를 모집하는 공고인가 (제목 기준, 우대 표기는 제외하고 판단)."""
    title = PREF_IN_TITLE_RE.sub(" ", p.title)
    return bool(OTHER_TRADE_RE.search(title)) and not re.search(r"안전\s*(?:관리|보건|담당|팀|환경)|보건\s*관리|HSE|EHS|SHE", title, re.I)


def relevant(p: Posting):
    """안전 직무 공고인가. True / False / None(상세 본문을 봐야 앎).

    - 제목에 안전·HSE 키워드, 또는 목록에 산업안전기사·건설안전기사가 보이면 True
    - 그룹 공채인데 직무 태그에 안전이 있으면 True
    - HSE·EHS·자격증 검색어로 걸린 공고는 상세 본문에서 자격증/HSE 언급을 확인(None)
    """
    tags = p.extra.get("sector", "") if p.source == "사람인" else p.listing_text
    # 제목의 '(안전관리 우대)' 같은 표기는 안전관리 우대가 명시된 것으로 보고 살린다
    if any(re.search(r"안전\s*관리", m.group(0)) for m in PREF_IN_TITLE_RE.finditer(p.title)):
        return True
    title = PREF_IN_TITLE_RE.sub(" ", p.title)
    if other_trade(p) and not re.search(r"안전|보건|HSE|EHS|EH&S|SHE", title, re.I):
        return None if p.extra.get("query") else False  # 타공종 모집 → 본문의 우대 명시 여부로 판단
    if SAFETY_RE.search(title) or CERT_KEY_RE.search(f"{p.title} {tags}"):
        return True
    if re.search(r"공채|공개\s*채용|신입\s*(사원|직원)", title) and SAFETY_RE.search(tags):
        return True
    if p.extra.get("query"):  # 검색어로 걸렸지만 제목만으로는 모를 때 → 상세 본문 확인
        return None
    return False


def relevant_after_detail(p: Posting) -> bool:
    r = relevant(p)
    if r is not None:
        return r
    t = p.detail_text[:12000]
    if CERT_KEY_RE.search(t) or NEBOSH_RE.search(t) or IOSH_RE.search(t) or INCLUDE_RE.search(t):
        return True
    # '안전관리' 우대가 명시돼 있으면 살린다
    pref = section(t, PREF_HEAD, 400)
    if re.search(r"안전\s*관리", pref) or re.search(r"안전\s*관리[^.\n]{0,30}우대", t):
        return True
    # 타공종을 모집하면서 '안전관리 경험/경력'만 요구하는 공고는 제외 (실제 안전관리 업무 병행은 인정)
    body = re.sub(r"안전\s*관리[^.\n]{0,15}(?:경험|경력)", " ", t) if other_trade(p) else t
    secs = " ".join(section(body, h, 400) for h in (QUAL_HEAD, DUTY_HEAD))
    if SAFETY_DUTY_RE.search(body) or re.search(r"안전\s*관리", secs):
        return True
    # HSE/EHS는 직무·팀 이름으로 쓰였을 때만 (단순 'EHS 규정 준수' 같은 언급은 제외).
    # 타공종 모집 공고에서 회사 EHS팀이 언급된 것만으로는 살리지 않는다
    if other_trade(p):
        return False
    return bool(HSE_ROLE_RE.search(t))


PUBLIC_CORP_RE = re.compile(r"(?:공단|공사|진흥원|기술원|연구원|안전원|재단)(?:\(.*?\))?$")  # 공공기관은 제외하지 않는다


def excluded_corp(p: Posting) -> bool:
    """회사명에 제외 용어(EXCLUDE_CORP_TERMS)가 있는 민간 업체인가. 공공기관은 제외하지 않는다."""
    name = re.sub(r"\s|\(주\)|㈜|주식회사", "", p.company or "")
    if not EXCLUDE_CORP_RE.search(name):
        return False
    return not ("공공" in p.company_type or PUBLIC_CORP_RE.search(name))


def keep(p: Posting, today) -> tuple[bool, str]:
    if excluded_corp(p):
        return False, "제외 업체명"
    blob = f"{p.title} {p.listing_text} {p.extra.get('sector', '')}"
    if p.extra.get("posted") is not None:  # 학과 게시판: 최근 글 + 채용 공고 + 안전 직무
        posted = safe_date(*map(int, p.extra["posted"].split("-"))) if p.extra["posted"] else None
        if posted and (today - posted).days > 75:
            return False, "오래된 게시글"
        if re.search(r"설명회|특강|공모|대외|세미나|박람회|사이트\s*안내|교육생|장학", p.title):
            return False, "채용 공고 아님"
        if not re.search(r"채용|모집|인턴|신입", p.title):
            return False, "채용 공고 아님"
        if not SAFETY_RE.search(f"{blob} {p.detail_text[:8000]}"):
            return False, "안전 직무 아님"
    elif not relevant_after_detail(p):
        return False, "안전 직무 아님"
    if NON_HSE_SAFETY_RE.search(p.title):
        return False, "안전 직무 아님"
    if p.extra.get("need_korea") and not KOREA_LOC_RE.search(p.extra.get("loc", "")):
        return False, "한국 근무 아님"
    if SALES_RE.search(p.title):
        return False, "영업직"
    if WATCH_RE.search(f"{p.title} {p.listing_text} {p.detail_text}"):
        return False, "감시단"
    if p.industry == "건설" and not p.extra.get("top100"):
        return False, "건설사(시평 100위 밖)"
    if p.level == "경력":
        return False, "대리급 이상" if p.extra.get("senior") else "경력직"
    if p.employment == "계약직" and not contract_ok(p):
        return False, "계약직(관심 기업 외)"
    if p.deadline_date and p.deadline_date < today.isoformat():
        return False, "마감"
    return True, ""


def norm_company(c):
    return re.sub(r"\(주\)|㈜|주식회사|\s|\(.*?\)", "", c or "").lower()


def norm_title(t, corp):
    t = re.sub(r"[\[\]\(\)【】<>『』\"'·,.\-_/|:~]|\s|20\d{2}년?|하반기|상반기|채용|모집|공고|안내", "", t or "")
    return t.replace(corp, "") if corp else t


def is_dup(p, kept):
    c, t = norm_company(p.company), norm_title(p.title, norm_company(p.company))
    for q in kept:
        qc = norm_company(q.company)
        if c and qc and (c in qc or qc in c):
            qt = norm_title(q.title, qc)
            if difflib.SequenceMatcher(None, t, qt).ratio() >= 0.6:
                return True
    return False


# ---------------------------------------------------------------- 출력
BADGE = {"A": "🔴 ", "B": "🔵 ", "F": "🌐 ", "": ""}
GROUPS = [("정규직", "[정규직]"), ("계약직", "[계약직]"), ("인턴", "[인턴]"), ("기타/미표기", "[고용형태 미표기]")]
LEGEND = ("🔴 데이터센터·하이테크·삼성·하이닉스 관련 · 🔵 대기업 계열사 · 🌐 외국계 회사 (여럿 해당하면 🔴 > 🔵 > 🌐, 업체명 옆에 [대기업 계열]/[외국계] 표기) · "
          "🟣 외국어·영어 능통 / NEBOSH / IOSH / CSP 우대 (🔴·🔵와 함께 표시될 수 있음) · [코스피]/[코스닥] 상장사 · 🤖 AI 역량 우대")


def md_cell(s):
    return clean(s).replace("|", "\\|") or "-"


def sort_key(p):
    return ({"A": 0, "B": 1, "F": 2}.get(p.hilite, 3), p.deadline_date or "9999")


def deadline_md(p, today):
    """3일 이내 마감은 ⏰·굵게·D-n 으로 표시 (마크다운은 글자색을 못 쓰므로 HTML에서만 붉은색)."""
    if p.deadline_date:
        left = (dt.date.fromisoformat(p.deadline_date) - today).days
        if left <= 3:
            return f"⏰ **{md_cell(p.deadline)} (D-{left})**" if left else f"⏰ **{md_cell(p.deadline)} (오늘 마감)**"
    return md_cell(p.deadline)


def render_md(postings, failures, now, stats):
    L = [f"# 안전관리자 채용 브리핑 — {now:%Y-%m-%d (%a) %H:%M} KST", ""]
    n_gen = sum(p.industry == "일반 산업" for p in postings)
    n_cert = sum(bool(p.certs) for p in postings)
    n_pref = sum(bool(p.prefs) for p in postings)
    L.append(f"신입·경력무관·인턴 공고 **{len(postings)}건** (경력직·마감 제외, 중복은 상위 사이트 우선) · "
             f"일반 산업체 {n_gen}건 · 건설 {len(postings) - n_gen}건 · 산업/건설안전기사·ISO 45001 명시 {n_cert}건 · "
             f"🟣 외국어·NEBOSH·IOSH·CSP 우대 {n_pref}건")
    L += ["", "건설사는 2026년 시공능력평가 상위 100개사(토목건축)만 싣습니다."]
    L += ["", f"범례: {LEGEND} · 🆕 지난 보고({last_report_date(now.date()):%m/%d}) 이후 추가", ""]
    new = sorted([p for p in postings if is_new(p, now.date())], key=sort_key)
    L += [f"## 🆕 신규 공고 {len(new)}건 (지난 보고 {last_report_date(now.date()):%m/%d} 이후)", ""]
    if new:
        L += ["| 업체명 | 공고명 | 고용형태 | 접수기한 | 출처 |", "|---|---|---|---|---|"]
        L += [f"| {BADGE[p.hilite]}{md_cell(p.company)} | {md_cell(p.title)} | {p.employment} | {deadline_md(p, now.date())} | [{p.source}]({p.url}) |" for p in new]
    else:
        L.append("_새로 추가된 공고가 없습니다._")
    L.append("")
    for key, tag in GROUPS:
        rows = sorted([p for p in postings if p.employment == key], key=sort_key)
        if not rows:
            continue
        L += [f"## {tag} {len(rows)}건", ""]
        L.append("| 구분 | 업체명 | 공고명 | 지원 자격 (학과·자격·영어·학력) | 우대 사항 | 접수기한 | 출처 |")
        L.append("|---|---|---|---|---|---|---|")
        for p in rows:
            corp = ("🆕 " if is_new(p, now.date()) else "") + BADGE[p.hilite] + (f"**{md_cell(p.company)}**" if p.hilite else md_cell(p.company))
            corp += "".join(f" [{g}]" for g in p.extra.get("groups", []))
            corp += f" [{p.extra['listed']}]" if p.extra.get("listed") else ""
            if p.industry == "건설" and p.extra.get("top100"):
                corp += f" (시평 {p.extra['top100']}위)"
            cert = f"**[{'·'.join(p.certs)} 명시]** " if p.certs else ""
            cert += f"🟣 **[{'·'.join(p.prefs)} 우대]** " if p.prefs else ""
            cert += "🤖 **[AI 우대]** " if p.extra.get("ai") else ""
            L.append(f"| {md_cell(p.level)} · {md_cell(p.industry)} | {corp} | {md_cell(p.title)} | {cert}{md_cell(p.qualification)} "
                     f"| {md_cell(p.preferred)} | {deadline_md(p, now.date())} | [{p.source}]({p.url}){' (이전 수집)' if p.extra.get('carried') else ''} |")
        L.append("")
    L += ["---", "", "**사이트별 수집 현황**", ""]
    for name, st in stats.items():
        L.append(f"- {name}: {st}")
    if failures:
        L += ["", "**수집 실패**", ""] + [f"- {n}: {e}" for n, e in failures]
    if CAREER_STATUS:
        L += ["", "**기업 채용 페이지**", "", "| 기업 | 결과 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in CAREER_STATUS.items()]
    L += ["", "_지원 자격·우대 사항은 상세 페이지에서 자동 추출한 요약입니다. 지원 전 원문을 확인하세요._"]
    return "\n".join(L) + "\n"


HTML_CSS = """
/* 레이아웃: sticky 헤더 + 좌측 섹션 내비(데스크톱) + 콘텐츠 캔버스(KPI → 차트 → 흐름도 → 필터 → 표) */
:root{
  --primary:#0F6FFF; --primary-hover:#0E65E8; --primary-active:#0B4FB5;
  --bg-page:#FFFFFF; --canvas:#EEF1F5; --surface:#FFFFFF; --alt1:#F2F3F6; --alt2:#E2E4E9;
  --text-strong:#000000; --text:#1C1C1C; --text-sub:#303030; --caption:#737373;
  --border:#E2E4E9; --border-strong:#CCD0D6; --divider:#E9EBEF;
  --success:#15B874; --warning:#FFA833; --error:#E63B3B; --purple:#B357FF; --sky:#00BDDE; --orange:#FE6F3F;
  --r-sm:8px; --r-md:12px; --r-lg:16px; --r-pill:9999px;
  --sh1:0 1px 3px rgba(0,0,0,.06);
  --font:"Pretendard Variable","Pretendard","Apple SD Gothic Neo","Noto Sans KR","Segoe UI",Roboto,-apple-system,sans-serif;
  --mono:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --primary:#3F8CFF; --primary-hover:#0F6FFF; --primary-active:#0E65E8;
  --bg-page:#1D1F24; --canvas:#15171C; --surface:#1D1F24; --alt1:#282B33; --alt2:#333741;
  --text-strong:#FFFFFF; --text:#EBECED; --text-sub:#C4C4C4; --caption:#8A8A8A;
  --border:#333741; --border-strong:#4A505F; --divider:#282B33;
  --success:#44C690; --warning:#FFB95C; --error:#EB5E5E; --purple:#C279FF; --sky:#33CAE5; --orange:#FE8C65; color-scheme:dark}}
:root[data-theme="dark"]{
  --primary:#3F8CFF; --primary-hover:#0F6FFF; --primary-active:#0E65E8;
  --bg-page:#1D1F24; --canvas:#15171C; --surface:#1D1F24; --alt1:#282B33; --alt2:#333741;
  --text-strong:#FFFFFF; --text:#EBECED; --text-sub:#C4C4C4; --caption:#8A8A8A;
  --border:#333741; --border-strong:#4A505F; --divider:#282B33;
  --success:#44C690; --warning:#FFB95C; --error:#EB5E5E; --purple:#C279FF; --sky:#33CAE5; --orange:#FE8C65; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--canvas);color:var(--text);font:400 14px/1.55 var(--font);margin:0}
.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg-page);border-bottom:1px solid var(--border);
  display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;padding:12px 20px}
.top h1{font-size:18px;font-weight:700;margin:0;color:var(--text-strong)}
.top .when{font-size:12px;color:var(--caption);font-variant-numeric:tabular-nums}
.top .chip{margin-left:auto}
.edit-bar{display:flex;align-items:center;gap:6px}
.edit-bar button{height:32px;padding:0 12px;border:1px solid var(--border-strong);border-radius:var(--r-sm);background:var(--surface);color:var(--text-sub);font:600 13px var(--font);cursor:pointer}
.edit-bar button:hover{background:var(--alt1)} .edit-bar button[aria-pressed="true"]{background:var(--primary);border-color:var(--primary);color:#FFFFFF}
.edit-bar #edit-msg{font-size:12px;color:var(--caption)}
.icon-btn{width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;border:0;background:none;color:var(--text-sub);border-radius:var(--r-sm);cursor:pointer}
.icon-btn:hover{background:var(--alt1);color:var(--text-strong)}
.edit-bar .icon-btn{width:40px;height:40px;padding:0;border:0;background:none}
body.editing main [contenteditable="true"]{outline:1px dashed var(--border-strong);outline-offset:2px;cursor:text}
body.editing main [contenteditable="true"]:focus{outline:2px solid var(--primary)}
.shell{display:grid;grid-template-columns:220px minmax(0,1fr);min-height:100%}
.side{background:var(--bg-page);border-right:1px solid var(--border);padding:12px 0;position:sticky;top:57px;align-self:start;height:calc(100vh - 57px);overflow:auto}
.side .sec{font-size:12px;font-weight:600;color:var(--caption);padding:12px 20px 4px;letter-spacing:.02em}
.side a{display:flex;align-items:center;justify-content:space-between;height:44px;padding:0 20px;color:var(--text-sub);text-decoration:none;font-size:14px}
.side a:hover{background:var(--alt1)} .side a b{font-weight:600;font-variant-numeric:tabular-nums;color:var(--caption)}
.side a:focus-visible,.chipnav a:focus-visible,button:focus-visible,input:focus-visible{outline:2px solid var(--primary);outline-offset:2px}
.chipnav{display:none;gap:8px;overflow-x:auto;padding-bottom:4px}
.chipnav a{flex:none;padding:6px 12px;border:1px solid var(--border);border-radius:var(--r-pill);background:var(--surface);color:var(--text-sub);text-decoration:none;font-size:13px}
main{padding:20px;display:grid;gap:16px;min-width:0;max-width:1400px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:16px;min-width:0}
.card h2{font-size:18px;font-weight:700;margin:0 0 12px;color:var(--text-strong);text-wrap:balance}
.card h2 .n{font-size:14px;font-weight:600;color:var(--caption);margin-left:6px}
.kpis{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:14px 16px;display:grid;gap:2px}
.kpi .l{font-size:12px;font-weight:600;color:var(--caption)}
.kpi .v{font-size:32px;font-weight:700;color:var(--text-strong);font-variant-numeric:tabular-nums;line-height:1.2}
.kpi .s{font-size:12px;color:var(--caption)}
.kpi .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:1px}
.charts{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr))}
.bars{display:grid;gap:8px}
.bar{display:grid;grid-template-columns:minmax(84px,32%) minmax(0,1fr) 36px;align-items:center;gap:8px;font-size:13px}
.bar .k{color:var(--text-sub);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .t{display:block;height:14px;background:var(--alt1);border-radius:4px;overflow:hidden}
.bar .f{display:block;height:100%;background:var(--primary);border-radius:0 4px 4px 0;min-width:2px}
.bar .f.warn{background:var(--error)} .bar .f.pp{background:var(--purple)} .bar .f.none{background:var(--border-strong)}
.bar .v{text-align:right;font-variant-numeric:tabular-nums;font-weight:600;color:var(--text)}
.bar:hover .k{color:var(--text-strong)}
.flow{display:flex;flex-wrap:nowrap;align-items:stretch;gap:8px;overflow-x:auto;padding-bottom:2px}
.step{flex:1 0 104px;border:1px solid var(--border);border-radius:var(--r-sm);padding:10px 12px;background:var(--alt1);display:grid;gap:2px}
.step .l{font-size:12px;font-weight:600;color:var(--caption)} .step .v{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums;color:var(--text-strong)}
.step.minus .v{color:var(--text-sub)} .step.final{background:var(--surface);border-color:var(--primary)} .step.final .v{color:var(--primary)}
.arrow{display:flex;align-items:center;color:var(--border-strong)}
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.tools input{flex:1 1 220px;min-width:0;height:40px;border:1px solid var(--border-strong);border-radius:var(--r-sm);padding:0 12px;background:var(--surface);color:var(--text);font:inherit}
.seg{display:flex;flex-wrap:wrap;gap:6px}
.seg button{height:40px;padding:0 14px;border:1px solid var(--border-strong);border-radius:var(--r-sm);background:var(--surface);color:var(--text-sub);font:600 13px var(--font);cursor:pointer}
.seg button:hover{background:var(--alt1)}
.seg button[aria-pressed="true"]{background:var(--primary);border-color:var(--primary);color:#FFFFFF}
.scroll{overflow-x:auto;border:1px solid var(--border);border-radius:var(--r-sm)}
table{border-collapse:collapse;width:100%;min-width:1000px}
th,td{padding:10px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--divider)}
th{font-size:12px;font-weight:600;color:var(--caption);background:var(--alt1);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td{min-height:52px} td.lv{white-space:nowrap;color:var(--text-sub)} td.lv small{display:block;font-size:12px;color:var(--caption)} td.corp{min-width:150px} td.corp strong{display:block;font-weight:600;color:var(--text-strong)}
td.dl{white-space:nowrap;font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:13px}
td.dl.soon{color:var(--error);font-weight:700}
td.dl.soon::after{content:"임박";display:inline-block;margin-left:6px;padding:0 6px;border-radius:var(--r-pill);font:600 11px var(--font);
  background:color-mix(in srgb,var(--error) 14%,transparent);color:var(--error)}
tr.hA{background:color-mix(in srgb,var(--error) 8%,var(--surface))}
tr.hB{background:color-mix(in srgb,var(--primary) 7%,var(--surface))}
tr.hF{background:color-mix(in srgb,var(--sky) 9%,var(--surface))}
.pill{display:inline-flex;align-items:center;gap:4px;margin-top:4px;font-size:11px;font-weight:600;padding:1px 8px;border-radius:var(--r-pill);border:1px solid var(--border-strong);color:var(--text-sub)}
.pill::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.pill.pa::before{background:var(--error)} .pill.pb::before{background:var(--primary)} .pill.pf::before{background:var(--sky)} .pill.pk{border-color:var(--text-sub);color:var(--text-strong)} .pill.pk::before{background:var(--text-strong);border-radius:2px} .pill.pc{margin:0 0 4px}.pill.pc::before{background:var(--success)}
.pill.pp{margin:4px 4px 0 0;border-color:var(--purple);background:color-mix(in srgb,var(--purple) 12%,transparent);color:var(--text-strong)}.pill.pp::before{background:var(--purple)}
td.ttl .prefs{display:flex;flex-wrap:wrap}
.pill.ok::before{background:var(--success)} .pill.bad::before{background:var(--error)} .pill.keep::before{background:var(--warning)}
a{color:var(--primary)} a:hover{color:var(--primary-hover)}
td.src{white-space:nowrap}
.src small{display:block;color:var(--caption)}
.empty{color:var(--caption);font-size:13px;padding:8px 0}
.note{font-size:12px;color:var(--caption);margin:0}
[hidden]{display:none!important}
/* 채용 달력: 주 단위 7열 그리드, 좁은 화면에서는 공고 있는 날짜만 목록으로 */
.cal-head{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:8px;margin-bottom:12px}
.cal-head h2{margin:0} .cal-head .range{font-size:12px;color:var(--caption);font-variant-numeric:tabular-nums}
.cal-legend{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;color:var(--caption);margin-bottom:8px}
.cal-legend span::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px;vertical-align:0;background:var(--border-strong)}
.cal-legend .tgl{font-style:normal;display:inline-flex;align-items:center;gap:4px}
.cal-legend .tgl .tg{font-style:normal;font-size:10px;font-weight:600;padding:0 4px;border-radius:4px;border:1px solid currentColor}
.cal-legend .tgl .tg.b{color:var(--primary)} .cal-legend .tgl .tg.f{color:var(--sky)} .cal-legend .tgl .tg.k{color:var(--text-sub)}
.cal-legend .la::before{background:var(--error)} .cal-legend .lb::before{background:var(--primary)} .cal-legend .lf::before{background:var(--sky)} .cal-legend .lp::before{background:var(--purple)}
.cal{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));border-top:1px solid var(--border);border-left:1px solid var(--border)}
.cal .wd{font-size:12px;font-weight:600;color:var(--caption);padding:6px 8px;background:var(--alt1);border-right:1px solid var(--border);border-bottom:1px solid var(--border)}
.cal .wd.sun{color:var(--error)}
.day{min-height:96px;padding:6px;border-right:1px solid var(--border);border-bottom:1px solid var(--border);display:grid;align-content:start;gap:3px;min-width:0}
.day .dn{font-size:12px;font-weight:600;color:var(--text-sub);font-variant-numeric:tabular-nums;display:flex;justify-content:space-between;gap:4px}
.day .dn .mo{color:var(--primary)} .day .dn .cnt{color:var(--caption);font-weight:600}
.day.out{background:var(--alt1)} .day.out .dn{color:var(--caption);opacity:.6}
.day.today{box-shadow:inset 0 0 0 2px var(--primary)} .day.soon .dn{color:var(--error)}
.day.sun .dn{color:var(--error)}
.ev{display:flex;align-items:center;gap:4px;font-size:12px;line-height:1.35;color:var(--text);text-decoration:none;min-width:0;border-radius:4px;padding:1px 2px}
.ev:hover{background:var(--alt1);color:var(--primary)} .ev:focus-visible{outline:2px solid var(--primary);outline-offset:1px}
.ev::before{content:"";flex:none;width:6px;height:6px;border-radius:50%;background:var(--border-strong)}
.ev.hA::before{background:var(--error)} .ev.hB::before{background:var(--primary)} .ev.hF::before{background:var(--sky)} .ev.pp::before{background:var(--purple)}
.ev span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.ev .tg{flex:none;font-style:normal;font-size:10px;font-weight:600;line-height:1.4;padding:0 4px;border-radius:4px;border:1px solid currentColor}
.ev .tg.b{color:var(--primary)} .ev .tg.f{color:var(--sky)} .ev .tg.k{color:var(--text-sub)} .ev .tg.ai{color:var(--orange)}
.pill.pn{border-color:var(--success);background:color-mix(in srgb,var(--success) 14%,transparent);color:var(--text-strong)} .pill.pn::before{background:var(--success)}
.ev .tg.n,.cal-legend .tgl .tg.n{color:var(--success)}
.pill.pai{margin:4px 4px 0 0;border-color:var(--orange);background:color-mix(in srgb,var(--orange) 12%,transparent);color:var(--text-strong)} .pill.pai::before{background:var(--orange)}
.cal-legend .tgl .tg.ai{color:var(--orange)}
.day details summary{font-size:12px;color:var(--primary);cursor:pointer;list-style:none} .day details summary::-webkit-details-marker{display:none}
.day details[open] summary{margin-bottom:2px}
td.corp a.co{color:var(--text-strong);text-decoration:none} td.corp a.co:hover{color:var(--primary);text-decoration:underline}
@media (max-width:719px){
  .cal{display:block;border:0}.cal .wd,.day.empty,.day.out{display:none}
  .day{min-height:0;border:1px solid var(--border);border-radius:var(--r-sm);margin-bottom:8px;padding:10px}
  .day .dn .wdn{display:inline} .day .dn .mo{display:none}}
@media (min-width:720px){.day .dn .wdn,.day .dn .mo2{display:none}}
@media (max-width:1023px){.shell{grid-template-columns:1fr}.side{display:none}.chipnav{display:flex}}
@media (max-width:480px){main{padding:16px}.kpi .v{font-size:28px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""

HTML_JS = """
(function(){
  /* 테마 전환: 다크 토큰을 직접 쓰는 data-theme 전환, 선택은 이 브라우저에만 기억 */
  var b=document.getElementById('theme-toggle'), r=document.documentElement; if(!b) return;
  try{var t=localStorage.getItem('brief-theme'); if(t) r.dataset.theme=t;}catch(e){}
  b.addEventListener('click',function(){
    var dark=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
    r.dataset.theme=dark?'light':'dark'; b.setAttribute('aria-pressed',String(!dark));
    try{localStorage.setItem('brief-theme',r.dataset.theme)}catch(e){}
  });
})();
(function(){
  /* 편집: 표·제목·메모 텍스트를 직접 고치고, 이 브라우저에 저장 (같은 날 브리핑에만 적용) */
  var bar=document.querySelector('.edit-bar'); if(!bar) return;
  var key=bar.dataset.key, main=document.querySelector('main');
  var tgl=document.getElementById('edit-toggle'), sv=document.getElementById('edit-save'),
      rs=document.getElementById('edit-reset'), msg=document.getElementById('edit-msg');
  var SEL='main h2, main td, main .note, main .kpi .l, main .kpi .s, main .step .l';
  function store(){try{return window.localStorage}catch(e){return null}}
  function say(t){msg.textContent=t; if(t) setTimeout(function(){msg.textContent=''},2500)}
  try{var st=store(), saved=st&&st.getItem(key); if(saved){main.innerHTML=saved; rs.hidden=false; say('저장된 편집본을 불러왔습니다')}}catch(e){}
  function setEdit(on){
    document.body.classList.toggle('editing',on); tgl.setAttribute('aria-pressed',String(on));
    tgl.textContent=on?'편집 끝내기':'편집'; sv.hidden=!on;
    document.querySelectorAll(SEL).forEach(function(el){ if(on) el.setAttribute('contenteditable','true'); else el.removeAttribute('contenteditable'); });
  }
  tgl.addEventListener('click',function(){setEdit(tgl.getAttribute('aria-pressed')!=='true')});
  main.addEventListener('click',function(ev){ if(document.body.classList.contains('editing')&&ev.target.closest('a')) ev.preventDefault(); });
  sv.addEventListener('click',function(){
    setEdit(false); var st=store();
    try{ st.setItem(key,main.innerHTML); rs.hidden=false; say('이 브라우저에 저장했습니다'); }
    catch(e){ say('이 환경에서는 저장할 수 없습니다. 파일 편집본(latest_edit.html)을 사용하세요'); }
    setEdit(true);
  });
  rs.addEventListener('click',function(){ try{store().removeItem(key)}catch(e){} location.reload(); });
})();
(function(){
  var q=document.getElementById('q'), mode='all';
  var btns=document.querySelectorAll('.seg button');
  function apply(){
    var t=(q.value||'').trim().toLowerCase();
    document.querySelectorAll('section.grp').forEach(function(sec){
      var n=0;
      sec.querySelectorAll('tbody tr').forEach(function(tr){
        var ok=(!t||tr.textContent.toLowerCase().indexOf(t)>=0)&&
          (mode==='all'||(mode==='A'&&tr.classList.contains('hA'))||(mode==='B'&&tr.dataset.grp.indexOf('대기업')>=0)||(mode==='F'&&tr.dataset.grp.indexOf('외국계')>=0)||(mode==='K'&&tr.dataset.listed!=='')||
           (mode==='soon'&&tr.querySelector('td.dl.soon'))||(mode==='gen'&&tr.dataset.ind==='일반 산업')||
           (mode==='cert'&&tr.dataset.cert==='1')||(mode==='pref'&&tr.dataset.pref==='1')||(mode==='ai'&&tr.dataset.ai==='1')||(mode==='new'&&tr.dataset.new==='1'));
        tr.hidden=!ok; if(ok)n++;
      });
      sec.querySelector('.n').textContent=n+'건';
      sec.querySelector('.empty').hidden=n>0; sec.querySelector('.scroll').hidden=n===0;
    });
  }
  q.addEventListener('input',apply);
  btns.forEach(function(b){b.addEventListener('click',function(){
    mode=b.dataset.mode; btns.forEach(function(x){x.setAttribute('aria-pressed',String(x===b))}); apply();});});
})();
"""


def parse_stat(v):
    """'목록 35, 채택 34, 경력직 1' → {'목록': 35, ...}"""
    return {k.strip(): int(n) for k, n in re.findall(r"([^,\d]+?)\s(\d+)(?=,|$)", v or "")}


SEMI_DC_RE = re.compile(r"반도체|하이닉스|(?<![A-Za-z])FAB(?![A-Za-z])|웨이퍼|데이터\s*센터|(?<![A-Za-z])IDC(?![A-Za-z])|클린룸", re.I)
SEMI_DC_TITLE_RE = re.compile(r"삼성(?!동)|하이테크")  # 제목·업체명에서만 (본문의 '삼성동' 주소 등 오인 방지)


def calendar_eligible(p):
    """관심 기업: 대기업 계열·외국계·코스피/코스닥 상장·데이터센터/반도체 관련.
    달력에는 이 공고만 싣고, 계약직은 이 조건일 때만 브리핑에 남긴다."""
    if p.extra.get("groups") or p.extra.get("listed") or p.hilite == "A":
        return True
    if SEMI_DC_TITLE_RE.search(f"{p.company} {p.title}"):
        return True
    return bool(SEMI_DC_RE.search(f"{p.company} {p.title} {p.listing_text} {p.extra.get('sector', '')} {(p.detail_text or '')[:4000]}"))


CONTRACT_TOP_RANK = 15  # 계약직 건설사는 시공능력평가(도급순위) 15위 이내도 인정


def contract_ok(p):
    """계약직 유지 조건: 관심 기업이거나, 도급순위 15위 이내 건설사."""
    rank = p.extra.get("top100")
    return calendar_eligible(p) or (p.industry == "건설" and bool(rank) and rank <= CONTRACT_TOP_RANK)


def render_calendar(postings, today, months=2, show=5):
    """접수기한 달력: 오늘부터 2개월, 주 단위. 업체명을 누르면 공고로 이동."""
    e = html.escape
    end_m, end_y = today.month + months, today.year
    while end_m > 12:
        end_m, end_y = end_m - 12, end_y + 1
    end = safe_date(end_y, end_m, min(today.day, 28)) or today + dt.timedelta(days=61)
    by_day = collections.defaultdict(list)
    for p in postings:
        if p.deadline_date and calendar_eligible(p):
            d = dt.date.fromisoformat(p.deadline_date)
            if today <= d <= end:
                by_day[d].append(p)
    start = today - dt.timedelta(days=(today.weekday() + 1) % 7)  # 일요일 시작
    last = end + dt.timedelta(days=(5 - end.weekday()) % 7)        # 토요일 끝
    wd = "".join(f'<div class="wd{" sun" if i == 0 else ""}">{w}</div>' for i, w in enumerate("일월화수목금토"))
    cells = []
    d = start
    while d <= last:
        items = sorted(by_day.get(d, []), key=lambda p: ({"A": 0, "B": 1, "F": 2}.get(p.hilite, 3 if not p.prefs else 2.5), p.company))
        cls = ["day"]
        if d < today or d > end:
            cls.append("out")
        if not items:
            cls.append("empty")
        if d == today:
            cls.append("today")
        if items and (d - today).days <= 3:
            cls.append("soon")
        if d.weekday() == 6:
            cls.append("sun")

        def ev(p):
            c = f"ev h{p.hilite}" + (" pp" if p.prefs and not p.hilite else "")
            tip = f"{p.company} · {p.title} · {p.deadline}"
            grp = p.extra.get("groups", [])
            tags = ('<i class="tg b" title="대기업 계열">대</i>' if "대기업 계열" in grp else "") + \
                   ('<i class="tg f" title="외국계">외</i>' if "외국계" in grp else "")
            if p.extra.get("listed"):
                ab = {"코스피": "KS", "코스닥": "KQ"}.get(p.extra["listed"], p.extra["listed"])
                tags += f'<i class="tg k" title="{e(p.extra["listed"])} 상장">{ab}</i>'
            if p.extra.get("ai"):
                tags += '<i class="tg ai" title="AI 우대">AI</i>'
            if is_new(p, today):
                tags += '<i class="tg n" title="지난 보고 이후 신규">N</i>'
            return (f'<a class="{c}" href="{e(p.url)}" target="_blank" rel="noopener" title="{e(tip)}">'
                    f'<span>{e(p.company or p.title)}</span>{tags}</a>')
        body = "".join(ev(p) for p in items[:show])
        if len(items) > show:
            body += f'<details><summary>+{len(items) - show}건 더 보기</summary>{"".join(ev(p) for p in items[show:])}</details>'
        mo = f'<span class="mo">{d.month}월</span> ' if d.day == 1 or d == start else ""
        wdn = f' <span class="wdn">({"월화수목금토일"[d.weekday()]})</span>'
        cnt = f'<span class="cnt">{len(items)}건</span>' if items else ""
        mo2 = f'<span class="mo2">{d.month}월 </span>'
        cells.append(f'<div class="{" ".join(cls)}"><div class="dn"><span>{mo}{mo2}{d.day}일{wdn}</span>{cnt}</div>{body}</div>')
        d += dt.timedelta(days=1)
    n = sum(len(v) for v in by_day.values())
    return (f'<section class="card" id="calendar"><div class="cal-head"><h2>채용 달력<span class="n">{n}건</span></h2>'
            f'<span class="range">{today:%Y-%m-%d} ~ {end:%Y-%m-%d} 접수 마감 · 대기업 계열·외국계·코스피/코스닥 상장·데이터센터/반도체 관련만</span></div>'
            '<div class="cal-legend"><span class="la">데이터센터·하이테크·삼성·하이닉스</span><span class="lb">대기업 계열</span><span class="lf">외국계</span>'
            '<span class="lp">외국어·NEBOSH·IOSH·CSP 우대</span><span>상장사·반도체 관련</span>'
            '<em class="tgl"><i class="tg b">대</i> 대기업 계열 <i class="tg f">외</i> 외국계 '
            '<i class="tg k">KS</i> 코스피 <i class="tg k">KQ</i> 코스닥 <i class="tg ai">AI</i> AI 우대 <i class="tg n">N</i> 신규</em></div>'
            f'<div class="cal">{wd}{"".join(cells)}</div></section>')


def new_pill(p, today):
    return '<span class="pill pn">신규</span>' if is_new(p, today) else ""


def group_pills(p):
    cls = {"대기업 계열": "pb", "외국계": "pf"}
    out = "".join(f'<span class="pill {cls[g]}">{g}</span>' for g in p.extra.get("groups", []))
    if p.extra.get("listed"):
        out += f'<span class="pill pk">{p.extra["listed"]} 상장</span>'
    return out


def rank_pill(p):
    r = p.extra.get("top100")
    return f'<span class="pill">시평 {r}위</span>' if p.industry == "건설" and r else ""


def ai_pill(p):
    return '<span class="pill pai">AI 우대</span>' if p.extra.get("ai") else ""


def pref_pills(p):
    if not p.prefs:
        return ""
    return '<span class="prefs">' + "".join(f'<span class="pill pp">{html.escape(x)} 우대</span>' for x in p.prefs) + "</span>"


def cert_pills(p):
    return "".join(f'<span class="pill pc">{html.escape(c)} 명시</span> ' for c in p.certs)


def render_html(postings, failures, now, stats):
    e = html.escape
    today = now.date()

    def days_left(p):
        return (dt.date.fromisoformat(p.deadline_date) - today).days if p.deadline_date else None

    soon = {id(p) for p in postings if days_left(p) is not None and days_left(p) <= 3}
    groups = [(key, tag, sorted([p for p in postings if p.employment == key], key=sort_key)) for key, tag in GROUPS]
    groups = [g for g in groups if g[2]]
    sid = {"정규직": "regular", "계약직": "contract", "인턴": "intern"}
    n_a = sum(p.hilite == "A" for p in postings)
    n_b = sum("대기업 계열" in p.extra.get("groups", []) for p in postings)
    n_f = sum("외국계" in p.extra.get("groups", []) for p in postings)
    n_ks = sum(p.extra.get("listed") == "코스피" for p in postings)
    n_kq = sum(p.extra.get("listed") == "코스닥" for p in postings)
    new_rows = sorted([p for p in postings if is_new(p, today)], key=sort_key)
    n_new = len(new_rows)
    failed = {n for n, _ in failures}
    ok_sites = len(SOURCES) - len(failed)

    # KPI 타일 (전체 공고는 직전 브리핑 대비 변화량)
    if PREV_TOTAL is None:
        delta_txt = "경력직·마감 제외"
    else:
        dv = len(postings) - PREV_TOTAL
        delta_txt = f"직전 대비 {'▲' if dv > 0 else '▼' if dv < 0 else '–'}{abs(dv) if dv else ''} (경력직·마감 제외)"
    def kpi(label, value, sub="", dot=""):
        d = f'<span class="dot" style="background:var({dot})"></span>' if dot else ""
        return f'<div class="kpi"><span class="l">{d}{e(label)}</span><span class="v">{value}</span><span class="s">{e(sub)}</span></div>'
    by = {k: len(r) for k, _, r in groups}
    kpis = "".join([
        kpi("전체 공고", len(postings), delta_txt),
        kpi("신규", n_new, f"지난 보고({last_report_date(today):%m/%d}) 이후 추가", "--success"),
        kpi("정규직", by.get("정규직", 0), f"{by.get('정규직', 0) * 100 // max(len(postings), 1)}%"),
        kpi("계약직", by.get("계약직", 0), f"{by.get('계약직', 0) * 100 // max(len(postings), 1)}%"),
        kpi("일반 산업체", sum(p.industry == "일반 산업" for p in postings), "건설 외 제조·서비스 등"),
        kpi("산업·건설안전기사·ISO 45001 명시", sum(bool(p.certs) for p in postings), "공고에 자격·인증 기재"),
        kpi("외국어·NEBOSH·IOSH·CSP 우대", sum(bool(p.prefs) for p in postings), "우대 조건 기재", "--purple"),
        kpi("AI 우대", sum(bool(p.extra.get("ai")) for p in postings), "우대 조건에 AI 역량", "--orange"),
        kpi("3일 내 마감", len(soon), "접수 서두름", "--error"),
        kpi("데이터센터·하이테크·삼성·하이닉스", n_a, "집중 관심", "--error"),
        kpi("대기업 계열", n_b, "그룹 계열사", "--primary"),
        kpi("외국계", n_f, "외국계 기업", "--sky"),
        kpi("외국계 채널", sum(p.source in ("피플앤잡", "기업 채용 페이지") for p in postings), "피플앤잡·기업 채용 페이지", "--sky"),
        kpi("코스피·코스닥 상장", n_ks + n_kq, f"코스피 {n_ks} · 코스닥 {n_kq}", "--text-strong"),
    ])

    # 막대 차트(단일 계열, primary 한 색)
    def bars(items, cls=lambda k: ""):
        mx = max([v for _, v in items] + [1])
        return '<div class="bars">' + "".join(
            f'<div class="bar" title="{e(k)}: {v}건"><span class="k">{e(k)}</span>'
            f'<span class="t"><span class="f {cls(k)}" style="width:{v * 100 / mx:.1f}%"></span></span><span class="v">{v}</span></div>'
            for k, v in items) + "</div>"
    by_src = collections.Counter(p.source for p in postings)
    src_items = [(n.replace(" 안전공학과", ""), by_src.get(n, 0)) for n, _, _ in SOURCES]
    buckets = [("3일 이내", 0, 3), ("4–7일", 4, 7), ("8–14일", 8, 14), ("15–30일", 15, 30), ("31일 이상", 31, 10**6)]
    dl_items = [(lab, sum(1 for p in postings if days_left(p) is not None and lo <= days_left(p) <= hi)) for lab, lo, hi in buckets]
    dl_items.append(("채용 시·미확인", sum(1 for p in postings if days_left(p) is None)))
    lv = collections.Counter(p.level for p in postings)
    lv_items = [(k, lv.get(k, 0)) for k in ("신입", "신입·경력", "경력무관", "인턴") if lv.get(k)]
    pref_items = [(x + " 우대", sum(x in p.prefs for p in postings)) for x in ("외국어·영어", "NEBOSH", "IOSH", "CSP")]
    ind_items = [("일반 산업", sum(p.industry == "일반 산업" for p in postings)),
                 ("건설", sum(p.industry == "건설" for p in postings)),
                 ("산업안전기사 명시", sum("산업안전기사" in p.certs for p in postings)),
                 ("건설안전기사 명시", sum("건설안전기사" in p.certs for p in postings)),
                 ("ISO 45001 명시", sum("ISO 45001" in p.certs for p in postings))]
    charts = (
        f'<div class="card"><h2>사이트별 채택 공고</h2>{bars(src_items)}</div>'
        f'<div class="card"><h2>접수기한까지 남은 기간</h2>'
        f'{bars(dl_items, lambda k: "warn" if k == "3일 이내" else "none" if k.startswith("채용") else "")}</div>'
        f'<div class="card"><h2>경력 구분</h2>{bars(lv_items)}</div>'
        f'<div class="card"><h2>업종 · 자격증 명시</h2>{bars(ind_items)}</div>'
        f'<div class="card"><h2>외국어 · NEBOSH · IOSH · CSP 우대</h2>{bars(pref_items, lambda k: "pp")}</div>')

    # 수집 → 채택 흐름도
    agg = collections.Counter()
    for n, v in stats.items():
        agg.update(parse_stat(v))
    total = agg.get("목록", 0)
    steps = [("수집 목록", total, "")]
    for lab, keys in (("안전 직무 외", ["안전 직무 아님", "채용 공고 아님"]), ("경력직·대리급 이상", ["경력직", "대리급 이상"]),
                      ("대상 기준 외", ["건설사(시평 100위 밖)", "계약직(관심 기업 외)", "영업직", "감시단", "한국 근무 아님"]),
                      ("마감·오래된 글", ["마감", "오래된 게시글"]), ("중복", ["중복(상위 사이트 우선)"])):
        c = sum(agg.get(k, 0) for k in keys)
        if c:
            steps.append((lab, f"−{c}", "minus"))
    n_carried = sum(1 for p in postings if p.extra.get("carried"))
    if n_carried:
        steps.append(("이전 수집 유지", f"+{n_carried}", "minus"))
    steps.append(("브리핑 채택", len(postings), "final"))
    arrow = '<span class="arrow" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>'
    flow = arrow.join(f'<div class="step {c}"><span class="l">{e(l)}</span><span class="v">{v}</span></div>' for l, v, c in steps)

    # 공고 표
    pill = {"A": '<span class="pill pa">데이터센터·하이테크·삼성·하이닉스</span>', "B": "", "F": "", "": ""}
    secs, nav = [], []
    for key, tag, rows in groups:
        i = sid.get(key, "other")
        nav.append((i, tag, len(rows)))
        trs = "".join(
            f'<tr class="h{p.hilite}" data-ind="{e(p.industry)}" data-cert="{1 if p.certs else 0}" data-pref="{1 if p.prefs else 0}" data-ai="{1 if p.extra.get("ai") else 0}" data-grp="{e(" ".join(p.extra.get("groups", [])))}" data-listed="{e(p.extra.get("listed", ""))}" data-new="{1 if is_new(p, today) else 0}"><td class="lv">{e(p.level)}<small>{e(p.industry)}</small></td>'
            f'<td class="corp"><strong><a class="co" href="{e(p.url)}" target="_blank" rel="noopener">{e(p.company or "-")}</a></strong>{new_pill(p, today)}{pill[p.hilite]}{group_pills(p)}{rank_pill(p)}</td>'
            f"<td class=\"ttl\">{e(p.title)}{pref_pills(p)}{ai_pill(p)}</td><td>{cert_pills(p)}{e(p.qualification or '-')}</td><td>{e(p.preferred or '-')}</td>"
            f'<td class="dl{" soon" if id(p) in soon else ""}">{e(p.deadline)}</td>'
            f'<td class="src"><a href="{e(p.url)}" target="_blank" rel="noopener">{e(p.source)}</a>'
            f'{"<small>이전 수집</small>" if p.extra.get("carried") else ""}</td></tr>'
            for p in rows)
        secs.append(
            f'<section class="card grp" id="{i}"><h2>{e(tag)}<span class="n">{len(rows)}건</span></h2>'
            '<p class="empty" hidden>조건에 맞는 공고가 없습니다.</p>'
            '<div class="scroll"><table><thead><tr><th>구분</th><th>업체명</th><th>공고명</th>'
            "<th>지원 자격 (학과·자격·영어·학력)</th><th>우대 사항</th><th>접수기한</th><th>출처</th></tr></thead>"
            f"<tbody>{trs}</tbody></table></div></section>")

    # 수집 현황 표
    srows = []
    for n, _, _ in SOURCES:
        v = stats.get(n, "")
        d = parse_stat(v)
        if n in failed and "유지" in v:
            st = '<span class="pill keep">실패 · 직전 공고 유지</span>'
        elif n in failed:
            st = '<span class="pill bad">수집 실패</span>'
        else:
            st = '<span class="pill ok">정상</span>'
        why = ", ".join(f"{k} {c}" for k, c in d.items() if k not in ("목록", "채택")) or "-"
        err = next((x.splitlines()[0] for m, x in failures if m == n), "")
        srows.append(f"<tr><td>{e(n)}</td><td>{st}</td><td class='dl'>{d.get('목록', '-')}</td>"
                     f"<td class='dl'>{d.get('채택', by_src.get(n, 0))}</td><td>{e(why)}</td><td>{e(err[:80]) or '-'}</td></tr>")
    status = ('<div class="scroll"><table style="min-width:760px"><thead><tr><th>사이트 (우선순위 순)</th><th>상태</th><th>목록</th>'
              f'<th>채택</th><th>제외 사유</th><th>오류</th></tr></thead><tbody>{"".join(srows)}</tbody></table></div>')

    crows = []
    for k, v in CAREER_STATUS.items():
        m = re.match(r"한국 HSE (\d+)건", v)
        st = ('<span class="pill ok">수집</span>' if m else
              '<span class="pill keep">API 없음</span>' if "API 없음" in v else '<span class="pill bad">접속 실패</span>')
        crows.append(f"<tr><td>{e(k)}</td><td>{st}</td><td class='dl'>{m.group(1) if m else '-'}</td>"
                     f"<td>{'-' if m else e(v)}</td></tr>")
    careers = ('<section class="card" id="careers"><h2>기업 채용 페이지 현황<span class="n">한국 근무 HSE·EHS·Safety 공고 기준</span></h2>'
               '<div class="scroll"><table style="min-width:560px"><thead><tr><th>기업</th><th>상태</th><th>한국 HSE 공고</th><th>비고</th></tr></thead>'
               f'<tbody>{"".join(crows)}</tbody></table></div></section>') if crows else ""
    nrows = "".join(
        f'<tr class="h{p.hilite}"><td class="corp"><strong><a class="co" href="{e(p.url)}" target="_blank" rel="noopener">{e(p.company or "-")}</a></strong>'
        f'{group_pills(p)}</td><td>{e(p.title)}</td><td class="lv">{e(p.employment)}<small>{e(p.level)}</small></td>'
        f'<td class="dl{" soon" if id(p) in soon else ""}">{e(p.deadline)}</td><td class="src"><a href="{e(p.url)}" target="_blank" rel="noopener">{e(p.source)}</a></td></tr>'
        for p in new_rows)
    newsec = (f'<section class="card" id="new"><h2>신규 공고<span class="n">{n_new}건 · 지난 보고({last_report_date(today):%m/%d}) 이후 추가</span></h2>'
              + ('<div class="scroll"><table style="min-width:720px"><thead><tr><th>업체명</th><th>공고명</th><th>고용형태</th><th>접수기한</th><th>출처</th></tr></thead>'
                 f'<tbody>{nrows}</tbody></table></div>' if new_rows else '<p class="empty">새로 추가된 공고가 없습니다.</p>')
              + '</section>')
    side = ('<div class="sec">요약</div><a href="#new">신규 공고 <b>' + str(n_new) + '</b></a><a href="#summary">지표·차트</a><a href="#calendar">채용 달력</a><a href="#flow">수집 흐름</a>'
            '<div class="sec">공고</div>' + "".join(f'<a href="#{i}">{e(t)} <b>{c}</b></a>' for i, t, c in nav)
            + '<div class="sec">수집</div><a href="#status">사이트 현황</a>'
            + ('<a href="#careers">기업 채용 페이지</a>' if crows else ""))
    chipnav = f'<a href="#new">신규 {n_new}</a><a href="#calendar">채용 달력</a>' + "".join(f'<a href="#{i}">{e(t)} {c}</a>' for i, t, c in nav)

    return f"""<title>안전관리자 채용 브리핑</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap">
<style>{HTML_CSS}</style>
<header class="top"><h1>안전관리자 채용 브리핑</h1>
  <span class="when">{now:%Y-%m-%d %H:%M} KST 수집</span>
  <span class="pill {'ok' if not failed else 'keep'} chip">{ok_sites}/{len(SOURCES)} 사이트 수집</span>
  <div class="edit-bar" data-key="brief-{now:%Y%m%d%H%M}">
    <button type="button" id="edit-toggle" aria-pressed="false">편집</button>
    <button type="button" id="edit-save" hidden>저장</button>
    <button type="button" id="edit-reset" hidden>원래대로</button>
    <span id="edit-msg" role="status"></span>
  <button type="button" class="icon-btn" id="theme-toggle" aria-label="라이트/다크 테마 전환" title="테마 전환">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
  </button></div></header>
<div class="shell">
<nav class="side" aria-label="섹션">{side}</nav>
<main>
<nav class="chipnav" aria-label="섹션">{chipnav}<a href="#status">사이트 현황</a></nav>
<div class="kpis" id="summary">{kpis}</div>
{newsec}
{render_calendar(postings, today)}
<div class="charts">{charts}</div>
<div class="card" id="flow"><h2>수집에서 채택까지</h2><div class="flow">{flow}</div></div>
<div class="card tools" role="search">
  <label for="q" class="sr" hidden>공고 검색</label>
  <input id="q" type="search" placeholder="업체명·공고명·자격 검색" aria-label="업체명, 공고명, 자격 검색">
  <div class="seg" role="group" aria-label="강조 필터">
    <button type="button" data-mode="all" aria-pressed="true">전체</button>
    <button type="button" data-mode="new" aria-pressed="false">신규</button>
    <button type="button" data-mode="A" aria-pressed="false">데이터센터·하이테크·삼성·하이닉스</button>
    <button type="button" data-mode="B" aria-pressed="false">대기업 계열</button>
    <button type="button" data-mode="F" aria-pressed="false">외국계</button>
    <button type="button" data-mode="K" aria-pressed="false">코스피·코스닥 상장</button>
    <button type="button" data-mode="gen" aria-pressed="false">일반 산업체</button>
    <button type="button" data-mode="cert" aria-pressed="false">산업·건설안전기사·ISO 45001 명시</button>
    <button type="button" data-mode="pref" aria-pressed="false">외국어·NEBOSH·IOSH·CSP 우대</button>
    <button type="button" data-mode="ai" aria-pressed="false">AI 우대</button>
    <button type="button" data-mode="soon" aria-pressed="false">3일 내 마감</button>
  </div></div>
{''.join(secs)}
<section class="card" id="status"><h2>사이트별 수집 현황</h2>{status}</section>
{careers}
<p class="note">지원 자격·우대 사항은 상세 페이지에서 자동 추출한 요약입니다. 지원 전 원문을 확인하세요.</p>
</main></div>
<script>{HTML_JS}</script>
"""


UNDATED_KEEP_DAYS = 14  # 마감일이 없는 공고('채용 시 마감' 등)는 처음 수집 후 이 기간만 유지


def carry_over(prev_path, failed, kept, stats, today):
    """직전 브리핑에서 아직 접수 중인 공고를 이어서 싣는다.

    검색 결과 순위가 바뀌어 오늘 목록에 안 보이거나, 사이트 수집에 실패해도
    접수기한이 남은 공고는 리스트에 남긴다. 마감일이 없는 공고는 처음 수집 후
    UNDATED_KEEP_DAYS 일까지만 유지한다. 지금 규칙(건설사 시평 100위 등)은 다시 적용한다.
    """
    try:
        prev = json.loads(prev_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    prev_day = prev.get("generated_at", "")[:10]
    added = collections.Counter()
    for d in prev.get("postings", []):
        try:
            p = Posting(**d)
        except TypeError:  # 이전 형식 필드
            continue
        if p.deadline_date:
            if p.deadline_date < today.isoformat():
                continue
        else:
            first = p.extra.get("first_seen") or prev_day
            if not first or (today - dt.date.fromisoformat(first)).days > UNDATED_KEEP_DAYS:
                continue
        if excluded_corp(p):  # 제외 업체명 재적용
            continue
        if p.industry == "건설" and not p.extra.get("top100"):
            continue
        if senior_rank(p) or NON_HSE_SAFETY_RE.search(p.title):  # 대리급 이상·비HSE 제외 재적용
            continue
        yrs = [int(m.group(1) or m.group(2)) for m in TITLE_YEARS_RE.finditer(p.title)]
        if yrs and min(yrs) >= 2 and not NEWBIE_RE.search(p.title):
            continue
        if SALES_RE.search(p.title) or WATCH_RE.search(f"{p.title} {p.detail_text}"):  # 영업직·감시단 제외 재적용
            continue
        if any(q.url == p.url for q in kept) or is_dup(p, kept):
            continue
        p.extra["carried"] = p.extra.get("carried") or prev_day
        p.hilite = classify_company(p, p.detail_text)  # 지금 기준으로 강조 다시 판정
        p.extra["listed"] = listed_market(p)
        if p.employment == "계약직" and not contract_ok(p):  # 계약직은 관심 기업만
            continue
        if "ai" not in p.extra:
            t = p.detail_text or ""
            p.extra["ai"] = bool(AI_RE.search(section(t, PREF_HEAD, 600)) or AI_NEAR_PREF_RE.search(t))
        kept.append(p)
        added[p.source] += 1
    for name, n in added.items():
        note = f"직전 브리핑에서 접수 중 공고 {n}건 유지"
        stats[name] = f"수집 실패 → {note}" if name in failed else f"{stats.get(name, '')}, {note}".lstrip(", ")


# ---------------------------------------------------------------- 상장사 (KRX)
KRX_MARKETS = [("코스피", "stockMkt"), ("코스닥", "kosdaqMkt")]
LISTED: dict = {}  # 정규화 업체명 → '코스피' / '코스닥'


def load_listed(f: Fetcher, cache: Path):
    """한국거래소 KIND 상장법인 목록을 받아 LISTED를 채운다. 실패하면 직전 캐시를 쓴다."""
    table, errors = {}, []
    for market, code in KRX_MARKETS:
        url = f"https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType={code}"
        try:
            s = BeautifulSoup(f.get(url, encoding="cp949"), "html.parser")
            rows = s.find_all("tr")
            head = [text_of(x) for x in rows[0].find_all(["th", "td"])] if rows else []
            col = head.index("회사명") if "회사명" in head else 0
            n = 0
            for tr in rows[1:]:
                tds = tr.find_all("td")
                if len(tds) > col and text_of(tds[col]):
                    table[norm_corp(text_of(tds[col]))] = market
                    n += 1
            if n < 100:
                raise RuntimeError(f"{market} 목록이 {n}건뿐")
        except Exception as e:
            errors.append(f"{market}: {type(e).__name__}")
    if table and not errors:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(table, ensure_ascii=False), encoding="utf-8")
    elif cache.exists():
        table = {**json.loads(cache.read_text(encoding="utf-8")), **table}
    LISTED.clear()
    LISTED.update(table)
    return errors


def listed_market(p: Posting):
    n = norm_corp(p.company)
    if n in LISTED:
        return LISTED[n]
    m = re.search(r"기업구분[^()]{0,20}\((코스피|코스닥|유가증권|KOSPI|KOSDAQ)", p.detail_text or "")
    if m:
        return {"유가증권": "코스피", "KOSPI": "코스피", "KOSDAQ": "코스닥"}.get(m.group(1), m.group(1))
    return ""


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="briefings", help="출력 디렉터리")
    ap.add_argument("--max-detail", type=int, default=500, help="상세 페이지 최대 조회 수")
    args = ap.parse_args()

    now = dt.datetime.now(KST)
    today = now.date()
    f = Fetcher()
    krx_err = load_listed(f, Path(args.out) / "krx_listed.json")
    if krx_err:
        print(f"[krx] {krx_err} (캐시 {len(LISTED)}개사 사용)", file=sys.stderr)
    try:  # 이전에 본 공고는 처음 수집일을 이어받는다
        for d in json.loads((Path(args.out) / "latest.json").read_text(encoding="utf-8")).get("postings", []):
            fs = (d.get("extra") or {}).get("first_seen")
            if fs:
                PREV_SEEN.setdefault(d["url"], fs)
                PREV_SEEN.setdefault(norm_company(d.get("company", "")) + "|" + norm_title(d.get("title", ""), d.get("company", "")), fs)
    except (OSError, ValueError, KeyError):
        pass
    raw, failures, stats = [], [], {}
    for name, fn, _ in SOURCES:
        for attempt in (1, 2):
            try:
                raw.append((name, fn(f)))
                break
            except Exception as e:  # 사이트 하나가 실패해도 나머지는 계속
                client_err = isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500
                if attempt == 1 and not client_err:
                    time.sleep(30)  # 사이트 단위로 한 번 더
                    continue
                msg = f"{type(e).__name__}: {e}".splitlines()[0][:160]
                if name in ("원티드", "캐치") and client_err and e.response.status_code == 403:
                    msg = "사이트가 해외·자동 접속(GitHub Actions)을 403으로 차단 — 수집 불가"
                if name == "충북대 안전공학과" and client_err:
                    msg = "학과 서버가 해외 접속(GitHub Actions)에 404를 반환 — 국내 IP에서만 열림 (학교 본 사이트는 정상)"
                failures.append((name, msg))
                stats[name] = "수집 실패"
                break

    kept, n_detail = [], 0
    for name, found in raw:
        counts = {"목록": len(found), "채택": 0}
        for p in found:
            # 목록 단계에서 명백히 무관한 것은 상세 조회 전에 거른다
            if p.extra.get("posted") is None and relevant(p) is False:
                counts["안전 직무 아님"] = counts.get("안전 직무 아님", 0) + 1
                continue
            # 목록에 '경력 n년'만 있는 공고(사람인·워커)는 경력직으로 보고 상세 조회 없이 제외
            lv = p.level or ""
            if p.source in ("사람인", "워커", "피플앤잡") and lv.startswith("경력") and not NEWBIE_RE.search(lv):
                counts["경력직"] = counts.get("경력직", 0) + 1
                continue
            if n_detail < args.max_detail:
                try:
                    t = fetch_detail(f, p)
                    if p.extra.get("posted") is not None:  # 게시판: 메뉴 등 사이트 공통부 제거, 본문만
                        i = t.find(p.title[:12])
                        t = t[i:] if i >= 0 else t
                    p.detail_text = t[:15000]
                    n_detail += 1
                    time.sleep(0.3)
                except Exception as e:
                    print(f"[detail] {p.url}: {e}", file=sys.stderr)
            analyze(p, today)
            ok, why = keep(p, today)
            if not ok:
                counts[why] = counts.get(why, 0) + 1
                continue
            if is_dup(p, kept):
                counts["중복(상위 사이트 우선)"] = counts.get("중복(상위 사이트 우선)", 0) + 1
                continue
            counts["채택"] += 1
            p.extra["first_seen"] = (PREV_SEEN.get(p.url) or PREV_SEEN.get(norm_company(p.company) + "|" + norm_title(p.title, p.company))
                                     or p.extra.get("first_seen") or today.isoformat())
            kept.append(p)
        stats[name] = ", ".join(f"{k} {v}" for k, v in counts.items())

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    global PREV_TOTAL
    try:
        PREV_TOTAL = len(json.loads((out / "latest.json").read_text(encoding="utf-8")).get("postings", []))
    except (OSError, ValueError):
        PREV_TOTAL = None
    carry_over(out / "latest.json", [n for n, _ in failures], kept, stats, today)
    uniq_kept, seen_url = [], set()  # 같은 공고(URL) 중복 방지
    for p in kept:
        if p.url not in seen_url:
            seen_url.add(p.url)
            uniq_kept.append(p)
    kept[:] = uniq_kept
    md = render_md(kept, failures, now, stats)
    (out / f"{today:%Y-%m-%d}.md").write_text(md, encoding="utf-8")
    (out / "latest.md").write_text(md, encoding="utf-8")
    page = render_html(kept, failures, now, stats)
    (out / "latest.html").write_text(page, encoding="utf-8")
    # 내려받아 편집기·브라우저에서 고칠 수 있는 완전한 HTML 문서
    (out / "latest_edit.html").write_text(
        '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + page.replace("</style>", "</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n", encoding="utf-8")
    for p in kept:
        p.detail_text = p.detail_text[:1500]
    (out / "latest.json").write_text(json.dumps(
        {"generated_at": now.isoformat(), "postings": [asdict(p) for p in kept], "failures": failures, "stats": stats,
         "careers": CAREER_STATUS},
        ensure_ascii=False, indent=1), encoding="utf-8")
    # 날짜별 보관본 — 이후 작업·규칙 변경 때도 이전 수집 정보를 되살릴 수 있게 남긴다
    hist = out / "history"
    hist.mkdir(exist_ok=True)
    with gzip.open(hist / f"{today:%Y-%m-%d}.json.gz", "wt", encoding="utf-8") as fh:
        json.dump({"generated_at": now.isoformat(), "postings": [asdict(p) for p in kept], "stats": stats},
                  fh, ensure_ascii=False)
    print(md)
    return 0 if len(failures) < len(SOURCES) else 2


if __name__ == "__main__":
    sys.exit(main())
```


### 3-7. `safety_jobs/construction_top100_2026.tsv`

```
# 2026년 시공능력평가 상위 100개사(토목건축) — 국토교통부 발표 자료 '참고 2' 기준
# 순위	업체명
1	삼성물산(주)
2	현대건설(주)
3	지에스건설(주)
4	현대엔지니어링(주)
5	(주)대우건설
6	디엘이앤씨(주)
7	롯데건설(주)
8	(주)포스코이앤씨
9	에스케이에코플랜트(주)
10	아이파크현대산업개발(주)
11	(주)한화
12	(주)호반건설
13	디엘건설(주)
14	계룡건설산업(주)
15	두산에너빌리티(주)
16	(주)서희건설
17	제일건설(주)
18	우미건설(주)
19	쌍용건설(주)
20	효성중공업(주)
21	(주)케이씨씨건설
22	대방건설(주)
23	코오롱글로벌(주)
24	(주)태영건설
25	동부건설(주)
26	두산건설(주)
27	금호건설(주)
28	에이치엘디앤아이한라(주)
29	한신공영(주)
30	(주)호반산업
31	(주)에이치제이중공업
32	(주)비에스한양
33	(주)금강주택
34	신세계건설(주)
35	삼성이앤에이(주)
36	자이씨앤에이(주)
37	(주)동원개발
38	씨제이대한통운(주)
39	(주)반도건설
40	(주)대광건영
41	중흥토건(주)
42	(주)라인건설
43	진흥기업(주)
44	(주)성도이엔지
45	에스지씨이앤씨(주)
46	(주)동양건설산업
47	대보건설(주)
48	에이치에스화성(주)
49	(주)서한
50	엘티삼보(주)
51	(주)라인산업
52	극동건설(주)
53	경남기업(주)
54	남광토건(주)
55	동문건설(주)
56	일성건설(주)
57	(주)케이알산업
58	아이에스동서(주)
59	동원건설산업(주)
60	자이에스앤디(주)
61	양우건설(주)
62	신동아건설(주)
63	(주)대명건설
64	(주)시티건설
65	(주)동아지질
66	(주)모아주택산업
67	(주)태왕이앤씨
68	일신건영(주)
69	(주)대림
70	요진건설산업(주)
71	영진종합건설(주)
72	금광기업(주)
73	(주)금성백조건설
74	에스케이에코엔지니어링(주)
75	에이스건설(주)
76	삼환기업(주)
77	우암건설(주)
78	강산건설(주)
79	씨에이이앤씨(주)
80	(주)우미개발
81	(주)금성백조주택
82	(주)원건설
83	(주)서해종합건설
84	(주)이안알앤씨
85	경동건설(주)
86	(주)보미건설
87	신원종합개발(주)
88	(주)동일토건
89	(주)화성개발
90	위본건설(주)
91	보광종합건설(주)
92	(주)한양건설
93	(주)모아종합건설
94	대상건설(주)
95	이수건설(주)
96	에스엠상선(주)
97	(주)까뮤이앤씨
98	(주)농협네트웍스
99	동아건설산업(주)
100	(주)동양
```


### 3-8. `server.py`

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp>=1.2.0",
#     "httpx>=0.27.0",
#     "pydantic>=2.0.0",
# ]
# ///
#!/usr/bin/env python3
"""MCP Server for OpenAI (ChatGPT).

This server lets an MCP client such as Claude Code call OpenAI's ChatGPT
models to delegate work. It wraps the OpenAI REST API (chat completions and
model listing) as MCP tools.

Authentication:
    Set the OPENAI_API_KEY environment variable to a valid OpenAI API key
    (https://platform.openai.com/api-keys). Optionally set OPENAI_BASE_URL to
    point at a compatible endpoint (Azure OpenAI, a proxy, or a self-hosted
    OpenAI-compatible server); it defaults to https://api.openai.com/v1.
"""

import json
import os
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

import httpx
from pydantic import Field

# The MCP Python SDK renamed the high-level server class in v2.0
# (FastMCP -> MCPServer). Import whichever this environment provides.
try:
    from mcp.server import MCPServer as _MCPServer  # mcp SDK >= 2.0
except ImportError:  # pragma: no cover - older SDKs
    from mcp.server.fastmcp import FastMCP as _MCPServer  # mcp SDK 1.x

# Initialize the MCP server
mcp = _MCPServer("openai_mcp")

# Constants
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o"
REQUEST_TIMEOUT = 120.0  # ChatGPT responses can take a while for long outputs.


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------
def _get_api_key() -> str:
    """Read the OpenAI API key from the environment."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Export a valid OpenAI API key "
            "(see https://platform.openai.com/api-keys) before using this server."
        )
    return key


def _base_url() -> str:
    """Resolve the API base URL, allowing an override for compatible endpoints."""
    return os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


async def _make_api_request(
    endpoint: str, method: str = "GET", json_body: Optional[dict] = None
) -> dict:
    """Reusable function for all OpenAI API calls."""
    headers = {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{_base_url()}/{endpoint.lstrip('/')}",
            headers=headers,
            json=json_body,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()


def _handle_api_error(e: Exception) -> str:
    """Consistent, actionable error formatting across all tools."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        # Surface the OpenAI error message, which is usually specific.
        detail = ""
        try:
            body = e.response.json()
            detail = (body.get("error", {}) or {}).get("message", "") or ""
        except Exception:
            detail = (e.response.text or "")[:500]
        if status == 401:
            return "Error: Authentication failed (401). Check that OPENAI_API_KEY is valid and active."
        if status == 403:
            return f"Error: Permission denied (403). Your key may lack access to this model. {detail}".strip()
        if status == 404:
            return f"Error: Not found (404). The model id may be wrong; call list_openai_models. {detail}".strip()
        if status == 429:
            return (
                "Error: Rate limit or quota exceeded (429). Wait and retry, or check your OpenAI billing/usage. "
                f"{detail}"
            ).strip()
        if status >= 500:
            return f"Error: OpenAI server error ({status}). Try again shortly. {detail}".strip()
        return f"Error: API request failed with status {status}. {detail}".strip()
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The model may be slow; try a smaller max_tokens or retry."
    if isinstance(e, RuntimeError):
        return f"Error: {e}"
    return f"Error: Unexpected {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@mcp.tool(
    name="ask_chatgpt",
    annotations={
        "title": "Ask ChatGPT",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def ask_chatgpt(
    prompt: Annotated[
        str,
        Field(
            description="The user prompt / task to send to ChatGPT (e.g. 'Summarize this text: ...').",
            min_length=1,
            max_length=1_000_000,
        ),
    ],
    model: Annotated[
        str,
        Field(
            description=(
                "OpenAI chat model id (e.g. 'gpt-4o', 'gpt-4o-mini', 'o3-mini'). "
                "Call list_openai_models to discover ids available to your account."
            ),
            min_length=1,
            max_length=100,
        ),
    ] = DEFAULT_MODEL,
    system: Annotated[
        Optional[str],
        Field(description="Optional system prompt that sets ChatGPT's role/behavior.", max_length=100_000),
    ] = None,
    temperature: Annotated[
        Optional[float],
        Field(
            description="Sampling temperature 0.0-2.0. Lower is more deterministic. Omit for the model default.",
            ge=0.0,
            le=2.0,
        ),
    ] = None,
    max_tokens: Annotated[
        Optional[int],
        Field(
            description="Maximum number of tokens to generate in the reply. Omit for the model default.",
            ge=1,
            le=128_000,
        ),
    ] = None,
    response_format: Annotated[
        ResponseFormat,
        Field(description="'markdown' for just the reply text, 'json' for reply plus usage metadata."),
    ] = ResponseFormat.MARKDOWN,
) -> str:
    """Send a prompt to an OpenAI ChatGPT model and return its reply.

    Use this to delegate a self-contained task to ChatGPT — drafting text,
    summarizing, translating, brainstorming, getting a second opinion, or any
    prompt you would type into ChatGPT. The model has no access to this
    machine or the Claude conversation; include all needed context in `prompt`
    (and optionally `system`).

    Args:
        prompt (str): The task/question to send.
        model (str): OpenAI model id (default 'gpt-4o').
        system (Optional[str]): Optional system prompt.
        temperature (Optional[float]): 0.0-2.0 sampling temperature.
        max_tokens (Optional[int]): Max tokens to generate.
        response_format (ResponseFormat): 'markdown' (reply only) or 'json' (reply + usage).

    Returns:
        str: For 'markdown', ChatGPT's reply text. For 'json', a JSON object:
        {
            "model": str,          # model that produced the reply
            "reply": str,          # the assistant message content
            "finish_reason": str,  # e.g. "stop", "length"
            "usage": {             # token accounting (may be absent)
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int
            }
        }
        On failure: "Error: <actionable message>".

    Examples:
        - "Ask ChatGPT to summarize this article: ..." -> prompt with the text.
        - "Get gpt-4o-mini to write a haiku" -> model="gpt-4o-mini".
        - Don't use to run code or read local files; ChatGPT cannot access them.
    """
    try:
        if not prompt.strip():
            return "Error: prompt cannot be empty or whitespace only."

        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body: Dict[str, Any] = {"model": model, "messages": messages}
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens

        data = await _make_api_request("chat/completions", method="POST", json_body=body)

        choices = data.get("choices") or []
        if not choices:
            return "Error: OpenAI returned no choices. Try a different prompt or model."

        choice = choices[0]
        reply = (choice.get("message") or {}).get("content") or ""
        finish_reason = choice.get("finish_reason", "")

        if response_format == ResponseFormat.MARKDOWN:
            return reply if reply else "(ChatGPT returned an empty response.)"

        result = {
            "model": data.get("model", model),
            "reply": reply,
            "finish_reason": finish_reason,
            "usage": data.get("usage", {}),
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="list_openai_models",
    annotations={
        "title": "List OpenAI Models",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def list_openai_models(
    filter: Annotated[
        Optional[str],
        Field(
            description="Optional case-insensitive substring to filter model ids (e.g. 'gpt-4', 'o3').",
            max_length=100,
        ),
    ] = None,
) -> str:
    """List the OpenAI model ids available to your API key.

    Use this to discover which model ids you can pass to ask_chatgpt (they
    change over time and vary by account). Optionally filter by substring.

    Args:
        filter (Optional[str]): Case-insensitive substring to match model ids.

    Returns:
        str: JSON object:
        {
            "count": int,          # number of models returned
            "models": [str, ...]   # sorted model ids
        }
        On failure: "Error: <actionable message>".

    Examples:
        - "What ChatGPT models can I use?" -> no filter.
        - "List gpt-4 models" -> filter="gpt-4".
    """
    try:
        data = await _make_api_request("models", method="GET")
        models = [m.get("id", "") for m in data.get("data", []) if m.get("id")]

        if filter:
            needle = filter.lower()
            models = [m for m in models if needle in m.lower()]

        models = sorted(models)
        return json.dumps({"count": len(models), "models": models}, indent=2)

    except Exception as e:
        return _handle_api_error(e)


if __name__ == "__main__":
    mcp.run()
```
