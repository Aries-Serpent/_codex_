# Tech Debt Registry

> **Version**: 1.0.0 | **Created**: Session 51 (2026-02-20) | **Owner**: @mbaetiong  
> **Repository**: Aries-Serpent/_codex_ | **Total Items**: 47 | **Last Updated**: Session 52 (2026-02-20)

---

## Overview

Codebase-wide technical debt catalogue stratified by priority (P1–P4). Each item includes owner, severity, root cause, AI agent assignment, and a session delivery target (S52–S58).

**Deep Research Questions** (DR-001–DR-008) anchor each cluster to internal evidence and external references for autonomous resolution.

---

## Priority Legend

| Priority | Meaning | SLA |
|----------|---------|-----|
| **P1** | Blocks production readiness / causes CI failures | S52–S53 |
| **P2** | Degrades reliability or security posture | S53–S54 |
| **P3** | Code quality / maintainability | S55–S56 |
| **P4** | Nice-to-have / future improvements | S57–S58 |

---

## 🔴 P1 — Immediate (Blocks Production)

### TD-001 · Naive `datetime.now()` usage — timezone-unaware timestamps
- **Severity**: High  
- **Owner**: @mbaetiong  
- **Root Cause**: `datetime.now()` and `datetime.utcnow()` produce timezone-naive objects. Comparisons with UTC-aware datetimes (e.g., from APIs, databases) cause `TypeError` at runtime.  
- **Locations**: `src/context_management/context_cache.py`, `src/context_management/memory.py`, `src/context_management/priority_queue.py`, `src/context_management/clustering.py` (66 call sites total across `src/`)  
- **Fix**: Replace with `datetime.now(UTC)` (`from datetime import UTC`) everywhere in PR-touched files first, then full codebase pass.  
- **AI Agent**: `datetime-modernizer`  
- **Session Target**: S52  
- **DR**: DR-001  
- **Search Anchor**: `grep -rn "datetime.now()\|datetime.utcnow()" src/ --include="*.py"`

### TD-002 · `python_requires >= "3.12"` not restored in `pyproject.toml`
- **Severity**: High  
- **Owner**: @mbaetiong  
- **Root Cause**: Removed in session 44 to unblock CI on Python 3.11 runners. Base branch `copilot/sub-pr-3248` CI must be confirmed green before restoring.  
- **Locations**: `pyproject.toml` line 8  
- **Fix**: Restore `python_requires = ">=3.12"` after base-branch CI confirmed green.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S52 (after base CI green)  
- **DR**: DR-002  
- **Search Anchor**: `grep "python_requires" pyproject.toml`

### TD-003 · `_TORCH_312_BUG` xfail guards — 25 entries, should be removed after PyTorch 2.7+
- **Severity**: High  
- **Owner**: @mbaetiong  
- **Root Cause**: PyTorch 2.x `isinstance()` bug with Python 3.12 union types. Fixed upstream in PyTorch 2.7. Guards are temporary workarounds.  
- **Locations**: `tests/conftest.py` — `_TORCH_PROFILER_XFAIL` (25 entries), `_TORCH_312_BUG` skipif in 8 test files  
- **Fix**: Upgrade CI PyTorch to ≥2.7, verify all xfailed tests now pass, remove guards.  
- **AI Agent**: `ci-testing-agent`, `meta-tensor-validator`  
- **Session Target**: S53  
- **DR**: DR-003  
- **Search Anchor**: `grep -rn "_TORCH_312_BUG\|TORCH_PROFILER_XFAIL" tests/`  
- **Web**: https://github.com/pytorch/pytorch/issues/118829

