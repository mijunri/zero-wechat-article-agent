#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=env.sh
source "${SKILL_DIR}/scripts/env.sh"
if [[ -z "${twitter_api_key:-}" ]]; then
  echo "Missing twitter_api_key — export twitter_api_key in your environment" >&2
  exit 1
fi
python3 "${SKILL_DIR}/scripts/search_tweets.py" search \
  --query "AI lang:en -is:retweet" \
  --query-type Top \
  --limit 3 \
  | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['count']>=1, d; print('zero-twitter-collect OK', d['count'], 'tweets')"
