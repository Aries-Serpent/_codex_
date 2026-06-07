# Gap 27 Verification: ModerationAdapter Coverage

**Verdict:** NEEDS_WORK
**Date:** 2026-06-05

---

## ModerationAdapter Analysis

`src/codex_ml/safety/moderation.py` implements a full moderation pipeline:

- **`ModerationSettings`** dataclass — configures provider, `fail_open`, `audit_log`, `rules_path`.  Default state: `enabled=False`, `fail_open=False`.
- **`ModerationAdapter.review(text, stage)`** — returns a `ModerationDecision` (non-raising).
- **`ModerationAdapter.enforce(text, stage)`** — calls `review()`, raises `ModerationRejection` when `approved=False` AND `fail_open=False`.
- **Offline fallback** — when provider is `"offline"` or unavailable, `SafetyFilters` rule engine is used.
- **Provider errors** — caught, logged via `log_error()`, then falls back to offline rules (not hard-abort).
- **Sanitization** — `decision.sanitized_text` propagated back to callers where wired.
- **Audit log** — optional NDJSON file (path configured via `ModerationSettings.audit_log`).

### Key Default Behaviour

| Setting | Default | Implication |
|---------|---------|-------------|
| `enabled` | `False` | Adapter is **opt-in** — disabled by default at every entry point |
| `fail_open` | `False` | When enabled, vetoed texts raise `ModerationRejection` (fail-closed) |
| `provider` | `"offline"` | Uses `SafetyFilters` rule engine; no external call |
| `audit_log` | `None` | No NDJSON audit trail unless explicitly configured |

---

## LLM Entry Points Found

| # | File | Mechanism | Moderation? |
|---|------|-----------|-------------|
| EP-01 | `src/codex_ml/cli/infer.py` | HF model + tokenizer via argparse CLI | ✅ Optional (`--moderation` flag) |
| EP-02 | `src/codex_ml/training/legacy_api.py` | Training loop `_apply_safety()` | ✅ Conditional on `moderation_settings.enabled` |
| EP-03 | `src/codex_ml/cli/simple_cli.py` | `CodexModel.generate(prompt, ...)` | ❌ No moderation |
| EP-04 | `src/codex/api/app.py` | FastAPI `/predict` endpoint — `model.generate(**encoded, ...)` | ❌ `DenylistEnforcer` only, no `ModerationAdapter` |
| EP-05 | `src/codex/intent/llm_client.py` | `OpenAI().chat.completions.create(...)` (`infer_intent`, `summarize_code`) | ❌ No moderation |
| EP-06 | `src/agents/orchestrator.py` | Async task queue with prompt submission | ❌ No moderation |
| EP-07 | `src/agents/autonomous_runner.py` | Autonomous task runner with prompt forwarding | ❌ No moderation |
| EP-08 | `src/codex_audit/prompting.py` | Builds template prompts (no direct LLM call here) | N/A |

---

## Coverage Analysis

### Covered (2 / 7 active entry points)

**EP-01 — `src/codex_ml/cli/infer.py`**
```
lines 140–172: moderation_adapter = ModerationAdapter.from_settings(...)
               prompt_decision = moderation_adapter.enforce(prompt_text, stage="prompt")
lines 185–198: output_decision = moderation_adapter.enforce(text, stage="output")
```
Pre-prompt **and** post-output enforcement present.  Sanitized text applied back to both `prompt_text` and `text`.
Rejection logged with `log_event(logger, "moderation.block", ...)`.
**Gap**: Gated by `--moderation` CLI flag; passes `enabled=False` settings when flag absent.

**EP-02 — `src/codex_ml/training/legacy_api.py`**
```
lines 862–925: ModerationAdapter constructed when moderation_settings.enabled
               moderation_adapter.enforce(sanitized_text, stage=stage)
```
Called for both `train_texts` ("prompt" stage) and `val_texts` ("eval" stage) via `_apply_safety()`.
Runs after `sanitize_prompt()` and `SafetyFilters.enforce()`.
**Gap**: Still conditional on `moderation_settings.enabled=True` in caller-provided config.

### Not Covered (5 / 7 active entry points)

**EP-03 — `src/codex_ml/cli/simple_cli.py`**
```python
# line 89: output = model.generate(prompt, max_tokens=max_tokens, temperature=temperature)
```
No import of `ModerationAdapter`, no safety check before or after `generate()`.

**EP-04 — `src/codex/api/app.py`**
```python
# line 220: _denylist().ensure_allowed(req.prompt)   ← DenylistEnforcer, not ModerationAdapter
# line 235: generated = model.generate(**encoded, ...)
```
Uses only `DenylistEnforcer` (denylist keyword matching).  `ModerationAdapter` is not imported or used.
Output from `model.generate()` is returned directly without post-flight check.

