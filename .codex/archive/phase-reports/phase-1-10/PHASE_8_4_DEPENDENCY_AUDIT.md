# 📦 PHASE 8.4 DEPENDENCY AUDIT — Workstream 8.4.1

**Track Lead:** packaging-validation-agent (Track 8.4)
**Authority:** @mbaetiong — D-tier autonomy — GO CONTINUE (all gates)
**Campaign:** Phase 8 Multi-Agent Deployment
**Branch:** `copilot/deploy-phase-8-agents`
**Generated:** 2026-07-03T01:36Z
**Session type:** AUDIT ONLY (no dependency, source, or workflow files modified)
**Source brief:** `.codex/PHASE_8_4_DEPENDENCY_STANDARDIZATION_BRIEF.md`

---

## 1. Executive Summary

This audit inventories **every** Python dependency declaration in the repository plus the
Node.js, Rust, Ruby, and Go ecosystem manifests. Data is parsed directly from the files on
`copilot/deploy-phase-8-agents`.

**Scope covered:**
- 1 × `pyproject.toml` (43 base deps + 30 optional-dependency extras groups)
- 10 × top-level `requirements-*.txt` files
- 7 × `requirements/*.txt` files (base, dev, docker, extras, agent, lock-eval, lock-ml)
- Ecosystem manifests: `package.json`, `Cargo.toml`, and their lock files

**Headline findings:**

| Metric | Value |
|--------|-------|
| Distinct Python packages (direct declarations) | **101** |
| Python requirement source files (excl. pyproject) | **17** |
| pyproject optional-dependency extras groups | **30** |
| Packages declared in ≥3 files (consolidation targets) | **31** |
| Packages with mismatched specifiers across files (conflicts) | **35** |
| **Hard** version conflicts (mutually unsatisfiable) | **3** (pytest-cov, pytest floor, pydantic/fastapi major-version split) |
| Fully unpinned declarations | **18** (14 concentrated in `requirements/dev.txt`) |
| Python lock files present | 4 (`uv.lock`, `requirements/lock.txt`, `requirements/lock-eval.txt`, `requirements/lock-ml.txt`) |
| Ecosystems WITHOUT a lock file | 0 active (Ruby/Go absent → N/A) |

**Overall posture:** The security-critical crypto/transport packages (cryptography, PyJWT,
urllib3, requests, certifi, jinja2, torch, transformers) are consistently pinned to modern,
CVE-patched floors in the *primary* surfaces (`requirements.txt`, `pyproject.toml`). The main
risks are **specifier drift** across the many parallel requirement files (11 top-level + 7 in
`requirements/`) and **stale/loose floors** in the secondary surfaces (`requirements/docker.txt`,
`requirements/dev.txt`). These are standardization problems, not (yet) known-exploit problems, and
feed directly into Workstream 8.4.2.

---

## 2. Complete Dependency Inventory (by file)

### 2.1 pyproject.toml — `[project].dependencies` (43 packages, requires-python `>=3.12`)

| Package | Specifier | Package | Specifier |
|---------|-----------|---------|-----------|
| omegaconf | >=2.3 | typer | >=0.12 |
| hydra-core | ==1.3.2 | libcst | >=1.0.0 |
| pydantic | >=2.4 | radon | >=6.0.1 |
| pydantic-settings | >=2.14.2 | parso | >=0.8.0 |
| pyyaml | >=6.0 | jinja2 | >=3.1.6 |
| pandas | >=3.0.3,<4 | certifi | >=2026.6.17 |
| marshmallow | >=3.7.1,<5 | filelock | >=3.29.0 |
| transformers | >=5.12.1,<6 | idna | >=3.18 |
| peft | >=0.19.1,<1 | urllib3 | >=2.7.0 |
| accelerate | >=1.14.0,<2 | requests | >=2.32.4 |
| datasets | >=5.0.0,<6 | defusedxml | >=0.7.1 |
| ray[serve] | >=2.9,<3 | cryptography | >=49.0.0,<50.0.0 |
| fastapi | >=0.135.3,<1 | PyJWT | >=2.13.0,<3.0.0 |
| litestar | >=2.22.0,<3 | PyNaCl | >=1.5.0,<2.0.0 |
| slowapi | >=0.1.9 | scikit-learn | >=1.9.0,<2 |
| starlette | >=1.0.1,<2 | duckdb | >=1.5.4 |
| httpx | >=0.26,<1 | sentencepiece | >=0.1.99 |
| evidently | >=0.7.21,<1 | torch | >=2.6.1,<3.0.0 |
| numpy | >=2.4.6,<3 | | |

