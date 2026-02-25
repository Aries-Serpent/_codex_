# Follow-Up Prompt — S75
**PR**: #3344 / #3348
**Branch**: `copilot/sub-pr-3248-again`
**Prepared by**: GitHub Copilot Agent (S74 session)
**Date**: 2026-02-23
**Status**: Ready for Copilot Execution

---

> **Autonomy Level:** Self-Healing · Self-Troubleshooting · Self-Iterating
>
> **Protocol**: Load Memory → Load Agency Policy → Run Recon Scout → Fix → Code Review → CodeQL → Post S76 Prompt

---

## 📊 S74 Completion Summary

| Task | Status | Commit |
|------|--------|--------|
| DRQ-S74-001: check-unsafe-xml (tools/validate.py stdlib fallback) | ✅ | S74 |
| DRQ-S74-002: EmbeddingCache.set() missing method | ✅ | S74 |
| DRQ-S74-003: unified_training monkeypatch broken (module ref) | ✅ | S74 |
| DRQ-S74-004: Ruff F401 resolve_strategy | ✅ | S74 |
| DRQ-S73-003: codex_init.py local datetime import → module level | ✅ | S74 |
| DRQ-S73-001,002,004 research + ANSWERED | ✅ | S74 |
| DRQ updated with S74 findings + new DRQ proposals | ✅ | S74 |
| COGNITIVE_BRAIN_STATUS_S74.md | ✅ | S74 |

---

## 🔴 Outstanding Items (Priority)

### P0 — Verify S74 CI Is Green

After pushing, confirm these jobs pass:
- [ ] Art_Validation Pipeline / Fast Validation
- [ ] Resilient Validation Suite / validation (slow)
- [ ] Resilient Validation Suite / validation (quick)
- [ ] Auto-Fix Common CI Issues / Detect and Fix Common Issues
- [ ] PR Auto-Fix Check / Detect CI Issues

### P0 — Unanswered Research Questions (with file:line links)

These DRQ items remain unresolved and require a dedicated deep-research session:

| DRQ ID | Question | File:Line |
|--------|----------|-----------|
| DRQ-S74-NEW-001 | **Are there function-level `from datetime import datetime` imports that use `datetime.now()` without `timezone.utc`?** Full codebase scan needed. | [`docs/tech_debt/research_queue/questions_for_research.md`](../../docs/tech_debt/research_queue/questions_for_research.md) · search: `grep -rn "^    from datetime import datetime" src/ tests/` |
| DRQ-S74-NEW-002 | **Where is `_emit_provenance_summary`?** Was it renamed or removed? Legacy DRQ-Q001 references it. | [`docs/tech_debt/research_queue/questions_for_research.md`](../../docs/tech_debt/research_queue/questions_for_research.md) · search: `grep -rn "_emit_provenance_summary" . --include="*.py"` |
| Q002 | **What is the root cause of `TestManageTenantIndices` test failures?** | [`docs/tech_debt/research_queue/questions_for_research.md`](../../docs/tech_debt/research_queue/questions_for_research.md) · search: `grep -n "TestManageTenantIndices" tests/ -r` |
| Q003 | **Why does `IncrementalSyncDecider` compute 95% change ratio on repetitive strings?** | [`docs/tech_debt/research_queue/questions_for_research.md`](../../docs/tech_debt/research_queue/questions_for_research.md) · see `src/services/crawler/content_diff.py:232` |
| Q006 | **Pytest string-path monkeypatch CI failure — is the interim S67 fix still holding?** | [`docs/tech_debt/research_queue/questions_for_research.md`](../../docs/tech_debt/research_queue/questions_for_research.md) · see related test in CI slow-suite |

### P1 — Pre-existing Quick-Suite Failures (base-branch verification needed)

These quick-suite failures appeared in CI run 22319999965 and are likely pre-existing on `0D_base_`.
Verify by checking `git log origin/0D_base_..HEAD -- <file>` for each:

