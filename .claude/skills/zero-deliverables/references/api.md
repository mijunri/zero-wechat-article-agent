# Deliverables REST API

Base: `http://api-manage.foxrouter.com`

## Auth

```
Authorization: Bearer zam_...
X-API-Key: zam_...
```

## Endpoints

### GET /api/deliverables/grouped

Query: `platform` optional (`wechat` | `toutiao` | `baijiahao` | `xiaohongshu` | `twitter`)

Response:

```json
{
  "platform": "wechat",
  "groups": [
    {
      "date": "2026-06-02",
      "date_label": "2026年6月2日 星期一",
      "items": [
        {
          "id": 1,
          "platform": "wechat",
          "platform_label": "微信公众号",
          "title": "...",
          "cover_url": "https://...",
          "image_count": 0,
          "published_at": "2026-06-02T01:30:00+08:00",
          "publish_date_bj": "2026-06-02"
        }
      ]
    }
  ]
}
```

### GET /api/deliverables/{id}

Returns `content_html` and `image_urls` (array).

### POST /api/deliverables

```json
{
  "platform": "wechat",
  "title": "标题",
  "cover_url": "https://...",
  "content_html": "<p>...</p>",
  "image_urls": [],
  "published_at": "2026-06-02T10:00:00+08:00"
}
```

**Xiaohongshu** — `platform: "xiaohongshu"`, `image_urls` required (≥1 URL). `content_html` is **plain text** (not HTML).

**Twitter** — `platform: "twitter"`, `content_html` required plain text. `image_urls` optional (omit or `[]` for text-only). `cover_url` optional (defaults to first image when present).

`published_at` optional; defaults to now (Asia/Shanghai).

### PUT /api/deliverables/{id}

Partial update; any subset of create fields.

### DELETE /api/deliverables/{id}

204 No Content.
