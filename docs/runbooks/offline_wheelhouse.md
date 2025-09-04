# Offline Build & Use of a Wheelhouse (1-page runbook)

**Purpose:** Enable **hermetic, offline installs** and faster local CI by pre-building wheels into a project-local `./wheelhouse/`, then installing with `--no-index --find-links`. Uses `uv` when present, with safe fallbacks to `pip`.
**Why:** Avoid network slowness/variance and rebuild churn; let Codex pick “fastest vs isolated” per task.

---

## Quick start

```bash
# Build/update wheelhouse & constraints (uses uv if available, else pip)
tools/bootstrap_wheelhouse.sh

# Install from wheelhouse completely offline (example)
python -m pip install --no-index --find-links ./wheelhouse -r requirements.txt
```

Refs: `pip download` produces a directory suitable for later `pip install --find-links` offline installs; `--no-index` ensures no network usage. :contentReference[oaicite:1]{index=1}

---

## Fast paths vs isolation

**Fastest loop (not isolated):**
- `nox --no-venv -s tests_sys` → run in the current interpreter; no env creation. Shortcut for `--force-venv-backend none`. :contentReference[oaicite:2]{index=2}

**Balanced speed & isolation:**
- `nox -r -s tests` → reuse virtualenvs and skip reinstalls; `tests` delegates to the `coverage` gate. :contentReference[oaicite:3]{index=3}

**Most isolated / fully offline:**
- Install strictly from `./wheelhouse` using `--no-index --find-links`. :contentReference[oaicite:4]{index=4}

---

## Build the wheelhouse

```bash
# Detects common requirements files and generates/updates:
#   ./wheelhouse/  (wheels)
#   ./constraints.txt  (pins via uv compile or pip freeze)
tools/make_wheelhouse.sh -r requirements.txt -r requirements-dev.txt
```

Notes:
- If `uv` is available, we **compile** requirements into a lock/constraints file (`uv pip compile`); else fallback uses a temp venv + `pip freeze`. :contentReference[oaicite:5]{index=5}
- Wheels are downloaded with `pip download` because `uv` doesn’t implement `download/wheel` subcommands; later installs can still use `uv pip`. :contentReference[oaicite:6]{index=6}

---

## Install strategy in sessions

1) Prefer `uv`:
   - `uv pip sync <lock-or-reqs.txt>` (idempotent sync to a file) or
   - `uv pip install -r requirements.txt`
   :contentReference[oaicite:7]{index=7}

2) Fallback to `pip` with cache:
   - respect `PIP_CACHE_DIR` (e.g., `./.cache/pip`) for warm wheels. :contentReference[oaicite:8]{index=8}

3) Fully offline:
   - `python -m pip install --no-index --find-links ./wheelhouse -r requirements.txt` (all deps must be present). :contentReference[oaicite:9]{index=9}

---

## Pitfalls & tips

- Mixed **branch vs statement** coverage artifacts can’t be combined. We enforce **branch** everywhere via `.coveragerc` + `--cov-branch` in tox/nox. :contentReference[oaicite:10]{index=10}
- Prefer `uv` for speed but be aware of minor compatibility differences vs `pip`. :contentReference[oaicite:11]{index=11}
- When using **wheelhouse**, include build tools (`setuptools`, `wheel`) as needed for sdists or PEP 517 backends. :contentReference[oaicite:12]{index=12}
