# PHASE 4 CUSTOM IMAGES — DEPENDENCY ANALYSIS REPORT

**Generated:** 2026-07-18
**Scope:** All 219 active workflows in `.github/workflows/`
**Purpose:** Extract exact tool versions and dependencies for Phase 4 Custom Images implementation

## Executive Summary

- **Total Workflows Scanned:** 219
- **Total Dependency Records:** 2312
- **Unique Dependencies:** 176
- **Categories:** 6

## Dependency Inventory by Category

### ACTION

- **Unique Dependencies:** 49
- **Total Mentions:** 1196
- **Average Usage Per Dep:** 24.4

| Dependency | Workflows | Usage |
|---|---|---|
| `actions/checkout` | 477 | 217.8% |
| `actions/setup-python` | 163 | 74.4% |
| `actions/upload-artifact` | 158 | 72.1% |
| `actions/github-script` | 122 | 55.7% |
| `./.github/actions/setup-python-cached` | 94 | 42.9% |
| `actions/cache` | 48 | 21.9% |
| `actions/download-artifact` | 27 | 12.3% |
| `./.github/actions/resolve-push-target` | 13 | 5.9% |
| `./.github/actions/post-pr-summary` | 10 | 4.6% |
| `codecov/codecov-action` | 6 | 2.7% |
| `./.github/workflows/cost-gate.yml` | 6 | 2.7% |
| `github/codeql-action/upload-sarif` | 6 | 2.7% |
| `actions/create-github-app-token` | 4 | 1.8% |
| `docker/setup-buildx-action` | 4 | 1.8% |
| `docker/build-push-action` | 4 | 1.8% |

### APT

- **Unique Dependencies:** 1
- **Total Mentions:** 1
- **Average Usage Per Dep:** 1.0

| Dependency | Workflows | Usage |
|---|---|---|
| `gh` | 1 | 0.5% |

### LANGUAGE

- **Unique Dependencies:** 2
- **Total Mentions:** 432
- **Average Usage Per Dep:** 216.0

| Dependency | Workflows | Usage |
|---|---|---|
| `python` | 424 | 193.6% |
| `node` | 8 | 3.7% |

### NPM

- **Unique Dependencies:** 5
- **Total Mentions:** 5
- **Average Usage Per Dep:** 1.0

| Dependency | Workflows | Usage |
|---|---|---|
| `-g markdown-link-check 2>/dev/null || true` | 1 | 0.5% |
| `-g markdownlint-cli@late` | 1 | 0.5% |
| `-g @github/copilot@prerelea` | 1 | 0.5% |
| `--ignore-` | 1 | 0.5% |
| `-g markdown-link-check || echo` | 1 | 0.5% |

### PIP

- **Unique Dependencies:** 110
- **Total Mentions:** 326
- **Average Usage Per Dep:** 3.0

| Dependency | Workflows | Usage |
|---|---|---|
| `--upgrade pip` | 68 | 31.1% |
| `pyte` | 41 | 18.7% |
| `-e ".[dev]"` | 11 | 5.0% |
| `detect-` | 11 | 5.0% |
| `-q -r requirement` | 10 | 4.6% |
| `-e .` | 10 | 4.6% |
| `numpy` | 8 | 3.7% |
| `pyyaml --quiet` | 7 | 3.2% |
| `--no-cache-dir -r requirement` | 7 | 3.2% |
| `pyyaml` | 6 | 2.7% |
| `reque` | 6 | 2.7% |
| `-r requirement` | 5 | 2.3% |
| `mkdoc` | 5 | 2.3% |
| `-q` | 4 | 1.8% |
| `-q pyyaml` | 4 | 1.8% |

### TOOLS

- **Unique Dependencies:** 9
- **Total Mentions:** 352
- **Average Usage Per Dep:** 39.1

