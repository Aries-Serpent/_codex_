# 🎯 PR Follow-Up Tasks - #3604

**PR**: #3604 - Phase 4 Production Hardening  
**Branch**: `copilot/analyze-gaps-and-risks`  
**Author**: @Copilot  
**Date**: 2026-03-17  
**Commit**: `257ef6d`  
**Status**: 🔄 ACTIVE

---

## 📋 PREVIOUS SESSION SUMMARY

### Completed Work (S129–S131)
- S129: NumpyStub 19 missing methods, `_NpStubDev` fallback, auth env leak fix
- S130: `github_provider.create_token()` + `update_token_scopes()`, Phase 4 plan, 5 tests
- S131: Health endpoint enhanced (BrainClient + PatternCompressor), ZendeskSyncer wired,
  coherence OTel export, reviewer feedback addressed (8 threads)

---

## 🎯 NEXT PHASE OBJECTIVES

### Priority 1: Immediate Tasks 🔴 CRITICAL
- [ ] Wire PatternCompressor compression ratio to `/api/health` response (live metrics)
- [ ] Add BrainClient `memory_search()` latency to health diagnostics
- [ ] End-to-end token rotation test with real GitHub App (requires human admin)

**Validation**:
```bash
python3 -m pytest tests/api/ tests/security/test_providers.py -q --timeout=30
python3 -m ruff check src/codex/api/app.py src/security/providers/github_provider.py
```

### Priority 2: Follow-Up Validation 🟡 HIGH
- [ ] Full broad test sweep (>10 min — run with `make ci` or `nox -s tests`)
- [ ] Build HTML→context adapter for `codex_digest` pipeline integration

### Priority 3: Future Enhancements 🟢 MEDIUM
- [ ] Implement Redis backend for distributed RAG cache (`src/codex/rag/cache/`)
- [ ] Add `@pytest.mark.slow` to any remaining unmarked long-running tests
- [ ] Promote `CODEX_VERY_STALE_BRANCH_DAYS` policy to `.codex/guardrails.md`

---

## ✅ EXECUTION CHECKLIST

- [ ] All Priority 1 tasks completed and validated
- [ ] All Priority 2 tasks completed or documented
- [ ] Priority 3 tasks reviewed and prioritized
- [ ] All validation checks passed
- [ ] Documentation updated
- [ ] Self-review completed (5 passes, 0 concerns)

---

## 🔍 MANDATORY SELF-REVIEW PROTOCOL

**CRITICAL**: Perform 5 comprehensive self-review passes BEFORE concluding.

### Pass 1: Code Quality & Correctness
- [ ] All syntax errors resolved
- [ ] No linting warnings introduced
- [ ] Type hints correct
- [ ] Error handling comprehensive
- [ ] Edge cases covered

### Pass 2: Testing & Validation
- [ ] All tests passing locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved
- [ ] CI/CD checks passing

### Pass 3: Documentation & Communication
- [ ] Code comments added for complex logic
- [ ] Docstrings updated
- [ ] README reflects changes
- [ ] CHANGELOG updated
- [ ] Commit messages descriptive

### Pass 4: Security & Safety
- [ ] No hardcoded secrets or credentials
- [ ] Input validation added
- [ ] Dependencies reviewed (no vulnerabilities)
- [ ] Security implications documented

### Pass 5: Integration & Dependencies
- [ ] No breaking changes (or properly documented)
- [ ] Backward compatibility maintained
- [ ] Cross-PR dependencies resolved
- [ ] No regressions introduced

**Failure Protocol**: If ANY checkpoint fails, document issue, create resolution plan, execute within current session, re-run until all checks clear. **NEVER defer** without explicit reasoning.

---

## 🤖 COPILOT AGENT INSTRUCTIONS

**When you see `@copilot continue` in PR #3604:**

1. Load this prompt from `.github/copilot-prompts/active/PR-3604-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-03-17  
**Template Version**: 2.0.0  
**Last Updated**: 2026-03-17 00:01:55
