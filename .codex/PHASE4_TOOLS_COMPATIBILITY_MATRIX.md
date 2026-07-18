# PHASE 4 — TOOLS COMPATIBILITY MATRIX

**Purpose:** Define exact tool versions for Phase 4 Custom Images
**Source:** Scanned 219 workflows in `.github/workflows/`
**Strategy:** Select versions that maximize compatibility across all workflows

## Language Runtime Versions

| Language | Min Version | Max Version | Recommended | Count |
|---|---|---|---|---|
| **python** | ${{ matrix.python-version }} | 6 | 3.12.x (LTS) | 9 |
| **node** | ${{ env.NODE_VERSION }} | 22 | 22.x (LTS) | 3 |

## GitHub Actions Tools (Top 20)

| Action | Latest Version Used | Recommendation |
|---|---|---|
| `actions/checkout` | v (auto) | Pin to v3 or latest |
| `actions/setup-python` | v (auto) | Use latest (auto-managed by GitHub) |
| `actions/upload-artifact` | v (auto) | Pin to stable release |
| `actions/github-script` | v (auto) | Pin to stable release |
| `./.github/actions/setup-python-cached` | v (auto) | Use latest (auto-managed by GitHub) |
| `actions/cache` | v (auto) | Pin to stable release |
| `actions/download-artifact` | v (auto) | Pin to stable release |
| `./.github/actions/resolve-push-target` | v (auto) | Pin to stable release |
| `./.github/actions/post-pr-summary` | v (auto) | Pin to stable release |
| `codecov/codecov-action` | v (auto) | Pin to stable release |
| `./.github/workflows/cost-gate.yml` | v (auto) | Pin to stable release |
| `github/codeql-action/upload-sarif` | v (auto) | Pin to stable release |
| `actions/create-github-app-token` | v (auto) | Pin to stable release |
| `actions/setup-node` | v (auto) | Use latest (auto-managed by GitHub) |
| `actions/upload-release-asset` | v (auto) | Pin to stable release |
| `./.github/actions/setup-agent-env` | v (auto) | Use latest (auto-managed by GitHub) |
| `github/codeql-action/init` | v (auto) | Pin to stable release |

## System Tools (Critical - Must Include)

| Tool | Min Version | Recommendation | Reason |
|---|---|---|---|
| `git` | 2.40+ | 2.43+ | Modern git operations required |
| `curl` | 7.80+ | 8.0+ | TLS 1.3, HTTP/2 support |
| `jq` | 1.6+ | 1.7+ | JSON parsing in scripts |
| `make` | 4.2+ | 4.3+ | Build automation |
| `gcc` | 11+ | 13+ | C/C++ compilation |
| `g++` | 11+ | 13+ | C++ compilation |
| `bash` | 4.0+ | 5.2+ | Shell scripting |
| `tar` | 1.32+ | 1.35+ | Archive handling |
| `zip` | 3.0+ | 3.0+ | Archive handling |
| `docker` | 20.10+ | 26.0+ | Container operations (if needed) |
| `python` | 3.10+ | 3.12+ | Python scripting |
| `perl` | 5.28+ | 5.38+ | Text processing |

## Pip Packages (Pre-install in Base Image)

Packages appearing in >10 workflows (high-priority for pre-installation):

| Package | Workflows | Note |
|---|---|---|
| `--upgrade pip` | 68 | Build tools |
| `pyte` | 41 | General utility |
| `-e ".[dev]"` | 11 | General utility |
| `detect-` | 11 | General utility |
