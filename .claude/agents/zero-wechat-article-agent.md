---
name: zero-wechat-article-agent
description: >
  微信公众号图文自动化子代理。负责公众号官方 API（素材、草稿、发布）与写稿编排。
  委派公众号相关任务时使用；凭证 WECHAT_MP_APPID / WECHAT_MP_SECRET。
---

# zero-wechat-article-agent

执行前阅读仓库根目录 `CLAUDE.md`，编排任务使用 Skill `/zero-wechat-article`。

## 边界

- ✅ 公众号后台 API、图文草稿与发布流程
- ❌ 微信支付、小程序、个人号挂机、Node/Electron 重型栈
