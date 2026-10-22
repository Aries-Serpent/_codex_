#!/usr/bin/env bash
# Structural/consumer guard, not a historical line-count or flag-value lock.
set -euo pipefail
TARGET=".github/workflows/copilot-setup-steps.yml"
python3 scripts/ci/validate_copilot_bootstrap.py "$TARGET"
if command -v yamllint >/dev/null 2>&1; then
  yamllint -c .yamllint.yml "$TARGET"
else
  echo "yamllint unavailable; structural check passed (lint still required before publication)"
fi
if command -v actionlint >/dev/null 2>&1; then
  actionlint "$TARGET"
else
  echo "actionlint unavailable here; run it before publication"
fi
