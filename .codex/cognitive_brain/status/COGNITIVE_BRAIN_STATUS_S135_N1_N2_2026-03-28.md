# Cognitive Brain Status — S135 Health Sweep N1+N2

**Generated:** 2026-03-28T06:15Z  
**Session:** S135 (Health Sweep — N1 Pattern 20 Fix + N2 Node.js 20 Upgrade)  
**Branch:** `copilot/s134-health-sweep-codebase`  
**Prior session:** S134 (2026-03-28T05:55Z)

---

## 🟢 Codebase State After S135

| Metric | Before S135 | After S135 | Change |
|--------|-------------|------------|--------|
| Pattern 20 (YAML multiline) | 4 workflows, 9 hits | **0** | ✅ Fixed |
| Pattern 21 refs (Node.js 20) | 211 refs, 123 workflows | **28 refs, 28 workflows** | ↓ 87% |
| Active `@v4` action refs | 187+ files | **0 active .yml files** | ✅ Upgraded |
| Ruff violations | 0 | **0** | → |
| Auto-fixable issues | 0 | **0** | → |
| CI health (main) | 100% | **100%** | → |

---

## 🔧 Fixes Applied

### N1 — Pattern 20 YAML Multiline Bash → printf

**Pattern:** `VAR="...\n...multiline..."` inside GitHub Actions `run: |` blocks  
**Risk:** actionlint YAML parse errors in CI; static analysis false positives  
**Fix:** Convert to `$(printf '%s\n' 'line1' "line2 ${VAR}" ...)` form

Files fixed (9 hits total):
1. `.github/workflows/agent-auth-delegation.yml` — `APPENDED` ×2, `NEW_BODY`
2. `.github/workflows/copilot-session-chain.yml` — `PR_BODY`, `TRIGGER_COMMENT` ×2
3. `.github/workflows/create-sub-pr-to-0D_base_.yml` — `PR_BODY`
4. `.github/workflows/promote-integration-branch.yml` — `PR_BODY` ×2

**Template for future use:**
```bash
# Static content only → single-quoted args
VAR=$(printf '%s\n' \
  '## Static heading' \
  '' \
  '- [ ] checklist item')

# Mix of static and dynamic → combine quoting styles
VAR=$(printf '%s\n' \
  '## Heading' \
  "**Branch:** \`${BRANCH_NAME}\`" \
  '```' \
  "${BRANCH_NAME}  ──►  main" \
  '```')
```

### N2 — Node.js 20 Actions: @v4 → @v5

**Actions upgraded to v5 (Node.js 24):**

| Action | Files Updated | Method |
|--------|--------------|--------|
| `actions/checkout` | 125 active + 14 disabled/template | batch replace |
| `actions/upload-artifact` | 44 active + 12 disabled/template | batch replace |
| `actions/download-artifact` | 10 active + 1 disabled | batch replace |
| `actions/cache` | 16 active + 1 disabled | batch replace |
| `actions/deploy-pages` | 2 active | batch replace |

**Pattern 21 checker updated (two-tier regex):**
- Group A (`checkout`, `upload-artifact`, `download-artifact`, `cache`, `setup-node`, `configure-pages`, `deploy-pages`): flag v1–v4 only (v5+ is Node.js 24)
- Group B (`setup-python`, `github-script`): flag v1–v5 (v6+ will be Node.js 24)

**Result:** Pattern 21: 211 refs → 28 refs (86.7% reduction)

---

## 📋 Next-Phase Plan (N4 onwards)

### N4 — setup-python @v5 → @v6 (Priority: Low, Deadline: 2026-06-02)
- **Target:** 28 workflows using `actions/setup-python@v5`
- **Blocker:** `actions/setup-python@v6` not yet widely available (check GitHub Marketplace first)
- **Approach:** Same batch replace pattern as N2

### N5 — P19 src-Import Enforcement (Priority: Low, Ongoing)
- **Policy:** Enforce `from <pkg>` in all NEW code; no mass-refactor
- **Mechanism:** PR review catch-all; `ruff` doesn't flag this (it's a convention, not a lint error)

---

## 🧠 New Patterns Learned

### PRINTF-001: YAML Multiline Bash Strings
- **Trigger:** `VAR="...\n...` inside GitHub Actions `run: |` blocks
- **Detection:** Pattern 20 checker (`auto_fix_common_issues.py`)
- **Fix:** `VAR=$(printf '%s\n' 'line1' "line2 ${VAR}" ...)`
- **Single-quote for static lines** (backticks are literal in single quotes)
- **Double-quote for lines needing `${VAR}` expansion**
- **triple backtick** in printf single-quoted arg → `'```'` (works perfectly)

### NODEJS20-001: Two-Tier Version Detection
- Different action families have different "safe" cutoff versions
- Group A (most actions): v5+ = Node.js 24
- Group B (setup-python, github-script): v5 is STILL Node.js 20; v6+ = Node.js 24
- Must track per-action-family safe version, not a single global cutoff

---

## 🔗 Cross-References
- `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` — S135 session summary
- `.codex/cognitive_brain/objectives_tracker.md` — v1.2.0, sweep log updated
- `scripts/ci/auto_fix_common_issues.py` — Pattern 21 two-tier regex (S135)
- `.github/workflows/copilot-session-chain.yml` — printf PR_BODY pattern (S135)
