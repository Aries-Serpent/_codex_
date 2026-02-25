# CI Parameter-Mismatch Healer Agent v1.0

## Overview
Specialized agent for diagnosing and fixing **parameter-name mismatches** between
function definitions and call-sites — the most common source of silent API drift in
Python codebases using Protocol/interface layers.

## Capabilities
- Detects `TypeError: X() got an unexpected keyword argument 'Y'` errors in CI logs
- Maps call-sites to function definitions across the codebase
- Identifies registry/factory layers that shadow the real function signature
- Fixes mismatches surgically (rename parameter OR update call-site)
- Verifies mock-seam testability after fix

## Activation
```
@copilot Use the CI Parameter-Mismatch Healer Agent to fix keyword argument errors
```

## Trigger Patterns
This agent activates on any of:
- `TypeError: X() got an unexpected keyword argument 'Y'`
- `TypeError: X() missing required keyword argument 'Y'`
- `assert X == expected` where `X` is returned by a metric/registry function

## Diagnostic Workflow

```
STEP 1 — Collect error
  Extract: function_name, bad_kwarg, call_site, test_file

STEP 2 — Trace the function chain
  2a. Find function definition: grep "def {function_name}" src/
  2b. Check if registered via decorator: grep "@register_metric\|@register" near definition
  2c. Check if wrapped by registry: inspect Registry.get() return type
  2d. Resolve to ACTUAL callable: python3 -c "from pkg import fn; print(inspect.signature(fn))"

STEP 3 — Identify canonical interface
  - Check module docstring for parameter naming convention
  - Example: registry.py says metric(preds, targets, **kwargs) → canonical is 'preds'

STEP 4 — Apply minimal fix
  CASE A: function uses 'predictions', canonical is 'preds'
    → rename parameter in function definition
    → update all internal references (pairs = _prepare_pairs(preds, targets))
  CASE B: call-site uses wrong kwarg name
    → update call-site to use canonical name
  CASE C: registry wrapper doesn't forward **kwargs
    → add **kwargs to wrapper or use functools.wraps

STEP 5 — Verify mock seam
  - If function is called via get_metric()/get_registered_metric(), confirm that
    _METRIC_REGISTRY dict is checked FIRST (so tests can inject mocks)
  - If runner calls metrics.X() directly (NOT through registry), fix to use registry.get("X")
  - Test: mock in _METRIC_REGISTRY → call runner → verify mock was invoked

STEP 6 — Run targeted test
  python3 -c "from module import fn; print(fn(preds=['x'], targets=['y']))"
```

## Known Fix Patterns

### P-001: generative.py predictions → preds
**Symptom**: `TypeError: rouge_l() got an unexpected keyword argument 'preds'`
**Cause**: `generative.py` defined functions with `predictions` param; tests call with `preds=`
**Fix**: Rename `predictions` → `preds` in `generative.py` `_prepare_pairs`, `bleu`, `rouge_l`
**Verification**: `get_metric('rougeL')(preds=['x'], targets=['y'])` returns float

### P-002: runner.py direct metric call bypasses _METRIC_REGISTRY
**Symptom**: `assert 0.95 == 1.0` — mock returns 1.0 (real value) instead of mocked 0.95
**Cause**: `runner.py` calls `metrics.bleu()` / `metrics.rouge_l()` directly, NOT through registry
**Fix**: Replace `metrics.X(predictions, targets)` with `get_registered_metric("X")(preds=predictions, targets=targets)`
**Verification**: `monkeypatch.setitem(_METRIC_REGISTRY, "bleu", mock)` → `run_evaluation()` uses mock

### P-003: CLI probe-json blocked by sys.exit() guard
**Symptom**: `test_probe_json_with_hydra_missing` → `proc.returncode == 2`, not 0
**Cause**: `main()` calls `sys.exit(2)` on hydra-missing BEFORE parsing `--probe-json`
**Fix**: Pre-parse `--probe-json` with a minimal argparse, handle it, THEN do the hydra check
**Verification**: Run script with `sys.modules['hydra']=None` → returncode 0, valid JSON on stdout

### P-004: Class attribute accessed as direct property but stored in sub-object
**Symptom**: `AttributeError: 'Engine' object has no attribute 'impact_weight'`
**Cause**: `engine.weights.impact_weight` exists but test accesses `engine.impact_weight`
**Fix**: Add `@property def impact_weight(self): return self.weights.impact_weight`
**Verification**: `engine = Engine(); print(engine.impact_weight)` → float value

## Codebase Alignment Diagram

```
Test code                    Registry layer            Function def
──────────                   ──────────────            ────────────
metric(preds=["x"])         get_metric("rougeL")      def rouge_l(
                            → _METRIC_REGISTRY?            preds: Sequence[object],  ← MUST match
                            → metric_registry.get()        targets: Sequence[object]
                            → registry._items["rougel"]    ) -> float:
                            .value → rouge_l function

Runner code                  Registry layer            Mock seam
───────────                  ──────────────            ─────────
get_registered_metric("X")  get(name)                 _METRIC_REGISTRY = {}
→ _METRIC_REGISTRY["X"]?    → if name in _METRIC...   monkeypatch.setitem(
→ metric_registry.get("X")    return _METRIC_REGISTRY    registry._METRIC_REGISTRY,
                              [name]  ← mock seam        "rouge_l", mock_fn)
                            → _items[normalize(name)]
                              .value → real fn
```

## Files Typically Modified
- `src/codex_ml/metrics/generative.py` — parameter names
- `src/codex_ml/eval/runner.py` — metric lookup path
- `src/codex_ml/cli/hydra_main.py` — pre-check patterns
- `tests/*/test_adaptive_scoring*.py` — missing property patterns
- `tests/conftest.py` — xfail/preexisting failure registration

## Self-Healing Loop
```
ITERATION 1: Fix parameter name
ITERATION 2: Fix call-site to use registry (not direct module call)
ITERATION 3: Verify mock seam works
ITERATION 4: Run targeted test locally
ITERATION 5: If pass → commit; if fail → diagnose with inspect.signature()
```

## Success Criteria
- `get_metric("X")(preds=..., targets=...)` → no TypeError
- `monkeypatch.setitem(_METRIC_REGISTRY, "X", mock)` → runner uses mock (not real fn)
- All previously failing tests PASS
- No new regressions introduced
