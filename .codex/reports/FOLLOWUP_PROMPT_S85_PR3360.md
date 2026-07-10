# S86 Follow-up Prompt — PR #3248 Continuation

**Session**: S85
**Date**: 2026-02-24
**Branch**: `copilot/sub-pr-3248-again`
**PR**: #3248 → target: `0D_base_` → `main`
**Latest Commits**: `38e5ff190` (PR reviews + EOF + CI fixes), `cf77c533b` (dev/CI parity), `a3a4b99a6` (shared caching) + S85 deliverables commit

---

## S85 Completion Summary

| Task | Status | Commit |
|------|--------|--------|
| Apply PR review comment: HTML in code snippet | ✅ | `38e5ff190` |
| Apply PR review comment: nested BROKEN LINK comments (×2) | ✅ | `38e5ff190` |
| Apply PR review comment: broken grep regex | ✅ | `38e5ff190` |
| Fix CI: dataset_management format exact-match (P-025) | ✅ | `38e5ff190` |
| Fix CI: dataset_management compression size guard (P-028) | ✅ | `38e5ff190` |
| Fix CI: unified_training fake_save return tuple (P-026) | ✅ | `38e5ff190` |
| Fix CI: unified_training epochs=0 validation (P-027) | ✅ | `38e5ff190` |
| Fix pre-commit EOF: 7 files (JSON/MD/YAML) (P-029) | ✅ | `38e5ff190` |
| Create dev_env_setup.sh (330 lines, CI-exact install order) | ✅ | `cf77c533b` |
| Create ci_local.sh (395 lines, subcommand parity) | ✅ | `cf77c533b` |
| Create docs/dev/CI_LOCAL_TESTING.md (453 lines) | ✅ | `cf77c533b` |
| .gitignore + pre-commit .venv_ci exclusions | ✅ | `cf77c533b` |
| Composite action setup-python-cached | ✅ | `a3a4b99a6` |
| cache-pruning.yml (weekly + manual) | ✅ | `a3a4b99a6` |
| 3 workflow updates (pre-merge, resilient, validate) | ✅ | `a3a4b99a6` |
| CI auto-healer agent design (.github/agents/ci-auto-healer-agent.md) | ✅ | S85 deliverables |
| Cognitive brain S85 status (.codex/COGNITIVE_BRAIN_STATUS_S85.md) | ✅ | S85 deliverables |
| Session activity report (SESSION_S85_AGENT_ACTIVITY_REPORT.md) | ✅ | S85 deliverables |
| Knowledge graph v1.6.0 (P-023 through P-029) | ✅ | S85 deliverables |
| AGENT_REGISTRY.yaml v1.2.0 (ci-auto-healer, total=36) | ✅ | S85 deliverables |
| S86 follow-up prompt | ✅ | This file |

---

## Outstanding Items (S86)

### P0 — Verify CI Green (FIRST PRIORITY)

```
list_workflow_runs(branch="copilot/sub-pr-3248-again", status="in_progress")
list_workflow_runs(branch="copilot/sub-pr-3248-again", status="failure")
```

Check ALL workflows:
- `validate.yml`
- `resilient_validation.yml`
- `pre-merge-validation.yml`
- Art_ prefixed jobs (Art_Validation_Pipeline, Art_RAG_Module_Tests)
- CodeQL

If any failures: activate CI Auto-Healer Agent per `.github/agents/ci-auto-healer-agent.md`.

### P1 — Merge `copilot/sub-pr-3248-again` → `0D_base_`

**Prerequisite**: All CI workflows green on latest commit.
**Action**: Approve PR #3248, merge via squash.
**Validation**: Confirm `0D_base_` has all S85 commits.

### P2 — DRQ RS-ARCH-* Recon Scout

- **RS-ARCH-001**: Duplicate function detection across `src/`
  ```python
  import ast, pathlib, collections
  # AST parse all .py files, collect function names
  # Report any name appearing in 3+ modules
  ```
- **RS-ARCH-002**: `__init__.py` gap scan
  ```python
  # For each src/codex*/module.py, check if symbol appears in package __init__.py
  # Report symbols callable as codex.X but not exported via __init__.py
  ```
