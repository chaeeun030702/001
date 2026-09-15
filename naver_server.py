# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp>=1.2.0",
#     "httpx>=0.27.0",
#     "pydantic>=2.0.0",
# ]
# ///
#!/usr/bin/env python3
"""MCP Server for Naver Search (네이버 검색).

This server lets an MCP client such as Claude Code query Naver's Search API
(blog, news, books, encyclopedia, cafe articles, Q&A, local, images, shopping,
and web/document search). It wraps the Naver Open API as MCP tools.

Authentication:
    Register an application at https://developers.naver.com/apps/ and enable
    the "검색" (Search) API. Then set the NAVER_CLIENT_ID and
    NAVER_CLIENT_SECRET environment variables to that application's client id
    and client secret.
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
mcp = _MCPServer("naver_mcp")

# Constants
BASE_URL = "https://openapi.naver.com/v1/search"
REQUEST_TIMEOUT = 30.0
DEFAULT_DISPLAY = 10
MAX_DISPLAY = 100
MAX_START = 1000


class SearchType(str, Enum):
    """Naver Search API categories (the `{type}.json` endpoint segment)."""

    BLOG = "blog"          # 블로그
    NEWS = "news"          # 뉴스
    BOOK = "book"          # 책
    ENCYC = "encyc"        # 백과사전
    CAFEARTICLE = "cafearticle"  # 카페글
    KIN = "kin"            # 지식iN
    LOCAL = "local"        # 지역
    WEBKR = "webkr"        # 웹문서
    IMAGE = "image"        # 이미지
    SHOP = "shop"          # 쇼핑
    DOC = "doc"            # 전문자료


class SortOrder(str, Enum):
    """Result ordering. Valid values depend on the search type.

    - sim:  by relevance/accuracy (정확도순). The default for most types.
    - date: by date, newest first (날짜순). Supported by blog, news,
            cafearticle, kin, and (as a valid value) shop.
    - asc:  ascending price (가격 낮은순). Shopping only.
    - dsc:  descending price (가격 높은순). Shopping only.
    """

    SIM = "sim"
    DATE = "date"
    ASC = "asc"
    DSC = "dsc"


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------
def _get_credentials() -> tuple[str, str]:
    """Read the Naver API client id/secret from the environment."""
    client_id = os.environ.get("NAVER_CLIENT_ID", "").strip()
    client_secret = os.environ.get("NAVER_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError(
            "NAVER_CLIENT_ID and/or NAVER_CLIENT_SECRET are not set. Create an "
            "application with the Search API enabled at "
            "https://developers.naver.com/apps/ and export both values before "
            "using this server."
        )
    return client_id, client_secret


async def _make_api_request(endpoint: str, params: Dict[str, Any]) -> dict:
    """Reusable function for all Naver Search API calls."""
    client_id, client_secret = _get_credentials()
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/{endpoint.lstrip('/')}",
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()


def _handle_api_error(e: Exception) -> str:
    """Consistent, actionable error formatting across all tools."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        # Surface the Naver error message, which is usually specific.
        detail = ""
        try:
            body = e.response.json()
            detail = body.get("errorMessage", "") or body.get("message", "") or ""
        except Exception:
            detail = (e.response.text or "")[:500]
        if status == 400:
            return f"Error: Bad request (400). Check query and parameters. {detail}".strip()
        if status == 401:
            return (
                "Error: Authentication failed (401). Check that NAVER_CLIENT_ID and "
                f"NAVER_CLIENT_SECRET are valid. {detail}"
            ).strip()
        if status == 403:
            return (
                "Error: Permission denied (403). Your application may not have the "
                f"Search API enabled at https://developers.naver.com/apps/. {detail}"
            ).strip()
        if status == 404:
            return f"Error: Not found (404). The search type may be wrong. {detail}".strip()
        if status == 429:
            return (
                "Error: Rate limit or daily quota exceeded (429). The Search API allows "
                f"25,000 calls/day per application. Wait and retry. {detail}"
            ).strip()
        if status >= 500:
            return f"Error: Naver server error ({status}). Try again shortly. {detail}".strip()
        return f"Error: API request failed with status {status}. {detail}".strip()
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Try again shortly."
    if isinstance(e, RuntimeError):
        return f"Error: {e}"
    return f"Error: Unexpected {type(e).__name__}: {e}"


def _clean_html(text: str) -> str:
    """Strip the <b>...</b> highlight tags Naver embeds and unescape entities."""
    if not text:
        return ""
    import html
    import re

    text = re.sub(r"</?b>", "", text)
    return html.unescape(text)


