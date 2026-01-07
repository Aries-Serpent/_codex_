# Repo Survey — work & PR 1926 — 2024-10-29 (UTC)

**Ref:** branch `work`  commit `c829fec7`  •  **Artifacts:** `docs/status_updates/artifacts/Previous Cycle-10-29-survey-work-and-1926`

---

## 1) Scope & Goal
- Branch: `work`
- PR: `#1926`
- Date (UTC): `Previous Cycle-10-29`
- Objective: Capture survey-writer and sanitizer updates for the work branch.

## 2) Targets Collected
- A) Trainer/orchestration — writer enforces slug creation and artifact mirroring.
- B) Reasoning harness (vectorization/trace) — N/A this change is tooling only.
- C) Baseline reasoning config & curricula — Template maintained for parity.
- D) Evaluation surfaces — Sanitizer keeps evidence readable for evaluation.
- E) CLI / repo-map — README documents commands for survey collection.
- F) Deployment promises (docs) — Updated instructions reference artifact mirroring.
- G) Referenced-missing assets — None; artifacts folder auto-created per run.
- H) Ring mentions (0A/0B/0C/0D/main) — Template retains ring guidance text.
- I) `ReasoningTrainer` presence — Not touched by this tooling update.
- J) CLI mismatch audit — No mismatches observed for survey workflow.

## 3) Findings (Highlights)
- **Summary:** Branch-aware writer now sanitizes slugs, mirrors the report into artifacts, and relies on a Python sanitizer for `[BEGIN/END CONTENT]` blocks.
- **Actionables:** Share updated README/template with release owners; integrate sanitized writer into survey SOPs.

## 4) Evidence
### 4.1 Files and Excerpts
**FILE:** scripts/survey.sh@HEAD
```text
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
```text

**FILE:** tools/survey_sanitize.py@HEAD
```python
from typing import Iterable

BEGIN_MARKER = "[BEGIN CONTENT]"
END_MARKER = "[END CONTENT]"

def _render_buffer(buffer: Iterable[str]) -> list[str]:
    return [line.rstrip("\r") for line in buffer]
```text
**FILE:** docs/status_updates/README.md@HEAD
```text
## Quick Flow
1) **Collect survey plaintext** from Codex (no nested fences; use the template in `templates/SURVEY_TEMPLATE.md`).
2) **Write the report** with the branch-aware writer:
   scripts/survey.sh --pr 1926 --stdin <<'EOF'
   <paste Codex plaintext survey here>
   EOF
   - Use `--from-file <path>` if the plaintext is saved locally.
3) **Resulting paths**:
   - Report: `docs/status_updates/survey-<branch>-and-<PR>-<YYYY-MM-DD>.md`
   - Artifacts: `docs/status_updates/artifacts/<YYYY-MM-DD>-survey-<branch>-and-<PR>/`
   - The artifact folder also mirrors the report at `report.md` for easy packaging.
```text

### 4.2 CLI/Docs Mismatches
- None observed; README and script usage align.

## 5) Gaps & Remediations
| Gap | Impact | Fix (owner) | Target Ring |
|---|---|---|---|
| _None_ | Tooling is ready for branch surveys. | N/A | main |

## 6) Promotion Signal
Let readiness be \( R = \alpha \cdot E + \beta \cdot T + \gamma \cdot D \).
- E (Eval completeness): `0.0`
- T (Trace quality): `0.0`
- D (Docs parity): `0.9`
- Weights: α=`0.2`, β=`0.2`, γ=`0.6`
- **R = 0.54** → **Recommendation:** `Proceed`

## 7) Artifacts
- `docs/status_updates/artifacts/Previous Cycle-10-29-survey-work-and-1926/report.md`
- `docs/status_updates/artifacts/Previous Cycle-10-29-survey-work-and-1926/metrics/`
- `docs/status_updates/artifacts/Previous Cycle-10-29-survey-work-and-1926/logs/`

## 8) Changelog
- Added branch-aware writer with slug sanitization and artifact mirroring.
- Added Python sanitizer that wraps `[BEGIN/END CONTENT]` blocks.
- Updated template and README to document new survey flow.

## 9) Next Steps
- Share the updated workflow with promotion leads.
- Backfill historical surveys with sanitized formatting if time allows.

---
_Generated with `scripts/survey.sh` • R = α·E + β·T + γ·D (α+β+γ=1)_
