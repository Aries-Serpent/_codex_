# Workflow Archive Access & Search Guide

**Document Type**: User Guide  
**Purpose**: How to find, search, and access archived workflows  
**Audience**: Developers, DevOps, Admins  
**Last Updated**: 2026-07-13

---

## 📍 Archive Location

**Primary**: `.github/workflow-archive/`  
**Search Index**: `.codex/WORKFLOW_ARCHIVE_INDEX.json`  
**Manifest**: `.codex/PHASE_4_ARCHIVE_MANIFEST.md`

---

## 🔍 Search Methods

### Method 1: Search Index (Recommended)

Use the searchable JSON index for fast lookups:

```bash
# Find workflows by function
jq '.workflows[] | select(.function=="testing")' .codex/WORKFLOW_ARCHIVE_INDEX.json

# Find workflows by keyword
jq '.workflows[] | select(.keywords[] | contains("cache"))' .codex/WORKFLOW_ARCHIVE_INDEX.json

# Find workflows consolidated into specific master
jq '.workflows[] | select(.master_workflow=="optimized-ci.yml")' .codex/WORKFLOW_ARCHIVE_INDEX.json

# Get all disabled workflows
jq '.workflows[] | select(.archive_type=="disabled") | .name' .codex/WORKFLOW_ARCHIVE_INDEX.json
```

### Method 2: File System Search

Find workflows directly in the archive:

```bash
# Find by name pattern
find .github/workflow-archive -name "*auth*" -o -name "*token*"

# Find by batch
ls .github/workflow-archive/backups/2026-02-06-235731-artifact-prefix/

# Find by function (grep comments)
grep -r "name: " .github/workflow-archive/disabled/*.yml | grep -i "cache"

# List all disabled workflows
ls .github/workflow-archive/disabled/ | sort
```

### Method 3: Consolidation Mapping

Use this to find what replaced a workflow:

```bash
# View consolidation mapping
cat .codex/PHASE_4_ARCHIVE_MANIFEST.md | grep -A 100 "Consolidation Mapping"

# Find what master contains a job
grep "job_cleanup" .github/workflows/cache-management.yml
```

---

## 📚 Common Search Queries

### Find All Testing Workflows

**Question**: "What test-related workflows were archived?"

**Answer**:
```bash
# Using index
jq '.workflows[] | select(.function=="testing")' .codex/WORKFLOW_ARCHIVE_INDEX.json

# Output:
# - test-suite.yml (→ optimized-ci.yml)
# - mcp-ci.yml (→ optimized-ci.yml)
# - integration-gated.yml (→ optimized-ci.yml)
# - test-comprehensive.yml (→ optimized-ci.yml)
# - test-rag.yml (→ optimized-ci.yml)
```

**How to restore**: See Scenario 1 in PHASE_4_ARCHIVE_MANIFEST.md

---

### Find Cache-Related Workflows

**Question**: "I need to restore cache functionality"

**Answer**:
```bash
# Using grep
find .github/workflow-archive -name "*cache*"

# Output:
# .github/workflow-archive/backups/2025-12-28/cache-cleanup.yml
# .github/workflow-archive/backups/2025-12-28/cache-warmer.yml
# .github/workflow-archive/disabled/cache-management.yml
# .github/workflow-archive/disabled/cache-cleanup.yml
# ... and more
```

**Master workflow**: `cache-management.yml` (active)

**How to restore**: Copy from `disabled/` or backups/

---

### Find Authentication Workflows

**Question**: "Where are the auth-related workflows?"

**Answer**:
```bash
# Find auth workflows
find .github/workflow-archive -name "*auth*" -o -name "*oauth*" -o -name "*token*" -o -name "*secret*"

# Results:
# .github/workflow-archive/disabled/auth-compliance-report.yml
# .github/workflow-archive/disabled/auth-mfa-enrollment.yml
# .github/workflow-archive/disabled/auth-oauth-app-sync.yml
# .github/workflow-archive/disabled/auth-secret-rotation.yml
# .github/workflow-archive/disabled/auth-security-audit.yml
# .github/workflow-archive/disabled/auth-token-rotation.yml
# .github/workflow-archive/disabled/token-rotation.yml
# ... and more
```

**Master workflow**: `agent-auth-delegation.yml` (active)

---

### Find Documentation Workflows

**Question**: "What documentation workflows are available?"

**Answer**:
```bash
# Using index
jq '.workflows[] | select(.function=="documentation")' .codex/WORKFLOW_ARCHIVE_INDEX.json

# Results:
# - docs.yml
# - validate-docs.yml
# - validate-docs-enhanced.yml
# And more

# Master workflow: pages-mkdocs.yml (active)
```

---

### Find Monitoring/Status Workflows

**Question**: "I need the daily status pipeline components"

**Answer**:
```bash
# Using index
jq '.workflows[] | select(.function=="monitoring")' .codex/WORKFLOW_ARCHIVE_INDEX.json

# Results:
# - daily_status_cron.yml (→ daily-status-pipeline.yml)
# - daily_status_enrich.yml (→ daily-status-pipeline.yml)
# - automation_ingest.yml (→ daily-status-pipeline.yml)
# - produce-trend.yml (→ daily-status-pipeline.yml)
# - report_publish.yml (→ daily-status-pipeline.yml)
```

**Master workflow**: `daily-status-pipeline.yml` (active)

---

## 🗂️ Archive Directory Structure

### Backups Folder

