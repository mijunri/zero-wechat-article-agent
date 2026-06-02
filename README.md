# zero-wechat-article-agent

**AI 知识博主** 微信公众号子代理 — 热点采集 → 写稿 → 草稿/发布。Agent 军团 `zero-*` 系列。

- **子代理 ID**：`zero-wechat-article-agent`
- **主编排 Skill**：`/zero-wechat-article`
- **技术栈**：Python 3.11+、`httpx`（无 Node / 无 Electron）

## Skills

| Skill | 说明 |
|-------|------|
| `zero-twitter-collect` | TwitterAPI.io 按话题查推文 |
| `zero-attentionvc-scrape` | AttentionVC AI 热榜长文 |
| `zero-wechat-article` | 公众号素材 / 草稿 / 发布 |

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
| `TWITTERAPI_IO_KEY` | [TwitterAPI.io](https://twitterapi.io/) — 见 `.claude/skills/zero-twitter-collect/scripts/agent.env.example` |
| `WECHAT_MP_APPID` | 公众号 AppID |
| `WECHAT_MP_SECRET` | 公众号 AppSecret |

见 [docs/WECHAT-MP-API.md](docs/WECHAT-MP-API.md)。

## 监督者登记

在 [zero-supervisor](https://github.com/mijunri/zero-supervisor) 的 `agents/zero-wechat-article-agent.md` 委派本仓库任务。

## 仓库

GitHub（待建）：`https://github.com/mijunri/zero-wechat-article-agent`
