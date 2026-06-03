#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP=$(mktemp -d)
cat > "${TMP}/brief.json" <<'JSON'
{
  "title": "Skill verify — AI digest",
  "cover_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&q=80",
  "lead": "这是一条 write skill 自检用的短文。",
  "sections": [
    {
      "h2": "要点",
      "paragraphs": ["采集、写稿、上传指挥台三步可串联。"]
    }
  ],
  "footer": "由 zero-wechat-article-write verify.sh 生成"
}
JSON
python3 "${SKILL_DIR}/scripts/write_article.py" write --brief-file "${TMP}/brief.json" --out "${TMP}/article.html"
test -s "${TMP}/article.html"
echo "zero-wechat-article-write OK"
