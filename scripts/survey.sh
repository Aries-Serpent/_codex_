#!/usr/bin/env bash
# Branch-aware survey writer for Codex plaintext output.
# Usage:
#   scripts/survey.sh --pr 1926 --stdin <<<'plain text'
#   scripts/survey.sh --pr 1926 --from-file /path/to/codex_plain.txt
set -euo pipefail

usage() {
  cat <<'USAGE' >&2
Usage: scripts/survey.sh --pr <PR_NUMBER> [--stdin | --from-file <path>]
  --pr <PR_NUMBER>     Pull request number the survey targets.
  --stdin              Read Codex survey plaintext from STDIN.
  --from-file <path>   Read Codex survey plaintext from the given file.
USAGE
}

sanitize_slug() {
  local value="$1"
  value="${value//\//_}"
  value="${value// /_}"
  value="${value//[^A-Za-z0-9._-]/_}"
  value="$(echo "${value}" | sed -E 's/_+/_/g; s/^_+//; s/_+$//')"
  printf '%s' "${value:-na}"
}

PR=""
FROM=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pr)
      PR="${2:-}"
      shift 2
      ;;
    --pr=*)
      PR="${1#*=}"
      shift
      ;;
    --from-file)
      FROM="${2:-}"
      shift 2
      ;;
    --from-file=*)
      FROM="${1#*=}"
      shift
      ;;
    --stdin)
      FROM="-"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "${PR}" ]]; then
  echo "Missing required --pr <PR_NUMBER> argument" >&2
  usage
  exit 1
fi

if [[ -z "${FROM}" ]]; then
  echo "Provide --stdin or --from-file <path>" >&2
  usage
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
ART_MD="${ART_DIR}/report.md"

mkdir -p "${OUT_DIR}" "${ART_DIR}"

if [[ "${FROM}" == "-" ]]; then
  RAW_CONTENT="$(cat)"
else
  RAW_CONTENT="$(cat "${FROM}")"
fi

SANITIZED="$(python3 tools/survey_sanitize.py <<< "${RAW_CONTENT}")"

{
  printf '# Repo Survey — %s & PR %s — %s (UTC)\n' "${BRANCH}" "${PR}" "${DATE}"
  echo
  printf '**Ref:** branch `%s`  commit `%s`  •  **Artifacts:** `%s`\n' "${BRANCH}" "${SHORT_SHA}" "${ART_DIR}"
  echo
  echo '---'
  echo
  printf '%s\n' "${SANITIZED}"
  echo
  echo '---'
  echo '_Generated with `scripts/survey.sh` • R = α·E + β·T + γ·D (α+β+γ=1)_'
} > "${OUT_MD}"

cp "${OUT_MD}" "${ART_MD}"

echo "✅ Wrote ${OUT_MD}"
echo "   Artifacts folder: ${ART_DIR}"
>&2 echo "Report also copied to ${ART_MD}"
