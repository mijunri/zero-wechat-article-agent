#!/usr/bin/env bash
# Verify WeChat MP credentials and token fetch.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -z "${WECHAT_MP_APPID:-}" || -z "${WECHAT_MP_SECRET:-}" ]]; then
  echo "FAIL: set WECHAT_MP_APPID and WECHAT_MP_SECRET in .env"
  exit 1
fi

if ! command -v python3 >/dev/null; then
  echo "FAIL: python3 required"
  exit 1
fi

python3 -c "
from zero_wechat_article.client import WeChatMPClient
c = WeChatMPClient()
t = c.get_access_token(force=True)
print('OK: access_token', t[:8] + '...')
" 2>/dev/null || {
  pip install -e . -q
  python3 -c "
from zero_wechat_article.client import WeChatMPClient
c = WeChatMPClient()
t = c.get_access_token(force=True)
print('OK: access_token', t[:8] + '...')
"
}

echo "verify.sh passed"