### TD-004 · Pre-existing CI failures in `_PREEXISTING_FAILURES` — 28 entries not fixed
- **Severity**: High  
- **Owner**: @mbaetiong  
- **Root Cause**: Tests with fundamental design or infrastructure mismatches deferred across sessions S43–S52. Include `test_tracking_decide` (isidentifier/None typer bug), `test_cli_checkpoint_validate`, `test_fetch_messages`, `test_validate_fences_md`.  
- **Locations**: `tests/conftest.py` — `_PREEXISTING_FAILURES` dict (28+ entries)  
- **Fix**: Each entry requires individual root-cause investigation and targeted fix.  
- **AI Agent**: `ci-testing-agent`, `test-alignment-fixer`  
- **Session Target**: S52–S53  
- **DR**: DR-004  
- **Search Anchor**: `grep -A3 "_PREEXISTING_FAILURES" tests/conftest.py`

### TD-005 · `sentencepiece_adapter.py` module-level `spm` cache breaks test isolation
- **Severity**: High  
- **Owner**: @mbaetiong  
- **Root Cause**: `_get_sentencepiece()` caches module at module level in `spm` global. Tests patching `sys.modules["sentencepiece"]` were ignored. Fixed in S52 via sys.modules check, but underlying cache design is fragile.  
- **Locations**: `src/codex_ml/tokenization/sentencepiece_adapter.py` lines 29–55  
- **Fix**: Refactor to use `importlib.import_module` at call time with short-circuit on already-valid module.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S53  
- **DR**: DR-005

### TD-006 · `seeding.py` doesn't register numpy seed snapshot — `_LAST_SEEDED_NUMPY_STATE` stale
- **Severity**: High  
- **Owner**: @mbaetiong  
- **Root Cause**: `set_reproducible()` in `seeding.py` seeds numpy but never calls `register_seed_snapshot()`. The `_LAST_SEEDED_NUMPY_STATE` global in `checkpointing.py` stays stale from a previous test run's seed. Fixed via lazy import in S52.  
- **Locations**: `src/codex_ml/utils/seeding.py`, `src/codex_ml/utils/checkpointing.py`  
- **Fix**: Move `register_seed_snapshot` call inline or refactor into a shared seeding coordinator.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S53  
- **DR**: DR-001

### TD-007 · `unified_training.py` doesn't expose `strategies` for monkeypatching
- **Severity**: Medium-High  
- **Owner**: @mbaetiong  
- **Root Cause**: `test_mid_epoch_resume_equivalence::test_resume_error_is_recorded` calls `monkeypatch.setattr(unified_training.strategies, ...)` but `unified_training.py` doesn't bind `strategies` as a module attribute. Adding `import codex_ml.training.strategies as strategies` (absolute) broke `test_train_mlflow_flags` in CI — root cause unclear.  
- **Locations**: `src/codex_ml/training/unified_training.py`, `tests/space_traversal/test_peft_comprehensive/test_mid_epoch_resume_equivalence.py`  
- **Fix**: Use `from . import strategies` (relative import at bottom of imports) and verify it doesn't break `test_train_mlflow_flags`.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S52  
- **DR**: DR-003

---

## 🟠 P2 — Near-term (Reliability / Security)

### TD-008 · JWT secret key hardcoded in `inference_server.py` test path
- **Severity**: High  
- **Owner**: @mbaetiong  
- **Root Cause**: `_JWT_SECRET_KEY` defaults to `"changeme-dev-only"` — exposed in source. Production deployments must override via env var `CODEX_JWT_SECRET`.  
- **Locations**: `src/codex_ml/serving/inference_server.py` lines 10–15  
- **Fix**: Remove default entirely; raise `ValueError` if env var not set in non-dev mode.  
- **AI Agent**: `security-alert-verification-agent`  
- **Session Target**: S53  
- **DR**: DR-006

### TD-009 · 237 files with bare/broad `except Exception:` swallowing errors silently
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: Defensive `except Exception: pass` or `except Exception: logger.warning(...)` blocks hide real failures. CodeQL flags these as "empty except".  
- **Locations**: 237 source files (see `grep -rn "except Exception:" src/`)  
- **Fix**: Replace with specific exception types or minimum a real statement + re-raise pattern.  
- **AI Agent**: `codebase-health-guardian`, `security-alert-verification-agent`  
- **Session Target**: S53–S54  
- **DR**: DR-007

