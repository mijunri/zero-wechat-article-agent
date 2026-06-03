---
name: volc-search
description: Chinese web search and content fetching using Volcano FeedCoop API. Use this skill whenever the user needs to search the web in Chinese, fetch webpage content, get recent news or information, or perform time-filtered searches. Always use this skill for Chinese-language search queries, finding recent articles, or when the user mentions "搜索", "联网搜索", "抓取网页", "最新资讯", or "新闻".
---

# Volcano Search

Chinese web search and content fetching using Volcano FeedCoop API.

## When to use

Use this skill when:
- User needs Chinese-language web search
- User needs to fetch full webpage content
- User wants recent news or time-filtered information
- User mentions "搜索", "search", "联网", "抓取网页", "最新资讯"

## API Configuration

API 配置存储在 `data/auth/volc_search.json`（已加入 .gitignore）：

```json
{
  "api_endpoint": "https://open.feedcoopapi.com/search_api",
  "api_key": "YOUR_API_KEY"
}
```

## Web Search

### Basic Search

```python
import asyncio
import aiohttp

async def web_search(query: str, count: int = 10) -> dict:
    payload = {
        "Query": query,
        "SearchType": "web",
        "Count": count,
        "ContentFormats": "text",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer isHArkf0ICQ8S0PEh61cpX2Ox5NogGpO",
    }
    timeout = aiohttp.ClientTimeout(total=30.0)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            "https://open.feedcoopapi.com/search_api/web_search",
            json=payload,
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
        # Handle wrapped response
        if isinstance(data.get("Result"), dict):
            return data["Result"]
        return data
```

### Time-Filtered Search

Add time filtering to get recent results:

```python
payload["TimeRange"] = "1d"  # Last 1 day
```

### Supported Time Ranges

| Format | Meaning |
|--------|---------|
| `1h`, `6h`, `12h`, `24h`, `48h`, `72h` | Hours |
| `1d`, `2d`, `3d`, `7d`, `15d`, `30d` | Days |
| `1w`, `2w`, `3w`, `4w` | Weeks |
| `1m`, `2m`, `3m`, `6m`, `12m` | Months |
| `1y`, `2y`, `3y` | Years |
| `today`, `week`, `month`, `year` | Predefined periods |

### Response Format

```python
{
    "WebResults": [
        {
            "Title": "标题",
            "Url": "https://...",
            "SiteName": "网站名",
            "Snippet": "摘要...",
            "Summary": "AI摘要...",
            "Content": "正文内容...",
            "PublishTime": "发布时间",
            "AuthInfoDes": "权威度"
        }
    ],
    "ResultCount": 10,
    "TimeCost": 123
}
```

## Web Fetch

Fetch full webpage content:

```python
async def web_fetch(url: str) -> dict:
    payload = {
        "Url": url,
        "ContentFormats": "text",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer isHArkf0ICQ8S0PEh61cpX2Ox5NogGpO",
    }
    timeout = aiohttp.ClientTimeout(total=60.0)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            "https://open.feedcoopapi.com/search_api/web_fetch",
            json=payload,
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
        if isinstance(data.get("Result"), dict):
            return data["Result"]
        return data
```

### Fetch Response Fields

- `Title` - Page title
- `Markdown` - Content in markdown format
- `Content` / `Text` - Plain text content
- `Html` - Raw HTML

## Output Format

Present search results to users in this format:

```markdown
### 1. [标题]
来源：[网站名]
链接：[URL]
发布时间：[时间]

**摘要：**[内容]

---
```

## Best Practices

1. **For recent news:** Use time_range parameter (e.g., "1d" for today's news)
2. **For full content:** Use web_fetch after getting URLs from web_search
3. **Default count:** Use 5-10 results for most queries
4. **Chinese queries work best:** This API is optimized for Chinese content

## Error Handling

- HTTP 401: Invalid API key
- HTTP 400: Invalid parameters (check time_range format)
- Timeout: Increase timeout value for large content