**Optional-dependency extras groups (30):** analysis, ast, auth, cli, eval, ge, marshmallow-v4,
configs, hydra, dev, dataops, dist, github, gpu, logging, metrics, ml, monitoring, ops, playwright,
perf, sharding, plugins, rag, symbolic, test-core, tokenizer, tokenizers, tracking, train, all.
`version = "0.1.0"`, `license = {text = "MIT"}` — PEP 621 `[project]` table is present and valid
(see §6).

### 2.2 Top-level `requirements-*.txt`

| File | Purpose | Exact `==` | Range | Unpinned | Notable pins |
|------|---------|:---:|:---:|:---:|--------------|
| `requirements.txt` | Core runtime | 2 | 19 | 1 | cryptography==49.0.0, pytest-cov==5.0.0, torch>=2.6.1,<3 |
| `requirements-dev.txt` | Dev tooling | 0 | 22 | 0 | pytest>=9.0.3,<10, cryptography>=49.0.0,<50 |
| `requirements-test.txt` | CI reproducibility | 9 | 6 | 0 | pytest==9.0.3, pytest-cov==5.0.0, hydra-core==1.3.2 |
| `requirements-minimal.txt` | Baseline | 0 | 23 | 3 | ruff>=0.15.15, pip-audit>=2.10.1 |
| `requirements-optional.txt` | Feature extras | 0 | 13 | 0 | nltk>=3.9.3, twisted>=24.7.0, configobj>=5.0.9 |
| `requirements-eval.txt` | Eval stack | 7 | 1 | 0 | scikit-learn==1.9.0, lm-eval==0.4.12, nltk==3.9.4 |
| `requirements-ml-cpu.txt` | CPU ML | 4 | 3 | 0 | torch==2.11.0+cpu, tokenizers==0.22.1 |
| `requirements-ml-lite.txt` | Lite CPU ML | 0 | 4 | 0 | torch>=2.6.1,<3, numpy>=2.4.6,<3 |
| `requirements-notebook.txt` | Notebook | 4 | 0 | 0 | jupyterlab==4.5.9, matplotlib==3.10.9 |
| `requirements-audio-transcription.txt` | Audio | 3 | 0 | 0 | faster-whisper==1.2.1, pyannote.audio==3.3.2 |

### 2.3 `requirements/` subdirectory

| File | Purpose | Exact `==` | Range | Unpinned | Notable |
|------|---------|:---:|:---:|:---:|---------|
| `requirements/base.txt` | Base runtime pins | 8 | 8 | 0 | torch==2.11.0 (GPU), transformers==5.12.1, numpy==2.4.6 |
| `requirements/dev.txt` | Dev bundle | 3 | 10 | **14** | pytest-cov==7.0.0, pre-commit==4.5.1, nox==2026.4.10 |
| `requirements/docker.txt` | Container runtime | 0 | 4 | 0 | fastapi>=0.95, pydantic>=1.10, requests>=2.31, uvicorn[standard]>=0.22 |
| `requirements/extras.txt` | Playwright extra | 0 | 1 | 0 | playwright>=1.40 |
| `requirements/agent.txt` | Copilot agent env | 0 | 32 | 0 | pip>=26.1.2, mkdocs-material>=9.7.6, pyjwt[crypto]>=2.13.0 |
| `requirements/lock-eval.txt` | Eval lock | 8 | 0 | 0 | Fully pinned mirror of eval stack |
| `requirements/lock-ml.txt` | ML(cpu) lock | 7 | 0 | 0 | Fully pinned mirror of ML CPU stack |
| `requirements/lock.txt` | uv-compiled full lock | 255 pkgs | — | — | Autogenerated by `uv pip compile` (transitive closure) |

