# zero-wechat-article-agent — 指挥手册

> 本仓库是 **微信公众号图文自动化** 的唯一权威实现。监督者 `zero-supervisor` 仅登记与委派，不在此堆叠其它领域逻辑。

## 定位

自动化 **公众号后台能力**（官方 API）：素材、草稿、发布；配合 LLM 完成「写稿 → 入库 → 可选发布」流水线。

## 命名

| 项 | 值 |
|----|-----|
| 仓库 | `zero-wechat-article-agent` |
| 子代理 | `zero-wechat-article-agent` |
| Skill | `zero-wechat-article`（`/zero-wechat-article`） |

## 原则

1. **轻量**：Python + httpx，禁止引入 Node 桌面栈。
2. **证据优先**：发布/群发前必须有人工确认或显式 `CONFIRM_PUBLISH=1`。
3. **凭证不入库**：仅 `.env` / 环境变量。
4. **小步交付**：先 token → 素材 → 草稿 → 发布，每步可 `verify.sh` 验证。

## 目录

```text
zero-wechat-article-agent/
├── CLAUDE.md
├── AGENTS.md
├── src/zero_wechat_article/   # API 客户端与编排
├── .claude/skills/zero-wechat-article/
└── docs/
```

## 分派

| 任务 | 处理 |
|------|------|
| 公众号 API、写稿发布流程 | 本仓库 `/zero-wechat-article` |
| GitHub 仓库/PR | 委派 `zero-supervisor` → `github-manager` |
| 阿里云 OSS/ECS | 委派 `zero-aliyun-agent` |

## 凭证

`WECHAT_MP_APPID`、`WECHAT_MP_SECRET` — 见 `.env.example`。

## 迭代焦点

1. ⬜ `access_token` 缓存与刷新
2. ⬜ 图片上传 + 草稿图文 API
3. ⬜ CLI：`draft create` / `publish submit`
4. ⬜ Agent 工作流模板（选题 → 草稿）
