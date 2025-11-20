#!/usr/bin/env bash
set -euo pipefail
BASE_BRANCH="codex/add-decode-artifact-pipeline"
branches=(
  "codex/pr2310/add-requirements-dev"
  "codex/pr2310/add-conftest"
  "codex/pr2310/ci-validate-phase-a"
  "codex/pr2310/add-baseline-gen"
  "codex/pr2310/add-coverage-fixture"
  "codex/pr2310/stable-manifest"
  "codex/pr2310/update-docs"
)
for br in "${branches[@]}"; do
  if git ls-remote --exit-code origin "refs/heads/${BASE_BRANCH}" >/dev/null 2>&1; then
    git checkout -b "${br}" "origin/${BASE_BRANCH}"
  else
    git checkout -b "${br}" origin/main
  fi
  git commit --allow-empty -m "chore(pr2310): placeholder branch ${br}"
  git push --set-upstream origin "${br}"
  gh pr create --title "[chore/pr2310] follow-up: ${br}" --body "Placeholder PR for ${br}" --head "${br}" --base "${BASE_BRANCH}" || true
done
