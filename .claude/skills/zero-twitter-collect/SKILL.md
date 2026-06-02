---
name: zero-twitter-collect
description: >
  Collect tweets by topic/keyword via TwitterAPI.io (docs.twitterapi.io). USE when user
  mentions Twitter/X 推文采集、话题搜索、AI Twitter 热点、twitterapi.io, or needs tweet data
  for the AI blogger WeChat pipeline. Requires env twitter_api_key. Never log or commit keys.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*)
metadata:
  version: "1.0.0"
  argument-hint: "[search --query ...] [--query-type Top|Latest]"
---

# zero-twitter-collect

为 **AI 知识博主** 公众号流水线采集 Twitter/X 话题推文（[TwitterAPI.io](https://docs.twitterapi.io/introduction)）。

## 启动（每次）

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR}"
export twitter_api_key="..."   # 或已在 shell / 部署环境中配置
bash "${SKILL_DIR}/scripts/verify.sh"
```

凭证：环境变量 **`twitter_api_key`**（TwitterAPI.io API Key）。可选 `source scripts/env.sh` 加载本地 `scripts/agent.env`（gitignore）。

## CLI

```bash
# 热门 AI 相关（Top，默认 20 条）
python3 "${SKILL_DIR}/scripts/search_tweets.py" search \
  --query "(AI OR LLM OR Claude OR GPT) lang:en -is:retweet" \
  --query-type Top \
  --limit 20

# 中文 AI 话题（Latest）
python3 "${SKILL_DIR}/scripts/search_tweets.py" search \
  --query "人工智能 OR 大模型 lang:zh" \
  --query-type Latest \
  --limit 15 \
  --json-out /tmp/ai-tweets.json
```

## 参数

| 参数 | 说明 |
|------|------|
| `--query` | Twitter 高级搜索语法（必填） |
| `--query-type` | `Top` 或 `Latest`（默认 `Top`） |
| `--limit` | 最多返回条数（默认 20，分页自动拉取） |
| `--json-out` | 可选，写入 JSON 文件 |

## 输出

JSON：`{ "query", "query_type", "count", "tweets": [{ id, url, text, created_at, metrics, author }] }`

详见 [references/api.md](references/api.md)。

## 注意

- 遵守 TwitterAPI.io 配额与条款；仅用于选题研究，发布公众号需二次创作。
- 禁止将 API Key 写入仓库或日志。
