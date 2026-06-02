#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "${SKILL_DIR}/scripts/fetch_ai_hot.py" fetch --period 7d --limit 5 \
  | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['count']>=3, d; print('zero-attentionvc-scrape OK', d['count'], 'articles, top:', d['articles'][0]['title'][:50])"