def _format_markdown(search_type: str, data: dict) -> str:
    """Render a compact, human-readable summary of the search results."""
    items = data.get("items") or []
    total = data.get("total", 0)
    if not items:
        return f"No results found (total reported: {total})."

    lines = [f"Naver {search_type} search — showing {len(items)} of {total} results", ""]
    for i, item in enumerate(items, 1):
        title = _clean_html(item.get("title", "")) or "(no title)"
        link = item.get("link", "")
        lines.append(f"{i}. {title}")

        # Type-specific secondary fields, when present.
        if item.get("roadAddress") or item.get("address"):  # local
            addr = item.get("roadAddress") or item.get("address")
            lines.append(f"   {_clean_html(addr)}")
            if item.get("telephone"):
                lines.append(f"   ☎ {item['telephone']}")
        if item.get("lprice"):  # shop
            lines.append(f"   {int(item['lprice']):,}원" if str(item["lprice"]).isdigit() else item["lprice"])
            if item.get("mallName"):
                lines.append(f"   {item['mallName']}")
        if item.get("author"):  # book
            lines.append(f"   {_clean_html(item['author'])}")
        if item.get("pubDate"):  # news
            lines.append(f"   {item['pubDate']}")

        desc = _clean_html(item.get("description", ""))
        if desc:
            lines.append(f"   {desc}")
        if link:
            lines.append(f"   {link}")
        lines.append("")

    return "\n".join(lines).rstrip()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@mcp.tool(
    name="search_naver",
    annotations={
        "title": "Search Naver",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def search_naver(
    query: Annotated[
        str,
        Field(
            description="The search keyword(s), e.g. '제주도 맛집' or 'python asyncio'.",
            min_length=1,
            max_length=1000,
        ),
    ],
    search_type: Annotated[
        SearchType,
        Field(
            description=(
                "Which Naver Search category to query: blog(블로그), news(뉴스), "
                "book(책), encyc(백과사전), cafearticle(카페글), kin(지식iN), "
                "local(지역), webkr(웹문서), image(이미지), shop(쇼핑), doc(전문자료)."
            ),
        ),
    ] = SearchType.BLOG,
    display: Annotated[
        int,
        Field(
            description="Number of results to return, 1-100 (default 10). The 'local' type caps at 5.",
            ge=1,
            le=MAX_DISPLAY,
        ),
    ] = DEFAULT_DISPLAY,
    start: Annotated[
        int,
        Field(
            description="1-based index of the first result, 1-1000 (for pagination). The 'local' type caps at 1.",
            ge=1,
            le=MAX_START,
        ),
    ] = 1,
    sort: Annotated[
        Optional[SortOrder],
        Field(
            description=(
                "Result ordering. sim=relevance (default), date=newest first, "
                "asc/dsc=price ascending/descending (shopping only). Omit for the type's default."
            ),
        ),
    ] = None,
    response_format: Annotated[
        ResponseFormat,
        Field(description="'markdown' for a readable summary, 'json' for the raw Naver response."),
    ] = ResponseFormat.MARKDOWN,
) -> str:
    """Search Naver and return matching results.

    Use this to find Korean-web content across Naver's search verticals: blog
    posts, news articles, books, encyclopedia entries, cafe posts, 지식iN Q&A,
    local businesses/places, web documents, images, shopping listings, and
    professional/academic documents.

    Args:
        query (str): The search keyword(s).
        search_type (SearchType): Which vertical to search (default 'blog').
        display (int): How many results to return, 1-100 (default 10).
        start (int): 1-based offset of the first result, 1-1000 (pagination).
        sort (Optional[SortOrder]): Ordering; sim/date, or asc/dsc for shopping.
        response_format (ResponseFormat): 'markdown' (summary) or 'json' (raw).

    Returns:
        str: For 'markdown', a readable list of results (title, key fields,
        link). For 'json', the raw Naver API response, which includes:
        {
            "total": int,        # total matches available
            "start": int,        # offset of this page
            "display": int,      # number of items in this page
            "items": [ ... ]     # per-type result objects
        }
        On failure: "Error: <actionable message>".

    Examples:
        - "Search Naver blogs for '서울 카페'" -> search_type='blog'.
        - "Find recent Naver news about 인공지능, newest first" ->
          search_type='news', sort='date'.
        - "Cheapest Naver shopping results for '무선 이어폰'" ->
          search_type='shop', sort='asc'.
    """
    try:
        if not query.strip():
            return "Error: query cannot be empty or whitespace only."

        params: Dict[str, Any] = {
            "query": query,
            "display": display,
            "start": start,
        }
        if sort is not None:
            params["sort"] = sort.value

        endpoint = f"{search_type.value}.json"
        data = await _make_api_request(endpoint, params)

        if response_format == ResponseFormat.MARKDOWN:
            return _format_markdown(search_type.value, data)

        return json.dumps(data, indent=2, ensure_ascii=False)

    except Exception as e:
        return _handle_api_error(e)


if __name__ == "__main__":
    mcp.run()
