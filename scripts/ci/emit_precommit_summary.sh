#!/usr/bin/env bash
# emit_precommit_summary.sh — Surface failing pre-commit hook details to $GITHUB_STEP_SUMMARY
#
# Usage: emit_precommit_summary.sh <validation.log> <artifact-name>
#
# S236/OBJ-001: Makes the failing hook name visible directly in the CI job log
# so agents never need to download the validation artifact to identify the hook.
#
# S237/OBJ-001-F: Also writes hook_failures.json to the workspace so any
# downstream step or workflow job can parse failures without grepping raw logs.
# JSON path: ${JSON_OUT:-hook_failures.json}
#
# Output goes to $GITHUB_STEP_SUMMARY (set by GitHub Actions runner).
# When run locally, outputs to stdout.

set -euo pipefail

LOG_FILE="${1:-validation.log}"
ARTIFACT_NAME="${2:-validation-log}"
SUMMARY_TARGET="${GITHUB_STEP_SUMMARY:-/dev/stdout}"
# OBJ-001-F: JSON output file (override via env var if needed)
JSON_OUT="${JSON_OUT:-hook_failures.json}"

if [ ! -f "$LOG_FILE" ]; then
  # The validation step may not have run (e.g., early-exit before pre-commit stage).
  # This is non-fatal for the summary step itself; the real failure is captured by
  # the validation job exit code, not this diagnostic step.
  echo "⚠️ $LOG_FILE not found — validation step may have failed before pre-commit ran" >> "$SUMMARY_TARGET"
  # Write empty JSON so downstream steps can always parse the file.
  printf '{"status":"no_log","hooks":[]}\n' > "$JSON_OUT"
  exit 0
fi

# Extract the block between "Running pre-commit hooks" and "pre-commit checks failed"
HOOK_BLOCK=$(awk '/Running pre-commit hooks/{found=1} found{print} /pre-commit checks failed/{exit}' "$LOG_FILE")

# Find failure-signal lines:
#   - hook result lines ending in "Failed" (e.g., "fix end of files.......Failed")
#   - hook id annotation lines (e.g., "- hook id: end-of-file-fixer")
#   - exit code lines  (e.g., "- exit code: 1")
#   - files modified   (e.g., "- files were modified by this hook")
#   - file fix lines   (e.g., "Fixing .github/workflows/resilient_validation.yml")
# `|| true` suppresses grep exit-1 when no lines match (expected when pre-commit
# passed all hooks); FAILED will be empty and the summary will say so below.
FAILED=$(echo "$HOOK_BLOCK" | \
  grep -E "\.{3,}\s*Failed$|^- hook id:|^- exit code:|^- files were modified|^Fixing " \
  || true)

# ── OBJ-001-F: Emit hook_failures.json ────────────────────────────────────────
# Parses the failure block into structured JSON so CI jobs and downstream
# workflows can identify the failing hook by name without grepping raw logs.
# Schema: { "status": "ok|failed|no_failures_parsed", "hooks": [ { "id": str,
#           "exit_code": int|null, "files_modified": bool, "fixed_files": [...] } ] }
# Environment variables used (avoids positional-arg-in-heredoc pattern):
#   FAILED   — the extracted failure block text
#   JSON_OUT — output path for hook_failures.json
FAILED="$FAILED" JSON_OUT="$JSON_OUT" python3 - <<'PYEOF'
import json, os, re, sys

raw   = os.environ.get("FAILED", "")
out   = os.environ.get("JSON_OUT", "hook_failures.json")
lines = raw.splitlines() if raw.strip() else []

hooks    = []
current  = None

for line in lines:
    line = line.strip()
    # Hook result line: "some hook name.......Failed"
    if re.search(r'\.{3,}\s*Failed$', line):
        name = re.sub(r'\.{3,}\s*Failed$', '', line).strip()
        current = {"id": name, "exit_code": None, "files_modified": False, "fixed_files": []}
        hooks.append(current)
    elif line.startswith('- hook id:') and current is None:
        hook_id = line.replace('- hook id:', '').strip()
        current = {"id": hook_id, "exit_code": None, "files_modified": False, "fixed_files": []}
        hooks.append(current)
    elif line.startswith('- hook id:') and current is not None:
        # Duplicate hook-id after result line — fill in canonical id
        current["id"] = line.replace('- hook id:', '').strip()
    elif line.startswith('- exit code:') and current is not None:
        try:
            current["exit_code"] = int(line.replace('- exit code:', '').strip())
        except ValueError:
            pass
    elif line == '- files were modified by this hook' and current is not None:
        current["files_modified"] = True
    elif line.startswith('Fixing ') and current is not None:
        current["fixed_files"].append(line.replace('Fixing ', '').strip())

status = "failed" if hooks else ("ok" if not raw.strip() else "no_failures_parsed")
payload = {"status": status, "hooks": hooks}
with open(out, 'w') as f:
    json.dump(payload, f, indent=2)
    f.write('\n')
sys.stderr.write(f"OBJ-001-F: wrote {out} ({len(hooks)} failing hook(s))\n")
PYEOF

# ── Step summary (markdown) ───────────────────────────────────────────────────
{
  echo "## ❌ Pre-commit Failure Summary"
  echo ""
  if [ -n "$FAILED" ]; then
    echo "\`\`\`"
    echo "$FAILED"
    echo "\`\`\`"
  else
    echo "_No hook-level failure lines extracted — download the full log artifact for details._"
  fi
  echo ""
  echo "**Full log:** download artifact \`${ARTIFACT_NAME}\` for complete output including diffs."
  echo ""
  echo "> **Local reproduction:** \`pre-commit run --show-diff-on-failure --files <changed-files>\`"
  echo ""
  echo "> **Hook catalog:** \`.codex/cognitive_brain/objectives_tracker.md\` — OBJ-001 (28 hooks documented)"
  echo ""
  echo "> **Structured output:** \`hook_failures.json\` artifact — machine-readable hook failure list (OBJ-001-F)"
} >> "$SUMMARY_TARGET"
