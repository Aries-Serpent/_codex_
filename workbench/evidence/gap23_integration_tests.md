# Gap 23 – Automated Integration Tests: Evidence

**Status:** ✅ Implemented  
**Date:** 2026-06-06  
**Test file:** `tests/integration/test_gap23_boundaries.py`

---

## Summary

19 integration test functions created across 4 cross-component boundaries.
All tests pass with `pytest tests/integration/test_gap23_boundaries.py -v --tb=short -m integration`.

---

## Test Count by Boundary

| Boundary | Tests | Description |
|----------|-------|-------------|
| API ↔ model-service | 5 | FastAPI TestClient end-to-end request/response |
| Monitoring ↔ alerting | 4 | Alert events fire when thresholds breached |
| Data-pipeline ↔ training | 4 | Data flows correctly into training loop |
| Config ↔ runtime | 6 | Hydra/pydantic configs load and apply correctly |
| **Total** | **19** | All decorated `@pytest.mark.integration` |

---

## Test Functions

### Boundary 1 – API ↔ model-service
1. `test_api_health_endpoint_returns_healthy` – `/health` returns `status=healthy`
2. `test_api_readiness_probe_reports_ready` – `/readiness` responds 200 OK
3. `test_api_liveness_probe_reports_alive` – `/liveness` responds 200 with uptime
4. `test_api_ci_metrics_endpoint_structure` – `/api/metrics/ci` has `timestamp` key
5. `test_api_root_lists_known_endpoints` – `/` advertises ci_metrics/alerts routes

### Boundary 2 – Monitoring ↔ alerting
6. `test_alerting_fires_on_training_failure` – CRITICAL event delivered on RuntimeError
7. `test_alerting_suppresses_events_below_min_severity` – INFO filtered when min=ERROR
8. `test_alerting_delivers_to_multiple_channels` – fan-out to two stub channels
9. `test_alerting_timestamp_is_filled_automatically` – fill_timestamp() populates ISO-8601

### Boundary 3 – Data-pipeline ↔ training
10. `test_data_pipeline_deterministic_order_is_stable` – same seed → same order
11. `test_data_pipeline_different_seeds_produce_different_orders` – seeds 42 vs 7 differ
12. `test_data_pipeline_dataset_registry_roundtrip` – register → retrieve roundtrip
13. `test_data_pipeline_loader_callable_invoked_correctly` – loader yields records

### Boundary 4 – Config ↔ runtime
14. `test_config_load_base_config_returns_dict` – conf/config.yaml loads as dict
15. `test_config_experiment_basic_loads_and_merges` – basic experiment merges with base
16. `test_config_schema_train_config_defaults_valid` – default TrainConfig validates
17. `test_config_schema_train_config_custom_values` – custom values applied at runtime
18. `test_config_schema_train_config_rejects_invalid_lr` – negative LR raises ValidationError
19. `test_config_codex_schema_roundtrip` – CodexConfig instantiated and field-checked

---

## Test Run Output

```
================================================= test session starts ==================================================
collected 19 items

tests/integration/test_gap23_boundaries.py ...................                                                   [100%]

=================================================== warnings summary ===================================================
src/tokenization/train_tokenizer.py:41
  RuntimeWarning: Hydra extras plugin (`hydra.extra`) is unavailable. ...

../../../../home/runner/.local/lib/python3.12/site-packages/fastapi/testclient.py:1
  StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================================ 19 passed, 2 warnings in 1.28s ============================================
```

---

## Key Design Decisions

- **No real network calls**: All external services (Slack, email, GitHub API) are
  replaced with in-memory `_StubChannel` implementations.
- **TestClient for FastAPI**: The `fastapi.testclient.TestClient` runs the ASGI app
  in-process with no socket connections.
- **Independently runnable**: Each test function is self-contained with its own
  imports and fixtures; none depend on another test's side-effects.
- **`@pytest.mark.integration` on every function**: Compatible with the `integration`
  marker already declared in `pytest.ini`.