---

## 3. Version-Pin Analysis

### 3.1 Aggregate classification (direct declarations across all 17 requirement files)

| Class | Count (declarations) | Share |
|-------|:---:|:---:|
| Exact-pinned (`==`) | 55 | ~35% |
| Range/bounded (`>=`, `<`, `~=`, `^`) | 146 | ~55% |
| Fully unpinned | 18 | ~10% |

> Note: counts are per-declaration (a package appearing in 5 files counts 5×). Distinct package
> count is **101**. The `pyproject.toml` base table adds 43 range-style declarations on top.

### 3.2 Unpinned / loosely-pinned offenders

**Fully unpinned (no version specifier) — 18 declarations:**

| File | Unpinned packages |
|------|-------------------|
| `requirements/dev.txt` | black, isort, flake8, mypy, bandit, defusedxml, semgrep, detect-secrets, yamllint, shellcheck-py, pip-audit, pandas, pyarrow, zstandard (**14**) |
| `requirements-minimal.txt` | types-jsonschema, types-PyYAML, types-requests (3) |
| `requirements.txt` | nox (1) |

**Assessment:** `requirements/dev.txt` is the single largest source of non-determinism — 14 of the
18 fully unpinned declarations. Unpinned linters/scanners (semgrep, bandit, mypy) can silently
change behavior across CI runs. `pandas`, `pyarrow`, and `zstandard` unpinned here can also pull
majors that conflict with the `pandas>=3.0.3,<4` floor used everywhere else.

**Loosely-pinned floors that lag the primary surfaces (upgrade candidates):**
- `requirements/docker.txt`: `pydantic>=1.10` (allows Pydantic v1 — everywhere else requires v2),
  `fastapi>=0.95`, `requests>=2.31` (below the `>=2.34.2` security floor), `uvicorn[standard]>=0.22`.
- `requirements/agent.txt` & `requirements/dev.txt`: `pytest>=8.4` / `pytest>=8.0` — below the
  `>=9.0.3` floor mandated by CVE-2025-71176 in the primary files.

---

## 4. Duplicate / Conflict Report

**31 packages** are declared in ≥3 files; **35 packages** carry mismatched specifiers across files.
Below are the material conflicts, split by severity.

### 4.1 HARD conflicts (mutually unsatisfiable — must resolve in 8.4.2)

| Package | Conflicting specifiers | Files | Problem |
|---------|-----------------------|-------|---------|
| **pytest-cov** | `==7.0.0` vs `>=4.1.0,<6.0.0` vs `==5.0.0` | `requirements/dev.txt` vs `requirements-dev.txt`/`requirements-minimal.txt` vs `requirements.txt`/`requirements-test.txt` | 7.0.0 is **excluded** by `<6.0.0`; installing both bundles cannot be satisfied. |
| **pytest** | `>=8.0` / `>=8.4` vs `>=9.0.3,<10.0.0` / `==9.0.3` | `requirements/dev.txt`, `requirements/agent.txt` vs primary files | Lower floors 8.x **violate the CVE-2025-71176 security floor** (`>=9.0.3`) asserted elsewhere. |
| **pydantic / fastapi** | pydantic `>=1.10` & fastapi `>=0.95` vs pydantic `>=2.11.7` & fastapi `>=0.135.3,<1` | `requirements/docker.txt` vs `requirements/base.txt` / `requirements-dev.txt` | Docker surface permits Pydantic **v1** and ancient FastAPI — a major-version split from the rest of the project. |

