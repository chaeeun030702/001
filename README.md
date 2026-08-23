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
