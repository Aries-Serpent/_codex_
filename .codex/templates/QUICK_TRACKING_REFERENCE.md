# 📋 Quick Issue Tracking Reference Card

**For AI Agents**: Copy-paste these prompts to maintain effective issue tracking

---

## 🚀 Quick Start (3 Commands)

### 1. Session Start
```
@copilot Read `.codex/PR_{PR_NUMBER}_FAILURE_TRACKING_LOG.md` and show me:
- Current progress (%)
- Last attempt result
- Current failing checks
- Recommended next steps
```

### 2. Document Update
```
@copilot Update `.codex/PR_{PR_NUMBER}_FAILURE_TRACKING_LOG.md`:
- Add this session's changes
- Update fix summary table
- Update progress percentage
- Document learnings
```

### 3. Status Report
```
@copilot Generate status report showing:
- Issues fixed vs remaining
- Progress by category
- Blocking issues
- Next actions
```

---

## 📝 Essential Tracking Checklist

Before ANY commit:
```markdown
- [ ] Tracking document exists or created
- [ ] All issues documented (in + out of scope)
- [ ] Fix summary table updated
- [ ] Progress percentage calculated
- [ ] Active changes listed
- [ ] Next actions clear
```

---

## 🎯 Status Indicators (Copy-Paste)

### Issues
- ✅ FIXED
- 🔄 IN_PROGRESS  
- ⏳ PENDING
- 🔍 INVESTIGATING
- ⚠️ BLOCKED
- 📌 DEFERRED

### Progress Bar
```
[████████████████████] 100% (20/20)
[███████████████     ]  75% (15/20)
[██████████          ]  50% (10/20)
[█████               ]  25% (5/20)
[                    ]   0% (0/20)
```

---

## 🔄 Quick Update Template

```markdown
### Attempt N: {Description}
- **Date**: 2026-02-16T{TIME}Z
- **Change**: {what_changed}
- **Result**: {✅/❌/⏳}
- **Learning**: {insight}

## Active Changes
1. **{file}**: {change}
2. **{file}**: {change}

Commit: {hash} - "{message}"
```

---

## 📊 Quick Fix Summary

```markdown
| Category | Found | Fixed | Remaining |
|----------|-------|-------|-----------|
| Cat 1    | 5     | 5 ✅   | 0         |
| Cat 2    | 3     | 1 🔄   | 2         |
| **TOTAL**| **8** | **6** | **2**     |

Progress: 75% (6/8)
```

---

## 🚨 When to Escalate

- **5+ failed attempts** on same issue
- **Unknown root cause** after investigation
- **Blocking issues** prevent progress
- **Human approval** needed

---

## 📁 File Paths

- Tracking: `.codex/PR_{N}_FAILURE_TRACKING_LOG.md`
- Template: `.codex/templates/ISSUE_TRACKING_PROMPT_TEMPLATE.md`
- Root Cause: `.codex/PR_{N}_ROOT_CAUSE_ANALYSIS.md`

---

## 🎨 Visual Dashboard Template

```
┌─────────────────────────────────────┐
│ PR #{N} Status Dashboard            │
├─────────────────────────────────────┤
│ Progress: [████████    ] 75%        │
│                                     │
│ Issues by Category:                 │
│ 🟢 Workflows:  13/13 (100%) ✅      │
│ 🟡 Tests:       1/4  (25%)  🔄      │
│ 🔴 Blocked:     0/1  (0%)   ⚠️      │
│                                     │
│ Latest: Attempt 5 - Partial success │
│ Next: Fix remaining test patterns   │
└─────────────────────────────────────┘
```

---

## 💡 Pro Tips

1. **Update BEFORE committing** - Don't lose context
2. **Document failures too** - Learn from mistakes
3. **Link everything** - Commits, files, related docs
4. **Be specific** - "Fixed plugin loading" not "Fixed stuff"
5. **Calculate accurately** - Count ALL issues found

---

## 🔗 Full Documentation

See `.codex/templates/ISSUE_TRACKING_PROMPT_TEMPLATE.md` for:
- Complete template structure
- Detailed examples
- Best practices
- Troubleshooting guide

---

**Version**: 1.0.0 | **Last Updated**: 2026-02-16
