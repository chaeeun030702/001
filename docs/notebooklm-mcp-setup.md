# NotebookLM ↔ Claude MCP 연동 가이드

Google **NotebookLM**을 [alfredang/notebooklm-mcp](https://github.com/alfredang/notebooklm-mcp)
서버로 **Claude Code / Claude Desktop**에 연결하는 방법을 정리한 문서입니다.

노트북 관리·소스 추가·질문(Q&A)은 물론 팟캐스트·슬라이드·퀴즈·플래시카드 같은
콘텐츠 생성까지 자연어로 다룰 수 있습니다.

> ⚠️ **알아두기**
> NotebookLM은 공식 공개 API가 없어, 이 서버는 **브라우저 자동화 + Google 로그인**
> 방식으로 동작합니다. 따라서:
> - **브라우저가 있고 대화형 로그인이 가능한 본인 로컬 PC**에서 설정해야 합니다.
>   (헤드리스 원격 서버/클라우드 컨테이너 단독으로는 최초 로그인이 불가능)
> - 비공식 방식이라 NotebookLM UI가 바뀌면 일부 기능이 깨질 수 있습니다.
> - **본인 계정으로만** 사용하세요.

---

## 1. 사전 준비 — uv 설치

Python 패키지 매니저 [`uv`](https://docs.astral.sh/uv/)가 필요합니다.

**macOS / Linux**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# 또는: brew install uv
```

**Windows (PowerShell)**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# 또는: winget install --id=astral-sh.uv -e
# 또는: scoop install uv
```

설치 확인:
```bash
uv --version
```

---

## 2. 저장소 clone & 의존성 설치

```bash
git clone https://github.com/alfredang/notebooklm-mcp.git
cd notebooklm-mcp
uv sync
```

`.venv` 가상환경이 생성되고 `notebooklm-py`, `fastmcp`가 설치됩니다.

---

## 3. Google 로그인 (최초 1회)

```bash
uv run notebooklm login
```

브라우저 창이 열리면 NotebookLM에서 사용하는 **Google 계정으로 로그인**하세요.
터미널에 **`Success`** 가 표시되면 완료입니다. (인증 쿠키가 저장되어 이후 자동 인증)

**인증 확인 (선택):**
```bash
uv run python -c "
from notebooklm import NotebookLMClient
import asyncio
async def test():
    client = await NotebookLMClient.from_storage()
    async with client:
        notebooks = await client.notebooks.list()
        print(f'Authenticated! Found {len(notebooks)} notebooks.')
asyncio.run(test())
"
```

---

## 4. 서버 동작 확인 (선택)

```bash
uv run python server.py
```

정상 초기화 메시지가 나오면 `Ctrl+C`로 종료합니다.

---

## 5. Claude에 등록

먼저 두 경로를 확인합니다.

| 필요한 값 | 확인 명령 (macOS/Linux) | 확인 명령 (Windows) |
| --- | --- | --- |
| **UV 경로** | `which uv` | `where uv` |
| **프로젝트 경로** | `notebooklm-mcp`에서 `pwd` | `(Get-Location).Path` |

### ▶ Claude Code

```bash
claude mcp add notebooklm -- uv --directory <프로젝트_경로> run python server.py
```

확인:
```bash
claude mcp list
```
Claude Code 안에서 `/mcp`로 연결 상태를 볼 수 있습니다.

### ▶ Claude Desktop

설정 → **Developer → Edit Config**, 또는 아래 파일을 직접 편집:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

`<UV_경로>`, `<프로젝트_경로>`를 실제 값으로 바꿔 넣으세요
([`notebooklm.mcp.json.sample`](./notebooklm.mcp.json.sample) 참고):

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "<UV_경로>",
      "args": [
        "--directory",
        "<프로젝트_경로>",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

저장 후 **Claude Desktop을 완전히 재시작**하고, "내 NotebookLM 노트북 목록 보여줘"로 테스트하세요.

---

## 6. 사용 가능한 도구 (15종)

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

## 7. 문제 해결

| 증상 | 조치 |
| --- | --- |
| 도구가 안 보임 | Claude Code는 `/mcp`, Desktop은 **완전 재시작** 후 확인 |
| `uv sync` Python 버전 오류 | `uv python install`로 해당 버전 설치 |
| 로그인 후에도 인증 실패 | `uv run notebooklm login` 재실행 (쿠키 만료 가능) |
| 특정 도구만 오류 | NotebookLM UI 변경일 수 있음 → 저장소 [Issues](https://github.com/alfredang/notebooklm-mcp/issues) 확인 |
| 경로 인식 실패 | config의 경로에 **공백/한글**이 없는지 확인 (영문 경로 권장) |

---

## 참고 링크

- 서버 저장소: <https://github.com/alfredang/notebooklm-mcp>
- uv 설치 문서: <https://docs.astral.sh/uv/getting-started/installation/>
- NotebookLM: <https://notebooklm.google.com/>
