# Implementation Checklist - Copilot Agent Patterns

**Source:** Check run investigation (job 62523872141)  
**Date:** 2026-02-04  
**Status:** Ready for implementation

---

## ✅ Critical (Must Implement)

### 1. Workflow Script Error Handling

**File:** `.github/workflows/test-suite.yml`

**Change required:**
```bash
# Find the test collection step and update it:

# OLD CODE (problematic):
COLLECT_OUTPUT="$(python -m pytest tests/ --collect-only -q 2>&1)"
COLLECT_STATUS=$?
printf '%s\n' "$COLLECT_OUTPUT" | head -50

# NEW CODE (fixed):
set +e
COLLECT_OUTPUT="$(python -m pytest tests/ --collect-only -q 2>&1)"
COLLECT_STATUS=$?
set -e
printf '%s\n' "$COLLECT_OUTPUT"

if [ "$COLLECT_STATUS" -ne 0 ]; then
  echo "⚠️  Test collection failed with exit code $COLLECT_STATUS"
  exit "$COLLECT_STATUS"
fi
```

**Why:** Prevents loss of diagnostic information when pytest fails

**Test:** Run `python -m pytest tests/ --collect-only -q` locally first

**Status:** [ ] To Do

---

## ⭐ Recommended (Should Implement)

### 2. Multi-Format Reporting

**Pattern:** Create reports in multiple formats for different audiences

**For each investigation, create:**
- [ ] `EXECUTIVE_SUMMARY.md` - High-level overview for stakeholders
- [ ] `detailed-analysis.md` - Technical deep dive for developers
- [ ] `quick-ref.txt` - Fast lookup for anyone
- [ ] `summary.txt` - CLI-friendly text format
- [ ] `INDEX.md` - Navigation and report catalog

**Example structure:**
```
reports/
├── EXECUTIVE_SUMMARY.md
├── INDEX.md
├── ci-logs-[run-id]-job-[job-id].md
├── quick-ref.txt
└── summary.txt
```

**Status:** [ ] To Do

---

### 3. Artifact Organization

**Pattern:** Separate raw data from analysis

**Directory structure:**
```
artifacts/
├── job-[id]-full.log          # Raw GitHub Actions logs
├── [module]-output.log         # Test output logs
└── [other raw data]

reports/
├── EXECUTIVE_SUMMARY.md        # Analysis
├── INDEX.md                    # Navigation
├── [specific-reports].md       # Detailed analysis
└── [quick-references].txt      # Quick refs
```

**Status:** [ ] To Do

---

### 4. Change Log Documentation

**File:** `.codex/change_log.md`

**Pattern:** Each investigation entry should include:
```markdown
## 📝 [TIMESTAMP] - [TITLE]

### 🔍 [INVESTIGATION TYPE]
**Agent**: [agent-name]
**Authority**: [Read-only | Full | Limited]
**[Context identifiers]**: [values]

#### [Issue Title]
**Issue**: [Description]
**Impact**: [What broke/affected]
**Root Cause**: [Why it happened]

**Investigation Results**:
- ✅ [Success 1]
- ✅ [Success 2]
- ❌ [Limitation or blocked item]

**Artifacts Generated**:
- `path/to/artifact1` - Description
- `path/to/artifact2` - Description

**Remediation Recommendations**:
1. [Action 1]
2. [Action 2]

**Files Analyzed**:
- `path/to/file` (what was found)
```

**Status:** [ ] To Do

---

### 5. Investigation Methodology

**Standard process for CI failures:**

1. **Identify Failure Point**
   - [ ] Which phase? (setup, build, test collection, test execution, etc.)
   - [ ] What time did it fail?
   - [ ] How long did it run?

2. **Determine Exit Code**
   - [ ] What was the exit code?
   - [ ] What does that exit code mean?
   - [ ] Is this a test failure or system error?

3. **Analyze Timing**
   - [ ] How long did the failing step take?
   - [ ] Did it timeout?
   - [ ] Was it faster/slower than expected?

4. **List Likely Causes**
   - [ ] Based on exit code
   - [ ] Based on phase
   - [ ] Based on recent changes

5. **Provide Reproduction Steps**
   - [ ] Exact command to run locally
   - [ ] Environment requirements
   - [ ] Expected vs actual output

6. **Create Verification Checklist**
   - [ ] Items to verify
   - [ ] Success criteria
   - [ ] Follow-up actions

**Status:** [ ] To Do

---

### 6. Report Templates

**Create reusable templates for:**

- [ ] **Executive Summary Template**
  - Key findings section
  - Impact assessment
  - Recommendations
  - Success criteria

- [ ] **Technical Analysis Template**
  - Timeline
  - Command breakdown
  - Error analysis
  - Environment details
  - Remediation steps

- [ ] **Quick Reference Template**
  - Problem statement
  - Root cause
  - Fix code
  - Verification steps

**Status:** [ ] To Do

---

## 📋 Implementation Priority

### Phase 1: Critical (Week 1)
- [x] Investigate check run 62527073812
- [ ] Fix workflow script error handling
- [ ] Test fix locally
- [ ] Deploy fix to CI

### Phase 2: Documentation (Week 2)
- [ ] Adopt multi-format reporting
- [ ] Organize artifacts directory
- [ ] Update change log pattern
- [ ] Create report templates

### Phase 3: Process (Week 3)
- [ ] Document investigation methodology
- [ ] Train team on new patterns
- [ ] Review existing reports
- [ ] Establish maintenance schedule

---

## 🎯 Success Criteria

**You'll know the implementation is complete when:**

1. ✅ CI workflow scripts never lose diagnostic output
2. ✅ All investigations have executive summaries
3. ✅ Reports follow consistent multi-format pattern
4. ✅ Artifacts are organized in standard directories
5. ✅ Change log follows documented pattern
6. ✅ Investigation methodology is documented and followed
7. ✅ Team can easily find and navigate reports

---

## 📚 Reference Documents

- `reports/copilot_implementation_summary.md` - Complete implementation guide
- `reports/check_run_62527073812_investigation.md` - Detailed investigation
- `reports/EXECUTIVE_SUMMARY.md` - Example executive summary
- `reports/INDEX.md` - Example report index
- `reports/CI-QUICK-REF.txt` - Example quick reference

---

## 🚀 Quick Start

**To implement immediately:**

1. Fix the workflow script (30 min)
2. Test locally (10 min)
3. Update one existing report to new format (1 hour)
4. Create templates directory (30 min)
5. Document process in team wiki (1 hour)

**Total time:** ~3 hours for critical path

---

**Checklist Version:** 1.0  
**Last Updated:** 2026-02-04 19:10 UTC  
**Owner:** Team Lead / DevOps
