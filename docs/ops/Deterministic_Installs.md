# [Guide]: Deterministic Installs (uv-first, offline-friendly)

 Energy: 5/5 

## Why
- Recreate environments deterministically from the lockfile (uv.lock)
- Avoid network drift; prefer frozen syncs

## Commands
| Task | Command | Notes |
|------|--------|-------|
| Sync from lock (frozen) | make uv-sync | Uses uv.lock; no updates |
| Install project extras | make uv-install-extras | Installs .[dev,test,cli] |
| Refresh lockfile | make lock-refresh | Network required; opt-in |

## Tips
- Prefer `NOX_PREFER_UV=1` for nox sessions when available.
- For CI-like local runs: `uv sync --frozen && nox -s ci`.
- Pip fallback remains available; uv path is recommended for determinism.

*End*
