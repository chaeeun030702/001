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
