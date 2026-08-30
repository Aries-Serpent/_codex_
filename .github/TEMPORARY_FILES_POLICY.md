# 🚨 CRITICAL: Temporary File Usage Policy

**Policy Status**: MANDATORY - Zero Tolerance  
**Last Updated**: 2025-12-29  
**Enforcement**: All agents, scripts, and contributors

---

## 🔴 ABSOLUTE PROHIBITION

**NEVER store important files, content, or work products in temporary directories.**

### Prohibited Locations
- `/tmp/` - NEVER use for important files
- `/var/tmp/` - NEVER use for important files  
- System temp directories - NEVER use for important files
- Any location that may be cleared on reboot/cleanup

### What Qualifies as "Important Files"
- **ANY** content that represents work product
- Documentation, reports, or analysis results
- Follow-up prompts or task lists
- Code snippets or templates
- Configuration or metadata
- Generated artifacts or outputs
- Backup copies or archives
- **Anything that took effort to create**

---

## ✅ REQUIRED PRACTICES

### 1. Use Repository Structure
All work products MUST be stored in the repository proper locations:

```
✅ CORRECT Locations:
- .github/copilot-prompts/active/     → Follow-up prompts
- docs/                               → Documentation
- .codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/ → Canonical owner-review archive location (legacy root alias kept only for compatibility)
- artifacts/                          → Generated artifacts
- reports/                            → Analysis reports
- patches/                            → Patches and fixes
- .codex/                            → Session data

❌ WRONG Locations:
- /tmp/anything.md                    → PROHIBITED
- /var/tmp/file.json                  → PROHIBITED
- ~/temp/output.txt                   → PROHIBITED
```

### 2. Immediate Correction Protocol
If you realize you've placed important content in `/tmp/`:

1. **STOP immediately**
2. **Retrieve the content** from `/tmp/`
3. **Move to proper repository location** based on content type
4. **Commit the file** to ensure it's tracked
5. **Delete the `/tmp/` file** after confirming move
6. **Document the correction** in commit message

### 3. Acceptable /tmp/ Usage
The ONLY acceptable use of `/tmp/` is for:

- **Truly temporary** intermediate processing files
- Files that will be **immediately** moved to proper location
- **Test files** during validation (deleted after test)
- **Scratch space** for calculations (results moved elsewhere)

**Rule**: If it has value, it doesn't belong in `/tmp/`

---

## 🔍 Verification Checklist

Before concluding ANY work session:

- [ ] **Search for /tmp/ references**: `grep -r "/tmp/" .`
- [ ] **Verify no important files in /tmp/**: `ls -la /tmp/ | grep -E "\.(md|txt|json|yaml|py)$"`
- [ ] **Confirm all work products in repository**: Check git status
- [ ] **No temp file references in docs**: Review documentation
- [ ] **Clean up any /tmp/ files created**: Remove scratch files

---

## 📋 Examples

### ❌ WRONG: Storing Work Product in /tmp/
```bash
# BAD - Do NOT do this
echo "# Follow-up tasks" > /tmp/followup_prompt.md
echo "Important analysis results" > /tmp/report.txt
cp important_config.yaml /tmp/backup.yaml

# Content saved at: /tmp/followup_prompt.md  ← VIOLATION!
```

### ✅ CORRECT: Using Repository Structure
```bash
# GOOD - Do this instead
echo "# Follow-up tasks" > .github/copilot-prompts/active/PR-XXXX-followup.md
echo "Important analysis results" > reports/analysis_$(date +%Y%m%d).md
cp important_config.yaml .codex/backups/config_backup_$(date +%Y%m%d).yaml

# Content saved at: .github/copilot-prompts/active/PR-XXXX-followup.md ← CORRECT!
```

### ✅ ACCEPTABLE: Temporary Intermediate Processing
```bash
# OK - Truly temporary, immediately processed
wget https://example.com/data.json -O /tmp/data_download.json
jq '.results' /tmp/data_download.json > reports/processed_results.json
rm /tmp/data_download.json  # Cleaned up immediately

# OK - Test scratch file
echo "test data" > /tmp/test_input.txt
python validate.py /tmp/test_input.txt
rm /tmp/test_input.txt  # Cleaned up after test
```

---

## 🚨 Violation Consequences

**This is a CRITICAL policy violation because:**

1. **Data Loss Risk**: `/tmp/` may be cleared at any time
2. **Work Loss**: Effort invested in creating content is wasted
3. **Continuity Breaks**: Other agents/users cannot access the work
4. **Policy Violation**: Contradicts repository mandates
5. **Trust Impact**: Indicates poor understanding of importance

**If violation occurs:**
- Immediate correction required
- Document the incident
- Update relevant documentation
- Add safeguards to prevent recurrence

---

## 🔧 Implementation Guidance

### For Bash Scripts
```bash
# DON'T use /tmp/ for important files
# WRONG
output_file="/tmp/results.txt"

# DO use repository paths
# CORRECT  
output_file="reports/results_$(date +%Y%m%d).txt"
```

### For Python Scripts
```python
# DON'T use /tmp/ for important files
# WRONG
import tempfile
with open('/tmp/output.json', 'w') as f:
    json.dump(results, f)

# DO use repository paths
# CORRECT
output_path = Path('artifacts/generated') / f'output_{timestamp}.json'
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(results, f)
```

### For Copilot Agents
When creating any content that represents work:

```markdown
❌ WRONG:
**Content saved at:** `/tmp/followup_prompt.md`

✅ CORRECT:
**Content saved at:** `.github/copilot-prompts/active/PR-2639-followup.md`
```

---

## 📚 Related Policies

- **File Removal Policy**: `.codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/README.md` (legacy root alias is compatibility-only)
- **Archive Management**: `docs/guides/codex_archive_runbook.md`  
- **Repository Structure**: `.github/AGENTS_FILE_STRUCTURE.md`
- **Contribution Guidelines**: `CONTRIBUTING.md`

---

## ✅ Compliance Verification

**Pre-Commit Checklist:**
```bash
# 1. Check for /tmp/ references in new code
git diff --cached | grep -i "/tmp/"

# 2. Verify no important files left in /tmp/
ls -la /tmp/ | grep -E "\.(md|txt|json|yaml|py)$"

# 3. Confirm all work products are in repository
git status

# 4. Clean up any test files
rm -f /tmp/test_* /tmp/scratch_*
```

---

## 🎯 Key Takeaway

**If it matters, it doesn't go in /tmp/**

When in doubt, use the repository structure. Storage is cheap, lost work is expensive.

---

**Policy Version**: 1.0.0  
**Effective Date**: 2025-12-29  
**Review Frequency**: Quarterly  
**Owner**: Repository Automation Team
