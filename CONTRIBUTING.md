# Contributing

Thank you for improving `codex-universal`.

## Getting Started

This project accepts documentation updates and `.codex` artefacts. Before submitting a pull request, run the standard checks:

```bash
pre-commit run --all-files
mypy .
pytest
```

## Workflow consolidation

`codex_workflow.py` at the repository root is the canonical workflow script. Run
it via `python -m codex_workflow`.

If additional `codex_workflow*.py` files appear elsewhere in the repository,
use `python tools/workflow_merge.py` to merge logic into the authoritative
module and update imports.

If the secret scan (detect-secrets) fails due to a false positive (and no actual secret is present), update the baseline by running:

```
$ detect-secrets scan --baseline .secrets.baseline
```

Secret scanning runs as part of ``pre-commit``. To scan specific files prior to
committing, run:

```
pre-commit run detect-secrets --files <files>
```

To verify third-party dependency licenses, run:

```
python scripts/check_licenses.py
```
Only MIT, Apache-2.0, BSD, and ISC licenses are currently allowed. The script
exits with a non-zero status if disallowed licenses are detected.

## Manual Validation

When changes affect the snapshot database or related tooling, perform manual validation. Follow the [Manual Verification Template](documentation/manual_verification_template.md) and record the steps you completed (A1–A4, B1–B2, or C1) in your pull request description or issue.

## Scope

See [AGENTS.md](AGENTS.md) for full guidelines.

## Local quality gates (no GitHub Actions)

- First run may be slow while `pre-commit` installs hook environments; use `--verbose` and `pre-commit clean` if needed.
- Tests with coverage: `pytest --cov=src --cov-report=term`.
- **Do not** enable any GitHub Actions. All checks run locally.

## Error capture → commit comment (optional)

Errors are appended to `Codex_Questions.md` with the header:

```
Question for ChatGPT @codex {{TIMESTAMP}}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

`tools/install_codex_hooks.py` installs a `prepare-commit-msg` hook that appends trailers
(`Codex-Questions-Count`, `Codex-Report-Path`) using `git interpret-trailers`.

Optionally post the consolidated `codex_commit_comment.txt` as a commit comment:

```bash
export GH_PAT=***  # or GITHUB_TOKEN
export CODEX_POST_COMMIT_COMMENT=1
python tools/codex_run_tasks.py
# or via GH CLI:
tools/post_commit_comment.sh
```
