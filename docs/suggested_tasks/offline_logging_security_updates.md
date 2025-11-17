# Suggested Task: clarify offline safeguards across logging, security, and training stacks

## Summary
Strengthen repo documentation so contributors can exercise the new Hydra override and API middleware safeguards without
network access. The patch below adds an actionable quickstart block that chains the deterministic tests we rely on for
configuration and serving hardening.

## Ready-to-apply patch
```diff
--- a/docs/offline_quickstart.md
+++ b/docs/offline_quickstart.md
@@
 ## 5) Coverage artifacts (local only)

 Use `nox -s coverage_html` to produce `artifacts/coverage/html/index.html` and `artifacts/coverage/coverage.xml` locally.
 These are emitted without touching any CI or remote services.
+
+## 6) Config & API safeguard smoke tests
+
+Run the focused pytest modules that guard Hydra override propagation and the offline API boundary. The suites are
+hermetic and stub external dependencies so they run with only the default repo environment:
+
+    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q \
+      tests/configuration/test_hydra_override_propagation.py \
+      tests/services/api/test_rate_limit_middleware.py
+
+The configuration test ensures Hydra experiment presets (e.g. `experiment=debug`) compose correctly while still honoring
+explicit CLI overrides like `training.seed` and offline metric sinks. The API test drives the FastAPI middleware to verify
+that the request rate limiter and prompt length safeguards fail closed when quotas are exceeded.
```text

## Validation checklist
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/configuration/test_hydra_override_propagation.py`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/services/api/test_rate_limit_middleware.py`
- Documentation spell check (`codespell`) if available