### 4.2 SOFT conflicts (satisfiable but drift — consolidate)

| Package | Distinct specifiers observed | # files |
|---------|------------------------------|:---:|
| torch | `>=2.6.1,<3.0.0`, `==2.11.0`, `==2.11.0+cpu` | 5 |
| transformers | `>=5.12.1,<6`, `==5.12.1` | 6 |
| sentencepiece | `>=0.1.99`, `==0.2.1` | 5 |
| requests | `>=2.34.2`, `>=2.34.2,<3`, `>=2.31` | 5 |
| pydantic | `>=2.4,<3`, `>=2.5.0`, `>=2.11.7`, `>=1.10`, `>=2.7` | 5 |
| pytest-randomly | `>=3.16,<5`, `==4.0.1`, `>=3.15`, `>=4.0` | 5 |
| nox | `(unpinned)`, `>=2026.4.10,<2027`, `==2026.4.10`, `>=2026.4.10` | 4 |
| numpy | `>=2.4.6,<3`, `==2.4.6` | 4 |
| accelerate | `>=1.14.0,<2`, `>=1.14.0`, `==1.14.0` | 4 |
| peft | `>=0.19.1,<1`, `==0.19.1` | 4 |
| defusedxml | `>=0.7.1,<1.0.0`, `>=0.7.1`, `(unpinned)` | 4 |
| jsonschema | `>=4.26.0`, `>=4.22.0` | 4 |
| pytest-xdist | `>=3.5.0,<4.0.0`, `==3.8.0`, `>=3.5` | 4 |
| cryptography | `==49.0.0`, `>=49.0.0,<50.0.0` | 2 |
| hydra-core | `==1.3.2`, `>=1.3.2` | 3 |
| nltk | `>=3.9.3`, `==3.9.4` | 3 |
| pandas | `>=3.0.3,<4`, `(unpinned)`, `==3.0.3` | 3 |
| pre-commit | `>=3,<5`, `==4.5.1`, `>=3.7` | 3 |
| omegaconf | `>=2.3`, `==2.3.0` | 2 |
| typer | `>=0.12`, `>=0.12.5` | 3 |
| rouge-score / sacrebleu | range vs `==` mirror | 3 each |

> The soft conflicts are individually satisfiable (the `==` lock files sit inside the range floors)
> but represent maintenance burden: every version bump must be edited in up to 6 places.

### 4.3 Documented-intentional divergence (leave as-is)

- **torch** `==2.11.0` (GPU/CUDA, `requirements/base.txt`) vs `==2.11.0+cpu`
  (`requirements-ml-cpu.txt` / `requirements/lock-ml.txt`): the CPU build is intentionally sourced
  from `https://download.pytorch.org/whl/cpu`. Inline comments confirm this is deliberate. Flag for
  documentation in 8.4.2, not remediation.

---

## 5. Lock-File Gap Analysis

| Ecosystem | Manifest | Lock file | Status |
|-----------|----------|-----------|--------|
| Python (project) | `pyproject.toml` | `uv.lock` (353 pkgs, `requires-python>=3.12`) | ✅ Present |
| Python (pip compile) | `requirements/base.txt` + extras | `requirements/lock.txt` (255 pkgs, uv-compiled) | ✅ Present |
| Python (eval) | `requirements-eval.txt` | `requirements/lock-eval.txt` | ✅ Present |
| Python (ML cpu) | `requirements-ml-cpu.txt` | `requirements/lock-ml.txt` | ✅ Present |
| Node.js | `package.json` | `package-lock.json` (lockfileVersion 3) | ⚠️ Present but **empty** — zero third-party runtime deps declared (scripts-only harness). Acceptable; no action needed unless deps are added. |
| Rust | `Cargo.toml` (14 direct crates) | `Cargo.lock` | ✅ Present |
| Ruby | — | — | N/A (no Gemfile) |
| Go | — | — | N/A (no go.mod) |

