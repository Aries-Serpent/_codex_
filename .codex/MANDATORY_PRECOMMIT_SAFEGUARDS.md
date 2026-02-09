# 🚨 MANDATORY: Pre-Commit Safeguards for Copilot Sessions

**Policy**: ZERO TOLERANCE for temporary file violations  
**Authority**: Repository owner requirement + .github/TEMPORARY_FILES_POLICY.md  
**Status**: MANDATORY - Must be followed by ALL agents

---

## ⚠️ CRITICAL: Why This Matters

**Previous Violations**:
- Session 1: Stored 42KB of analysis in `/tmp/` → LOST
- Session 2: Referenced `/tmp/` files in PR description → INACCESSIBLE
- **Impact**: Hours of work lost, continuity broken, trust damaged

**Root Cause**: Not verifying commit contents + using /tmp/ for work products

---

## ✅ MANDATORY Checklist (Before EVERY Commit)

### Step 1: Verify No Files in /tmp/
```bash
# Run this FIRST
bash scripts/verify_no_tmp_files.sh

# If it fails: Move files to proper locations IMMEDIATELY
# Example:
mv /tmp/important_file.md .codex/important_file.md
git add .codex/important_file.md
```

### Step 2: Review What Will Be Committed
```bash
# Run this BEFORE git commit
bash scripts/verify_commit_contents.sh

# Review output carefully:
# - Are all files in correct locations?
# - Are there any /tmp/ references?
# - Do filenames match their content?
```

### Step 3: Verify With Git Status
```bash
# ALWAYS run before committing
git status

# Check:
# ✓ Files are in .codex/, docs/, reports/, or artifacts/
# ✗ NO files in tmp/, temp/, or temporary locations
```

### Step 4: Review Staged Changes
```bash
# ALWAYS run before committing
git diff --cached

# Verify:
# ✓ Changes are intentional
# ✓ No /tmp/ paths in content
# ✓ No debugging code left in
```

### Step 5: List Committed Files in Message
```bash
# Commit message MUST list files
git commit -m "type(scope): Description

Files modified:
- .codex/analysis.md (NEW - 10KB analysis document)
- docs/guide.md (Updated implementation section)
- scripts/tool.sh (Added verification)

[Verification completed: scripts/verify_no_tmp_files.sh ✓]
"
```

---

## 🛠️ Tools Provided

### 1. verify_no_tmp_files.sh
**Purpose**: Check for important files left in /tmp/  
**When**: Before EVERY commit  
**Action**: Fails if any .md, .txt, .json, etc. found in /tmp/

```bash
bash scripts/verify_no_tmp_files.sh
# Must show: ✅ No important files in /tmp/
```

### 2. verify_commit_contents.sh
**Purpose**: Review what will be committed  
**When**: Before EVERY commit  
**Action**: Shows files, checks locations, finds /tmp/ refs

```bash
bash scripts/verify_commit_contents.sh
# Review output carefully before proceeding
```

### 3. Quick Verification (Combined)
```bash
# Run both checks
bash scripts/verify_no_tmp_files.sh && \
bash scripts/verify_commit_contents.sh && \
git status && \
git diff --cached --stat
```

---

## 📋 Proper File Locations

### ✅ CORRECT Locations

| File Type | Location | Example |
|-----------|----------|---------|
| Analysis documents | `.codex/` | `.codex/PR3178_analysis.md` |
| Session summaries | `.codex/` | `.codex/session_2026_02_09.md` |
| Implementation guides | `.codex/` | `.codex/quick_start.md` |
| Plans & roadmaps | `.codex/` | `.codex/implementation_plan.md` |
| Reports | `reports/` | `reports/test_results.md` |
| Documentation | `docs/` | `docs/guides/testing.md` |
| Artifacts | `artifacts/` | `artifacts/generated/output.json` |
| Scripts | `scripts/` | `scripts/verify_tool.sh` |

### ❌ PROHIBITED Locations

| Location | Why Prohibited | Alternative |
|----------|----------------|-------------|
| `/tmp/` | Cleared on reboot | `.codex/` |
| `/var/tmp/` | Cleared periodically | `.codex/` |
| `~/tmp/` | Not tracked in git | `.codex/` |
| `/home/runner/work/_temp/` | CI temporary | `.codex/` |

