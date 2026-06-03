# zero-wechat-article-agent — 指挥手册

> **AI 知识博主** 微信公众号子代理：热点采集 → 写稿 → **上传指挥台** →（可选）公众号 API 发布。

## ⚠️ 看不到新文章？先核对账号

产物按 **登录用户** 隔离。`ZAM_API_KEY` 必须是你浏览器登录 **同一账号** 在  
http://manage.foxrouter.com/app/api-keys 创建的 Key。

```bash
export ZAM_API_KEY="zam_..."
curl -sS -H "Authorization: Bearer $ZAM_API_KEY" \
  http://api-manage.foxrouter.com/api/auth/me
# 显示的 email 必须与你浏览器登录一致
```

## 全自动流水线（推荐）

一条命令完成：**Twitter 采集 → AttentionVC 热榜 → 生成 brief → HTML → 上传 wechat 产物**。

```bash
cd zero-wechat-article-agent
export twitter_api_key="..."
export ZAM_API_KEY="zam_..."   # 与浏览器登录同一账号

python3 scripts/auto_daily_wechat.py
```

成功后打开（需同一账号登录）：

http://manage.foxrouter.com/app/deliverables?platform=wechat

缓存与中间文件：`.cache/auto-daily/`（已 gitignore）。

## Skill Roster

| Skill | 职责 |
|-------|------|
| **zero-twitter-collect** | TwitterAPI.io 话题推文（`twitter_api_key`） |
| **zero-attentionvc-scrape** | AttentionVC AI 24h 热榜 |
| **zero-wechat-article-write** | brief → 微信 HTML |
| **zero-deliverables** | 上传指挥台 `platform=wechat`（`ZAM_API_KEY`） |
| **zero-wechat-article** | 公众号官方 API（`WECHAT_MP_*`） |

## 流程图

```text
auto_daily_wechat.py
    ├─ zero-twitter-collect (today Top)
    ├─ zero-attentionvc-scrape (24h)
    ├─ brief_from_signals.py
    ├─ write_article.py pipeline
    └─ zero-deliverables → manage.foxrouter.com
```

## 凭证

| 变量 | 用途 |
|------|------|
| `twitter_api_key` | TwitterAPI.io |
| `ZAM_API_KEY` | 指挥台产物 API（**与登录账号一致**） |
| `ZAM_API_BASE` | 默认 `http://api-manage.foxrouter.com` |
| `WECHAT_MP_APPID` / `WECHAT_MP_SECRET` | 公众号后台 |

## 手动分步（调试）

```bash
python3 .claude/skills/zero-attentionvc-scrape/scripts/fetch_ai_hot.py fetch --period 24h --limit 10 --json-out /tmp/av.json
python3 .claude/skills/zero-twitter-collect/scripts/search_tweets.py search \
  --query "(AI OR LLM) since:$(TZ=Asia/Shanghai date +%Y-%m-%d) -is:retweet" --query-type Top --limit 15 --json-out /tmp/tw.json
python3 scripts/brief_from_signals.py --twitter-json /tmp/tw.json --attentionvc-json /tmp/av.json --out /tmp/brief.json
python3 .claude/skills/zero-wechat-article-write/scripts/write_article.py pipeline --brief-file /tmp/brief.json
```

## 原则

1. 二次创作，标注来源；禁止整篇搬运。
2. 写完**必须**入库指挥台 `wechat`，便于预览与复制。
3. 公众号群发须人工确认。

## 迭代

1. ✅ 全自动 `auto_daily_wechat.py`
2. ⬜ LLM 润色 brief（可选接入）
3. ⬜ 公众号草稿 API