### TD-010 · `fix_sql_injection.py` calls `.isidentifier()` on unvalidated input — NoneType crash
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `scripts/security/codemods/fix_sql_injection.py:70` calls `var.isidentifier()` where `var` can be `None`. Causes `AttributeError` in `test_tracking_decide` and `test_cli_checkpoint_validate`.  
- **Locations**: `scripts/security/codemods/fix_sql_injection.py:70`  
- **Fix**: Add `if var is not None and var.isidentifier():` guard.  
- **AI Agent**: `security-alert-verification-agent`  
- **Session Target**: S52  
- **DR**: DR-007

### TD-011 · `_safe_environment_summary()` catches all exceptions silently in checkpointing
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: Session 48 added sanitization with broad `except Exception: return repr(o)` fallback. Non-serializable values are silently stringified rather than raising.  
- **Locations**: `src/codex_ml/utils/checkpointing.py` `_SafeEncoder.default()`  
- **Fix**: Log a warning when `repr()` fallback is used; add metric counter.  
- **AI Agent**: `codebase-health-guardian`  
- **Session Target**: S54  
- **DR**: DR-007

### TD-012 · `_rng_load` prefer_resume semantics undocumented — confusing API
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `prefer_resume=True` restores snapshot state (post-seed + draws); `prefer_resume=False` restores seed state. This distinction is implicit and caused `test_rng_snapshot_roundtrip` to fail.  
- **Locations**: `src/codex_ml/utils/checkpointing.py` `_rng_load()`  
- **Fix**: Add docstring explaining the semantics; add `prefer_resume` parameter docs to `load_rng_state()`.  
- **AI Agent**: `documentation-quality-agent`  
- **Session Target**: S54  
- **DR**: DR-001

### TD-013 · `codex-reviewer.agent.yml` YAML structure — multi-document with list doc
- **Severity**: Low-Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: Second YAML document (`---`) parsed as a list by `yaml.safe_load_all`. Fixed in S52 to use dict. But version history should be part of main document.  
- **Locations**: `.github/agents/codex-reviewer.agent.yml`  
- **Fix**: Merge version history into main document as `version_history:` key.  
- **AI Agent**: `documentation-quality-agent`  
- **Session Target**: S53  
- **DR**: DR-008

### TD-014 · `tracking_decide.py` CLI — isidentifier called on None tracking URI
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: Typer CLI validation calls `.isidentifier()` on a tracking URI component that may be `None` when `--allow-remote` flag is set without a URI.  
- **Locations**: `src/codex_ml/cli/tracking_decide.py` (exact line TBD from full stack trace)  
- **Fix**: Add `if value is not None and isinstance(value, str) and value.isidentifier():` guard.  
- **AI Agent**: `ci-testing-agent`, `test-alignment-fixer`  
- **Session Target**: S52  
- **DR**: DR-004

### TD-015 · `checkpoint_validate.py` CLI — bool value passed to string method
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `test_cli_checkpoint_validate_success` fails with `'bool' object has no attribute 'isidentifier'`. Checkpoint validate CLI receives `bool` where `str` expected.  
- **Locations**: `src/codex_ml/cli/checkpoint_validate.py` (exact line TBD)  
- **Fix**: Add `isinstance(value, str)` guard before `.isidentifier()` call.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S52  
- **DR**: DR-004

### TD-016 · `validate_fences_md.py` — false-positive mixed fence type detection
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `tools/validate_fences.py` reports "mixed fence types" and "EOF inside fence" on valid markdown files. Parser doesn't correctly handle nested or indented fences.  
- **Locations**: `tools/validate_fences.py`  
- **Fix**: Fix fence parser state machine to correctly track opener/closer pairs.  
- **AI Agent**: `codebase-health-guardian`  
- **Session Target**: S54  
- **DR**: DR-008