---

## 🔍 Detection Patterns

### What Triggers a Violation?

1. **File in /tmp/ with important extension**:
   - `*.md`, `*.txt`, `*.json`, `*.yaml`, `*.py`, `*.sh`
   - Files with keywords: analysis, report, summary, followup, plan, guide

2. **/tmp/ reference in code**:
   ```python
   # ❌ WRONG
   output_path = "/tmp/analysis.md"
   
   # ✅ CORRECT
   output_path = Path(".codex") / "analysis.md"
   ```

3. **Commit without verification**:
   - No verification script run
   - Files not reviewed
   - /tmp/ refs in commit

---

## 🚀 Workflow Example

### Correct Workflow
```bash
# 1. Create files in proper location from the start
echo "# Analysis" > .codex/analysis.md

# 2. Verify no files in /tmp/
bash scripts/verify_no_tmp_files.sh
# Output: ✅ No important files in /tmp/

# 3. Stage files
git add .codex/analysis.md

# 4. Verify commit contents
bash scripts/verify_commit_contents.sh
# Output: Shows file will be committed in correct location

# 5. Review changes
git diff --cached

# 6. Commit with file listing
git commit -m "docs: Add analysis document

Files added:
- .codex/analysis.md (NEW - analysis results)

[Verified: scripts/verify_no_tmp_files.sh ✓]
"

# 7. Push
git push
```

### Wrong Workflow (DO NOT DO THIS)
```bash
# ❌ Creating file in /tmp/
echo "# Analysis" > /tmp/analysis.md

# ❌ Committing without verification
git commit -m "Add analysis"

# ❌ Result: File not committed, work lost when /tmp/ cleared
```

---

## 🎯 Success Criteria

### Before Considering Session Complete

- [ ] Ran `bash scripts/verify_no_tmp_files.sh` → PASSED
- [ ] Ran `bash scripts/verify_commit_contents.sh` → PASSED
- [ ] Ran `git status` → Reviewed all files
- [ ] Ran `git diff --cached` → Reviewed all changes
- [ ] Commit message lists all files modified
- [ ] All files in proper locations (.codex/, docs/, etc.)
- [ ] No /tmp/ references in any committed content
- [ ] Verification noted in commit message

---

## 📊 Verification Log Template

Add this to EVERY commit message:

```
[Pre-Commit Verification]
✓ scripts/verify_no_tmp_files.sh - PASSED
✓ scripts/verify_commit_contents.sh - PASSED  
✓ git status reviewed
✓ git diff --cached reviewed
✓ All files in proper locations
✓ No /tmp/ references
```

---

## 🚨 Enforcement

### If Violation Detected

1. **STOP immediately**
2. **Run verification scripts**
3. **Move any /tmp/ files to proper locations**
4. **Remove /tmp/ references from code**
5. **Re-verify before committing**
6. **Document the correction**

### Violation Response Template
```markdown
## Policy Violation Corrected

**Issue**: Files found in /tmp/ directory
**Files Affected**: [list files]
**Action Taken**: Moved to .codex/ directory
**Verification**: scripts/verify_no_tmp_files.sh PASSED

All files now properly stored in repository structure.
```

---

## 💾 Memory Storage

Store these facts in memory for future sessions:

1. **NEVER use /tmp/ for work products**
2. **ALWAYS run verification scripts before commit**
3. **ALWAYS list files in commit message**
4. **ALWAYS verify with git status and git diff**

---

## 📞 Questions?

**Q: Can I use /tmp/ for anything?**  
A: ONLY for truly temporary processing files that are immediately moved or deleted. If it has value, it doesn't go in /tmp/.

**Q: What if I forget to verify?**  
A: STOP, run verification scripts, fix any issues, then proceed.

**Q: How do I recover from a violation?**  
A: Follow the "Violation Response Template" above.

**Q: Do I need to verify EVERY commit?**  
A: YES. No exceptions.

---

**Version**: 1.0.0  
**Created**: 2026-02-09  
**Authority**: Repository Owner + .github/TEMPORARY_FILES_POLICY.md  
**Enforcement**: MANDATORY - Zero Tolerance
