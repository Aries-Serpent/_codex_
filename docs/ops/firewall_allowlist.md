<!-- BEGIN: FIREWALL_ALLOWLIST -->

# Firewall Allow-List — _codex_ Repository

**Last Updated:** 2026-06-22

> **Registered:** 2026-02-28  
> **Scope:** All outbound connections made by the codebase, CI/CD pipelines,  
> and developer tooling on any machine running this repository.  
> **Primary test machine:** Intel Core Ultra 5 135U · Windows 11 Pro  
> (see `docs/ops/primary_test_machine.md`)  
> **Maintained by:** @mbaetiong

---

## How to Use This Document

Every entry is tagged with the context in which the connection is made:

| Tag | Meaning |
|-----|---------|
| `[CI]` | Required only in GitHub Actions runners |
| `[DEV]` | Required on developer machines |
| `[RUNTIME]` | Required by the running application (server / API) |
| `[OPT]` | Optional / feature-flagged — only needed when the feature is enabled |
| `[TEST]` | Required during test execution |
| `[WIN]` | Extra note for Windows 11 primary test machine |

---

## 1. Python Package Registries

These must be reachable any time `pip install` or `pip download` is run.

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `pypi.org` | 443 | HTTPS | `[DEV]` `[CI]` | Primary PyPI index — all `pip install` |
| `files.pythonhosted.org` | 443 | HTTPS | `[DEV]` `[CI]` | PyPI wheel / sdist downloads |
| `download.pytorch.org` | 443 | HTTPS | `[DEV]` `[CI]` | CPU-only PyTorch wheels (`--extra-index-url https://download.pytorch.org/whl/cpu`) |
| `test.pypi.org` | 443 | HTTPS | `[CI]` | Test PyPI — pre-release publish validation |

> **Windows note `[WIN]`:** All four hosts must be allowed. The `download.pytorch.org` wheel server is the only source of `torch==2.x+cpu` wheels for Windows.

---

## 2. GitHub & GitHub Actions

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `github.com` | 443 | HTTPS / Git | `[DEV]` `[CI]` | Clone, push, pull, PR operations |
| `api.github.com` | 443 | HTTPS | `[CI]` `[RUNTIME]` | GitHub REST API (CodeQL upload, PR checks, Dependabot, labeler, `codex_bridge` GitHub client) |
| `uploads.github.com` | 443 | HTTPS | `[CI]` | Artifact and SARIF upload |
| `raw.githubusercontent.com` | 443 | HTTPS | `[CI]` `[DEV]` | Raw file downloads in CI scripts |
| `codeload.github.com` | 443 | HTTPS | `[CI]` | Action / repo archive downloads |
| `objects.githubusercontent.com` | 443 | HTTPS | `[CI]` | LFS and release asset downloads |
| `marketplace.github.com` | 443 | HTTPS | `[CI]` | GitHub Actions Marketplace metadata |
| `token.actions.githubusercontent.com` | 443 | HTTPS | `[CI]` | OIDC token endpoint for sigstore / PyPI trusted publishing |
| `aries-serpent.github.io` | 443 | HTTPS | `[CI]` | GitHub Pages deployment destination |

---

## 3. GitHub Actions — Third-Party Action Hosts

All `uses:` actions in `.github/workflows/` fetch their bundles from:

| Host | Port | Protocol | Context | Actions sourced |
|------|------|----------|---------|-----------------|
| `github.com` _(above)_ | 443 | HTTPS | `[CI]` | `actions/*`, `github/codeql-action/*`, `peter-evans/create-pull-request`, `pypa/gh-action-pypi-publish`, `codecov/codecov-action`, `docker/build-push-action`, `docker/setup-buildx-action`, `anchore/sbom-action`, `anchore/scan-action`, `rustsec/audit-check`, `dtolnay/rust-toolchain`, `actions-rust-lang/setup-rust-toolchain` |

---