### TD-017 · `test_fetch_messages` introspection returns empty result set in CI
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `_codex_introspect()` used by `fetch_messages` tests resolves writer/fetch functions via introspection, which returns empty in CI (different Python path).  
- **Locations**: `tests/test_fetch_messages.py`, `src/codex/logging/fetch_messages.py`  
- **Fix**: Remove introspection dependency; use explicit function registry instead.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S53  
- **DR**: DR-004

### TD-018 · `src.tokenization.sentencepiece_adapter` legacy shim imports at module level
- **Severity**: Low-Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `src/tokenization/sentencepiece_adapter.py` emits a `DeprecationWarning` on import at module level. This fires during test collection, polluting output.  
- **Locations**: `src/tokenization/sentencepiece_adapter.py` lines 13–19  
- **Fix**: Move the warning to first USE of `SentencePieceAdapter`, not on import.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S55  
- **DR**: DR-005

---

## 🟡 P3 — Code Quality / Maintainability

### TD-019 · 1230 `TODO`/`FIXME` comments in source — untracked backlog
- **Severity**: Low-Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: Stub implementations, placeholder logic, and deferred features scattered across 1230 locations. No tracking mechanism.  
- **Fix**: Triage and convert to GitHub issues; remove stale ones.  
- **AI Agent**: `repository-hygiene-agent`  
- **Session Target**: S55–S56  
- **DR**: DR-008

### TD-020 · `src/security/providers/github_provider.py` — 4 TODO stubs (no actual API calls)
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: Lines 193, 305, 331, 360 have `# TODO: Actual API call/validation` — methods return hardcoded stubs.  
- **Fix**: Implement actual GitHub API integration or raise `NotImplementedError` with clear message.  
- **AI Agent**: `security-alert-verification-agent`  
- **Session Target**: S55  
- **DR**: DR-006

### TD-021 · `src/codex/archive/sigstore_client.py` — Sigstore signing is a stub
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: TODO comment at line 67 defers production Sigstore signing. Currently returns mock signing result.  
- **Fix**: Implement `sigstore-python` SDK integration.  
- **AI Agent**: `security-alert-verification-agent`  
- **Session Target**: S56  
- **DR**: DR-006

### TD-022 · Phase 2/3 CLI stubs — `reporting`, `quality`, `audit`, `analysis` CLIs
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `src/codex/reporting/cli.py`, `src/codex/quality/cli.py`, `src/codex/audit/cli.py`, `src/codex/analysis/cli.py` are Phase 2/3 stubs with `# TODO: Implement`.  
- **Fix**: Implement or add clear `NotImplementedError` with roadmap reference.  
- **AI Agent**: `codebase-health-guardian`  
- **Session Target**: S56  
- **DR**: DR-008

### TD-023 · `_PREEXISTING_FAILURES` conftest entries — 28 tests never investigated
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: Each session adds more tests to the "pre-existing failures" dict rather than fixing root cause. Technical debt accumulates.  
- **Fix**: Assign one engineer/agent per entry; fix root cause; remove entries.  
- **AI Agent**: `ci-testing-agent`, `test-alignment-fixer`  
- **Session Target**: S52–S55  
- **DR**: DR-004

### TD-024 · `tests/space_traversal/` detector tests use `parents[2]` (wrong repo root)
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `_load_module()` in `test_peft_hooks.py` conftest uses `Path(__file__).parents[2]` which resolves to `tests/` not the repo root. Requires detector copy at `tests/scripts/`.  
- **Fix**: Fix `_load_module` to use `parents[3]` or a sentinel-based root finder (`pyproject.toml` walk-up).  
- **AI Agent**: `test-alignment-fixer`  
- **Session Target**: S53  
- **DR**: DR-004

