# MCP servers for Claude Code — ChatGPT & Naver Search

MCP (Model Context Protocol) servers that give **Claude Code** extra tools.
This repo ships two:

**`server.py` — OpenAI (ChatGPT)**

| Tool | What it does |
| --- | --- |
| `ask_chatgpt` | Send a prompt to a ChatGPT model and get its reply (draft, summarize, translate, second opinion, …). |
| `list_openai_models` | List the model ids your API key can use. |

**`naver_server.py` — Naver Search (네이버 검색)**

| Tool | What it does |
| --- | --- |
| `search_naver` | Search Naver across blog, news, book, encyc, cafearticle, kin, local, webkr, image, shop, and doc verticals. |

Each server is a single file with its dependencies declared inline (PEP 723),
so [`uv`](https://docs.astral.sh/uv/) runs it with **no manual install or build
step**.

---

## 1. Prerequisites

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed
  (`uv --version` to check).
- An **OpenAI API key** from <https://platform.openai.com/api-keys>.
  > This uses the paid OpenAI API and is billed separately from a ChatGPT
  > subscription. You need API credits on your OpenAI account.

## 2. Provide your credentials

The servers read their credentials from environment variables — they are
**never** written into any file in this repo. Export whichever server(s) you
want to use in your shell:

```bash
# OpenAI (server.py)
export OPENAI_API_KEY="sk-...your key..."
# optional: point at a compatible endpoint (Azure OpenAI, a proxy, etc.)
# export OPENAI_BASE_URL="https://api.openai.com/v1"

# Naver Search (naver_server.py)
export NAVER_CLIENT_ID="...your client id..."
export NAVER_CLIENT_SECRET="...your client secret..."
```

For Naver, register an application at <https://developers.naver.com/apps/>,
enable the **검색 (Search)** API, and copy its client id and client secret.

Put the `export` lines in your `~/.zshrc` / `~/.bashrc` to make them persistent.

## 3. Register with Claude Code

This repo already includes a project-scoped [`.mcp.json`](./.mcp.json)
registering both servers. When you open Claude Code in this directory it will
detect them and ask you to approve — accept, and the `ask_chatgpt` /
`list_openai_models` / `search_naver` tools become available.

Prefer a global registration (works in any directory)? Run:

```bash
claude mcp add openai --env OPENAI_API_KEY="$OPENAI_API_KEY" -- uv run /full/path/to/server.py
claude mcp add naver \
  --env NAVER_CLIENT_ID="$NAVER_CLIENT_ID" \
  --env NAVER_CLIENT_SECRET="$NAVER_CLIENT_SECRET" \
  -- uv run /full/path/to/naver_server.py
```

Verify they're connected from inside Claude Code with `/mcp`.

## 4. Try it

Ask Claude Code things like:

- "Use ask_chatgpt to summarize this text: …"
- "Ask gpt-4o-mini to write a limerick about MCP."
- "List the OpenAI models I can use."
- "Search Naver blogs for 제주도 맛집."
- "Find recent Naver news about 인공지능, newest first."
- "Show the cheapest Naver shopping results for 무선 이어폰."

## Notes & troubleshooting

**OpenAI (`server.py`)**

- **`OPENAI_API_KEY is not set`** → the variable isn't exported in the
  environment Claude Code launched from. Re-export it and restart Claude Code.
- **401 / authentication failed** → the key is wrong, revoked, or lacks access.
- **429 / quota exceeded** → out of credits or hitting rate limits; check
  <https://platform.openai.com/usage>.
- **Wrong model id (404)** → run `list_openai_models` to see valid ids; the
  default is `gpt-4o`.
- ChatGPT called this way has **no access** to your files, terminal, or the
  Claude conversation. Put everything it needs directly in the prompt.

**Naver Search (`naver_server.py`)**

- **`NAVER_CLIENT_ID … not set`** → export both `NAVER_CLIENT_ID` and
  `NAVER_CLIENT_SECRET` and restart Claude Code.
- **401 / authentication failed** → the client id/secret are wrong.
- **403 / permission denied** → the application doesn't have the 검색 (Search)
  API enabled at <https://developers.naver.com/apps/>.
- **429 / quota exceeded** → the Search API allows 25,000 calls/day per
  application. Wait, or use another application's credentials.
- Note: the `local` (지역) vertical caps `display` at 5 and `start` at 1.

## Run manually (debugging)

```bash
# starts a stdio MCP server; use the MCP Inspector to poke at it
uv run server.py          # OpenAI
uv run naver_server.py    # Naver Search
# or:
npx @modelcontextprotocol/inspector uv run naver_server.py
```
