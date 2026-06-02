# zero-wechat-article-agent — 指挥手册

> **AI 知识博主** 微信公众号子代理。本仓库负责：热点采集 → 选题 → 写稿 → 草稿/发布（官方 API）。

## 定位

面向 **AI 主题公众号**（教程、资讯、工具评测、行业观察），自动化内容供应链：

| 阶段 | 能力 | Skill |
|------|------|-------|
| 采集 | Twitter 话题推文、AttentionVC 热门 AI 长文 | `zero-twitter-collect`、`zero-attentionvc-scrape` |
| 生产 | 选题、写稿、配图 | `zero-wechat-article`（公众号 API） |
| 发布 | 草稿、人工确认后发布 | `zero-wechat-article` |

监督者 [zero-supervisor](https://github.com/mijunri/zero-supervisor) 仅登记与委派，不在此堆叠其它领域逻辑。

## 命名

| 项 | 值 |
|----|-----|
| 仓库 | `zero-wechat-article-agent` |
| 子代理 | `zero-wechat-article-agent` |
| 主编排 Skill | `zero-wechat-article` |

## 原则

1. **AI 博主视角**：采集信号服务于「读者能学到什么 / 行业发生了什么」，避免纯搬运。
2. **轻量**：Python + httpx/urllib，禁止 Node 桌面栈。
3. **证据优先**：发布前必须人工确认或 `CONFIRM_PUBLISH=1`。
4. **凭证不入库**：`.env`、`scripts/agent.env` 仅本地；仓库只保留 `*.example`。
5. **小步交付**：采集 Skill 先 `verify.sh`，再写稿流水线。

## 目录

```text
zero-wechat-article-agent/
├── CLAUDE.md
├── AGENTS.md
├── src/zero_wechat_article/          # 公众号 API 客户端
├── .claude/skills/
│   ├── zero-twitter-collect/         # TwitterAPI.io 话题检索
│   ├── zero-attentionvc-scrape/      # AttentionVC AI 热榜
│   └── zero-wechat-article/          # 公众号草稿/发布
└── docs/
```

## Skill Roster

| Skill | 命令 | 职责 |
|-------|------|------|
| **zero-twitter-collect** | `/zero-twitter-collect` | 按话题/关键词查推文（TwitterAPI.io） |
| **zero-attentionvc-scrape** | `/zero-attentionvc-scrape` | AttentionVC AI 分类热榜长文 |
| **zero-wechat-article** | `/zero-wechat-article` | 公众号 token、素材、草稿、发布 |

## 分派

| 任务 | 处理 |
|------|------|
| Twitter 话题数据 | `/zero-twitter-collect` |
| AttentionVC 热门 AI 帖 | `/zero-attentionvc-scrape` |
| 公众号 API、写稿发布 | `/zero-wechat-article` |
| GitHub / PR | `zero-supervisor` → `github-manager` |

## 凭证

| Skill | 环境变量 |
|-------|----------|
| zero-twitter-collect | `TWITTERAPI_IO_KEY` |
| zero-attentionvc-scrape | （公开 API，无需 key） |
| zero-wechat-article | `WECHAT_MP_APPID`、`WECHAT_MP_SECRET` |

## 迭代焦点

1. ✅ 采集：Twitter + AttentionVC Skills
2. ⬜ 选题模板：从采集 JSON 生成公众号提纲
3. ⬜ `access_token` 缓存、草稿图文 API
4. ⬜ 发布门禁与 CLI 完善