| Test | Failure | File:Line |
|------|---------|-----------|
| `test_critical_path/test_persistence.py::TestBackupRestoreWorkflows::test_backup_database` | `TypeError: backup() argument 'target' must be sqlite3.Connection, not PooledConnectionProxy` | [`tests/critical_path/test_persistence.py`](../../tests/critical_path/test_persistence.py) |
| `test_serving/test_inference_chaos.py::TestModelFailures::test_model_oom_scenario` | `assert 200 == 500` | [`tests/serving/test_inference_chaos.py`](../../tests/serving/test_inference_chaos.py) |
| `test_distributed/test_distributed_enhanced.py::TestAccelerateInitGuard::test_safe_init_no_accelerate` | `assert 'cpu_only' == 'no_accelerate'` | [`tests/distributed/test_distributed_enhanced.py`](../../tests/distributed/test_distributed_enhanced.py) |
| `test_monitoring/test_codex_logging_offline.py::test_logging_bootstrap_offline` | MLflow URI mismatch: `'file:///tmp/...' == 'uri'` | [`tests/monitoring/test_codex_logging_offline.py:43`](../../tests/monitoring/test_codex_logging_offline.py#L43) |
| `test_codex/logging/test_db_manager.py::test_init_with_custom_path` | `PosixPath != PosixPath` (same path, different objects) | [`tests/codex/logging/test_db_manager.py`](../../tests/codex/logging/test_db_manager.py) |
| `test_codex_plans/test_contracts.py::TestContractCompliance::test_returns_path_objects_only` | `isinstance(PosixPath, Path)` is False — wrong `Path` import | [`tests/codex_plans/test_contracts.py`](../../tests/codex_plans/test_contracts.py) |
| `test_codex_sequence_validations.py::test_gradient_accumulation_optimizer_steps` | `assert 1 == 2` | [`tests/test_codex_sequence_validations.py`](../../tests/test_codex_sequence_validations.py) |
| `test_interface_loader_env.py::test_get_component_env` | `RuntimeError: failed to load component: dummy_mod:DummyTokenizer` | [`tests/test_interface_loader_env.py`](../../tests/test_interface_loader_env.py) |

### P2 — Knowledge Graph v1.2.0

- [ ] Expand `.codex/knowledge_graph/graph.json` to v1.2.0 (add S74 nodes/edges)
- [ ] Bump `AGENT_REGISTRY.yaml` `total_agents` for S74 session

---

## 📋 Execution Protocol

```
1. @copilot LOAD: memory patterns (module-ref-monkeypatch, xml-unsafe-import-fallback,
   embedding-cache-set-api, save-checkpoint-payload-kw, follow-up-prompt-format)
2. @copilot LOAD: .codex/CODEBASE_AGENCY_POLICY.md
3. Use GitHub tools (NOT bash/curl) to retrieve CI run logs for validation
4. Invoke CI Testing Agent for deep research on DRQ-S74-NEW-001 and pre-existing failures
5. Fix all regressions from this branch; file DRQ entries for pre-existing failures
6. Self-review (5-pass)
7. code_review tool
8. codeql_checker tool
9. report_progress
10. Post FOLLOWUP_PROMPT_S76_PR3344.md (include Outstanding Items with file:line links)
```

---

## 🧠 Memory Patterns Required

- `follow-up-prompt-format` — Outstanding Items MUST include file:line links for deep-research sessions
- `module-ref-monkeypatch` — production code must use `module.func()` not `from module import func` when tests monkeypatch at module level
- `xml-unsafe-import-fallback` — NEVER add `import xml.etree.ElementTree` fallback; raise ImportError instead
- `embedding-cache-set-api` — `EmbeddingCache.set(key, value, *args, **kwargs)` is required for generic callers
- `save-checkpoint-payload-kw` — use `payload=state` not `state=state` when test mock requires `payload=`
- `checkpoint-sha256-embed` — save_checkpoint embeds digest before writing
- `stub-dunder-AttributeError` — stubs raise AttributeError for dunders
- `duplicate-logger-warning` — never duplicate logger.warning in except blocks
