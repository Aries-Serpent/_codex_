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
Operational templates keep common operational tasks consistent across services. Treat them as the starting point—not the finish line.

### Responsibilities
- **Developers** own the initial implementation. When you copy a template into a new service or workflow, fill in every `[PLACEHOLDER: …]` prompt, add any service-specific safeguards, and create or expand the tests that ship with the template. Keep overall coverage at or above **85%** by locating the matching regression suite (usually under `tests/` next to the new feature) and extending it so reviewers can see how expectations evolve alongside the code.
- **Maintainers** keep the source templates and shared tests healthy. They reconcile template updates across services, align guidance in `docs/` with the latest operational standards, and enforce the 85% baseline during review by pointing contributors to the most recent regression suites and ensuring any new tests land with the template changes.

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

# Run the focused tests you just created/updated (keeps coverage ≥85%)
pytest tests/services/my-new-service --cov=services.my_new_service
```
