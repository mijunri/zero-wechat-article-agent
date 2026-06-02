# TwitterAPI.io — advanced search

- Docs: https://docs.twitterapi.io/introduction
- Endpoint: `GET https://api.twitterapi.io/twitter/tweet/advanced_search`
- Header: `X-API-Key: $TWITTERAPI_IO_KEY`

## Query parameters

| Name | Required | Description |
|------|----------|-------------|
| `query` | yes | Advanced search string (e.g. `AI lang:en -is:retweet`) |
| `queryType` | yes | `Latest` or `Top` |
| `cursor` | no | Pagination; empty on first page |

## Response (simplified)

```json
{
  "tweets": [ { "id", "text", "url", "createdAt", "likeCount", "retweetCount", "viewCount", "author": { "userName", "name" } } ],
  "has_next_page": true,
  "next_cursor": "..."
}
```

## Example queries for AI blogger

| Goal | query |
|------|-------|
| English AI hot | `(AI OR "artificial intelligence" OR LLM) lang:en -is:retweet` |
| Chinese AI | `(人工智能 OR 大模型 OR AGI) lang:zh -is:retweet` |
| From thought leaders | `from:karpathy (AI OR LLM)` |
