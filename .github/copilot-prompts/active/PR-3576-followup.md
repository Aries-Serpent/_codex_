# 🎯 PR Follow-Up Tasks - #3576

**PR**: #3576 — fix: BrokenPipeError in setup-agent-env + PyJWT 2.12.1 (CVE-2026-32597) + gitignore/.venv_agent + docs_lint nav scoping  
**Branch**: `copilot/hotfix-checkpoint-sessions-22-28` → merged into `main`  
**Author**: @Copilot  
**Merged**: 2026-03-14T10:00Z (SHA: `faecbfb`)  
**Status**: ✅ MERGED — post-merge work queue active

---

## 📋 PR #3576 CHANGES SUMMARY

PR #3576 fixed four cascading agent-runner blockers that prevented self-healing:

| Commit | Deliverable |
|--------|-------------|
| `e53e0d4` | `.venv_agent/` added to `.gitignore`; `_extract_nav_entries` nav scoping fix (line-by-line state machine replaces `yaml.safe_load` + global regex) |
| `faecbfb` | `setup-agent-env`: `PYTHONUNBUFFERED=1`, `PYTHONIOENCODING=utf-8`, `trap '' PIPE` to suppress BrokenPipeError (exit 120); PyJWT bumped to 2.12.1 (CVE-2026-32597 CVSS 7.5 High) |

### Files Modified
- `.gitignore` — `.venv_agent/` pattern added (line 15)
- `scripts/ci/docs_lint.py` — `_extract_nav_entries` rewritten as line-by-line state machine
- `.github/actions/setup-agent-env/action.yml` — BrokenPipeError suppression
- `requirements/lock.txt` — `pyjwt==2.12.1`
- `requirements/agent.txt` — `pyjwt[crypto]>=2.12.1`
- `pyproject.toml` — PyJWT pins updated (×3 locations)

---

## 🎯 POST-MERGE WORK QUEUE

### Priority 1: Immediate Tasks 🔴 CRITICAL

- [x] Verify merge landed cleanly on `main` (SHA: `faecbfb`)
- [x] Run CI capability tests: `python -m pytest tests/capabilities/ci_test/ -q` — 50/50 ✅
- [x] Run ruff: `ruff check scripts/ tests/ src/ --select F401,F841,I001` — 0 issues ✅
- [x] Run `docs_lint --fix` — fixed 5 BROKEN_CLOSER errors in templates/ ✅
- [x] Create missing `.nojekyll` in repository root (GitHub Pages fix) ✅
- [ ] Verify Dependabot alert #3578 (PyJWT CVE-2026-32597) auto-dismissed after pin lands

**Validation**:
```bash
# Verify nav extraction — ~70 clean .md paths, no crash
python3 -c "
from pathlib import Path; import sys; sys.path.insert(0, 'scripts/ci')
from docs_lint import _extract_nav_entries
entries = _extract_nav_entries(Path('mkdocs.yml'))
print(len(entries), 'entries | bad:', [e for e in entries if not e.endswith('.md')])"

# Confirm docs_lint passes
python3 scripts/ci/docs_lint.py --no-links --json | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('pass:', d['pass'])"

# Confirm PyJWT version
python3 -c "import jwt; print(jwt.__version__)"
```

### Priority 2: Follow-Up Validation 🟡 HIGH

- [ ] `T-002`: Open a test PR, confirm cost-gate posts GREEN/YELLOW/RED tier comment — **@mbaetiong**
- [ ] `T-003`: Branch protection: add `cost-gate / classify-and-gate` as required check — **@mbaetiong**
- [ ] MkDocs docs sync: confirm `docs-health.yml` auto-ran on merge to main
- [ ] GitHub Pages: check `https://aries-serpent.github.io/_codex_/` deploys correctly

### Priority 3: Infra (Admin only) 🟢 MEDIUM

- [ ] Fix GHCR registry auth/permissions (Build & Push Preview Image workflow fails)
- [ ] `T-007`: Production sign-off on cost gate (deadline: 2026-04-01) — **@mbaetiong**

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

**When you see `@copilot continue` in PR #3576:**

1. Load this prompt from `.github/copilot-prompts/active/PR-3576-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-03-14  
**Template Version**: 2.0.0  
**Last Updated**: 2026-03-14 07:31:01
