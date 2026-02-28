# S93 — RVS CI Continuation Prompt
<!-- type: continuation-prompt | session: S93 | created: 2026-02-28 -->
<!-- mirrors format of: PHASE_8_10_CONTINUATION_PROMPT.md, PHASE_8_11_CONTINUATION_PROMPT.md -->

> **Use this prompt** to open Session S93 targeting the Resilient Validation Suite CI,
> full test coverage, and resolution of all errors identified in S92.

---

## 🎯 Objective

Achieve a **fully green Resilient Validation Suite** in CI and locally, eliminating every
failure enumerated by the parallel batch pre-flight toolchain introduced in S92.

---

## 🔃 Mandatory Context Load

Before any action, load:
1. `.github/agents/BATCH_SCAN_PROTOCOL.md` — **all scanning MUST use `rvs_preflight.py`**
2. `docs/ops/DEPLOYMENT_READINESS_S92.md` — blocking items B-01 through B-07
3. `.github/agents/AI_AGENT_INTUITIVENESS_SCORE_V3.md` — current AAIS 94.7/100
4. `docs/ops/primary_test_machine.md` — Intel Core Ultra 5 135U, Windows 11, CPU-only, no CUDA
5. `.codex/change_log.md` — S91–S92 history
6. `.github/agents/ci-testing-agent.md` Phase 3 Pattern Library (17 known fix patterns)

---

## ⚡ Scanning Protocol (MANDATORY)

**NEVER run `pytest tests/` directly.**  Always use the parallel batch runner:

```bash
# Step 1: Preview scope
python scripts/ci/rvs_preflight.py --group quick --preview

# Step 2: Enumerate all failures (produces structured JSON)
python scripts/ci/rvs_preflight.py \
  --group quick \
  --workers 6 \
  --batch-size 30 \
  --report /tmp/rvs_s93_quick.json

# Step 3: Parse structured failures
python -c "
import json
d = json.load(open('/tmp/rvs_s93_quick.json'))
for g, v in d['groups'].items():
    print(f'{g}: {v[\"failed\"]} failure(s), {v[\"passed\"]} passed')
    for f in v['failed_tests'][:30]:
        print(f'  FAIL: {f}')
"

# Step 4: After fixing, verify clean
python scripts/ci/rvs_preflight.py --group quick --workers 6  # must exit 0
```

---

## 📋 Task List (execute in order)

### Task 1 — Enumerate ALL RVS `quick` group failures (Blocking item B-01)

Use `rvs_preflight.py` as above.  For each failure:
- Match against `ci-testing-agent.md` Phase 3 pattern library
- Apply the correct fix pattern
- Re-run the **specific batch** that contained that failure before running full sweep

### Task 2 — Fix timestamp assertion failure (Blocking item B-02)

**File:** `tests/tracking/test_tracking_writers_offline.py::test_ndjson_writer_injects_defaults`  
**Symptom:** `AssertionError: assert '2026-02-28T...' == '2024-01-02T03:04:05Z'`

**Fix — freeze time in the test:**
```python
from unittest.mock import patch
import datetime as _dt

FROZEN = _dt.datetime(2024, 1, 2, 3, 4, 5, tzinfo=_dt.timezone.utc)

def test_ndjson_writer_injects_defaults(writer, tmp_path, monkeypatch):
    # ... existing setup ...

    class _FakeDateTime:
        @staticmethod
        def now(tz=None):
            return FROZEN

    import sys as _sys  # noqa: PLC0415
    _writers_mod = _sys.modules["codex_ml.tracking.writers"]
    monkeypatch.setattr(_writers_mod, "datetime", _FakeDateTime)
    # ... rest of test unchanged ...
```

### Task 3 — SQL f-string B608 parameterised helper (Tech debt T-02)

**File:** `src/codex_ml/metrics/api.py:354`

Replace the f-string SQL construction with a whitelist-validated helper:
```python
import re as _re

_IDENT_RE = _re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,63}$')

def _validated_insert_sql(table: str, cols: list[str]) -> str:
    """Build a parameterised INSERT statement with identifier validation.

    Raises ValueError for table/column names that fail the identifier check,
    eliminating the B608 SQL injection vector at source.
    """
    if not _IDENT_RE.match(table):
        raise ValueError(f"Invalid table identifier: {table!r}")
    safe_cols = []
    for c in cols:
        if not _IDENT_RE.match(c):
            raise ValueError(f"Invalid column identifier: {c!r}")
        safe_cols.append(c)
    placeholders = ", ".join("?" * len(safe_cols))
    col_list = ", ".join(f'"{c}"' for c in safe_cols)
    return f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders})'
```

