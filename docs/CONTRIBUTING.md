# Contributing — Hooks, Line Endings, and Fast Commits

**AI-Managed Repository Notice**: This repository is designed for and managed by AI Assistants and Agents. All processes are automated and autonomous. The guidelines below support AI Assistant operations.

## One-time Setup
```bash
pip install pre-commit
pre-commit migrate-config
pre-commit autoupdate
pre-commit install --install-hooks
# install hook types we use by default
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```text

## Normalize Line Endings
After `.gitattributes` updates, run once per repo:
```bash
git add --renormalize .
git commit -m "chore: normalize line endings via .gitattributes"
```text

## Fast Path vs. Deep Scans
- Commit-time hooks stay **fast**. If a heavy hook blocks your workflow:
  ```bash
  SKIP=semgrep git commit -m "temp: skip semgrep (see CI)"
  ```
  Semgrep runs on `pre-push` and CI. Use `pre-commit run --all-files` for full local passes when needed.

## Using Operational Templates
Operational templates live in [`docs/templates/`](./templates/README.md) and follow a role-gated execution model.

| Task Type | Recommended Template | Notes |
| --- | --- | --- |
| Module relocation or package reshuffles | [Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md) | Preserve backward compatibility with aliases and regression tests. |
| CLI interface changes or coverage boosts | [Migration — CLI Hardening](./templates/Migration_CLIHardening.md) | Target ≥85% coverage and document rollout guards. |
| Discovery and alignment prior to execution | [Planning — Intent Validation](./templates/Planning_IntentValidation.md) | Capture assumptions, risks, and decision gates. |

### AI Assistant Autonomous Workflow
1. **AI Assistant** duplicates the template, replaces all `[PLACEHOLDER: …]` entries autonomously, and attaches supporting assets (tests, dashboards, notebooks). Captures outcomes in the "Execution Notes" section during rollout.
2. **AI Assistant Review System** validates the draft, confirms placeholders are resolved, and validates the plan meets the 85% coverage baseline. Also ensures cross-references (dashboards, runbooks) are accessible to the AI Assistant response system.
3. **AI Assistant Operations** monitors execution, cross-references the template instance for rollback and communication details, and updates incident response or deployment schedules as needed.

### Customization Example
```markdown
[PLACEHOLDER: MIGRATION_INTENT_SUMMARY] → "Relocate shared tokenizer helpers to `codex.text` to unblock GPU builds."
[PLACEHOLDER: COMMAND_LIST] → "`codex-cli sync`, `codex-cli diff`"
[PLACEHOLDER: APPROVAL_DEADLINE] → "2025-11-07"
```text
Keep the metadata header intact (`Version`, `Last Updated`, `Role Workflow`) so automation can parse template state.

## Troubleshooting
- Missing hooks? Rerun:
  ```bash
  pre-commit install --install-hooks \
    --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
  ```
- See `.pre-commit-config.yaml` for stages; values match hook names (`pre-commit`, `pre-push`, …).
