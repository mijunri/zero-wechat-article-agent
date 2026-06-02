# WeChat Official Account API（参考）

> 以[微信公众平台文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)为准；此处仅列本 Agent 首期用到的接口。

## 凭证

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 开发 → 基本配置 → AppID / AppSecret
3. 写入 `.env`：`WECHAT_MP_APPID`、`WECHAT_MP_SECRET`

## 常用接口（服务号能力更全）

| 能力 | 方法 | 路径（cgi-bin 下） |
|------|------|-------------------|
| 获取 token | GET | `token?grant_type=client_credential` |
| 新增草稿 | POST | `draft/add` |
| 获取草稿 | POST | `draft/get` |
| 发布草稿 | POST | `freepublish/submit` |
| 上传永久图片 | POST | `material/add_material` |

## 权限说明

- **订阅号**与**服务号**接口权限不同，发布能力以账号类型为准。
- 未认证账号部分接口受限，开发前请在后台确认接口权限列表。

## 本仓库验证

```bash
bash .claude/skills/zero-wechat-article/scripts/verify.sh
# 或
zero-wechat-article token
```