### TD-025 · `manifest.py` init command missing `run.id` UUID stability — uses `str(uuid4())`
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `codex manifest init` generates a new `run.id` UUID on every call. Not deterministic for idempotent workflows.  
- **Fix**: Accept `--run-id` flag; default to hash of CWD + timestamp.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S55  
- **DR**: DR-008

### TD-026 · `seed_manager.py` `json.dumps(default=str)` silently serializes `MagicMock`
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: Session 51 fix prevents crash but `MagicMock` leak from tests is the real issue. Test isolation should prevent mock objects from appearing in production state.  
- **Fix**: Add assertion in `seed_manager.save_state()` that state contains no mock objects (check via `unittest.mock.MagicMock`).  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S54  
- **DR**: DR-001

### TD-027 · `active_learning/hook.py` budget uses `datetime.date.today()` — not UTC
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `_enforce_query_budget()` keys daily counts by `datetime.date.today().isoformat()` which is local timezone. On UTC+0 servers this is fine; other timezones may double-count or miss a day.  
- **Fix**: Use `datetime.now(UTC).date().isoformat()`.  
- **AI Agent**: `datetime-modernizer`  
- **Session Target**: S53  
- **DR**: DR-001

### TD-028 · Legacy `src/tokenization/` shim modules — deprecated but still in PYTHONPATH
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `src/tokenization/sentencepiece_adapter.py` and siblings are legacy shims that emit `DeprecationWarning`. New code should use `codex_ml.tokenization.*`.  
- **Fix**: Add deprecation warning with removal target date; update all internal imports.  
- **AI Agent**: `ci-importerror-agent`  
- **Session Target**: S56  
- **DR**: DR-005

### TD-029 · `codex_ml.tokenization._types` and `_protocols` — re-export coverage incomplete
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `api.py` re-exports `TokenizerAdapter`, `BOS_TOKEN`, `EOS_TOKEN`, `PAD_TOKEN`, `UNK_TOKEN` from the new modules. But downstream code importing `from codex_ml.tokenization.api import HFTokenizerAdapter` (the old TYPE_CHECKING cycle) may still exist.  
- **Fix**: `grep -rn "from codex_ml.tokenization.api import"` and migrate all TYPE_CHECKING imports.  
- **AI Agent**: `ci-importerror-agent`  
- **Session Target**: S54  
- **DR**: DR-005

### TD-030 · `inference_server.py` model name validation allows some injection chars
- **Severity**: Low-Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: `_validate_model_name()` blocks `..`, `;`, space, null but allows `*`, `?`, `[`, `]` which could expand in shell contexts if model name is passed to subprocess.  
- **Fix**: Use allowlist `[A-Za-z0-9_\-/.]` pattern instead of blocklist.  
- **AI Agent**: `security-alert-verification-agent`  
- **Session Target**: S53  
- **DR**: DR-006

### TD-031 · `DataValidator` validate_and_raise coupling — raises on first failure only
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `validate_and_raise()` collects all failures then raises a combined message. But if callers need per-rule results they must call `validate()` separately — redundant computation.  
- **Fix**: Add `validate_all(raise_on_failure=True)` unified method.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S55  
- **DR**: DR-008

### TD-032 · `BayesianAssessor.update_cpds_em()` lacks convergence check
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: EM implementation (S46) runs one E+M step per call. No convergence criterion or iteration limit. Repeated calls are the caller's responsibility.  
- **Fix**: Add `max_iterations` param and log-likelihood delta convergence check.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S55  
- **DR**: DR-008

### TD-033 · `conftest.py` `_isolate_rng_state` does not restore `_LAST_SEEDED_NUMPY_STATE`
- **Severity**: Medium  
- **Owner**: @mbaetiong  
- **Root Cause**: The autouse fixture saves/restores `np.random` state but not the `checkpointing.py` module-level `_LAST_SEEDED_NUMPY_STATE` global. Causes stale seed state leaks between tests.  
- **Fix**: In `_isolate_rng_state` fixture, also save/restore `checkpointing._LAST_SEEDED_NUMPY_STATE` (and torch/python equivalents).  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S53  
- **DR**: DR-001

