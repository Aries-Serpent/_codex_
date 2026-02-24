# S84 Follow-up Prompt — PR #3359 Continuation

**Session**: S84
**Date**: 2026-02-24
**Branch**: `copilot/sub-pr-3248`
**PR**: #3359 → target: `0D_base_` → `main`
**Latest Commit**: `b4d157b` (defusedxml fix)

---

## S84 Completion Summary

| Task | Status | Commit |
|------|--------|--------|
| Fix CodeQL alert: file_paths→files in indexer.py | ✅ | `eee8a0f` |
| Fix CodeQL alert: __all__ in cli_rag.py | ✅ | `eee8a0f` |
| Strip trailing whitespace from S83 docs | ✅ | `eee8a0f` |
| Fix Resilient Suite: defusedxml dependency | ✅ | `b4d157b` |
| Fix Resilient Suite: import guards in tests/scripts | ✅ | `b4d157b` |
| Fix RAGIndexer.build_index return type Dict→Path | ✅ | `b4d157b` |
| datetime.now() TD-001: 3 utcnow→now(utc) | ✅ | pending commit |
| Cognitive brain S84 status | ✅ | pending commit |
| Knowledge graph v1.5.0 | ✅ | pending commit |
| QA coach self-review (iteration 1) | ✅ | All areas PASS |
| Verify CI green on b4d157b | ⏳ | Awaiting run completion |

---

## Outstanding Items (S85)

### P0 — Verify CI Green
- **Commit**: Latest after S84 commit
- **Action**: `list_workflow_runs(branch="copilot/sub-pr-3248")` — check ALL workflows

### P1 — DRQ RS-ARCH-* Recon Scout
- **File**: `docs/tech_debt/research_queue/questions_for_research.md`
- **RS-ARCH-001**: Duplicate function detection across `src/`
- **RS-ARCH-002**: `__init__.py` gap scan — find missing re-exports
- **Method**: AST analysis with `ast.parse()` across all Python files

### P2 — Agent Ecosystem Map Update
- **Current**: 54 agents registered
- **Target**: 70+ agents
- **Action**: Scan `.github/agents/` for unregistered agents, update AGENT_REGISTRY.yaml

### P3 — run_hf_trainer Extended Tests
- **Location**: `tests/space_traversal/`
- **Purpose**: Integration tests for `run_hf_trainer` with various configurations
- **Dependencies**: torch, transformers, accelerate (use `pytest.importorskip`)

### P4 — Coverage Phase 23-26 Roadmap
- **Current**: fail_under=90, CI coverage 2.87% gap
- **Action**: Identify lowest-coverage modules, create targeted test files

### P5 — Production Copilot Agent Design
- **Scope**: Design CI-targeted agent with Mermaid diagrams
- **Integration**: cognitive brain pattern library, AfterMath/PDA loops
- **Deliverable**: `.github/agents/ci-auto-healer-agent.md`

---

## Execution Instructions

```
@copilot continue with S85 tasks on PR #3359

Load: .codex/reports/FOLLOWUP_PROMPT_S84_PR3359.md

Priority order:
1. Verify CI green on latest commit
2. P1 — DRQ RS-ARCH-* recon scout
3. P2 — Agent ecosystem map expansion
4. P3 — run_hf_trainer extended tests
5. P5 — CI auto-healer agent design

Run QA coach agent before finalizing.
Update cognitive brain with S85 status.
Post follow-up prompt for S86.
```
