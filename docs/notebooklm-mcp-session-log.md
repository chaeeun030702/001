# NotebookLM ↔ Claude MCP 연동 작업 기록

> 저장소: `chaeeun030702/001` · 브랜치: `claude/notebooklm-mcp-integration-hctsox`
> 세션: https://claude.ai/code/session_0162an1Jge2zTJLQ51PFbHX8

이 문서는 "Claude에서 NotebookLM을 MCP로 연동" 요청부터 문서화·PR 생성·모니터링까지의
전체 작업 기록과 산출물을 한 파일로 정리한 것입니다.

---

## 1. 요청 요약

| 항목 | 내용 |
| --- | --- |
| 목표 | Claude에서 Google NotebookLM을 MCP로 연동 |
| 방식 | GitHub 공개 NotebookLM MCP 서버 활용 |
| 선택안 | **옵션 2 — alfredang/notebooklm-mcp** (콘텐츠 생성 기능 포함) |
| 산출물 | 설정 가이드 문서 + 샘플 config, PR #1 |

---

## 2. 핵심 결론

- NotebookLM은 **공식 공개 API가 없음** → 모든 NotebookLM MCP 서버는
  **브라우저 자동화 + Google 로그인** 방식으로 동작.
- 따라서 **실제 연동은 브라우저 로그인이 가능한 로컬 PC**에서 해야 함.
  (헤드리스 원격/클라우드 컨테이너 단독으로는 최초 로그인 불가)
- 비공식 방식이라 NotebookLM UI 변경 시 일부 기능이 깨질 수 있음 → 본인 계정으로만 사용.

---

## 3. 검토한 GitHub 저장소

| 저장소 | 특징 | 기반 |
| --- | --- | --- |
| **alfredang/notebooklm-mcp** (채택) | 노트북 생성·소스·Q&A + 팟캐스트/슬라이드/퀴즈/플래시카드 등 콘텐츠 생성 15종 | Python / `uv` |
| PleasePrompto/notebooklm-mcp | 조사·질문·인용(citation) 특화, `npx`로 간편 | Node.js ≥ 18 |
| ray-manaloto/notebooklm-claude-integration | 노트북 라이브러리 관리 통합 | Python |

---

## 4. 채택안 설정 절차 (alfredang/notebooklm-mcp)

> 아래 명령은 모두 **본인 로컬 PC 터미널**에서 실행.

### 4-1. uv 설치
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
확인: `uv --version`

### 4-2. 저장소 clone & 설치
```bash
git clone https://github.com/alfredang/notebooklm-mcp.git
cd notebooklm-mcp
uv sync
```

### 4-3. Google 로그인 (최초 1회)
```bash
uv run notebooklm login
```
브라우저에서 로그인 → 터미널에 `Success` 표시 → 쿠키 저장(이후 자동 인증).

### 4-4. 서버 동작 확인 (선택)
```bash
uv run python server.py   # 정상 초기화 후 Ctrl+C
```

### 4-5. Claude에 등록

경로 확인: `which uv`(또는 `where uv`), 프로젝트 폴더에서 `pwd`(또는 `(Get-Location).Path`)

**Claude Code:**
```bash
claude mcp add notebooklm -- uv --directory <프로젝트_경로> run python server.py
claude mcp list   # 확인
```

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "<UV_경로>",
      "args": ["--directory", "<프로젝트_경로>", "run", "python", "server.py"]
    }
  }
}
```
저장 후 **Claude Desktop 완전 재시작** → "내 NotebookLM 노트북 목록 보여줘"로 테스트.

---

## 5. 사용 가능한 도구 (15종)

| 분류 | 도구 | 설명 |
| --- | --- | --- |
| 노트북 | `list_notebooks` | 계정의 모든 노트북 목록 |
| 노트북 | `create_notebook` | 새 노트북 생성 |
| 노트북 | `get_notebook_summary` | 요약·핵심 인사이트 |
| 소스 | `add_source_url` | 웹 URL을 소스로 추가 |
| 소스 | `add_source_text` | 원문 텍스트를 소스로 추가 |
| 질문 | `ask_notebook` | 소스 기반 질의응답 |
| 생성 | `generate_audio_overview` | 팟캐스트형 오디오 |
| 생성 | `generate_video_overview` | 비디오 개요 |
| 생성 | `generate_slide_deck` | 슬라이드(PPT형) |
| 생성 | `generate_mind_map` | 인터랙티브 마인드맵 |
| 생성 | `generate_infographic` | 인포그래픽 |
| 생성 | `generate_quiz` | 퀴즈 문항 |
| 생성 | `generate_flashcards` | 학습 플래시카드 |
| 생성 | `generate_summary_report` | 브리핑 문서 |
| 생성 | `generate_data_table` | 데이터 표 추출 |

---

## 6. 산출물 (커밋/푸시 완료)

| 파일 | 설명 |
| --- | --- |
| `docs/notebooklm-mcp-setup.md` | 전체 설정 가이드 (한국어) |
| `docs/notebooklm.mcp.json.sample` | 등록용 `.mcp.json` 샘플 |
| `README.md` | NotebookLM 가이드 링크 추가 |
| `docs/notebooklm-mcp-session-log.md` | 이 작업 기록 문서 |

- 기존 `openai_mcp` 파일(`server.py`, `.mcp.json`, README 본문)은 **변경하지 않음**.
- 커밋: `Add NotebookLM MCP integration setup guide`

---

## 7. Pull Request

- **PR #1: Add NotebookLM MCP integration setup guide**
  → https://github.com/chaeeun030702/001/pull/1
- base: `claude/github-claude-code-connector-vbr24r` (저장소 기본 브랜치, `main` 없음)
- head: `claude/notebooklm-mcp-integration-hctsox`
- 상태: 열림 / CI 그린(Vercel 배포 2건 성공) / 머지 가능(clean)

---

## 8. 모니터링

- `subscribe_pr_activity`로 PR #1 이벤트(CI·리뷰·머지/종료) 구독 활성화.
- 주기적 자체 재점검(check-in)을 여러 차례 수행 — 매번 변화 없음(그린/머지 대기).
- 이후 자체 재점검 재예약이 시스템 분류기에 의해 차단되어 중단.
  단, **웹훅 구독은 계속 활성**이라 실제 이벤트 발생 시 자동 대응.

---

## 9. 다음 단계 (사용자)

1. 저장소에서 PR #1 머지 (원하는 경우).
2. 로컬 PC에서 `docs/notebooklm-mcp-setup.md` 절차대로 실제 NotebookLM MCP 연동 수행.
3. 연동 후 Claude에서 "노트북 목록 보여줘" 등으로 동작 확인.

---

## 참고 링크

- alfredang/notebooklm-mcp: https://github.com/alfredang/notebooklm-mcp
- PleasePrompto/notebooklm-mcp: https://github.com/PleasePrompto/notebooklm-mcp
- ray-manaloto/notebooklm-claude-integration: https://github.com/ray-manaloto/notebooklm-claude-integration
- uv 설치: https://docs.astral.sh/uv/getting-started/installation/
- NotebookLM: https://notebooklm.google.com/

---

_작성: Claude Code · 2026-11-18_