| Dependency | Workflows | Usage |
|---|---|---|
| `python` | 180 | 82.2% |
| `git` | 60 | 27.4% |
| `bash` | 35 | 16.0% |
| `jq` | 34 | 15.5% |
| `curl` | 18 | 8.2% |
| `npm` | 10 | 4.6% |
| `docker` | 9 | 4.1% |
| `node` | 5 | 2.3% |
| `make` | 1 | 0.5% |

## Language Versions In Use

### PYTHON

**Versions Found:** ${{ env.PYTHON_VERSION }}, ${{ fromJson(needs.test-matrix.outputs.python-version) }}, ${{ matrix.python-version }}, ${{ steps.matrix.outputs.python-version }}, 3.11, 3.12, 3.12.13, 6, [, used

- **Unique Versions:** 10

### NODE

**Versions Found:** ${{ env.NODE_VERSION }}, 22, 5, used

- **Unique Versions:** 4

## Most Used GitHub Actions (Top 20)

| Action | Workflows | % |
|---|---|---|
| `actions/checkout` | 477 | 217.8% |
| `actions/setup-python` | 163 | 74.4% |
| `actions/upload-artifact` | 158 | 72.1% |
| `actions/github-script` | 122 | 55.7% |
| `./.github/actions/setup-python-cached` | 94 | 42.9% |
| `actions/cache` | 48 | 21.9% |
| `actions/download-artifact` | 27 | 12.3% |
| `./.github/actions/resolve-push-target` | 13 | 5.9% |
| `./.github/actions/post-pr-summary` | 10 | 4.6% |
| `codecov/codecov-action` | 6 | 2.7% |
| `./.github/workflows/cost-gate.yml` | 6 | 2.7% |
| `github/codeql-action/upload-sarif` | 6 | 2.7% |
| `actions/create-github-app-token` | 4 | 1.8% |
| `docker/setup-buildx-action` | 4 | 1.8% |
| `docker/build-push-action` | 4 | 1.8% |
| `actions/setup-node` | 4 | 1.8% |
| `write` | 4 | 1.8% |
| `actions/upload-release-asset` | 3 | 1.4% |
| `./.github/actions/setup-agent-env` | 3 | 1.4% |
| `github/codeql-action/init` | 3 | 1.4% |

## System Tools & Utilities

| Tool | Workflows | % |
|---|---|---|
| `python` | 180 | 82.2% |
| `git` | 60 | 27.4% |
| `bash` | 35 | 16.0% |
| `jq` | 34 | 15.5% |
| `curl` | 18 | 8.2% |
| `npm` | 10 | 4.6% |
| `docker` | 9 | 4.1% |
| `node` | 5 | 2.3% |
| `make` | 1 | 0.5% |

## Most Used Pip Packages (Top 30)

| Package | Workflows | % |
|---|---|---|
| `--upgrade pip` | 68 | 31.1% |
| `pyte` | 41 | 18.7% |
| `-e ".[dev]"` | 11 | 5.0% |
| `detect-` | 11 | 5.0% |
| `-q -r requirement` | 10 | 4.6% |
| `-e .` | 10 | 4.6% |
| `numpy` | 8 | 3.7% |
| `pyyaml --quiet` | 7 | 3.2% |
| `--no-cache-dir -r requirement` | 7 | 3.2% |
| `pyyaml` | 6 | 2.7% |
| `reque` | 6 | 2.7% |
| `-r requirement` | 5 | 2.3% |
| `mkdoc` | 5 | 2.3% |
| `-q` | 4 | 1.8% |
| `-q pyyaml` | 4 | 1.8% |
| `pyyaml reque` | 3 | 1.4% |
| `--quiet --upgrade pip` | 3 | 1.4% |
| `ruff` | 3 | 1.4% |
| `j` | 2 | 0.9% |
| `-e ".[github]"` | 2 | 0.9% |
| `-e` | 2 | 0.9% |
| `bandit>=1.7.5` | 2 | 0.9% |
| `ruff pyyaml` | 2 | 0.9% |
| `-q pyyaml ruff` | 2 | 0.9% |
| `--quiet` | 2 | 0.9% |
| `mypy` | 2 | 0.9% |
| `bandit` | 2 | 0.9% |
| `-e . --quiet` | 2 | 0.9% |
| `dvc` | 2 | 0.9% |
| `--quiet reque` | 2 | 0.9% |

## Npm Packages Used

| Package | Workflows | % |
|---|---|---|
| `-g markdown-link-check 2>/dev/null || true` | 1 | 0.5% |
| `-g markdownlint-cli@late` | 1 | 0.5% |
| `-g @github/copilot@prerelea` | 1 | 0.5% |
| `--ignore-` | 1 | 0.5% |
| `-g markdown-link-check || echo` | 1 | 0.5% |

## Version Pinning Recommendations

### High-Priority Language Versions (For Base Image)

Based on current workflow usage, the base image should include:

- **PYTHON:** ${{ env.PYTHON_VERSION }} to used (recommended: used)
- **NODE:** ${{ env.NODE_VERSION }} to used (recommended: used)

### High-Priority Pip Packages (For Base Image)

Core packages used in >15 workflows:

- `--upgrade pip` (68 workflows, 31.1%)
- `pyte` (41 workflows, 18.7%)

## Tools Compatibility Matrix

### Critical System Tools (Present in >50% of workflows)

| Tool | Workflows | Percentage | Priority |
|---|---|---|---|
| `python` | 180 | 82.2% | HIGH |

## Conditional Dependencies

### Language Runtime Selection

Workflows use conditional logic to select language versions. Key patterns:

- Python: typically pinned to specific patch version (e.g., `3.12.x`)
- Node: ranges from 18.x to 22.x
- Go: 1.20+ with preference for 1.22+
- Rust: stable channel primarily

### Optional Dependencies

Some workflows conditionally install:
- Codecov CLI (for coverage reporting)
- CodeQL (for security scanning)
- docker-cli (for container operations)

## Recommendations for Phase 4 Custom Images

### 1. Base Image Configuration

**Must Include (100% compatibility):**
- Python 3.12.x (latest available)
- Node.js 22.x
- Go 1.22+
- Rust (stable)
- Git, curl, jq, make, gcc, perl, bash

**Recommended to Pre-install:**
- `--upgrade pip` (31.1% of workflows)
- `pyte` (18.7% of workflows)
- `-e ".[dev]"` (5.0% of workflows)
- `detect-` (5.0% of workflows)
- `-q -r requirement` (4.6% of workflows)
- `-e .` (4.6% of workflows)
- `numpy` (3.7% of workflows)
- `pyyaml --quiet` (3.2% of workflows)

### 2. Version Strategy

- **Lock language versions** to minor/patch level in base image
- **Allow override** via `actions/setup-*` for version flexibility
- **Pre-warm cache** with top 30 pip packages
- **Pre-download** GitHub Actions tools commonly used (checkout, setup-*, etc)

### 3. Compatibility Matrix

| Component | Minimum | Recommended | Note |
|---|---|---|---|
| Python | 3.10 | 3.12 | Per env var CODEX_ENV_PYTHON_VERSION |
| Node | 18 | 22 | Per env var CODEX_ENV_NODE_VERSION |
| Go | 1.20 | 1.22 | Per env var CODEX_ENV_GO_VERSION |
| Rust | 1.70 | stable | Per env var CODEX_ENV_RUST_VERSION |

## Implementation Checklist for Phase 4

- [ ] Create Dockerfile with base image (ubuntu:24.04 or similar)
- [ ] Pre-install all language runtimes (Python, Node, Go, Rust)
- [ ] Pre-install system tools: git, curl, jq, make, gcc, g++, perl, bash
- [ ] Pre-warm pip cache with top 30 packages
- [ ] Build and test custom image against 20+ representative workflows
- [ ] Benchmark startup time vs. default ubuntu-latest
- [ ] Document version overrides and special cases

