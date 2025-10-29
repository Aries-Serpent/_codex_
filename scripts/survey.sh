#!/usr/bin/env bash
# Branch-agnostic survey writer for Codex plaintext output.
# Usage:
#   scripts/survey.sh --pr 1926 --stdin < <(codex-plain-output-here)
#   scripts/survey.sh --pr 1926 --from-file /path/to/codex_plain.txt
set -euo pipefail

PR="NA"
FROM=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pr)         PR="${2:-NA}"; shift 2 ;;
    --pr=*)       PR="${1#*=}"; shift ;;
    --from-file)  FROM="${2:-}"; shift 2 ;;
    --from-file=*)FROM="${1#*=}"; shift ;;
    --stdin)      FROM="-" ; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${FROM}" ]]; then
  echo "Provide --stdin or --from-file <path>" >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo detached)"
DATE="$(date -u +%F)"
SHORT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
SAN_BRANCH="$(echo "${BRANCH}" | tr '/ ' '_')"
# Sanitize the PR slug to avoid writing outside the status updates tree.
PR_SLUG="$(echo "${PR}" | tr -c '[:alnum:]_-' '_')"
if [[ -z "${PR_SLUG}" ]]; then
  PR_SLUG="NA"
fi

OUT_DIR="docs/status_updates"
ART_DIR="${OUT_DIR}/artifacts/${DATE}-survey-${SAN_BRANCH}-and-${PR_SLUG}"
OUT_MD="${OUT_DIR}/survey-${SAN_BRANCH}-and-${PR_SLUG}-${DATE}.md"

mkdir -p "${OUT_DIR}" "${ART_DIR}"

if [[ "${FROM}" == "-" ]]; then
  RAW="$(cat)"
else
  RAW="$(cat "${FROM}")"
fi

# Sanitize the Codex plaintext to Markdown-safe fences and blocks.
SANITIZED="$(python3 tools/survey_sanitize.py <<< "${RAW}")"

# Compose a consistent, readable header and append the sanitized body.
{
  echo "# Repo Survey — ${BRANCH} & PR ${PR_SLUG} — ${DATE} (UTC)"
  echo
  echo "**Ref:** branch \`${BRANCH}\`  commit \`${SHORT_SHA}\`  •  **Artifacts:** \`${ART_DIR}\`"
  echo
  echo "---"
  echo
  printf "%s\n" "${SANITIZED}"
  echo
  echo "---"
  echo "_Generated with \`scripts/survey.sh\` • R = α·E + β·T + γ·D (α+β+γ=1)_"
} > "${OUT_MD}"

echo "✅ Wrote ${OUT_MD}"
echo " Artifacts folder: ${ART_DIR}"

