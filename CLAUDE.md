# zero-wechat-article-agent — 指挥手册

> **AI 知识博主** 子代理：微信公众号（深度长文）+ 头条号（每日娱乐热点 ×3）。

## 头条号娱乐日产线（entertainment-article）

```text
hot-topics → 娱乐过滤 → volc-search 两轮 → compose_from_research → platform=toutiao
```

```bash
# 需配置 VOLC_SEARCH_API_KEY（见 data/auth/volc_search.json 或 volc-search/scripts/agent.env）
python3 scripts/pipeline_daily_toutiao_entertainment.py
```

写作规范：`.claude/skills/entertainment-article/SKILL.md`（源仓库 `mijunri/ai-article`）。

预览：http://manage.foxrouter.com/app/deliverables?platform=toutiao

## 微信公众号流水线

## 标准流水线（当前版本）

```text
AttentionVC AI 热榜 #1
    → TwitterAPI GET /twitter/article?tweet_id=…（完整长文）
    → Google 翻译 + 结构化中文解读（compose_chinese_article.py）
    → brief.json → HTML → zero-deliverables (wechat)
```

### 一键执行

```bash
cd zero-wechat-article-agent
pip install -e .   # 含 deep-translator

source .claude/skills/zero-twitter-collect/scripts/env.sh
source .claude/skills/zero-deliverables/scripts/env.sh

python3 scripts/pipeline_top_article.py
# 或
python3 scripts/auto_daily_wechat.py
```

预览：http://manage.foxrouter.com/app/deliverables?platform=wechat（**mongo** 账号）

## 分步调试

```bash
# 1) 热榜第一
python3 .claude/skills/zero-attentionvc-scrape/scripts/fetch_ai_hot.py fetch \
  --period 24h --limit 1 --json-out /tmp/av1.json

# 2) 推文长文（从 av1 里取 tweet_url 的 id）
python3 .claude/skills/zero-twitter-collect/scripts/get_tweet_article.py \
  --tweet-id TWEET_ID --json-out /tmp/tw.json

# 3) 中文理解 + 成稿 brief
python3 scripts/compose_chinese_article.py \
  --attentionvc-json /tmp/av1.json --tweet-json /tmp/tw.json --out /tmp/brief.json

# 4) 发布
python3 .claude/skills/zero-wechat-article-write/scripts/write_article.py pipeline \
  --brief-file /tmp/brief.json
```

## Skill Roster

| Skill | 职责 |
|-------|------|
| `zero-attentionvc-scrape` | 热榜 `limit=1` |
| `zero-twitter-collect` | `get_tweet_article.py` 拉完整长文 |
| `zero-wechat-article-write` | brief → HTML |
| `zero-deliverables` | 上传指挥台 |
| `hot-topics` | 60s 热榜 API（上游 skill） |
| `entertainment-article` | 娱乐写稿（来自 **ai-article**） |
| `volc-search` | 中文联网搜索（写作前必做） |
| `zero-toutiao-entertainment` | 头条号娱乐每日 3 篇 |
| `zero-wechat-article` | 微信公众号后台 API（未接） |

## 凭证（scripts/agent.env）

| Skill | 变量 |
|-------|------|
| Twitter | `twitter_api_key` |
| 指挥台 | `ZAM_API_KEY`（mongo） |

## 说明

- 旧版 `brief_from_signals.py`（多源拼凑）已弃用，质量不足。
- 翻译依赖 `deep-translator`（Google 翻译），成稿为「理解 + 博主解读」结构；发布前请人工润色。
