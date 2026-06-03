#!/usr/bin/env bash
# shellcheck disable=SC1091
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

if [[ -f "${SCRIPT_DIR}/agent.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/agent.env"
  set +a
fi
if [[ -f "${REPO_ROOT}/data/auth/volc_search.json" ]]; then
  export VOLC_SEARCH_API_KEY="${VOLC_SEARCH_API_KEY:-$(python3 -c "import json;print(json.load(open('${REPO_ROOT}/data/auth/volc_search.json'))['api_key'])")}"
fi
