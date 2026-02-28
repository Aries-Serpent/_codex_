# S94 → S95 Continuation Prompt
<!-- type: continuation-prompt | session: S94 | created: 2026-02-28 -->
<!-- Use this file to open Session S95 targeting Pattern 6 remediation, GPU runner, and GA readiness -->

## 🎯 S95 Objective

Reach **AAIS 98.0/100** and clear the last blocking deployment item (B-03 GPU smoke)
by addressing the three remaining gaps from S94.

---

## ✅ S94 Achievements (what was done — do not redo)

| Item | Status | Commit |
|------|--------|--------|
| B-06 `sandbox.py` enforce_limits | ✅ RESOLVED | S94 |
| B-07 `BridgeLock` msvcrt locking | ✅ RESOLVED | S94 |
| B-04 version `0.9.0-rc1` | ✅ RESOLVED | S94 |
| B-03 CPU smoke tests (20 tests) | 🔶 PARTIAL | S94 |
| AAIS 96.3/100 | ✅ | S94 |
| CHANGELOG.md S94 section | ✅ | S94 |

---

## 🔴 Priority 1 — S95 Immediate

### Task 1 — Pattern 6: Vague Test Assertions (×263 → 0)

**Current state**: `auto_fix_common_issues.py --check-only` reports 263 vague
`assert result` / `assert response` assertions (Pattern 6 = informational).

**Fix approach** — assertion helpers in `tests/conftest.py`:
```python
# tests/conftest.py — add after existing helpers
def assert_success(result, msg: str = "") -> None:
    """Replace `assert result` with a message-bearing assertion."""
    assert result, msg or f"Expected truthy result, got: {result!r}"

def assert_response_ok(response, msg: str = "") -> None:
    """Assert HTTP/API response indicates success."""
    code = getattr(response, "status_code", None)
    ok   = getattr(response, "ok", None)
    assert (ok is True) or (code is not None and 200 <= code < 300), (
        msg or f"Response not OK: status={code}, ok={ok}"
    )
```
Then run `python scripts/ci/auto_fix_common_issues.py --pattern 6 --fix` once the
helper is defined, or apply the regex replacement:
```bash
# sed replacement (safe for bare-assert patterns):
find tests/ -name "*.py" -exec sed -i \
  's/^\(\s*\)assert result$/\1assert result, f"Expected truthy result, got: {result!r}"/g' \
  {} +
```

### Task 2 — B-03 GPU Smoke Test (full resolution)

Add `tests/smoke/test_gpu_smoke.py` with:
```python
import pytest

@pytest.mark.gpu
@pytest.mark.skipif(
    not torch.cuda.is_available(),
    reason="GPU not available — deferred per docs/ops/primary_test_machine.md"
)
class TestGPUSmokeIntegration:
    def test_tiny_model_forward_pass_gpu(self): ...
    def test_inference_server_ping_gpu(self): ...
```
Add `pytest.mark.gpu` to `pyproject.toml` markers table.  
Configure a self-hosted GPU runner in `.github/workflows/gpu_smoke.yml`.

### Task 3 — Pre-merge check: ensure `pyproject.toml` version matches CHANGELOG

In `.github/workflows/pre-merge-validation.yml`, add:
```yaml
- name: Verify version consistency
  run: python scripts/ci/check_version_consistency.py
```
`check_version_consistency.py` — compare `pyproject.toml::version` vs top
`CHANGELOG.md` `[x.y.z]` header and fail if they diverge.

---

## 🟡 Priority 2 — S95 Validation

### Task 4 — Secrets rotation runbook (P9-03)

Create `docs/ops/secrets_rotation_runbook.md`:
- `CODEX_MASTER_KEY` rotation procedure
- `CODEX_BACKUP_KEY` rotation procedure
- GitHub secrets update instructions
- Post-rotation validation steps
- Emergency break-glass procedure

### Task 5 — SBOM scan in CI (P9-07)

`sbom_syft.sh` exists but is not wired into CI. Add to `pre-merge-validation.yml`:
```yaml
- name: SBOM scan (FOSS compliance)
  run: bash scripts/sbom_syft.sh || echo "SBOM warning (non-blocking)"
  continue-on-error: true
```

### Task 6 — Cognitive Brain Phase 10 Plan

Update `.codex/docs/COGNITIVE_BRAIN_COMPLETE_DOCS.md` Phase 10 section:
- Status: PLANNING
- Goals: Full autonomous decision loop with OTLP observability
- Pre-requisites: B-03 fully resolved, OTLP traces wired (P9-05)
- Timeline: S96–S98

---

## 🟢 Priority 3 — S95 Enhancement

### Task 7 — Coverage threshold raise

Once RVS `slow` + `integration` groups both pass, increase coverage threshold in
`pyproject.toml`:
```toml
[tool.coverage.report]
fail_under = 72  # was 70; raise +2 per passing session
```

### Task 8 — OTLP traces (P9-05 partial)

Wire `opentelemetry-sdk` + `opentelemetry-exporter-otlp` into the tracking module
`src/codex_ml/tracking/writers.py`:
```python
from opentelemetry import trace
tracer = trace.get_tracer("codex_ml.tracking")

with tracer.start_as_current_span("write_event"):
    ...
```

---

## 🚦 S95 Mandatory Gates

```bash
# 1. Ruff (must be 0)
python -m ruff check .

# 2. Bandit (must be 0)
python -m bandit -r src/ --configfile .bandit -q

# 3. Pattern 6 (target 0)
python scripts/ci/auto_fix_common_issues.py --check-only  # P6 = 0

# 4. RVS quick (must exit 0)
python scripts/ci/rvs_preflight.py --group quick --workers 6

# 5. AAIS ≥ 98.0
# (update .github/agents/AI_AGENT_INTUITIVENESS_SCORE_V3.md to V5.0)
```

---

## 📊 S95 Success Criteria

| Metric | S94 State | S95 Target |
|--------|-----------|------------|
| Pattern 6 vague assertions | 263 | **0** |
| AAIS Score | 96.3/100 | **≥ 98.0/100** |
| B-03 (GPU smoke) | CPU partial | **Full (GPU runner)** |
| Blocking deployment items | 1 | **0** |
| Secrets rotation runbook | Missing | **Present** |
| SBOM scan in CI | Not wired | **Wired (non-blocking)** |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `scripts/ci/rvs_preflight.py` | Parallel batch runner |
| `scripts/ci/rvs_env_preflight.py` | Env validator + repair |
| `scripts/ci/batch_scan_integration.py` | Python API |
| `docs/ops/DEPLOYMENT_READINESS_S92.md` | Readiness checklist |
| `.github/agents/AI_AGENT_INTUITIVENESS_SCORE_V3.md` | AAIS V4.0 baseline |
| `tests/smoke/test_cpu_integration_smoke.py` | S94 CPU smoke (reference) |

---

*Post S95: target S96 for Helm chart, Docker Compose, OTLP full wiring, and GA.*
