#!/usr/bin/env bash
set -euo pipefail
# Minimal Bash version using openssl + curl to fetch an installation token.
# Requires: GITHUB_APP_ID, GITHUB_APP_INSTALLATION_ID, and a PEM at GITHUB_APP_PRIVATE_KEY_PATH.
#
# JWT: RS256, <= 10 minutes; Installation token: ~1 hour.
# Docs: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app

: "${GITHUB_API:=https://api.github.com}"
: "${GITHUB_APP_ID:?set GITHUB_APP_ID}"
: "${GITHUB_APP_INSTALLATION_ID:?set GITHUB_APP_INSTALLATION_ID}"
: "${GITHUB_APP_PRIVATE_KEY_PATH:?set GITHUB_APP_PRIVATE_KEY_PATH}"

header_base64() {
  printf '{"alg":"RS256","typ":"JWT"}' | openssl base64 -A | tr '+/' '-_' | tr -d '='
}

payload_base64() {
  local now exp
  now=$(date +%s)
  exp=$(( now + 540 )) # 9 minutes
  printf '{"iat":%s,"exp":%s,"iss":"%s"}' "$((now-60))" "$exp" "$GITHUB_APP_ID" \
    | openssl base64 -A | tr '+/' '-_' | tr -d '='
}

sign() {
  local unsigned="$1"
  printf %s "$unsigned" | openssl dgst -sha256 -sign "$GITHUB_APP_PRIVATE_KEY_PATH" -binary \
    | openssl base64 -A | tr '+/' '-_' | tr -d '='
}

main() {
  local header payload unsigned sig jwt
  header="$(header_base64)"
  payload="$(payload_base64)"
  unsigned="${header}.${payload}"
  sig="$(sign "$unsigned")"
  jwt="${unsigned}.${sig}"
  curl --fail-with-body -sS -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${jwt}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "${GITHUB_API}/app/installations/${GITHUB_APP_INSTALLATION_ID}/access_tokens" \
    -d '{}' | jq -r '.token'
}

main "$@"