**Gaps / observations:**
1. **No dedicated lock for several install surfaces:** `requirements-dev.txt`, `requirements-minimal.txt`,
   `requirements-optional.txt`, `requirements-notebook.txt`, `requirements-audio-transcription.txt`,
   and `requirements-ml-lite.txt` have **no compiled lock**. Their transitive closures are not
   reproducibly pinned. `requirements/lock.txt` only compiles the pyproject + base + a subset of extras.
2. **Two overlapping Python lock strategies** coexist: root `uv.lock` (uv workspace lock) and
   `requirements/lock.txt` (uv-pip-compiled). 8.4.2 should declare one as authoritative to avoid drift.
3. **Node.js lock is a stub** — fine today (no dependencies), but CI should assert it stays in sync
   if any dependency is ever added.

---

## 6. PEP 621 Compliance Check (`pyproject.toml`)

| Check | Expected | Observed | Status |
|-------|----------|----------|:---:|
| `[project]` table present | ✅ | present | ✅ |
| `name` non-empty | string | `"codex-ml"` | ✅ |
| `version` or `dynamic` | present | `version = "0.1.0"` | ✅ |
| `requires-python` | `>=3.x` | `>=3.12` | ✅ |
| `license` | SPDX or `{file=}`/`{text=}` | `{text = "MIT"}` | ⚠️ Valid but uses deprecated table form; PEP 639 prefers SPDX string `license = "MIT"` |
| `dependencies` | list | list (43 items) | ✅ |
| `optional-dependencies` | table of lists | 30 groups | ✅ |

**Note (PEP621_002-adjacent):** `license = {text = "MIT"}` is accepted by current tooling but the
table form is deprecated under PEP 639 in favour of the SPDX expression string. Low priority; queue
for 8.4.2.

---

## 7. Vulnerability-Review Candidates

No live CVE lookup performed this session (per task scope). The following are flagged for automated
scanning (pip-audit / GitHub Advisory DB / Dependabot) in 8.4.2/8.4.3, prioritised by staleness of
floor:

**High priority (stale/loose floors that could resolve to vulnerable versions):**
- `requirements/docker.txt`: `requests>=2.31` (below the `>=2.34.2` fix floor for CVE-2024-35195 /
  CVE-2024-47081), `pydantic>=1.10`, `fastapi>=0.95`, `uvicorn[standard]>=0.22`.
- `requirements/dev.txt`: **unpinned** `semgrep`, `bandit`, `mypy`, `pandas`, `pyarrow`, `zstandard`
  — unbounded resolution; run advisory scan against whatever resolves.
- `requirements/agent.txt` / `requirements/dev.txt`: `pytest>=8.x` below the CVE-2025-71176 floor.

**Medium priority (feature/optional stack — confirm patched):**
- `requirements-optional.txt`: `tensorboard>=2.13.0`, `wandb>=0.15.0`, `twisted>=24.7.0`,
  `configobj>=5.0.9`, `opentelemetry-sdk>=1.24`.
- `requirements-audio-transcription.txt`: `pyannote.audio==3.3.2`, `faster-whisper==1.2.1`,
  `ffmpeg-python==0.2.0` (pinned but never scanned).
- `requirements-notebook.txt`: `jupyterlab==4.5.9`, `notebook==7.5.6`, `nbconvert==7.17.1`
  (Jupyter stack historically CVE-prone — verify).

