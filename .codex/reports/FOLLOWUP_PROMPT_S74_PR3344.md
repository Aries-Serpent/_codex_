# Follow-Up Prompt — S74
**PR**: #3344 / #3348
**Branch**: `copilot/sub-pr-3248-again`
**Prepared by**: GitHub Copilot Agent (S73 session)
**Date**: 2026-02-23
**Status**: Ready for Copilot Execution

---

> **Autonomy Level:** Self-Healing · Self-Troubleshooting · Self-Iterating
>
> **Protocol**: Load Memory → Load Agency Policy → Run Recon Scout → Fix → Code Review → CodeQL → Post S75 Prompt

---

## 📊 S73 Completion Summary

| Task | Status | Commit |
|------|--------|--------|
| `PRECOMMIT_FILES` bash unbound var | ✅ | S73 |
| checkpoint sha256 embed + verify fix | ✅ | S73 |
| checkpoint parent-index upsert | ✅ | S73 |
| `verify_checkpoint` deser wrapping | ✅ | S73 |
| `unified_training.strategies` module ref | ✅ | S73 |
| `_DummyTokenizer.pad_token_id` | ✅ | S73 |
| `test_roundtrip_and_integrity` include_rng=False | ✅ | S73 |
| `test_best_k_retention` exclude state.pt | ✅ | S73 |
| Jinja2 autoescape XSS fix | ✅ | S73 |
| 4× CodeQL import alerts (codex_init, registry, test_run_hf_trainer) | ✅ | S73 |
| `COGNITIVE_BRAIN_STATUS_S73.md` | ✅ | S73 |

---

## 🔴 Outstanding Items (Priority)

### P0 — Verify S73 CI Is Green
After pushing, confirm these jobs pass on the new CI run:
- [ ] Art_Validation Pipeline / Fast Validation
- [ ] Resilient Validation Suite / validation (slow)
- [ ] Resilient Validation Suite / validation (quick)
- [ ] Auto-Fix Common CI Issues
- [ ] GitHub Advanced Security — 5 alerts resolved

### P0 — Unanswered Research Questions (with file:line links)

These questions remain unresolved and need a dedicated deep-research session:

| DRQ ID | Question | File:Line |
|--------|----------|-----------|
| DRQ-S73-001 | **Why does `_prune_best_k` in the parent-index path silently fail to delete epoch dirs when called via `save_checkpoint`?** Is `keep_last` in `UnifiedTrainingConfig` sufficient or does the best-k index also need to track and clean epoch dirs? | [`src/codex_ml/utils/checkpoint_core.py:519`](../../src/codex_ml/utils/checkpoint_core.py#L519) |
| DRQ-S73-002 | **What is the expected behavior of `test_run_hf_trainer.py::test_run_hf_trainer_accepts_empty_texts`?** The test allows `ValueError/RuntimeError` with vague message conditions — should this be tightened or is an empty training set always a user error? | [`tests/space_traversal/test_run_hf_trainer.py:106`](../../tests/space_traversal/test_run_hf_trainer.py#L106) |
| DRQ-S70-004 | **44 remaining `datetime.now()` calls outside `src/`** — which test/script files still have TZ-naive datetime that could cause `TypeError` in Python 3.12 datetime comparison? Full scan needed. | [`docs/tech_debt/research_queue/questions_for_research.md`](../../docs/tech_debt/research_queue/questions_for_research.md) |
| DRQ-S73-003 | **`src/codex_init.py` line 345: `from datetime import datetime` (local import inside function)** — is this the same module-level `datetime` that was removed at line 15, or is it needed for a different purpose? Needs audit. | [`src/codex_init.py:345`](../../src/codex_init.py#L345) |
| DRQ-S73-004 | **`unified_training.py` has duplicate `logger.warning("Exception occurred", exc_info=True)` at lines 238-239**. This is the same anti-pattern fixed in S71 for `hydra_cs.py`. Should be deduplicated. | [`src/codex_ml/training/unified_training.py:238`](../../src/codex_ml/training/unified_training.py#L238) |

### P1 — Recon Scout RS-ARCH-* Rules
- [ ] Run Recon Scout RS-ARCH-* rules: duplicate function detection and `__init__.py` gap scan
- [ ] File new DRQ entries from RS-ARCH output into `docs/tech_debt/research_queue/questions_for_research.md`

### P2 — Validation
- [ ] Verify slow-suite and quick-suite are fully green (no regressions from S73 checkpoint changes)
- [ ] Expand `.codex/knowledge_graph/graph.json` to v1.2.0 (add S73 nodes/edges)
- [ ] Bump `AGENT_REGISTRY.yaml` `total_agents` to reflect S73 session

---

## 📋 Execution Protocol

```
1. @copilot LOAD: related memory (stub-dunder-AttributeError, torch-stub-real-getattr,
   duplicate-logger-warning, checkpoint-sha256-embed, verify-checkpoint-hash-method,
   follow-up prompt format)
2. @copilot LOAD: .codex/CODEBASE_AGENCY_POLICY.md
3. Use GitHub tools (NOT bash/curl) to retrieve CI run logs
4. Invoke Recon Scout Agent:
   "@copilot Use the Recon Scout Agent for pre-CodeQL reconnaissance and DRQ filing"
5. Fix all failures found
6. Self-review (5-pass)
7. code_review tool
8. codeql_checker tool
9. report_progress
10. Post FOLLOWUP_PROMPT_S75_PR3344.md (include Outstanding Items with file:line links)
```

---

## 🧠 Memory Patterns Required

- `follow-up prompt format` — Outstanding Items MUST include file:line links
- `checkpoint-sha256-embed` — `save_checkpoint` re-serializes after embedding digest
- `verify-checkpoint-hash-method` — `hashlib.sha256(_serialize_payload(...))` not `_digest_payload`
- `stub-dunder-AttributeError` — stubs raise `AttributeError` for dunders
- `torch-stub-real-getattr` — `__getattr__` delegation in `_real is not None` branch
- `duplicate-logger-warning` — never duplicate `logger.warning("Exception occurred", exc_info=True)`
