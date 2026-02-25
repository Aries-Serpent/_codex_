# Follow-Up Prompt S78 — PR #3344

**Generated**: S77 — 2026-02-24 — commit 088fc73

---

## 🔴 Outstanding Items (Priority)

### P1 — Verify CI is fully green after S77 commit

- [ ] Check `list_workflow_runs` for branch `copilot/sub-pr-3248-again`
- [ ] Read logs for every failed job with `get_job_logs`
- [ ] Fix any new failures before proceeding

### P2 — Open DRQ items requiring deep research

| DRQ ID | Question | Location |
|--------|----------|----------|
| DRQ-S75-001 | `defusedxml` lazy-import pattern — does it apply to other `tools/` files? | `docs/tech_debt/research_queue/questions_for_research.md:L1` |
| DRQ-S75-003 | FAISS `import faiss` before `FAISSStore` — CI isolation strategy | `docs/tech_debt/research_queue/questions_for_research.md:L1` |

### P3 — Dependabot PRs deferred from S76

| PR | Package | Action |
|----|---------|--------|
| #3356 | Major version bump | Compatibility audit required |
| #3354 | Major version bump | Compatibility audit required |
| #3352 | Transitive dep | Monitor |
| #3349 | Test-only dep | Fixture regression check |

### P4 — Knowledge graph expansion

- Expand `.codex/knowledge_graph/graph.json` beyond v1.2.0
- Add S77 fix nodes: checkpoint_core prune-bug, strategies resolve_strategy,
  unified_training new fields

---

## Execution Instructions

1. Open PR #3344 comment, post `@copilot continue`
2. Load this file: `.codex/reports/FOLLOWUP_PROMPT_S78_PR3344.md`
3. Load memory facts and agency policy FIRST
4. Execute P1 → P2 → P3 → P4 in order
5. Run SESSION COMPLETION CHECKLIST before concluding
