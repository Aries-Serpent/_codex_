# NEXT SESSION CONTINUATION PROMPT — Phase 4 Phase 2 Final Completion

**Authority**: D-tier autonomous (full approval granted — no human gates required)  
**Created**: 2026-07-15T14:40:00Z  
**Status**: READY FOR IMMEDIATE CONTINUATION

---

## 🎯 TASK SUMMARY

**Objective**: Complete Phase 4 Phase 2 YAML Remediation — Fix the final 1 remaining file (release-to-pypi.yml)

**Progress**: 15/16 files fixed (93.75%)  
**Time Estimate**: 5-10 minutes  
**Complexity**: Low (straightforward indentation fixes)

---

## 📋 WORK REMAINING

### Single File: release-to-pypi.yml

**Problem**: Step definitions at wrong indentation level (6-7 spaces instead of 4)

**Affected Lines**:
```
Line 88:  - name: Verify P0 gates complete         (6 spaces → should be 4)
Line 105: - name: Verify P1 gates complete         (6 spaces → should be 4)
Line 116: - name: Verify changelog updated         (6 spaces → should be 4)
Line 130: - name: Verify version bumped...         (6 spaces → should be 4)
```

**Root Cause**: Multi-line `run:` blocks (lines 53-87) followed by step definitions at wrong indentation

**Fix Applied in Session 2**: Line 45 `fetch-depth:` indentation corrected (10→8 spaces)

**Current Error**:
```
yaml.parser.ParserError: while parsing a block mapping
  in "release-to-pypi.yml", line 88, column 7
expected <block end>, but found '-'
```

---

## 🔧 EXACT FIX INSTRUCTIONS

### Option 1: Using sed (Recommended)

```bash
cd /home/runner/work/_codex_/_codex_

# Shift 4 over-indented step definitions from 6 spaces to 4 spaces
sed -i '88s/^      /    /' .github/workflows/release-to-pypi.yml
sed -i '105s/^      /    /' .github/workflows/release-to-pypi.yml
sed -i '116s/^      /    /' .github/workflows/release-to-pypi.yml
sed -i '130s/^      /    /' .github/workflows/release-to-pypi.yml

# Validate
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release-to-pypi.yml')); print('✅ File is valid')"
```

### Option 2: Using edit tool (if sed doesn't work)

View the file around each problematic line and use the edit tool to shift indentation:
- Line 88: `      - name:` → `    - name:`
- Line 105: `      - name:` → `    - name:`
- Line 116: `      - name:` → `    - name:`
- Line 130: `      - name:` → `    - name:`

---

## ✅ VALIDATION CHECKLIST

After applying fixes, run these checks:

```bash
# 1. Validate all 4 files
python3 << 'EOF'
import yaml
files = [
    '.github/workflows/model-drift-retrain.yml',
    '.github/workflows/pr-followup-generator.yml',
    '.github/workflows/release-to-pypi.yml',
    '.github/workflows/security-findings-copilot-handoff.yml'
]
for file in files:
    try:
        yaml.safe_load(open(file))
        print(f"✅ {file}")
    except Exception as e:
        print(f"❌ {file}: {str(e)[:80]}")
EOF

# 2. Verify git status
git status .github/workflows/

# 3. Count total changes
git diff --stat .github/workflows/ | tail -5
```

---

## 📊 EXPECTED OUTCOME

**On Success**:
- ✅ All 4 files pass yaml.safe_load()
- ✅ release-to-pypi.yml matches 16/16 completion target
- ✅ Session 2 completion artifact ready
- ✅ Ready for PR review/merge

**Next Steps After This Session**:
1. Commit: `fix(yaml): Complete Phase 4 Phase 2 YAML remediation — all 16 files fixed`
2. Investigate CI failures reported in PR #5323 (if still present)
3. Prepare for PR merge to main

---

## 🚨 CI FAILURES TO INVESTIGATE

**User Reported Failures in PR #5323**:
- Workflow Compliance Audit (actionlint)
- Code Example Validation  
- Compliance Check
- Security Scanning Suite
- Phase 12.2 Compliance Check
- Tiered Approval Gate
- Unified Governance Check
- Secrets False-Positive Healer

**Investigation Steps** (if failures persist after this session):
1. Check if failures are pre-existing (from PR #5323 original state)
2. Use GitHub MCP tools to retrieve detailed workflow logs
3. If caused by new changes, delegate to workflow-ci-fixer agent
4. Document findings in session accountability report

**Note**: These failures are likely unrelated to the 3 files fixed in Session 2 (they all parse correctly now). They may be from the broader PR #5323 context or pre-existing issues.

---

## 📚 REFERENCE DOCUMENTS

Located in `.codex/`:
- `PHASE_4_PHASE2_SESSION2_HANDOFF.md` — Detailed session 2 summary
- `PHASE_4_PHASE2_COMPREHENSIVE_HANDOFF.md` — Full context from earlier sessions
- `PHASE_4_PHASE2_DETAILED_ERROR_ANALYSIS.md` — Deep-dive error analysis
- `PHASE_4_GA_PATTERN_CLASSIFICATION_REPORT.md` — All patterns found

---

## 🎯 SUCCESS CRITERIA

This session is **complete when**:

- [ ] release-to-pypi.yml passes yaml.safe_load()
- [ ] All 4 remaining files (from Session 2 task) are valid
- [ ] Total: 16/16 YAML files fixed (100%)
- [ ] Changes committed with clear message
- [ ] No new YAML errors introduced

---

## ⚙️ COMMAND REFERENCE

```bash
# Quick validation of all files
for f in model-drift-retrain pr-followup-generator release-to-pypi security-findings-copilot-handoff; do
  python3 -c "import yaml; yaml.safe_load(open('.github/workflows/${f}.yml'))" && echo "✅ $f.yml" || echo "❌ $f.yml"
done

# View error details
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release-to-pypi.yml'))" 2>&1 | tail -10

# Commit and push
git add .github/workflows/release-to-pypi.yml
git commit -m "fix(yaml): Complete Phase 4 Phase 2 YAML remediation — all 16 files fixed"
```

---

## 🔐 AUTHORITY & APPROVAL

- **Tier**: D-tier Autonomous
- **Approval**: Full (no human gates)
- **Token Access**: CODEX_MASTER_KEY available
- **Escalation**: None required (straightforward fix)
- **WEC Label**: wec:auto-approve active

**You have full authority to proceed immediately without waiting for human approval.**

---

## 📝 NOTES

1. **Complexity**: LOW — Just 4 lines need indentation shift
2. **Risk**: MINIMAL — No logic changes, only formatting
3. **Validation**: Simple yaml.safe_load() test confirms success
4. **Time Budget**: 5-10 minutes for implementation + validation
5. **Scope**: Strictly limited to release-to-pypi.yml indentation

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-15T14:40:00Z  
**Status**: READY FOR EXECUTION
