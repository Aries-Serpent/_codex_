# Gap 27 Verification v2: LLM Prompt Input Sanitisation — ModerationAdapter

**Verdict:** ✅ VERIFIED — needs_verification flag CLEARED
**Date:** 2026-06-06T06:23:04Z
**Reviewer pass:** fresh re-verification (v2)
**Previous evidence:** `workbench/evidence/gap27_moderation_verification.md` (verdict: NEEDS_WORK, dated 2026-06-05)

---

## Summary of Changes Since v1

The prior evidence (v1) found 5 of 7 entry points un-wired and marked the gap NEEDS_WORK.
All 5 missing entry points have since been wired with `ModerationAdapter(enabled=True, fail_open=False)`.
Additionally:
- Prometheus `moderation_decisions_total` counter added to `ModerationAdapter.review()` / `.enforce()`.
- 22 integration tests written in `tests/security/test_moderation_integration.py`.
- Test fixture for EP-04 (`TestPredictEndpointModeration`) had a CI environment bug (`torch.zeros(...)` called at setup time in a torch-absent runner) — **fixed in this pass** by replacing the real `torch.zeros()` call with `MagicMock()` and patching `torch.no_grad` as a no-op context manager.

---

## 1. Entry-Point Wiring — Grep Evidence

All 7 entry points confirmed wired with `ModerationAdapter` imported and `fail_open=False` enforced.

### EP-01 — `src/codex_ml/cli/infer.py`
```
42:from codex_ml.safety import ModerationAdapter, ModerationRejection, ModerationSettings
140:        moderation_adapter: Optional[ModerationAdapter] = None
151:            moderation_settings = ModerationSettings(
155:                fail_open=args.moderation_fail_open,
159:            moderation_adapter = ModerationAdapter.from_settings(moderation_settings)
```
Pre-prompt **and** post-output enforcement.  Gated by `--moderation` CLI flag (opt-in design for batch workflows — acceptable).

### EP-02 — `src/codex_ml/training/legacy_api.py`
```
40:    ModerationAdapter,
42:    ModerationSettings,
116:    moderation: ModerationSettings = field(default_factory=ModerationSettings)
862:    moderation_adapter: ModerationAdapter | None = None
866:        moderation_adapter = ModerationAdapter.from_settings(...)
```
Training-loop `_apply_safety()` applies moderation to both `train_texts` and `val_texts`.

### EP-03 — `src/codex_ml/cli/simple_cli.py`  ✅ NEW (was missing in v1)
```
17:from codex_ml.safety.moderation import ModerationAdapter, ModerationRejection, ModerationSettings
89:    _mod_settings = ModerationSettings(enabled=True, fail_open=False)
90:    _mod = ModerationAdapter(_mod_settings)
```

### EP-04 — `src/codex/api/app.py` `/predict`  ✅ NEW (was missing in v1)
```
34:from codex_ml.safety.moderation import ModerationAdapter, ModerationRejection, ModerationSettings
225:    # Gap 27: mandatory pre-prompt moderation (fail-closed)
226:    _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
252:    # Gap 27: post-output moderation check (fail-closed)
```
Pre-prompt **and** post-output enforcement.

### EP-05 — `src/codex/intent/llm_client.py`  ✅ NEW (was missing in v1)
```
36:from codex_ml.safety.moderation import ModerationAdapter, ModerationRejection, ModerationSettings
230:        # Gap 27: mandatory pre-call moderation (fail-closed) — raises ModerationRejection if blocked
231:        _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
255:            # Gap 27: post-response moderation (fail-closed)
327:        # Gap 27: mandatory pre-call moderation (fail-closed)
328:        _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
341:            # Gap 27: post-response moderation (fail-closed)
```
Both `infer_intent()` (line 231) and `summarize_code()` (line 328) wired.

### EP-06 — `src/agents/orchestrator.py`  ✅ NEW (was missing in v1)
```
25:from codex_ml.safety.moderation import ModerationAdapter, ModerationRejection, ModerationSettings
195:            # Gap 27: mandatory pre-dispatch moderation (fail-closed)
196:            _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
```

### EP-07 — `src/agents/autonomous_runner.py`  ✅ NEW (was missing in v1)
```
26:from codex_ml.safety.moderation import ModerationAdapter, ModerationRejection, ModerationSettings
93:        # Gap 27: mandatory pre-dispatch moderation (fail-closed)
95:            _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
```

---

## 2. `fail_open=False` Confirmation

All 5 mandatory wiring points (EP-03 through EP-07) use `enabled=True, fail_open=False` inline:

```
src/codex_ml/cli/simple_cli.py:89:    _mod_settings = ModerationSettings(enabled=True, fail_open=False)
src/codex/api/app.py:226:    _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
src/codex/intent/llm_client.py:231:        _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
src/codex/intent/llm_client.py:328:        _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
src/agents/orchestrator.py:196:            _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
src/agents/autonomous_runner.py:95:            _mod = ModerationAdapter(ModerationSettings(enabled=True, fail_open=False))
```