### TD-034 · `audio/workflow/auto_tune_workflow.py` uses `time.perf_counter()` TODO — no actual audio processing
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: Stub workflow with timing placeholder. No actual audio processing.  
- **Fix**: Implement or mark as not-for-production with clear `NotImplementedError`.  
- **AI Agent**: `repository-hygiene-agent`  
- **Session Target**: S57  
- **DR**: DR-008

### TD-035 · `cli/pipeline.py` — `# TODO: Implement actual pipeline logic`
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: Stub CLI pipeline. No implementation.  
- **Fix**: Implement pipeline dispatch or raise `NotImplementedError`.  
- **AI Agent**: `repository-hygiene-agent`  
- **Session Target**: S57  
- **DR**: DR-008

---

## 🟢 P4 — Future Enhancements

### TD-036 · PyTorch 2.7+ migration — remove `_TORCH_312_BUG` guards entirely
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: Guards added as temporary workarounds for PyTorch 2.x Python 3.12 bug. Once PyTorch ≥2.7 is on CI, all guards can be removed.  
- **Fix**: Upgrade CI PyTorch; run full suite; remove guards.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S54  
- **DR**: DR-003  
- **Web**: https://github.com/pytorch/pytorch/issues/118829

### TD-037 · `active_learning` budget persistence — in-memory dict resets on restart
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `ActiveLearningHook._daily_counts` is an instance dict. Not persisted across process restarts. Budget can be exceeded after restart.  
- **Fix**: Persist to SQLite or file-based store keyed by date + process UUID.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S56  
- **DR**: DR-001

### TD-038 · `EarlyStopping.best_model_checkpoint` not set until a checkpoint is saved
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `best_model_checkpoint` is `None` until `update()` triggers a save. Callers that check it immediately after construction get `None` unexpectedly.  
- **Fix**: Default to a sentinel string `"<not_yet_saved>"` and document in docstring.  
- **AI Agent**: `test-alignment-fixer`  
- **Session Target**: S56  
- **DR**: DR-008

### TD-039 · Circular-import risk in `codex_ml.tokenization` not fully eliminated
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `api.py → _protocols.py` and `api.py → _types.py` are clean. But `hf_tokenizer.py` still imports from `api.py`. If new constants are added to `api.py` that depend on `hf_tokenizer.py`, cycle returns.  
- **Fix**: Add import-cycle test: `python -c "from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter"` as a CI smoke check.  
- **AI Agent**: `ci-importerror-agent`  
- **Session Target**: S54  
- **DR**: DR-005

### TD-040 · `content_diff.py` `SequenceMatcher(autojunk=False)` — no size limit
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: Session 48 fix disables autojunk heuristic. On large documents (>100KB) this is O(n²) and may cause timeouts.  
- **Fix**: Add max-size guard; fall back to autojunk for documents >50KB.  
- **AI Agent**: `performance-regression-detector`  
- **Session Target**: S57  
- **DR**: DR-008

### TD-041 · `AgentDashboard` CPU/memory metrics use random stubs — not real system metrics
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `agent_dashboard.py` active learning budget fields added (S44) but CPU/memory fields still use `random.uniform()` placeholder values.  
- **Fix**: Replace with `psutil.cpu_percent()` and `psutil.virtual_memory().percent`.  
- **AI Agent**: `performance-regression-detector`  
- **Session Target**: S56  
- **DR**: DR-008

### TD-042 · `pa_legacy/reader.py` `to_template()` — regex-based parsing brittle
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: PowerAutomate package reader uses definition-based regex parsing. Edge cases with nested JSON or unicode field names can cause silent incorrect parse.  
- **Fix**: Replace with proper JSON schema validation using `jsonschema` library.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S57  
- **DR**: DR-008