## 4. HuggingFace Hub (ML Models & Datasets)

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `huggingface.co` | 443 | HTTPS | `[DEV]` `[CI]` `[RUNTIME]` `[OPT]` | Model card pages, API queries |
| `cdn-lfs.huggingface.co` | 443 | HTTPS | `[DEV]` `[RUNTIME]` `[OPT]` | Large File Storage — model weight downloads (`from_pretrained`) |
| `cdn-lfs-us-1.huggingface.co` | 443 | HTTPS | `[DEV]` `[RUNTIME]` `[OPT]` | US-region LFS CDN node |

> **Note:** `from_pretrained(...)` calls in `src/codex_ml/serving/model_loader.py`, `src/codex_ml/hf_loader.py`, and the `RAGPipeline` will contact these hosts. Set `HF_DATASETS_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` to disable in fully air-gapped environments.

---

## 5. Experiment Tracking Services

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `<your-mlflow-host>` (configurable) | 5000 | HTTP/S | `[RUNTIME]` `[OPT]` | MLflow tracking server — configured via `CODEX_MLFLOW_URI` or `mlflow-tracking-uri` Hydra override |
| `api.wandb.ai` | 443 | HTTPS | `[RUNTIME]` `[OPT]` | Weights & Biases run logging — only when `wandb` extra installed |
| `files.wandb.ai` | 443 | HTTPS | `[RUNTIME]` `[OPT]` | W&B artifact uploads |

> **Default:** CI uses `file:./artifacts/mlruns` (local filesystem). Remote MLflow and W&B are opt-in.

---

## 6. Container Registries

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `ghcr.io` | 443 | HTTPS | `[CI]` | GitHub Container Registry — `docker/build-push-action` push target |
| `registry-1.docker.io` | 443 | HTTPS | `[CI]` `[DEV]` | Docker Hub base image pulls |
| `auth.docker.io` | 443 | HTTPS | `[CI]` `[DEV]` | Docker Hub authentication |
| `production.cloudflare.docker.com` | 443 | HTTPS | `[CI]` | Docker Hub CDN layer downloads |

---

## 7. Security & Code-Quality Services

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `fulcio.sigstore.dev` | 443 | HTTPS | `[CI]` | Sigstore Fulcio CA — code signing certificate issuance |
| `rekor.sigstore.dev` | 443 | HTTPS | `[CI]` | Sigstore Rekor transparency log — signing record upload |
| `codecov.io` | 443 | HTTPS | `[CI]` | Coverage report upload (`codecov/codecov-action`) |
| `keybase.io` | 443 | HTTPS | `[CI]` `[OPT]` | Codecov GPG key verification |

---

## 8. Rust / Cargo Ecosystem

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `crates.io` | 443 | HTTPS | `[CI]` `[DEV]` | Cargo crate registry index |
| `static.crates.io` | 443 | HTTPS | `[CI]` `[DEV]` | Crate tarball downloads |
| `index.crates.io` | 443 | HTTPS | `[CI]` `[DEV]` | Sparse registry index (Cargo ≥ 1.68) |
| `rustsec.org` | 443 | HTTPS | `[CI]` | `rustsec/audit-check` advisory database |

---

## 9. npm / Node.js Ecosystem

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `registry.npmjs.org` | 443 | HTTPS | `[CI]` `[DEV]` | npm package downloads (JS tooling, lock file packages) |

---

## 10. JavaScript CDN Assets (Documentation & Dashboard)

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `cdn.jsdelivr.net` | 443 | HTTPS | `[RUNTIME]` `[OPT]` | Chart.js (`cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js`) and Mermaid diagram renderer (`cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js`) — used by status dashboards |
| `d3js.org` | 443 | HTTPS | `[RUNTIME]` `[OPT]` | D3.js visualisation library |

---

## 11. External API Integrations

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `{subdomain}.zendesk.com` | 443 | HTTPS | `[RUNTIME]` `[OPT]` | Zendesk knowledge-base sync (`src/services/crawler/zendesk_sync.py`) — subdomain is customer-configured |
| `hooks.slack.com` | 443 | HTTPS | `[RUNTIME]` `[OPT]` | Slack incoming webhook — alert notifications |
| `{org}.webhook.office.com` | 443 | HTTPS | `[RUNTIME]` `[OPT]` | Microsoft Teams incoming webhook |
| `api.duckduckgo.com` | 443 | HTTPS | `[RUNTIME]` `[OPT]` | DuckDuckGo search API — used by deep-research task processor |

