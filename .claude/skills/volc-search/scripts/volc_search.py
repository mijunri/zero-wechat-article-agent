"""Volcano Search API helper script."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import aiohttp


REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_FILE = REPO_ROOT / "data" / "auth" / "volc_search.json"
ENV_FILE = Path(__file__).resolve().parent / "agent.env"


def _load_env_file() -> None:
    if not ENV_FILE.is_file():
        return
    import os

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip()
        if v and k not in os.environ:
            os.environ[k] = v


def _load_config() -> dict[str, str]:
    """Load Volc search API config (no hardcoded keys in repo)."""
    import os

    _load_env_file()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if cfg.get("api_key"):
                return cfg
    key = os.environ.get("VOLC_SEARCH_API_KEY", "").strip()
    if not key:
        return {
            "api_endpoint": "https://open.feedcoopapi.com/search_api",
            "api_key": "",
        }
    return {
        "api_endpoint": os.environ.get(
            "VOLC_SEARCH_API_ENDPOINT", "https://open.feedcoopapi.com/search_api"
        ),
        "api_key": key,
    }


_config = _load_config()
VOLC_API_KEY = _config.get("api_key", "")
VOLC_SEARCH_URL = f"{_config.get('api_endpoint', '')}/web_search"
VOLC_FETCH_URL = f"{_config.get('api_endpoint', '')}/web_fetch"


def _unwrap_result(body: dict[str, Any]) -> dict[str, Any]:
    if isinstance(body.get("Result"), dict):
        return body["Result"]
    return body


async def web_search(
    query: str,
    count: int = 10,
    time_range: str | None = None,
) -> dict[str, Any]:
    """Volcano web search.

    Args:
        query: Search query
        count: Number of results (default: 10)
        time_range: Time filter (e.g., "1d", "1w", "1m", "1y")

    Returns:
        Search results dict with WebResults, ResultCount, TimeCost
    """
    payload: dict[str, Any] = {
        "Query": query,
        "SearchType": "web",
        "Count": count,
        "ContentFormats": "text",
    }

    if time_range:
        payload["TimeRange"] = time_range

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VOLC_API_KEY}",
    }

    timeout = aiohttp.ClientTimeout(total=30.0)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(VOLC_SEARCH_URL, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            body = await resp.json(content_type=None)

    return _unwrap_result(body)


async def web_fetch(url: str, content_format: str = "text") -> dict[str, Any]:
    """Fetch full webpage content.

    Args:
        url: URL to fetch
        content_format: Response format (text/markdown/html)

    Returns:
        Fetched content dict
    """
    payload: dict[str, Any] = {"Url": url, "ContentFormats": content_format}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VOLC_API_KEY}",
    }

    timeout = aiohttp.ClientTimeout(total=60.0)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(VOLC_FETCH_URL, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            body = await resp.json(content_type=None)

    return _unwrap_result(body)


def format_markdown(data: dict[str, Any]) -> str:
    """Format search results as Markdown."""
    lines: list[str] = []

    web_results = data.get("WebResults") or []
    for i, item in enumerate(web_results, 1):
        title = item.get("Title") or "无标题"
        url = item.get("Url") or ""
        site = item.get("SiteName") or ""
        snippet = item.get("Snippet") or ""
        summary = item.get("Summary") or ""
        publish_time = item.get("PublishTime") or ""

        lines.append(f"### {i}. {title}")
        if site:
            lines.append(f"来源：{site}")
        if url:
            lines.append(f"链接：{url}")
        if publish_time:
            lines.append(f"发布时间：{publish_time}")
        lines.append("")

        if summary:
            lines.append(f"**摘要：**{summary}")
        elif snippet:
            lines.append(snippet)
        lines.append("")
        lines.append("---")
        lines.append("")

    result_count = data.get("ResultCount", 0)
    time_cost = data.get("TimeCost", 0)
    lines.append(f"\n> 共 {result_count} 条结果，耗时 {time_cost}ms")

    return "\n".join(lines).strip()


async def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: volc_search.py <query> [count] [time_range]")
        print("Example: volc_search.py '杨幂 新闻' 5 1d")
        sys.exit(1)

    query = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    time_range = sys.argv[3] if len(sys.argv) > 3 else None

    data = await web_search(query, count, time_range)
    print(format_markdown(data))


if __name__ == "__main__":
    asyncio.run(main())