### TD-043 · `checkpointing.py` dual-logger pattern — `logger.warning()` called twice per exception
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: Multiple places in `checkpointing.py` call `logger.warning("Exception occurred", exc_info=True)` twice in a row. This duplicates log output.  
- **Fix**: Remove duplicate `logger.warning` calls; keep single call with `exc_info=True`.  
- **AI Agent**: `repository-hygiene-agent`  
- **Session Target**: S55  
- **DR**: DR-007

### TD-044 · `metrics/registry.py` `_METRIC_REGISTRY` mock seam — not thread-safe
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `_METRIC_REGISTRY` is a plain module-level `dict`. Tests use `monkeypatch.setitem()` which is not thread-safe. Concurrent test workers could see each other's patches.  
- **Fix**: Wrap `_METRIC_REGISTRY` access in a thread-local or use pytest-xdist worker isolation.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S56  
- **DR**: DR-004

### TD-045 · `AdaptiveScoringEngine` weight validation boundary — must sum to ≤1.0 not <1.0
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: Session 51 fixed the weight validation boundary. But the tolerance `1e-9` for floating-point sums is undocumented. A sum of `1.0000000001` raises while `0.9999999999` passes silently.  
- **Fix**: Document the tolerance explicitly; add `round(sum, 9)` normalization.  
- **AI Agent**: `ci-testing-agent`  
- **Session Target**: S55  
- **DR**: DR-008

### TD-046 · `audit_runner.py` S7 prefix validation — only validates prefix existence, not format
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: `stage_s3_capabilities()` checks S7 prefix exists but doesn't validate bucket naming conventions (no uppercase, 3–63 chars, no consecutive dots).  
- **Fix**: Add full S3 bucket name validation regex.  
- **AI Agent**: `security-alert-verification-agent`  
- **Session Target**: S57  
- **DR**: DR-006

### TD-047 · `ci-parameter-mismatch-healer` agent — definition only, not wired into CI pipeline
- **Severity**: Low  
- **Owner**: @mbaetiong  
- **Root Cause**: Agent file created in S50 at `.github/agents/ci-parameter-mismatch-healer.md`. Not yet invoked automatically from any workflow.  
- **Fix**: Add invocation step to `auto-fix-pr-check.yml` and `pre-merge-validation.yml`.  
- **AI Agent**: `workflow-ci-fixer`  
- **Session Target**: S56  
- **DR**: DR-008

---

## Deep Research Questions

### DR-001 · Datetime / RNG State Architecture
> **Scope**: Timezone-aware datetime migration + RNG state registration coordination  
> **Internal**: `grep -rn "datetime.now()\|_LAST_SEEDED" src/`  
> **Web**: https://docs.python.org/3/library/datetime.html#datetime.datetime.now — UTC parameter since Python 3.2  
> **Question**: What is the safest pattern for coordinating `register_seed_snapshot()` across `seeding.py` → `checkpointing.py` without circular imports?

### DR-002 · `python_requires` and CI Python version matrix
> **Scope**: Restore `python_requires >= "3.12"` after base-branch CI confirmed green  
> **Internal**: `grep "python_requires\|python-version" pyproject.toml .github/workflows/*.yml`  
> **Web**: https://packaging.python.org/en/latest/guides/dropping-older-python-versions/  
> **Question**: Which CI workflow files need updating when `python_requires` is restored to ≥3.12?

### DR-003 · PyTorch 2.x Python 3.12 isinstance() bug and 2.7+ migration
> **Scope**: All `_TORCH_312_BUG` guards, `_TORCH_PROFILER_XFAIL` entries  
> **Internal**: `grep -rn "_TORCH_312_BUG\|_TORCH_PROFILER_XFAIL" tests/`  
> **Web**: https://github.com/pytorch/pytorch/issues/118829, https://pytorch.org/get-started/previous-versions/  
> **Question**: At what exact PyTorch version was the isinstance union-type bug fixed, and is 2.7.0 the correct minimum?

