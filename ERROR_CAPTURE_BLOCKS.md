# Error Capture Blocks

```
Question for ChatGPT-5 2025-08-28T04:45Z:
While performing STEP 1: run `chatgpt-codex --prompt-file AUDIT_PROMPT.md`, encountered the following error:
`bash: command not found: chatgpt-codex`
Context: generating audit file. What are the possible causes, and how can this be resolved while preserving intended functionality?

Possible Causes:
1) The CLI is not installed or not on PATH.
2) The active shell/venv differs from the one where the CLI was installed.
3) The environment disallows nonstandard CLIs in offline/sandboxed mode.

Resolution:
A) Prefer a portable, offline fallback: replace the CLI with an internal Python entrypoint:
   - `python tools/audit_builder.py --prompt-file AUDIT_PROMPT.md`
B) If the CLI is required, install it into the active venv and verify PATH.
C) Keep the fallback as the default to ensure determinism; retain CLI only as optional.
```

```
Question for ChatGPT-5 2025-08-28T04:50Z:
While performing STEP 2: `pre-commit run --all-files`, encountered the following issue:
`command hung without producing output after >100s`
Context: executing repository hooks. What are the possible causes, and how can this be resolved while preserving intended functionality?

Possible Causes:
1) First run building hook environments is slow; heavy hooks amplify delay.
2) A hook is waiting on input or misconfigured.
3) Hook caches are stale/corrupted.

Resolution:
A) Diagnose: `pre-commit run --all-files --verbose` to identify the stalling hook.
B) Clean and rehydrate: `pre-commit clean` then re-run.
C) Temporarily skip a known-slow hook to unblock: `SKIP=<hook_id> pre-commit run --all-files`.
D) Scope heavy hooks to pre-push or changed files only; keep pre-commit fast/offline.
E) Add a local timeout wrapper in your script; print which hook exceeded the threshold.
```

```
Question for ChatGPT-5 2025-08-28T04:55Z:
While performing STEP 3: `pytest`, encountered the following error:
`pytest: error: unrecognized arguments: --cov=src/codex_ml --cov-report=term --cov-fail-under=70`
Context: running unit tests; pytest-cov plugin missing. What are the possible causes, and how can this be resolved while preserving intended functionality?

Possible Causes:
1) `pytest-cov` plugin not installed in the active environment.
2) Using a global `pytest` without the plugin instead of the venv’s `pytest`.

Resolution:
A) Install plugin in the active venv: `pip install pytest-cov`.
B) Verify plugin availability: `pytest --version` (plugins listed).
C) Re-run coverage: `pytest --cov=src/codex_ml --cov-report=term --cov-fail-under=70`.
D) If coverage is temporarily blocking, run tests without coverage, then re-enable after adding the plugin.
```
