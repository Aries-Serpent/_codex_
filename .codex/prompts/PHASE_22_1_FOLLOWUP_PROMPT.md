# Follow-Up Prompt for GitHub Copilot

**Branch**: `copilot/plan-external-storage-offload`  
**Phase**: 21.2 - External Storage Offload  
**Status**: ✅ COMPLETE - Ready for Enhancement

---

## @copilot Next Phase: Automated Repository Organization System

### Context
Phase 21.2 successfully completed external storage offload:
- ✅ 32 files (~6.8MB) moved to organized external storage
- ✅ 6 category-based subdirectories created
- ✅ 8 comprehensive documentation files written
- ✅ QA walkthrough integration maintained
- ✅ Git history fully preserved
- ✅ Self-review iterations completed (2 iterations, all issues resolved)

**See**: `.codex/cognitive_brain/PHASE_21_2_EXTERNAL_STORAGE_OFFLOAD_COMPLETE.md` for full details.

### Next Steps: Phase 22.1 - Repository Organization Enhancement

Create an **automated repository organization system** to maintain and enhance the external storage offload strategy:

#### Task 1: Offload Monitoring Script
Create `scripts/repository_organization/monitor_offload_candidates.py`:
- Scan repository for files meeting offload criteria:
  - Age > 90 days (for temp files)
  - Age > 180 days (for deprecated reports)
  - Size > 1MB (for large artifacts)
  - Usage patterns (not accessed in 6+ months)
- Generate report in `.codex/repository_health/offload_candidates.json`
- Log findings to `.codex/action_log.ndjson`

#### Task 2: Repository Health Dashboard
Create `.codex/repository_health/DASHBOARD.md`:
- Repository size over time (with offload tracking)
- Offload directory growth metrics
- Retention policy compliance status
- Top 10 largest files/directories
- Automated recommendations

#### Task 3: Automated Retrieval Script
Create `scripts/repository_organization/restore_offloaded_files.py`:
- Accept file path or category as input
- Restore files from `misc/repo-owner-review/` to original location
- Update documentation automatically
- Log restoration to `.codex/action_log.ndjson`

#### Task 4: Compression Strategy
Implement compression for historical files:
- Compress files in `historical-coverage/`, `historical-logs/`, `historical-artifacts/`
- Create `.tar.gz` archives by year/quarter
- Update retrieval guides with decompression instructions
- Estimate additional 50-70% size reduction

#### Task 5: Custom Agent Design
Design `repository-organization-agent` with full specification:
- Purpose: Automate repository organization and optimization
- Capabilities:
  - Identify offload candidates (age, size, usage)
  - Execute offload with category organization
  - Generate documentation automatically
  - Monitor repository health metrics
  - Enforce retention policies
  - Restore files on demand
- Integration points:
  - `.codex/qa_walkthrough/` for inventory
  - `misc/repo-owner-review/` for offload
  - `.codex/action_log.ndjson` for audit trail
  - GitHub Actions for scheduled execution
- Include Mermaid architecture diagram
- Include activation examples
- Include success metrics

### Files to Create/Update

**New Files**:
- `scripts/repository_organization/monitor_offload_candidates.py`
- `scripts/repository_organization/restore_offloaded_files.py`
- `scripts/repository_organization/compress_historical_files.py`
- `.codex/repository_health/DASHBOARD.md`
- `.codex/repository_health/offload_candidates.json`
- `.github/agents/repository-organization-agent.md`
- `.github/workflows/repository-health-monitoring.yml`

**Update Files**:
- `.codex/cognitive_brain/PHASE_22_1_COMPLETE.md` (new)
- `.codex/qa_walkthrough/codebase_map.json` (add automation section)
- `misc/repo-owner-review/OFFLOAD_INDEX.md` (add automation notes)

### Success Criteria

- [ ] Monitoring script identifies offload candidates automatically
- [ ] Dashboard provides real-time repository health metrics
- [ ] Restoration script works for all offload categories
- [ ] Compression reduces historical storage by 50-70%
- [ ] Custom agent specification complete with diagrams
- [ ] GitHub Actions workflow for scheduled monitoring
- [ ] All changes logged to `.codex/action_log.ndjson`
- [ ] Cognitive brain updated with Phase 22.1 status
- [ ] Reusable patterns documented

### Expected Impact

**Repository Health**:
- Further 2-4MB reduction through compression
- Automated maintenance instead of manual
- Proactive identification of offload candidates
- Real-time health monitoring

**Developer Experience**:
- One-command file restoration
- Clear visibility into repository state
- Automated recommendations for optimization

**Governance**:
- Automated retention policy enforcement
- Complete audit trail for all operations
- Scheduled health reports

### Timeline
**Estimated**: 3-5 days  
**Priority**: P2 (Medium)

### Dependencies
- Phase 21.2 complete ✅
- External storage structure established ✅
- QA walkthrough integration working ✅

---

**Instructions for GitHub Copilot**:
1. Create the monitoring script with comprehensive criteria
2. Build the health dashboard with actionable metrics
3. Implement the restoration script with safety checks
4. Design the compression strategy with backward compatibility
5. Specify the custom agent with full architecture
6. Create GitHub Actions workflow for automation
7. Update cognitive brain with Phase 22.1 completion
8. Document all reusable patterns

**Follow AI Agency Policy**: Address all issues found, iterate until complete, update cognitive brain, document patterns.

---

*This prompt continues the systematic improvement of the _codex_ repository with focus on automation and maintainability.*