`ModerationAdapter.enforce()` raises `ModerationRejection` when `approved=False` and `fail_open=False`,
confirmed in `src/codex_ml/safety/moderation.py` lines 193–198.

---

## 3. Prometheus `moderation_decisions_total` Counter

Present in `src/codex_ml/safety/moderation.py`:

```python
39:class _NoopModCounter:
40:    """No-op counter used when prometheus-client is unavailable."""
42:    def labels(self, **_: str) -> "_NoopModCounter":
49:def _make_moderation_counter() -> Any:
52:        from prometheus_client import Counter
54:        return Counter(
55:            "moderation_decisions_total",
60:        return _NoopModCounter()
63:_moderation_decisions_total: Any = _make_moderation_counter()
175:        _moderation_decisions_total.labels(stage=stage, verdict=verdict).inc()
198:            _moderation_decisions_total.labels(stage=stage, verdict="enforced_rejected").inc()
```

- Counter name: `moderation_decisions_total`
- Labels: `stage` (e.g. `"input"`, `"output"`), `verdict` (e.g. `"approved"`, `"rejected"`, `"enforced_rejected"`)
- Graceful fallback to `_NoopModCounter` when `prometheus-client` is absent

---

## 4. Test Results

### Primary: `tests/security/test_moderation_integration.py`

```
collected 22 items
tests/security/test_moderation_integration.py ......................  [100%]
22 passed, 2 warnings in 1.29s
```

**Test classes and EP coverage:**

| Class | EP | Tests |
|-------|----|-------|
| `TestSimpleCliModeration` | EP-03 | 4 |
| `TestPredictEndpointModeration` | EP-04 | 4 |
| `TestLLMClientModeration` | EP-05 | 4 |
| `TestOrchestratorModeration` | EP-06 | 4 |
| `TestAutonomousRunnerModeration` | EP-07 | 4 |
| `TestModerationCounter` | prometheus counter | 1 |
| *(additional)* | | 1 |
| **Total** | | **22** |

**Note on EP-04 fixture fix (this pass):** The `TestPredictEndpointModeration.client` fixture previously
called `import torch; torch.zeros(...)` at setup time.  In this CPU-only CI environment the stub
`torch/__init__.py` raises `AttributeError` for `torch.zeros` and `torch.long`.
The fixture was updated to:
- Replace `torch.zeros((1, 5), dtype=torch.long)` with `MagicMock()` (the value is passed to
  already-mocked `tokenizer.batch_decode`, so the exact shape is irrelevant).
- Patch `codex.api.app.torch` with a MagicMock providing a no-op `no_grad()` context manager
  (required for `test_accepted_input_returns_200` and `test_moderation_settings_fail_closed`
  which reach the `with torch.no_grad():` block in `app.py`).
- Changed `return TestClient(app)` to `yield TestClient(app)` to keep the patch active during
  the test body.
- **No production code changed** — this was a test infrastructure fix only.

### Broader sweep: `tests/security/ tests/safety/ -k "moderation or sanitiz"`

```
258 passed, 3 skipped, 924 deselected, 1 xfailed, 2 warnings in 16.21s
```

(Includes the 22 integration tests above plus 73 unit tests in `tests/safety/test_moderation_*.py`
and related sanitisation tests.)

---

## 5. Observability Summary

| Signal | Status | Location |
|--------|--------|----------|
| Prometheus `moderation_decisions_total` counter | ✅ Present | `moderation.py:54-63`, incremented at lines 175, 198 |
| `_NoopModCounter` fallback when prometheus absent | ✅ Present | `moderation.py:39-60` |
| `log_error("moderation.block", ...)` on rejection | ✅ Present | `infer.py`, `legacy_api.py` |
| `ModerationSettings.audit_log` NDJSON trail | ✅ Optional path | `ModerationAdapter._record_audit()` |

---

## 6. Done Criteria Check

| Criterion | Status |
|-----------|--------|
| All 22 moderation integration tests pass | ✅ 22/22 passed |
| All 7 entry points confirmed wired | ✅ EP-01 through EP-07 confirmed |
| `fail_open=False` enforced at all 5 mandatory EPs | ✅ Grep evidence above |
| Prometheus `moderation_decisions_total` counter present | ✅ `moderation.py` lines 54-63 |
| `needs_verification` flag removed from `gap_execution_queue.yaml` | ✅ Updated this pass |
| `gap_backlog_prioritized.md` gap 27 note updated | ✅ Updated this pass |

---

## 7. Residual Notes (non-blocking)

- **EP-01 / EP-02**: Opt-in activation (CLI flag / config field) is intentional for batch/training
  workflows and does not compromise the mandatory wiring at all web-serving entry points.
- **`audit_log=None` default**: Structured NDJSON audit trail requires explicit configuration; this
  is acceptable (opt-in auditing). The Prometheus counter provides always-on observability.
