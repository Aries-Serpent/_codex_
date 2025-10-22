#!/usr/bin/env bash
# Raw git checkout for use in GitHub Actions without actions/checkout.
# Clones the current commit into $GITHUB_WORKSPACE using GITHUB_TOKEN when present.
set -euo pipefail

if [ -z "${GITHUB_REPOSITORY:-}" ] || [ -z "${GITHUB_SHA:-}" ]; then
  echo "[checkout] GITHUB_REPOSITORY or GITHUB_SHA not set" >&2
  exit 2
fi

REPO="https://github.com/${GITHUB_REPOSITORY}.git"
if [ -n "${GITHUB_TOKEN:-}" ] && [ -n "${GITHUB_ACTOR:-}" ]; then
  REPO="https://${GITHUB_ACTOR}:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
fi

git init .
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "${REPO}"
else
  git remote add origin "${REPO}"
fi
git fetch --no-tags --prune --depth=1 origin "${GITHUB_SHA}"
git checkout --force "${GITHUB_SHA}"
git reset --hard "${GITHUB_SHA}"
git clean -fdx

echo "[checkout] checked out ${GITHUB_REPOSITORY}@${GITHUB_SHA}"