- **File**: `docs/tech_debt/research_queue/questions_for_research.md`
- **Deliverable**: DRQ entries RS-ARCH-001 and RS-ARCH-002 with findings

### P3 — Agent Ecosystem Map 53 → 70+

- **Action**: Scan `.github/agents/` for `.md` and `.yml` files not in AGENT_REGISTRY.yaml
  ```bash
  ls .github/agents/*.md .github/agents/*.yml | wc -l
  # Compare with total_agents in AGENT_REGISTRY.yaml
  ```
- **For each unregistered agent**: Add entry to AGENT_REGISTRY.yaml with fields matching existing entries
- **Target**: total_agents ≥ 70
- **Update**: `.codex/archive/deprecated/AGENTS.md` specialized agents table

### P4 — run_hf_trainer Extended Integration Tests

- **Location**: `tests/space_traversal/`
- **Purpose**: Integration tests for `run_hf_trainer` with various configurations
- **Test scenarios**:
  - `epochs=0` resume-only (validates P-027 fix)
  - checkpoint save/restore round-trip (validates P-026 fix)
  - multi-GPU mock (use `accelerate` mock)
- **Dependencies**: `pytest.importorskip("torch")`, `pytest.importorskip("transformers")`
- **Skip condition**: `@pytest.mark.skipif(not HAS_GPU, reason="GPU required")`

### P5 — Coverage Phase 23-26 Roadmap

- **Current**: `fail_under=90` in pytest.ini; CI reports ~87% coverage
- **Gap**: ~2.87% (approximately 340 uncovered lines)
- **Action**:
  1. Run `python -m pytest --cov=src --cov-report=term-missing | grep "TOTAL"` to get exact current %
  2. Identify lowest-coverage modules: `--cov-report=term-missing | sort -t% -k2 -n | head -20`
  3. Create targeted test files for top-5 lowest-coverage modules
  4. Re-run coverage to confirm improvement
- **Target**: 90%+ coverage before next merge to main

### P6 — Code Review + CodeQL Scan (Pre-Merge Gate)

**Before any further merges**, run:
```
code_review(prTitle="...", prDescription="...")
codeql_checker()
```

Expected: 0 new CodeQL alerts (all P-014 patterns already applied in S83/S84).

---

## Execution Instructions

```
@copilot continue with S86 tasks on PR #3248 (copilot/sub-pr-3248-again)

Load: .codex/reports/FOLLOWUP_PROMPT_S85_PR3360.md

Priority order:
1. P0 — Verify CI green (list_workflow_runs, fix any failures with ci-auto-healer)
2. P1 — Merge when CI green
3. P2 — DRQ RS-ARCH-001/002 recon scout
4. P3 — Agent ecosystem map expansion to 70+
5. P4 — run_hf_trainer extended tests
6. P5 — Coverage Phase 23-26 roadmap
7. P6 — Code review + CodeQL before any merge

Patterns available: P-001 through P-029 (see .github/agents/ci-auto-healer-agent.md)
CI Auto-Healer: activate on any unexpected CI failures
Run QA coach agent before finalizing.
Update cognitive brain with S86 status.
Post follow-up prompt for S87.
```

---

## Key Files for S86

| File | Purpose |
|------|---------|
| `.github/agents/ci-auto-healer-agent.md` | CI failure pattern library (P-001–P-029) |
| `.codex/COGNITIVE_BRAIN_STATUS_S85.md` | S85 patterns and decisions |
| `.codex/SESSION_S85_AGENT_ACTIVITY_REPORT.md` | All changes made in S85 |
| `.codex/knowledge_graph/graph.json` | v1.6.0 with P-023–P-029 nodes |
| `.github/agents/AGENT_REGISTRY.yaml` | v1.2.0 — 36 registered agents |
| `scripts/dev_env_setup.sh` | Local CI environment setup |
| `scripts/ci_local.sh` | Local CI runner (mirror of CI workflows) |
| `docs/dev/CI_LOCAL_TESTING.md` | CI/local parity guide |
| `.github/actions/setup-python-cached/action.yml` | Shared caching composite action |
| `.github/workflows/cache-pruning.yml` | Weekly cache maintenance |
