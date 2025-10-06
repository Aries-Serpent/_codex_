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
