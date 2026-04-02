<!-- pr-followup-prompt-generated -->
# S267 Follow-Up Prompt — Next Copilot Agent

**PR:** #3846 (`0D_base_`)
**Session:** S267 — 2026-04-01T21:47Z
**Status:** CI fixes applied (commit pending)

---

## ✅ Completed in S267

1. **actionlint SC2288** — `resilient_validation.yml:95` fixed (env var for `${{ github.base_ref }}`)
2. **Trailing whitespace** — `AGENT_ACCOUNTABILITY_REPORT.md:26` stripped
3. **Line length** — `src/codex/rag/embeddings.py:652` wrapped (102→77 chars)
4. **SHA-scoped rescue markers** — 6 workflows + `ci_rescue.py` updated
5. **S266 PDA AfterMath** — retroactively documented (session job 69598659895 ended at cache-save)
6. **Cognitive brain** — S266 + S267 entries added

---

## 🔴 Priority 1 — Must Verify on Next Push

After pushing S267 fixes, verify CI passes on:
- [ ] `Workflow Compliance Audit (actionlint)` — should be green (SC2288 fixed)
- [ ] `Validation Pipeline / Fast Validation` — should be green (trailing whitespace fixed)
- [ ] `PR Auto-Fix Check` — should be green (line length fixed)
- [ ] **SHA-scoped comment grouping** — confirm next CI failure posts to `<!-- ci-rescue:{pr}:sha-{sha12} -->` (not run-ID marker)

---

## 🟡 Priority 2 — Remaining RAG Test Failures (13 complex)

See `.github/copilot-prompts/active/RAG-test-failures-followup.md` for full RCA.

Key failures still outstanding:
1. `test_rag_utils_safe_model_to_device` — mock patch target changed after `has_meta_tensors()` refactor
2. `test_rag_indexer_*` — FAISS index wiring, `IndexFlatL2` constructor mock
3. `test_rag_retriever_*` — `RAGRetriever.retrieve()` network-access guard tests
4. `test_embedding_model_*` — `EmbeddingModel._ensure_loaded()` lazy-load sequence

**Investigation steps:**
```bash
# Run just the RAG tests to see current status
python -m pytest tests/codex/rag/ -x -v 2>&1 | head -80
```

---

## 🟡 Priority 3 — mypy Baseline Update

After CI confirms error count ≤ 297:
```bash
python scripts/ci/mypy_baseline.py --update
git add .mypy_baseline && git commit -m "fix(mypy): ratchet baseline to N after S265 cleanup"
```

---

## 🟢 Priority 4 — Further mypy unused-ignore cleanup

Apply same pattern as `src/training/` to:
- `src/codex_ml/` — check for `import-untyped` ignores
- `src/workers/` — check for `import-untyped` ignores
- `src/tokenization/` — check for `import-untyped` ignores
- `src/evaluation/` — check for `import-untyped` ignores

---

## 📋 Self-Review Checklist (MANDATORY before concluding)

- [ ] All 3 CI failures from run 23871259844/23871259959/23871259960 resolved
- [ ] SHA-scoped rescue comments tested (all failures for same commit → same PR comment)
- [ ] AGENT_ACCOUNTABILITY_REPORT.md updated
- [ ] Cognitive brain metadata updated
- [ ] No new actionlint errors introduced
- [ ] No new ruff/mypy errors introduced
- [ ] WEC block preserved in PR body with `documentation-link-checker.yml` entry

---

## 🧠 Key Patterns to Remember

| Pattern | Resolution |
|---------|-----------|
| `${{ github.* }}` in `run:` | Always use `env:` block → reference `$VAR_NAME` |
| Trailing whitespace in accountability report | Always run `sed -i 's/[[:space:]]*$//'` before committing |
| rescue comment scoping | SHA-scoped: same commit = same comment; new push = new comment |
| agent session terminated at cache-save | Code was committed; only AfterMath doc was missed — always write AfterMath FIRST |

---

## 📌 WEC Preservation Note

Always include `documentation-link-checker.yml` in the `## 📄 Documentation` section of the WEC block.
