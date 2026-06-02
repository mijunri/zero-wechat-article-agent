# AttentionVC Articles API

- Site: https://www.attentionvc.ai/article/ai?lang=en%2Czh
- Base: `https://api.attentionvc.ai`

## Leaderboard

`GET /v1/articles/leaderboard`

| Query | Description |
|-------|-------------|
| `category` | `ai` (fixed for this skill) |
| `period` | `24h`, `7d`, `14d`, `all` |
| `lang` | e.g. `en,zh` |

### Response fields (per entry)

| Field | Description |
|-------|-------------|
| `rank` | Leaderboard rank |
| `title` | Article title |
| `previewText` | Excerpt |
| `viewCount` | Views |
| `tweetId` | Source tweet id |
| `author.handle` | Author @handle |
| `tags`, `trendingTopics` | Taxonomy |

## Categories (reference)

`GET /v1/articles/categories` — lists `ai` with article counts.
