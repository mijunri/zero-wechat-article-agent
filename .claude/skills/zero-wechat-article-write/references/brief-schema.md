# Article brief schema

```json
{
  "title": "公众号标题（≤ 64 字建议）",
  "cover_url": "https://... 封面图 16:9",
  "lead": "导语段落，1–3 句",
  "sections": [
    {
      "h2": "小节标题",
      "paragraphs": ["段落1", "段落2"],
      "image": "https://optional-inline-image.jpg"
    }
  ],
  "footer": "文末引导关注/参考资料（可选）",
  "sources": [
    {"label": "NVIDIA 官方", "url": "https://..."}
  ]
}
```

`write_article.py pipeline` 读取该文件，生成 HTML 并 POST 到产物 API。
