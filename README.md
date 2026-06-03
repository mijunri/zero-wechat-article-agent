# zero-wechat-article-agent

**AI 知识博主** 微信公众号子代理 — 热点采集 → 写稿 → 草稿/发布。Agent 军团 `zero-*` 系列。

- **子代理 ID**：`zero-wechat-article-agent`
- **主编排 Skill**：`/zero-wechat-article`
- **技术栈**：Python 3.11+、`httpx`（无 Node / 无 Electron）

## Skills

| Skill | 说明 |
|-------|------|
| `zero-attentionvc-scrape` | AttentionVC AI 热榜（`limit=1`） |
| `zero-twitter-collect` | `get_tweet_article.py` 拉 X 长文全文 |
| `zero-wechat-article-write` | brief → 微信 HTML → 指挥台 |
| `zero-deliverables` | [指挥台产物](http://manage.foxrouter.com/app/deliverables?platform=wechat) |
| `zero-wechat-auto` | 一键：`pipeline_top_article.py` |
| `hot-topics` | 微博/抖音/头条等热榜（60s API） |
| `zero-toutiao-entertainment` | 头条号娱乐新闻，每日 3 篇 |

```bash
pip install -e .
source .claude/skills/zero-deliverables/scripts/env.sh

# 公众号：AttentionVC #1 深度稿
source .claude/skills/zero-twitter-collect/scripts/env.sh
python3 scripts/pipeline_top_article.py

# 头条号：娱乐热点 ×3
python3 scripts/pipeline_daily_toutiao_entertainment.py
```

## 能力范围

| 能力 | 说明 |
|------|------|
| 采集 | Twitter 话题 + AttentionVC AI 热榜 |
| 素材 | 图片/语音/视频上传至永久或临时素材库 |
| 草稿 | 新建/更新/获取草稿图文 |
| 发布 | 提交发布、发布状态轮询 |
| 编排 | 选题 → 生成正文 → 配图 → 草稿 → 人工确认 → 发布 |

**不负责**：微信支付、小程序、企业微信、个人号 RPA（另立子代理）。

## 快速开始

```bash
cd zero-wechat-article-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # 填入公众号 AppID / Secret
bash .claude/skills/zero-wechat-article/scripts/verify.sh
```

## 凭证（勿提交仓库）

| 变量 | 说明 |
|------|------|
| `twitter_api_key` | [TwitterAPI.io](https://twitterapi.io/) API Key（环境变量） |
| `WECHAT_MP_APPID` | 公众号 AppID |
| `WECHAT_MP_SECRET` | 公众号 AppSecret |

见 [docs/WECHAT-MP-API.md](docs/WECHAT-MP-API.md)。

## 监督者登记

在 [zero-supervisor](https://github.com/mijunri/zero-supervisor) 的 `agents/zero-wechat-article-agent.md` 委派本仓库任务。

## 仓库

GitHub（待建）：`https://github.com/mijunri/zero-wechat-article-agent`