**Baseline good (already pinned to CVE-patched floors — verify, don't expect findings):**
- cryptography (`==49.0.0`/`>=49.0.0,<50`), PyJWT (`>=2.13.0`), urllib3 (`>=2.7.0`),
  certifi (`>=2026.6.17`), jinja2 (`>=3.1.6`), idna (`>=3.18`), filelock (`>=3.29.0`),
  torch (`>=2.6.1` — CVE-2025-32434 weights_only RCE fix), transformers (`>=5.12.1`),
  nltk (`==3.9.4` in eval/lock — CVE-2025-14009 fixed; but `requirements-optional.txt` still
  allows `>=3.9.3` → tighten).

**Rust crates to scan (`cargo audit` in 8.4.3):** pyo3 0.24.1, tokio 1.36, serde 1.0.197,
lz4 1.24.0, zstd 0.13.0, flate2 1.1, crossbeam 0.8.4 — no live audit run this session.

---

## 8. Prioritized Recommendations → Workstream 8.4.2

| # | Priority | Recommendation | Rationale |
|---|----------|----------------|-----------|
| R1 | 🔴 Critical | Resolve the **pytest-cov** hard conflict (`==7.0.0` vs `<6.0.0` vs `==5.0.0`) | Currently the dev bundles cannot be co-installed. |
| R2 | 🔴 Critical | Raise `pytest` floor to `>=9.0.3` in `requirements/dev.txt` & `requirements/agent.txt` | Enforces CVE-2025-71176 fix uniformly. |
| R3 | 🔴 Critical | Reconcile the `requirements/docker.txt` Pydantic v1 / FastAPI 0.95 split | Prevents an entirely different major stack in containers. |
| R4 | 🟠 High | Pin the 14 unpinned tools in `requirements/dev.txt` (semgrep, bandit, mypy, pandas, pyarrow, zstandard, …) | Eliminates the largest non-determinism source; enables reproducible CI. |
| R5 | 🟠 High | Establish a **single source of truth** for the 31 multi-file packages (torch, transformers, pytest*, requests, pydantic, numpy, accelerate, peft…) | Removes soft-conflict maintenance burden across ≤6 files. |
| R6 | 🟠 High | Choose **one** authoritative Python lock strategy (`uv.lock` vs `requirements/lock.txt`) and document it | Two overlapping locks will drift. |
| R7 | 🟡 Medium | Generate compiled locks for uncovered surfaces (dev, minimal, optional, notebook, audio, ml-lite) | Closes reproducibility gaps identified in §5. |
| R8 | 🟡 Medium | Tighten `nltk>=3.9.3` → `>=3.9.4` in `requirements-optional.txt`; align `requests`/`defusedxml`/`hydra-core`/`numpy` specifiers | Removes residual security-floor drift. |
| R9 | 🟢 Low | Convert `license = {text="MIT"}` → SPDX string `license = "MIT"` (PEP 639) | Modern packaging compliance. |
| R10 | 🟢 Low | Run `pip-audit` + `cargo audit` against §7 candidates and feed results into 8.4.2 remediation log | Confirms real CVE exposure vs theoretical. |
| R11 | 🟢 Low | Add CI assertion that `package-lock.json` stays in sync if Node deps are introduced | Preempts a future lock gap. |

---

## 9. Success-Criteria Status (Workstream 8.4.1)

- ✅ 100% of dependency files identified (11 top-level requirements + 7 `requirements/` + pyproject + 4 ecosystem manifests)
- ✅ Complete dependency inventory produced (101 distinct Python packages + 43 pyproject base + 14 Rust crates)
- ✅ Version-pin analysis complete (55 exact / 146 range / 18 unpinned)
- ✅ Conflicts identified and assessed (3 hard, 30+ soft, 1 intentional)
- ✅ Duplication map created (31 packages in ≥3 files)
- ✅ Lock-file gaps documented; vulnerability-review candidates flagged for 8.4.2/8.4.3
- ✅ Audit report generated (this document)

**Session constraint compliance:** No dependency, source, or GitHub Actions workflow files were
modified. This report is the sole artifact and resides in `.codex/`.

---

*Generated by packaging-validation-agent — Phase 8 Track 8.4 — 2026-07-03T01:36Z*