### Task 4 — Wire inject_batch_scan_protocol.py into pre-merge-validation.yml (Tech debt T-11)

Add this step to `.github/workflows/pre-merge-validation.yml`:
```yaml
- name: Verify agent batch-scan protocol coverage
  run: |
    python scripts/ci/inject_batch_scan_protocol.py --dry-run
    # Fails if any applicable agent is missing the section (non-zero = new agent added without it)
```

### Task 5 — Update AGENT_REGISTRY.yaml to version 1.4.0 (Tech debt T-04)

```python
import pathlib, re
reg = pathlib.Path('.github/agents/AGENT_REGISTRY.yaml')
c = reg.read_text()
c = re.sub(r"^version: '1\.3\.0'", "version: '1.4.0'", c, flags=re.MULTILINE)
c = re.sub(r"^last_updated: '.*?'", f"last_updated: '2026-02-28T00:00:00Z'", c, flags=re.MULTILINE)
reg.write_text(c)
print("AGENT_REGISTRY updated to 1.4.0")
```

### Task 6 — Add `install_hooks.sh` call to `dev_env_setup.sh` (Tech debt T-09)

Find the `dev_env_setup.sh` post-install section and add:
```bash
# Install git hooks (pre-push RVS pre-flight)
if [[ -f "$ROOT/scripts/install_hooks.sh" ]]; then
  bash "$ROOT/scripts/install_hooks.sh" || true
fi
```

### Task 7 — Run full `slow` + `integration` groups to confirm no regressions

```bash
python scripts/ci/rvs_preflight.py --group slow        --workers 4 --batch-size 15
python scripts/ci/rvs_preflight.py --group integration --workers 6 --batch-size 20
```

### Task 8 — Create `CHANGELOG.md` at repo root (Blocking item B-05)

Minimum viable changelog covering the S81–S92 arc:
- `## [Unreleased]` section (contents of current PR branch)
- `## [0.9.0-rc1]` placeholder section with S88–S92 highlights
- Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format

---

## 🚦 Mandatory Gates (must all pass before concluding S93)

```bash
# 1. Linting
python -m ruff check .                                          # 0 errors ✅

# 2. Security
python -m bandit -r src/ --configfile .bandit -q               # 0 issues ✅

# 3. Auto-fix patterns
python scripts/ci/auto_fix_common_issues.py --check-only       # P1-P5, P7-P11 = 0 ✅

# 4. Full RVS quick sweep (MUST exit 0)
python scripts/ci/rvs_preflight.py \
  --group quick --workers 6 --batch-size 30 \
  --report docs/ops/rvs_s93_final_report.json

# 5. Timestamp test specifically
python -m pytest tests/tracking/test_tracking_writers_offline.py -v  # all pass ✅
```

---

## 📊 Success Criteria

| Metric | S92 State | S93 Target |
|--------|-----------|------------|
| RVS `quick` failures | Unknown (hits --maxfail=20) | **0** |
| RVS `slow` failures | Unknown | **0** |
| Timestamp test | FAIL | **PASS** |
| SQL B608 nosec annotations | 1 | **0** |
| AGENT_REGISTRY version | 1.3.0 (stale) | **1.4.0** |
| AAIS Score | 94.7/100 | **≥ 96.0/100** |
| Blocking deployment items | 7 | **≤ 3** (B-03, B-06, B-07 may defer to S94) |

---

## 📁 Key Files (S92 deliverables to build on)

| File | Purpose |
|------|---------|
| `scripts/ci/rvs_preflight.py` | Parallel batch runner — USE THIS for all scanning |
| `scripts/ci/batch_scan_integration.py` | Python API for agents (`BatchScanRunner`) |
| `.github/agents/BATCH_SCAN_PROTOCOL.md` | Canonical protocol reference |
| `docs/ops/DEPLOYMENT_READINESS_S92.md` | Full blocking/tech-debt item list |
| `.github/agents/AI_AGENT_INTUITIVENESS_SCORE_V3.md` | AAIS baseline for comparison |
| `scripts/ci_local.sh preflight` | Shell alias for rvs_preflight |
| `nox -s rvs_preflight` | Nox session alias |
| `.github/hooks/pre-push` | Git hook template |

---

## 🔁 Self-Healing Loop

After each fix cycle:
1. Run `rvs_preflight.py --group quick --changed-only --workers 4` (fast delta check)
2. If failures remain → apply next fix → repeat
3. Only run full `--group quick` sweep when `--changed-only` shows 0 failures
4. Commit only after full sweep shows 0 failures

---

*Continue iterating until all S93 success criteria are met.*  
*Post follow-up prompt targeting S94 (GPU smoke tests + CI parallel sharding) when complete.*
