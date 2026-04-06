# Repository Health Dashboard

**Last Updated**: 2026-04-06T00:56:19Z  
**Status**: ✅ Operational  
**Monitoring**: Automated via `monitor_offload_candidates.py`

---

## 📊 Quick Status

| Metric | Value | Status |
|--------|-------|--------|
| **Repository Size** | 133MB | 🟢 Healthy |
| **Offload Directory** | 6.1MB | 🟢 Active |
| **Current Candidates** | 1 file (1.14MB) | 🟡 Review Needed |
| **Phase** | 22.1 (Automated Organization) | 🔄 In Progress |
| **Last Offload** | 2026-01-26 (Phase 21.2) | ✅ Complete |

---

## 🎯 Repository Size Trends

### Historical Data

| Date | Total Size | Offloaded | Working Tree | Notes |
|------|------------|-----------|--------------|-------|
| 2026-01-26 (Before) | ~141MB | 0MB | ~141MB | Pre-offload baseline |
| 2026-01-26 (After) | 133MB | 6.1MB | 127MB | Phase 21.2 offload complete |
| **Current** | **133MB** | **6.1MB** | **127MB** | Post-offload state |

### Size Reduction Summary

```
Initial:    141MB working tree
Offloaded:  -6.8MB (32 files moved to external storage)
Current:    134MB working tree
Reduction:  ~5% size reduction achieved
```

---

## 📈 Offload Directory Metrics

### By Category

| Category | Files | Size | Retention | Status |
|----------|-------|------|-----------|--------|
| **historical-coverage** | 8 | ~2.8MB | Permanent | ✅ Organized |
| **historical-logs** | 7 | ~1.4MB | Permanent | ✅ Organized |
| **historical-artifacts** | 7 | ~500KB | Permanent | ✅ Organized |
| **archive-files** | 3 | ~800KB | Permanent | ✅ Organized |
| **temp-outputs** | 1 dir | ~280KB | 90 iterations | ✅ Organized |
| **deprecated-reports** | 6 | ~120KB | 180 iterations | ✅ Organized |
| **Total** | **32** | **~6.8MB** | - | **✅ Complete** |

### Growth Rate

- **Phase 21.2**: 32 files (6.8MB) offloaded
- **Phase 22.1**: 0 new offloads (monitoring active)
- **Projected**: ~1-2MB/quarter based on historical patterns

---

## 🔍 Current Offload Candidates

**Source**: `.codex/repository_health/offload_candidates.json`  
**Last Scan**: 2026-04-06T00:56:19Z

### Summary

