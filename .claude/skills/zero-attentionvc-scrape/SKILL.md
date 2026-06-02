---
name: zero-attentionvc-scrape
description: >
  Fetch hot AI articles from AttentionVC leaderboard (attentionvc.ai/article/ai).
  USE when user mentions AttentionVC、AI 热榜长文、推特转长文热榜、采集 AI 热门文章,
  or needs ranked AI content signals for the WeChat AI blogger pipeline. No API key required.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*)
metadata:
  version: "1.0.0"
  argument-hint: "[fetch --period 7d] [--limit 30]"
---

# zero-attentionvc-scrape

从 [AttentionVC AI Articles](https://www.attentionvc.ai/article/ai?lang=en%2Czh) 拉取 **AI 分类热榜**（基于 `api.attentionvc.ai` 公开接口）。

## 启动

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR}"
bash "${SKILL_DIR}/scripts/verify.sh"
```

## CLI

```bash
# 近 7 天 AI 热榜，前 30 篇（按浏览量已排序）
python3 "${SKILL_DIR}/scripts/fetch_ai_hot.py" fetch \
  --period 7d \
  --lang "en,zh" \
  --limit 30

# 24 小时热榜
python3 "${SKILL_DIR}/scripts/fetch_ai_hot.py" fetch --period 24h --limit 10

# 写入 JSON 供选题
python3 "${SKILL_DIR}/scripts/fetch_ai_hot.py" fetch --period 7d --limit 50 \
  --json-out /tmp/attentionvc-ai-hot.json
```

## 参数

| 参数 | 说明 |
|------|------|
| `--period` | `24h` \| `7d` \| `14d` \| `all`（默认 `7d`） |
| `--lang` | 语言过滤，默认 `en,zh` |
| `--limit` | 返回条数上限（默认 30） |
| `--json-out` | 可选输出文件 |

## 输出

JSON：`{ "category", "period", "count", "updated_at", "articles": [...] }`

每篇含：`rank`, `title`, `preview_text`, `view_count`, `author_handle`, `tweet_url`, `tags`, `trending_topics`。

详见 [references/api.md](references/api.md)。

## 注意

- 数据来自 Twitter 长文聚合，选题时请改写，勿整篇搬运。
- 接口为第三方站点公开 API，若变更请更新 `fetch_ai_hot.py`。
