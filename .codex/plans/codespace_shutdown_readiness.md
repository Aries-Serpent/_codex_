# Codespace Shutdown Readiness Contract

This document records the durable restart and shutdown contract for the repository's agent-maintained Codespace. Runtime artifacts are intentionally not copied into Git; the committed code reconstructs them from reviewed source, locks, and Codespaces secrets.

## Durable Startup Contract

- `.devcontainer/scripts/update-content.sh` restores Python dependencies with `uv sync --frozen --extra dev` from `uv.lock`.
- `post-create.sh`, `post-start.sh`, and `devcontainer.json` use the same persistent state root: `/home/codex/.codex` in the managed container, or `${HOME}/.codex` when scripts are run outside that fixed user contract.
- `CODEX_DB_PATH`, `CODEX_RUNTIME_DIR`, and `CODEX_SESSION_LOG_DIR` all support explicit overrides and otherwise point inside the persisted state root.
- The CLI API and Cognitive App start idempotently on ports 8765 and 5173. PID files, logs, bootstrap capabilities, and environment reports stay in `CODEX_RUNTIME_DIR`, not the Git worktree.
- Unfinished route operations remain visible through `/api/health` and `/api/routes/incomplete`. They are never guessed complete; authenticated `/api/routes/reconcile` records a verified result or failure and permits later idempotent replay.
- Webhook/repository-variable synchronization and port visibility changes remain opt-in through `CODEX_SYNC_CODESPACE_WEBHOOKS=true`.

## Readiness Audit

Run the strict audit before stopping, rebuilding, or deleting a Codespace:

```bash
.venv/bin/python scripts/autonomous/codespace_readiness.py \
  --strict \
  --worktree "$PWD"
```

When multiple worktrees exist, pass one `--worktree` for each and one `--temp-root` for each temporary area that must be reviewed. The command is read-only, emits JSON without command lines or credential values, and returns nonzero for:

- dirty, invalid, or operation-in-progress Git worktrees;
- upstream divergence;
- existing stashes;
- repository-owned API, Vite, Playwright, or MCP processes.

The report lists temporary candidates but does not delete them. Classify and review them explicitly before cleanup.

## Current Artifact Dispositions

- `cognitive_app/src/lib/__tests__/codex-api-client.test.ts` in the clone worktree is ignored because a broad `lib/` pattern matches `src/lib`; its assertions are already covered by the stronger tracked `cognitive_app/src/services/__tests__/brain-session.test.ts`. Do not force-add the duplicate.
- `/tmp/clone-authoritative-paths.txt`, overlap/session path files, sibling merge diffs, and reconciliation process snapshots are derived Git/process reports. Their authority remains the remote refs and worktrees; delete them after final verification.
- `/tmp/semgrep-validation-venv/` and failed 18-byte Node archive downloads are disposable caches/artifacts. Do not copy them into the repository.
- `/workspaces/.codespaces/shared/*`, VS Code connection tokens, IPC sockets, Codespace creation/termination logs, and active host processes are platform-managed. Do not read values, commit them, alter permissions, or delete them while the Codespace is active.
- `.venv`, `node_modules`, package caches, build output, Playwright reports, SQLite databases, CLI logs, PID files, cookies, and bootstrap files are reproducible or runtime-only state and remain outside Git.

## Dependency Security Boundary

The project graph no longer installs Semgrep, ChromaDB, `lm-eval`, or DVC. Semgrep remains a dedicated CI/nox scanner installed in an isolated environment. FAISS remains the supported vector store. Evaluation and DVC workflows requiring the removed tools must use a separately reviewed isolated environment; they must not be reintroduced into `pyproject.toml` or `uv.lock` until no-fix findings have a supported upstream resolution and security review.

## Final Termination Gate

Before terminating the Codespace, require all of the following on the same candidate SHA:

1. `HEAD == origin/0D_base_`, no local divergence, no Git operation, no stashes, and no dirty tracked/untracked work.
2. `uv lock --check`, Python compile/Ruff/Black/isort, focused tests, YAML parsing/action validation, shell syntax, frontend build/tests, and `git diff --check` pass.
3. The strict readiness audit exits zero with all registered worktrees included.
4. No repository-owned API, Vite, Playwright, or MCP process remains; intended VS Code/Copilot/Codespaces infrastructure remains untouched.
5. Useful local-only state is represented by committed source/docs/tests or a sanitized report; reviewed disposable caches and derived `/tmp` artifacts have been deleted.
6. GitHub PR/check state is refreshed for the exact head. The Trivy fixed-package findings remain absent, all three Dockerfile scan configurations upload, and any no-fix finding has not been reintroduced.
