---
name: zero-wechat-article
description: >
  WeChat Official Account (微信公众号) article automation — drafts, media, publish via
  official MP API. USE when user mentions 公众号、微信图文、群发、草稿箱、素材库、推文自动化、
  zero-wechat-article, or WeChat article publishing. Requires WECHAT_MP_APPID and
  WECHAT_MP_SECRET. Never log or commit secrets. Default: draft only; publish needs confirm.
when_to_use: 公众号 图文 草稿 发布 素材 推文 微信写作 automation
argument-hint: "[subcommand: token | draft | publish ...]"
---

# zero-wechat-article

## 职责

- 获取/刷新 `access_token`
- 上传素材、创建/更新**草稿**图文
- 在**用户明确确认**后提交发布

**不负责**：付费阅读、小程序、视频号、个人微信号 RPA。

## 启动

```bash
cd zero-wechat-article-agent
source .venv/bin/activate 2>/dev/null || true
export $(grep -v '^#' .env | xargs) 2>/dev/null || true
bash .claude/skills/zero-wechat-article/scripts/verify.sh
```

## 执行步骤

1. 读 `docs/WECHAT-MP-API.md` 确认接口与权限（服务号/订阅号能力不同）
2. `verify.sh` 通过后再调 API
3. 写稿：生成 Markdown/HTML → 转草稿 JSON → `draft/add`
4. 发布：仅当用户确认或 `CONFIRM_PUBLISH=1` → `freepublish/submit`

## 安全

- 禁止未确认群发/发布
- 禁止 AppSecret 入库、打日志
- `errcode != 0` 时停止并回报完整错误（脱敏）

## 代码入口

| 项 | 路径 |
|----|------|
| 客户端 | `src/zero_wechat_article/client.py` |
| CLI | `zero-wechat-article token` |
| 文档 | `docs/ARCHITECTURE.md` |