- **Total Candidates**: 1 file
- **Total Size**: 1.14MB
- **Largest File**: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` (1.14MB)

### Candidate Details

| File | Category | Size | Age | Recommendation |
|------|----------|------|-----|----------------|
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | unknown | 1.14MB | 0d | review_manually |

### Recommendations

1. **📄 Large Documentation File**: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
   - **Action**: Review whether this large documentation file can be compressed, split, or offloaded to external storage
   - **Impact**: Could reduce repo size by 1.14MB
   - **Priority**: P2 (Medium - documentation file)

---

## 📋 Retention Policy Compliance

### Current Status

| Category | Retention | Compliance | Next Review |
|----------|-----------|------------|-------------|
| **historical-coverage** | Permanent | ✅ N/A | N/A |
| **historical-logs** | Permanent | ✅ N/A | N/A |
| **historical-artifacts** | Permanent | ✅ N/A | N/A |
| **archive-files** | Permanent | ✅ N/A | N/A |
| **temp-outputs** | 90 days | ✅ Current | 2026-04-26 |
| **deprecated-reports** | 180 days | ✅ Current | 2026-07-26 |

### Upcoming Reviews

- **2026-04-26**: Review `temp-outputs/` for deletion (90-day retention)
- **2026-07-26**: Review `deprecated-reports/` for deletion (180-day retention)

---

## 📊 Top 10 Largest Files/Directories

**Command**: `du -sh * | sort -hr | head -10`

```
15M   tools
15M   tests
14M   docs
10M   src
4.8M  scripts
3.7M  coverage_reports  ⚠️ Active directory (keep current files)
2.1M  cognitive_app
1.7M  logs              ⚠️ Active directory (keep error_captures.log)
1.6M  artifacts         ⚠️ Active directory (keep metrics, models)
1.4M  archive
```

### Analysis

- **tools/** (15M): Contains `github-secrets-cli` binary (12.35MB) - review needed
- **tests/** (15M): Test suite - keep as is
- **docs/** (14M): Documentation - keep as is
- **src/** (10M): Source code - keep as is
- **scripts/** (4.8M): Automation scripts - keep as is

---

## 🎯 Automated Recommendations

### Immediate Actions (P1)

1. **Review `github-secrets-cli` binary** (12.35MB)
   - Consider using package manager instead of committing binary
   - Or document why binary must be in repo
   - Potential reduction: ~9% of repo size

2. **Add validation logs to .gitignore**
   - Pattern: `.codex/validation/*/pre-commit.log`
   - Prevent future large log files from being tracked

### Near-Term Actions (P2)

3. **Implement compression for historical files** (Phase 22.1 Task 4)
   - Compress `historical-coverage/`, `historical-logs/`, `historical-artifacts/`
   - Expected reduction: 50-70% of offload directory (3-5MB additional savings)
   - Target: `.tar.gz` archives by year/quarter

4. **Schedule per-phase offload monitoring**
   - Run `monitor_offload_candidates.py` per-phase
   - Review candidates and execute offloads as needed
   - Automate via GitHub Actions (see Phase 22.1 Task 6)

### Long-Term Actions (P3)

5. **Compression automation**
   - Automatically compress files > 180 iterations old
   - Transparent decompression on access
   - Target: 2026-Q2

6. **Repository size monitoring dashboard**
   - Track size trends over time
   - Alert on unusual growth
   - Target: 2026-Q2

---

## 🔧 Maintenance Schedule

### per-phase Tasks
- [x] Run offload monitoring script (automated)
- [ ] Review offload candidates
- [ ] Execute offloads for reviewed candidates

### Monthly Tasks
- [ ] Update `OFFLOAD_INDEX.md` with new offloads
- [ ] Review offload categories for optimization
- [ ] Update this dashboard with latest metrics

### Quarterly Tasks
- [ ] Review temp-outputs/ (90-day retention)
- [ ] Review deprecated-reports/ (180-day retention)
- [ ] Analyze repository size trends
- [ ] Update retention policies as needed

### Annual Tasks
- [ ] Archive historical files to compressed format
- [ ] Review and optimize directory structure
- [ ] Update documentation with lessons learned

---

## 📚 Related Documentation

- **Offload Index**: `misc/repo-owner-review/OFFLOAD_INDEX.md`
- **Phase 21.2 Report**: `.codex/qa_walkthrough/EXTERNAL_STORAGE_OFFLOAD_REPORT.md`
- **Cognitive Brain Status**: `.codex/cognitive_brain/PHASE_21_2_EXTERNAL_STORAGE_OFFLOAD_COMPLETE.md`
- **Phase 22.1 Prompt**: `.codex/prompts/PHASE_22_1_FOLLOWUP_PROMPT.md`

---

## 🛠️ Automation Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| **monitor_offload_candidates.py** | Scan for offload candidates | `scripts/repository_organization/` |
| **restore_offloaded_files.py** | Restore files from external storage | `scripts/repository_organization/` |
| **compress_historical_files.py** | Compress historical files (planned) | `scripts/repository_organization/` |

### Usage Examples

```bash
# Monitor offload candidates
python scripts/repository_organization/monitor_offload_candidates.py

# List available categories
python scripts/repository_organization/restore_offloaded_files.py --list

# Restore a category
python scripts/repository_organization/restore_offloaded_files.py --category historical-coverage --dry-run

# Restore a specific file
python scripts/repository_organization/restore_offloaded_files.py --file historical-coverage/phase1_iteration1.json
```

---

## ✅ Health Check

**Last Check**: 2026-04-06T00:56:19Z

| Check | Status | Details |
|-------|--------|---------|
| Repository size < 150MB | ✅ Pass | 133MB |
| Offload directory organized | ✅ Pass | 6 categories |
| Retention policies defined | ✅ Pass | All categories documented |
| Active files preserved | ✅ Pass | Coverage, logs, metrics intact |
| Git history intact | ✅ Pass | All moves tracked as renames |
| Documentation complete | ✅ Pass | 8 READMEs + offload index |
| Monitoring active | ✅ Pass | Scripts operational |

**Overall Status**: 🟢 **HEALTHY**

---

**Maintained by**: Repository Organization System  
**Agent**: `repository-organization-monitor`  
**Version**: 1.0.0  
**Last Updated**: 2026-04-06T00:56:19Z
