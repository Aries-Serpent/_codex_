# Contributing — Hooks, Line Endings, and Fast Commits

## One-time setup
```bash
pip install pre-commit
pre-commit migrate-config
pre-commit autoupdate
pre-commit install --install-hooks
# also install hook types we use by default:
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

## Normalize line endings (once per repo after .gitattributes change)
```bash
git add --renormalize .
git commit -m "chore: normalize line endings via .gitattributes"
```

## Fast path vs. deep scans
- Commit-time hooks stay **fast**. If a heavy hook blocks your workflow, run:
  ```bash
  SKIP=semgrep git commit -m "temp: skip semgrep (see CI)"
  ```
  …then push; Semgrep runs on `pre-push`/CI. (Use `pre-commit run --all-files` for a full local pass.)

## Troubleshooting
- Missing hooks? Re-run:
  ```bash
  pre-commit install --install-hooks \
    --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
  ```
- See `.pre-commit-config.yaml` for stages; values now match hook names (`pre-commit`, `pre-push`, …).

## Using Operational Templates
- **Developers** own the initial implementation. When you copy a template into a new service or workflow, fill in every `[PLACEHOLDER: …]` prompt, add any service-specific safeguards, and write or update the accompanying tests. Keep overall coverage at or above **85%** by expanding the suites that ship with the template—new scenarios should live next to the feature so reviewers can see how expectations evolve.
- **Maintainers** keep the source templates and shared tests healthy. They reconcile template updates across services, align guidance in `docs/` with the latest operational standards, and enforce the 85% baseline during review by pointing contributors to the most recent regression suites.

### Role-based template workflow
1. **Draft (Developer)** — Select the right template from [`docs/templates/README.md`](./templates/README.md), duplicate it into the target service, and replace all placeholders. Capture open questions in the template’s “Risks” block before requesting review.
2. **Review (Maintainer)** — Validate that coverage gates are met (≥85%), placeholders are resolved, and the rollback section addresses tenant and dependency impacts. Update the source template when repeated adjustments appear across services.
3. **Execute (Operations/Release owner)** — Run the rollout or migration steps during the agreed window, post status in the ops channel, and confirm the validation checklist. If issues occur, revert using the documented rollback script and file follow-up actions.

| Template Type | Primary Drafter | Required Reviewer | Execution Lead | Notes |
| --- | --- | --- | --- | --- |
| Migration — Python File Relocation | Service developer | Template maintainer | Release engineer | Ensure import graphs are re-scanned before deploy. |
| Migration — CLI Hardening | CLI feature owner | Maintainer with CLI coverage context | Runtime operator | Coordinate feature flag toggles and CLI docs updates. |
| Planning — Intent Validation | Discovery lead | Maintainer or PM | Product/ops partner | Feed validated risks into downstream implementation plan. |

### Quick-start: copy and adapt a template
```bash
# Copy the operational template into your service
cp templates/operations/alerting.yaml services/my-new-service/alerting.yaml

# Replace placeholders directly in the new file
rg "\[PLACEHOLDER:" services/my-new-service/alerting.yaml
python - <<'PY'
from pathlib import Path
path = Path("services/my-new-service/alerting.yaml")
text = path.read_text()
text = text.replace("[PLACEHOLDER: TEAM_NAME]", "safety-response")
text = text.replace("[PLACEHOLDER: ALERT_CHANNEL]", "#prod-alerts")
path.write_text(text)
PY

# Run the focused tests that accompany the template (keeps coverage ≥85%)
pytest tests/services/my-new-service --cov=services.my_new_service
```
