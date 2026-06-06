# 头条号 HTML 文章模板（多风格）

每次写稿时**随机选择一种风格**，保持内容新鲜感。

---

## 风格 1：清爽蓝（默认）

适用：社会热点、科普类

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{文章标题}</title>
    <style>
        body { max-width: 680px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; line-height: 1.8; color: #333; background: #f5f5f5; }
        .article-container { background: #fff; padding: 30px 20px; border-radius: 8px; }
        h1 { font-size: 24px; font-weight: bold; margin-bottom: 20px; line-height: 1.4; color: #1a1a1a; }
        h2 { font-size: 18px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; color: #2c2c2c; }
        p { margin-bottom: 15px; text-align: justify; }
        .info-box { background: #f8f9fa; border-left: 4px solid #007bff; padding: 15px 20px; margin: 20px 0; border-radius: 4px; }
        .highlight-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px 20px; margin: 20px 0; border-radius: 4px; }
        .warning-box { background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px 20px; margin: 20px 0; border-radius: 4px; }
        strong, b { color: #1a1a1a; font-weight: 600; }
    </style>
</head>
<body>
    <div class="article-container">
        <h1>{文章标题}</h1>
        <p>{开头}</p>
        <div class="info-box"><p><strong>关键信息：</strong></p><p>• {信息1}</p><p>• {信息2}</p></div>
        <p>{正文}</p>
        <h2>{小标题}</h2>
        <p>{正文}</p>
        <div class="highlight-box"><p>{重点}</p></div>
        <div class="warning-box"><p><strong>提醒：</strong>{警示}</p></div>
    </div>
</body>
</html>
```

---

## 风格 2：暖橙红

适用：家庭、情感、民生话题

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{文章标题}</title>
    <style>
        body { max-width: 680px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; line-height: 1.8; color: #333; background: #fff8f0; }
        .article-container { background: #fff; padding: 30px 20px; border-radius: 12px; box-shadow: 0 2px 12px rgba(255, 153, 102, 0.1); }
        h1 { font-size: 26px; font-weight: bold; margin-bottom: 20px; line-height: 1.4; color: #d35400; }
        h2 { font-size: 18px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; color: #e67e22; }
        p { margin-bottom: 15px; text-align: justify; }
        .info-box { background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px 20px; margin: 20px 0; border-radius: 8px; }
        .highlight-box { background: #fce4ec; border-left: 4px solid #e91e63; padding: 15px 20px; margin: 20px 0; border-radius: 8px; }
        .warning-box { background: #ffebee; border-left: 4px solid #f44336; padding: 15px 20px; margin: 20px 0; border-radius: 8px; }
        strong, b { color: #d35400; font-weight: 600; }
    </style>
</head>
<body>
    <div class="article-container">
        <h1>{文章标题}</h1>
        <p>{开头}</p>
        <div class="info-box"><p><strong>关键信息：</strong></p><p>• {信息1}</p><p>• {信息2}</p></div>
        <p>{正文}</p>
        <h2>{小标题}</h2>
        <p>{正文}</p>
        <div class="highlight-box"><p>{重点}</p></div>
        <div class="warning-box"><p><strong>提醒：</strong>{警示}</p></div>
    </div>
</body>
</html>
```

---

## 风格 3：清新绿

适用：健康、环保、正能量话题

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{文章标题}</title>
    <style>
        body { max-width: 680px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; line-height: 1.8; color: #333; background: #f0f8f0; }
        .article-container { background: #fff; padding: 30px 20px; border-radius: 16px; border: 1px solid #c8e6c9; }
        h1 { font-size: 24px; font-weight: bold; margin-bottom: 20px; line-height: 1.4; color: #2e7d32; }
        h2 { font-size: 18px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; color: #388e3c; }
        p { margin-bottom: 15px; text-align: justify; }
        .info-box { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px 20px; margin: 20px 0; border-radius: 8px; }
        .highlight-box { background: #fff9c4; border-left: 4px solid #fbc02d; padding: 15px 20px; margin: 20px 0; border-radius: 8px; }
        .warning-box { background: #ffcdd2; border-left: 4px solid #ef5350; padding: 15px 20px; margin: 20px 0; border-radius: 8px; }
        strong, b { color: #2e7d32; font-weight: 600; }
    </style>
</head>
<body>
    <div class="article-container">
        <h1>{文章标题}</h1>
        <p>{开头}</p>
        <div class="info-box"><p><strong>关键信息：</strong></p><p>• {信息1}</p><p>• {信息2}</p></div>
        <p>{正文}</p>
        <h2>{小标题}</h2>
        <p>{正文}</p>
        <div class="highlight-box"><p>{重点}</p></div>
        <div class="warning-box"><p><strong>提醒：</strong>{警示}</p></div>
    </div>
</body>
</html>
```

---

## 风格 4：极简灰

适用：严肃话题、财经、政策解读

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{文章标题}</title>
    <style>
        body { max-width: 700px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; line-height: 1.8; color: #1a1a1a; background: #e0e0e0; }
        .article-container { background: #fafafa; padding: 35px 25px; border-radius: 2px; }
        h1 { font-size: 28px; font-weight: 700; margin-bottom: 25px; line-height: 1.3; color: #000; letter-spacing: -0.5px; }
        h2 { font-size: 20px; font-weight: 600; margin-top: 35px; margin-bottom: 18px; color: #212121; border-bottom: 2px solid #424242; padding-bottom: 8px; }
        p { margin-bottom: 16px; text-align: justify; }
        .info-box { background: #eeeeee; border-left: 3px solid #424242; padding: 18px 22px; margin: 20px 0; }
        .highlight-box { background: #e0e0e0; border-left: 3px solid #616161; padding: 18px 22px; margin: 20px 0; font-weight: 500; }
        .warning-box { background: #ffcdd2; border-left: 3px solid #d32f2f; padding: 18px 22px; margin: 20px 0; }
        strong, b { color: #000; font-weight: 700; }
    </style>
</head>
<body>
    <div class="article-container">
        <h1>{文章标题}</h1>
        <p>{开头}</p>
        <div class="info-box"><p><strong>关键信息：</strong></p><p>• {信息1}</p><p>• {信息2}</p></div>
        <p>{正文}</p>
        <h2>{小标题}</h2>
        <p>{正文}</p>
        <div class="highlight-box"><p>{重点}</p></div>
        <div class="warning-box"><p><strong>提醒：</strong>{警示}</p></div>
    </div>
</body>
</html>
```

---

## 风格 5：卡片式

适用：奇闻趣事、吃瓜话题

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{文章标题}</title>
    <style>
        body { max-width: 680px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; line-height: 1.7; color: #333; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .article-container { background: #fff; padding: 30px 20px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        h1 { font-size: 24px; font-weight: bold; margin-bottom: 20px; line-height: 1.4; color: #5b42f3; }
        h2 { font-size: 18px; font-weight: bold; margin-top: 25px; margin-bottom: 12px; color: #667eea; background: #f3f4ff; padding: 8px 12px; border-radius: 8px; }
        p { margin-bottom: 15px; text-align: justify; }
        .info-box { background: linear-gradient(135deg, #f3f4ff 0%, #e8eaff 100%); border-radius: 12px; padding: 16px 20px; margin: 18px 0; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15); }
        .highlight-box { background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%); border-radius: 12px; padding: 16px 20px; margin: 18px 0; box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2); }
        .warning-box { background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-radius: 12px; padding: 16px 20px; margin: 18px 0; box-shadow: 0 2px 8px rgba(244, 67, 54, 0.2); }
        strong, b { color: #5b42f3; font-weight: 600; }
    </style>
</head>
<body>
    <div class="article-container">
        <h1>{文章标题}</h1>
        <p>{开头}</p>
        <div class="info-box"><p><strong>关键信息：</strong></p><p>• {信息1}</p><p>• {信息2}</p></div>
        <p>{正文}</p>
        <h2>{小标题}</h2>
        <p>{正文}</p>
        <div class="highlight-box"><p>{重点}</p></div>
        <div class="warning-box"><p><strong>提醒：</strong>{警示}</p></div>
    </div>
</body>
</html>
```

---

## 快速选择指南

| 话题类型 | 推荐风格 |
|---------|---------|
| 社会热点、科普 | 风格 1：清爽蓝 |
| 家庭、情感、民生 | 风格 2：暖橙红 |
| 健康、环保、正能量 | 风格 3：清新绿 |
| 财经、政策、严肃 | 风格 4：极简灰 |
| 奇闻趣事、吃瓜 | 风格 5：卡片式 |

每次写稿时可以：
1. 根据话题类型选择对应风格
2. 或者随机选择一个风格，保持变化