**EP-05 — `src/codex/intent/llm_client.py`**
```python
# line 211: response = self._client.chat.completions.create(...)  # infer_intent
# line 267: response = self._client.chat.completions.create(...)  # summarize_code
```
Direct external OpenAI API calls.  Neither `infer_intent()` nor `summarize_code()` invoke `ModerationAdapter`.
No ModerationAdapter import in module.

**EP-06 — `src/agents/orchestrator.py`**
Rate-limit enforcement only (`_enforce_rate_limits(prompt)`).  No `ModerationAdapter` import or call.

**EP-07 — `src/agents/autonomous_runner.py`**
Task runner calls LLM; no moderation import or invocation found.

---

## Fail-Closed Behavior

| Aspect | Status |
|--------|--------|
| `enforce()` raises on rejection (when `fail_open=False`) | ✅ Implemented in `ModerationAdapter.enforce()` |
| Provider error falls back to offline rules (not hard abort) | ✅ Defensive — `provider_error` captured, `_offline_review()` used |
| Provider import failure falls back to offline | ✅ `_resolve_provider()` returns `None` on any exception |
| Default `enabled=False` means no enforcement at unconfigured sites | ⚠️ Gap — opt-in, not mandatory |
| `codex/api/app.py` `/predict` fail-closed? | ❌ No moderation path; `DenylistEnforcer` raises HTTP 400 on keyword match only |
| `llm_client.py` fail-closed? | ❌ No moderation; raw exceptions from OpenAI only |

**Summary**: Fail-closed design is **correct within ModerationAdapter itself** — when enabled with `fail_open=False`, rejections raise `ModerationRejection`. However, five of seven entry points never instantiate the adapter at all, making the fail-closed guarantee moot for those paths.

---

## Observability

| Signal | Present | Where |
|--------|---------|-------|
| `log_error("moderation.block", ...)` on rejection | ✅ | `infer.py`, `legacy_api.py` |
| `log_event(logger, "moderation.block", ...)` | ✅ | `infer.py` |
| `ModerationSettings.audit_log` NDJSON trail | ✅ | `ModerationAdapter._record_audit()` (optional path) |
| Prometheus / metrics counter for moderation decisions | ❌ | Not present |
| Structured metric for `approved=True` / `approved=False` ratio | ❌ | Not present |
| Audit log enabled by default | ❌ | `audit_log=None` default |

---

## Test Run Output

```
python -m pytest tests/safety/ -k moderation -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
collected 218 items / 145 deselected / 73 selected

tests/safety/test_moderation_comprehensive.py .......................... [ 35%]
................                                                         [ 57%]
tests/safety/test_moderation_coverage.py ............................... [100%]

================ 73 passed, 145 deselected, 1 warning in 1.17s =================
```

73 tests covering `ModerationSettings`, `ModerationDecision`, `ModerationAdapter` (offline + provider paths, fail-open/fail-closed, audit logging).  All pass.  
**Gap**: No tests covering EP-03, EP-04, EP-05, EP-06, EP-07 integration with the adapter.

---

## Missing Pieces (NEEDS_WORK)

| ID | Gap | Severity |
|----|-----|----------|
| M-01 | `src/codex/api/app.py` `/predict` uses `DenylistEnforcer` only — `ModerationAdapter` not wired | High |
| M-02 | `src/codex/intent/llm_client.py` makes raw OpenAI API calls without any pre- or post-moderation | High |
| M-03 | `src/codex_ml/cli/simple_cli.py` `infer` command calls `CodexModel.generate()` without moderation | Medium |
| M-04 | `src/agents/orchestrator.py` prompt submission has no moderation gate | Medium |
| M-05 | `src/agents/autonomous_runner.py` task runner has no moderation gate | Medium |
| M-06 | `ModerationSettings.enabled=False` by default — moderation is opt-in, not mandatory | Medium |
| M-07 | No Prometheus/metrics counters for moderation decisions (only log_error calls) | Low |
| M-08 | `audit_log=None` by default — structured audit trail only available when explicitly configured | Low |

### Recommended Actions

1. **EP-04 (highest risk)**: Wire `ModerationAdapter` into `src/codex/api/app.py` `/predict` alongside `DenylistEnforcer`.  Consider setting `enabled=True` from application config.
2. **EP-05**: Add a pre-call `enforce(prompt, stage="prompt")` and post-call `enforce(response, stage="output")` wrapper in `CodexLLMClient`.
3. **EP-03**: Add a `--moderation` flag to `simple_cli.py infer` (mirrors `cli/infer.py` pattern) or enable by default.
4. **M-06**: Change default `ModerationSettings.enabled` to `True` in production configs, or add a factory that forces enabled in non-test environments.
5. **M-07**: Add a Prometheus counter `moderation_decisions_total{stage, approved, provider}` in `ModerationAdapter.review()`.