```
.github/workflow-archive/backups/
├── 2025-12-28/                          # Batch 1: Initial consolidation
│   ├── agent-runtime.yml
│   ├── api-documentation.yml
│   ├── audit-improvement-pipeline.yml
│   └── ... (66 workflows)
│
├── 2026-02-06-235537/                   # Pre-artifact-prefix backup
│   └── agent-chain-orchestrator.yml
│
├── 2026-02-06-235636-artifact-prefix/   # Batch 2: Artifact prefix
│   ├── audit-improvement-pipeline.yml
│   ├── ci-health-suite.yml
│   └── ... (41 workflows)
│
└── 2026-02-06-235731-artifact-prefix/   # Batch 3: Security/auth
    ├── auth-mfa-enrollment.yml
    ├── cache-suite.yml
    └── ... (21 workflows)
```

### Disabled Folder

```
.github/workflow-archive/disabled/
├── auth-*.yml                  # 6 auth workflows
├── cache-*.yml                 # 6 cache workflows
├── test-*.yml                  # 5 test workflows
├── *-ci.yml                    # CI workflows
├── documentation-*.yml         # Documentation
├── workflow-*.yml              # Workflow management
└── ... (72 total)
```

### Consolidation Folder

```
.github/workflow-archive/s174-consolidation/
├── pr3178-pytest-execution.yml
├── self-healing.yml
└── self_healing_ci.yml
```

---

## 🎯 Troubleshooting: Finding a Specific Workflow

### Problem: "I can't find workflow X"

**Solution Steps**:

1. **Search the index**:
   ```bash
   jq '.workflows[] | select(.name=="X.yml")' .codex/WORKFLOW_ARCHIVE_INDEX.json
   ```

2. **Search the file system**:
   ```bash
   find .github/workflow-archive -name "X.yml" -o -name "*X*"
   ```

3. **Check disabled folder**:
   ```bash
   ls .github/workflow-archive/disabled/ | grep -i X
   ```

4. **Check backups**:
   ```bash
   find .github/workflow-archive/backups -name "*X*"
   ```

5. **Check if consolidated**:
   ```bash
   grep -l "X" .codex/PHASE_4_ARCHIVE_MANIFEST.md | head -5
   ```

6. **Last resort**: Check all active workflows
   ```bash
   ls .github/workflows/ | grep -i X
   ```

---

## 📊 Archive Statistics

View archive statistics:

```bash
# Total workflows by type
jq '.statistics.by_archive_type' .codex/WORKFLOW_ARCHIVE_INDEX.json

# Workflows by function
jq '.statistics.by_function' .codex/WORKFLOW_ARCHIVE_INDEX.json

# Consolidation targets
jq '.statistics.master_workflows' .codex/WORKFLOW_ARCHIVE_INDEX.json
```

**Current Statistics**:
- Total archived: 204
- Backups: 129
- Disabled: 72
- Consolidation: 3
- Functions represented: 9 categories

---

## 🔗 Quick Links

| Resource | Path | Purpose |
|----------|------|---------|
| Archive Manifest | `.codex/PHASE_4_ARCHIVE_MANIFEST.md` | Complete inventory & recovery |
| Search Index | `.codex/WORKFLOW_ARCHIVE_INDEX.json` | Machine-readable index |
| This Guide | `.codex/ARCHIVE_ACCESS_GUIDE.md` | How to find workflows |
| Emergency Rollback | `.github/workflow-archive/EMERGENCY_ROLLBACK.md` | Disaster recovery |
| Consolidation Report | `.github/workflow-archive/CONSOLIDATION_REPORT.md` | Consolidation details |

---

## 💡 Tips & Best Practices

### Tip 1: Use jq for Complex Searches

```bash
# Find all workflows consolidat into one master
jq '.workflows[] | select(.master_workflow=="optimized-ci.yml") | {name, function}' \
  .codex/WORKFLOW_ARCHIVE_INDEX.json

# Export workflow list by function
jq -r '.workflows[] | select(.function=="testing") | .name' \
  .codex/WORKFLOW_ARCHIVE_INDEX.json > test_workflows.txt
```

### Tip 2: Before Restoring

```bash
# Always check what it consolidated into
jq '.workflows[] | select(.name=="WORKFLOW.yml") | .master_workflow' \
  .codex/WORKFLOW_ARCHIVE_INDEX.json

# Verify master workflow exists
ls -l .github/workflows/MASTER_WORKFLOW.yml
```

### Tip 3: Keep Backups

```bash
# Before any restoration, backup current workflows
mkdir -p .github/workflows-backup-$(date +%s)
cp .github/workflows/*.yml .github/workflows-backup-$(date +%s)/
```

### Tip 4: Document Changes

```bash
# Always commit restoration with detailed message
git commit -m "restore: Re-enable WORKFLOW.yml from archive

Reason: [Why you're restoring this]
Consolidated from: [What master now contains it]
Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

---

## 📞 Getting Help

### For Workflow Lookups

1. Check this guide first
2. Use the search index
3. Ask: "Where is workflow X?"

### For Restoration

1. Read PHASE_4_ARCHIVE_MANIFEST.md
2. Choose appropriate scenario
3. Follow step-by-step instructions

### For Emergency Recovery

1. Follow Scenario 5 in PHASE_4_ARCHIVE_MANIFEST.md
2. SLA: < 5 minutes
3. Restore to known-good batch

---

## ✅ Checklist: Before You Search

- [ ] Have you read this guide?
- [ ] Do you know what function you're looking for?
- [ ] Have you checked the active workflows first?
- [ ] Have you searched the index?
- [ ] Do you need the full workflow or just the jobs?

---

**Questions?** Create GitHub issue with `[ARCHIVE-SEARCH]` tag.

*This guide is maintained alongside PHASE_4_ARCHIVE_MANIFEST.md*