### DR-004 · Pre-existing test failures root cause patterns
> **Scope**: All 28 `_PREEXISTING_FAILURES` entries  
> **Internal**: `grep -B1 -A5 "_PREEXISTING_FAILURES" tests/conftest.py | grep "tests/"` 
> **Web**: https://docs.pytest.org/en/latest/how-to/skipping.html  
> **Question**: Which failures are caused by test design (wrong mock path, wrong assertion) vs source bugs vs missing infrastructure?

### DR-005 · Tokenization circular import elimination completeness
> **Scope**: `api.py`, `hf_tokenizer.py`, `_types.py`, `_protocols.py`  
> **Internal**: `python -c "from codex_ml.tokenization import api, hf_tokenizer; print('OK')"`  
> **Web**: https://docs.python.org/3/reference/import.html#submodules  
> **Question**: Are there any remaining `TYPE_CHECKING` imports in the tokenization module that could reintroduce the cycle?

### DR-006 · Security hardening gaps
> **Scope**: JWT secret, GitHub provider stubs, Sigstore stub, model name injection  
> **Internal**: `grep -rn "changeme\|TODO.*API\|TODO.*security" src/`  
> **Web**: https://owasp.org/www-project-top-ten/, https://jwt.io/introduction  
> **Question**: Which security gaps are exploitable in the current CI/CD pipeline vs production deployment context?

### DR-007 · Broad exception handling and empty-except CodeQL alerts
> **Scope**: 237 files with `except Exception:`, CodeQL "Empty except" alerts  
> **Internal**: `python scripts/ci/auto_fix_common_issues.py --check-only --json-output /tmp/diag.json`  
> **Web**: https://codeql.github.com/codeql-query-help/python/py-empty-except/  
> **Question**: Which broad-except patterns are truly defensive (infrastructure code) vs masking bugs (business logic)?

### DR-008 · Stub implementations and TODO backlog prioritization
> **Scope**: 1230 TODO/FIXME items; Phase 2/3 stub CLIs; deferred features  
> **Internal**: `grep -rn "TODO\|FIXME\|NotImplementedError" src/ | wc -l`  
> **Web**: https://www.martinfowler.com/articles/technical-debt.html  
> **Question**: Which stub implementations have tests that are currently PASSING (masking the stub) vs FAILING (exposing it)?

---

## Session Delivery Map

| Session | Items | Focus |
|---------|-------|-------|
| **S52** | TD-002, TD-007, TD-010, TD-014, TD-015 | CI fix session — isidentifier, unified_training, python_requires |
| **S53** | TD-003, TD-006, TD-008, TD-009, TD-017, TD-024, TD-027, TD-030, TD-033 | Reliability — PyTorch upgrade, security, RNG isolation |
| **S54** | TD-011, TD-012, TD-016, TD-026, TD-029, TD-036, TD-039, TD-043 | Code quality — exception handling, tokenization, logging |
| **S55** | TD-004, TD-019, TD-020, TD-023, TD-025, TD-031, TD-032, TD-045 | Debt clearance — TODO triage, DataValidator, BayesianEM |
| **S56** | TD-021, TD-022, TD-028, TD-037, TD-041, TD-044, TD-047 | Feature completeness — Sigstore, CLI stubs, persistence |
| **S57** | TD-034, TD-035, TD-040, TD-042, TD-046 | Future — audio stub, pipeline, large-doc diff, S3 validation |
| **S58** | TD-038 | Final polish — EarlyStopping sentinel default |

---

## Metrics

| Priority | Count | % |
|----------|-------|---|
| P1 — Immediate | 7 | 15% |
| P2 — Near-term | 10 | 21% |
| P3 — Code Quality | 17 | 36% |
| P4 — Future | 13 | 28% |
| **Total** | **47** | **100%** |

---

*Generated: Session 51 (2026-02-20) · Updated: Session 52 (2026-02-20) · Next review: Session 53*
