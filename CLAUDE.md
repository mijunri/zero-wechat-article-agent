# zero-wechat-article-agent — 指挥手册

> **AI 知识博主** 微信公众号子代理：热点采集 → 写稿 → **上传指挥台预览** →（可选）公众号 API 发布。

## 定位

面向 **AI 主题公众号**（教程、资讯、工具评测、行业观察），自动化内容供应链。

## 标准流水线（必会）

```text
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│ zero-twitter-   │     │ zero-wechat-       │     │ zero-deliverables   │
│ collect         │──┐  │ article-write      │────▶│ (platform=wechat) │
│ zero-attentionvc│  │  │ brief.json → HTML  │     │ manage.foxrouter.com│
│ -scrape         │──┘  └──────────────────────┘     └─────────────────────┘
└─────────────────┘                                              │
                                                                 ▼
                        http://manage.foxrouter.com/app/deliverables?platform=wechat
```

### 一键跑通（写稿 + 入库）

```bash
cd zero-wechat-article-agent

# 凭证（环境变量，勿提交）
export twitter_api_key="..."          # 采集用
export ZAM_API_KEY="zam_..."          # 指挥台产物 API
export ZAM_API_BASE="http://api-manage.foxrouter.com"

# 1) 可选：采集今日热点
python3 .claude/skills/zero-attentionvc-scrape/scripts/fetch_ai_hot.py fetch --period 24h --limit 10 --json-out /tmp/av.json
python3 .claude/skills/zero-twitter-collect/scripts/search_tweets.py search \
  --query "(AI OR LLM) since:$(TZ=Asia/Shanghai date +%Y-%m-%d) -is:retweet" --query-type Top --limit 10 --json-out /tmp/tw.json

# 2) 编辑 examples/brief-daily-ai.json（或自建 brief）

# 3) 生成 HTML 并上传指挥台
python3 .claude/skills/zero-wechat-article-write/scripts/write_article.py pipeline \
  --brief-file examples/brief-daily-ai.json

# 4) 浏览器打开产物页核对
# http://manage.foxrouter.com/app/deliverables?platform=wechat
```

### 分步命令

| 步骤 | Skill | 命令 |
|------|-------|------|
| 采集 Twitter | `zero-twitter-collect` | `search_tweets.py search --query "..."` |
| 采集 AttentionVC | `zero-attentionvc-scrape` | `fetch_ai_hot.py fetch --period 24h` |
| 写 HTML | `zero-wechat-article-write` | `write_article.py write --brief-file ...` |
| 上传指挥台 | `zero-deliverables` | `deliverables.py create --platform wechat ...` |
| 合并写+传 | `zero-wechat-article-write` | `write_article.py pipeline --brief-file ...` |
| 公众号后台 | `zero-wechat-article` | 草稿/发布（需 `WECHAT_MP_*`，人工确认） |

## Skill Roster

| Skill | 命令 | 职责 |
|-------|------|------|
| **zero-twitter-collect** | `/zero-twitter-collect` | TwitterAPI.io 话题推文 |
| **zero-attentionvc-scrape** | `/zero-attentionvc-scrape` | AttentionVC AI 热榜 |
| **zero-wechat-article-write** | `/zero-wechat-article-write` | brief → 微信 HTML |
| **zero-deliverables** | `/zero-deliverables` | 产物 CRUD（指挥台） |
| **zero-wechat-article** | `/zero-wechat-article` | 公众号官方 API |

## 凭证

| 变量 | 用途 |
|------|------|
| `twitter_api_key` | TwitterAPI.io |
| `ZAM_API_KEY` | manage 产物 API（`Authorization: Bearer`） |
| `ZAM_API_BASE` | 默认 `http://api-manage.foxrouter.com` |
| `WECHAT_MP_APPID` / `WECHAT_MP_SECRET` | 公众号后台 API |

可选本地文件（gitignore）：各 Skill 的 `scripts/agent.env`。

## 原则

1. **AI 博主视角**：二次创作，标注来源，禁止整篇搬运。
2. **指挥台优先**：写完先入库 `platform=wechat`，人工在网页抽屉里复制/下载封面。
3. **发布门禁**：公众号群发须确认或 `CONFIRM_PUBLISH=1`。
4. **凭证不入库**。

## 目录

```text
zero-wechat-article-agent/
├── CLAUDE.md
├── examples/brief-daily-ai.json
├── .claude/skills/
│   ├── zero-twitter-collect/
│   ├── zero-attentionvc-scrape/
│   ├── zero-wechat-article-write/
│   ├── zero-deliverables/
│   └── zero-wechat-article/
└── src/zero_wechat_article/
```

## 迭代焦点

1. ✅ 采集 Skills
2. ✅ 写稿 + 指挥台上传流水线
3. ⬜ brief 自动从采集 JSON 生成
4. ⬜ 公众号草稿 API 对接