---

## 12. AWS / Cloud Metadata

| Host / URL | Port | Protocol | Context | Purpose |
|-----------|------|----------|---------|---------|
| `169.254.169.254` | 80 | HTTP | `[RUNTIME]` `[OPT]` | AWS EC2 IMDSv2 metadata — `src/codex/ci/cache_manager.py` and `tests/conftest_shared.py` probe this endpoint when running inside an EC2 instance. **Must NOT be reachable from the Windows dev machine unless running inside AWS.** |

---

## 13. OS-Level Package Sources

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `apt.llvm.org` | 443 | HTTPS | `[CI]` | LLVM/Clang apt mirror — used in `scripts/` CI helpers for building native extensions |
| `packages.microsoft.com` | 443 | HTTPS | `[WIN]` `[OPT]` | Microsoft apt/winget repository — Visual C++ Build Tools (required for some Python native wheels on Windows) |
| `visualstudio.microsoft.com` | 443 | HTTPS | `[WIN]` `[OPT]` | VS Build Tools installer download |

---

## 14. Pre-commit & Developer Tool Metadata

| Host / URL Pattern | Port | Protocol | Context | Purpose |
|-------------------|------|----------|---------|---------|
| `pre-commit.com` | 443 | HTTPS | `[DEV]` | pre-commit hook metadata |
| `astral.sh` | 443 | HTTPS | `[DEV]` | Ruff / uv installer (`curl -LsSf https://astral.sh/ruff/install.sh`) |

---

## Summary — Minimal Allowlist for Primary Test Machine (Windows 11 Dev)

This is the minimum set of outbound HTTPS rules needed for a developer on the  
registered primary test machine to clone, install, test, and push changes:

```
# Python packages
ALLOW HTTPS pypi.org
ALLOW HTTPS files.pythonhosted.org
ALLOW HTTPS download.pytorch.org       # CPU torch wheels

# GitHub
ALLOW HTTPS github.com
ALLOW HTTPS api.github.com
ALLOW HTTPS raw.githubusercontent.com
ALLOW HTTPS objects.githubusercontent.com

# ML models (optional — set TRANSFORMERS_OFFLINE=1 to disable)
ALLOW HTTPS huggingface.co
ALLOW HTTPS cdn-lfs.huggingface.co
ALLOW HTTPS cdn-lfs-us-1.huggingface.co
```

---

## Summary — Full CI Runner Allowlist

```
# All of the above PLUS:
ALLOW HTTPS uploads.github.com
ALLOW HTTPS codeload.github.com
ALLOW HTTPS token.actions.githubusercontent.com
ALLOW HTTPS aries-serpent.github.io
ALLOW HTTPS ghcr.io
ALLOW HTTPS registry-1.docker.io
ALLOW HTTPS auth.docker.io
ALLOW HTTPS production.cloudflare.docker.com
ALLOW HTTPS fulcio.sigstore.dev
ALLOW HTTPS rekor.sigstore.dev
ALLOW HTTPS codecov.io
ALLOW HTTPS crates.io
ALLOW HTTPS static.crates.io
ALLOW HTTPS index.crates.io
ALLOW HTTPS rustsec.org
ALLOW HTTPS registry.npmjs.org
ALLOW HTTPS test.pypi.org
```

---

## Not Required (Block or Leave Default-Deny)

The following domains appear in source code **only as test fixtures, negative  
examples, or documentation references** and must **NOT** be added to the allowlist:

| Domain | Reason present in code | Action |
|--------|----------------------|--------|
| `attacker.com`, `evil.com`, `malicious.org` | Security test fixtures | **BLOCK** |
| `169.254.169.254` | AWS IMDS — not needed on Windows dev | **BLOCK on dev machine** |
| `api.stackexchange.com` | Documentation link only | No action needed |
| `notebooklm.google.com` | Documentation reference | No action needed |
| `lite.datasette.io` | Documentation link | No action needed |

<!-- END: FIREWALL_ALLOWLIST -->
