# Phase 22.2 Follow-Up Prompt: Advanced Repository Organization

**Branch**: `copilot/plan-external-storage-offload` (or new branch after merge)  
**Previous Phase**: 22.1 - Automated Repository Organization ✅ COMPLETE  
**Status**: Ready for Advanced Automation

---

## @copilot Phase 22.2: Advanced Automation & Production Optimization

### Context

Phase 22.1 successfully completed with all 5 tasks:
- ✅ Offload monitoring script (tested, functional)
- ✅ Repository health dashboard (comprehensive metrics)
- ✅ Automated retrieval script (6 categories supported)
- ✅ Compression strategy (50-70% reduction ready)
- ✅ Custom agent specification (full architecture)
- ✅ GitHub Actions workflow (per-phase scheduled)

**Current State**:
- Repository: 133MB (6.8MB offloaded)
- Candidates: 2 files (13.4MB) identified
- Scripts: 3 automation tools operational
- Documentation: 16 files comprehensive
- Workflow: Scheduled per-phase monitoring

**See**: `.codex/cognitive_brain/PHASE_22_1_COMPLETE.md` for full Phase 22.1 details.

---

## Phase 22.2: Advanced Automation Tasks

### Task 1: Execute Compression for Historical Files

**Objective**: Reduce offload directory size by 50-70% through compression

**Actions**:
1. Run compression script on historical files:
   ```bash
   python scripts/repository_organization/compress_historical_files.py --all --min-age-days 0
   ```

2. Measure actual compression ratios:
   - Before: 6.1MB offload directory
   - Expected: 2-3MB after compression
   - Document actual savings

3. Update retrieval guides:
   - Add decompression instructions to category READMEs
   - Update `OFFLOAD_INDEX.md` with compression status
   - Document restoration process for compressed files

4. Verify restoration works with compressed files:
   - Test decompression on-the-fly
   - Update restore script if needed

**Success Criteria**:
- [ ] Compression executed on all eligible files
- [ ] 50-70% size reduction achieved
- [ ] Retrieval guides updated with decompression steps
- [ ] Restoration tested and verified

---

### Task 2: Address Current Offload Candidates

**Objective**: Review and offload the 2 identified candidates (13.4MB)

**Candidates**:
1. **`.codex/validation/20250910T135035Z/pre-commit.log`** (1.04MB)
   - Category: logs
   - Recommendation: Review manually
   - Action: Decide if validation logs should be offloaded or added to .gitignore

2. **`tools/github-secrets-cli/github-secrets-cli`** (12.35MB)
   - Category: unknown (large binary)
   - Recommendation: Compress or offload
   - Action: Determine if binary is needed in repo or can use package manager

**Actions**:
1. **For validation log**:
   - Review if historical validation logs are needed
   - If not needed: Add pattern `.codex/validation/*/pre-commit.log` to .gitignore
   - If needed: Keep but add to offload monitoring for future

2. **For github-secrets-cli binary**:
   - Check if binary is actively used or can be installed via package manager
   - If not needed in repo: Remove and document installation method
   - If needed: Keep but document reasoning in repository health notes
   - Potential: 9% repository size reduction if removed

3. Update monitoring script to exclude these patterns if decisions made

**Success Criteria**:
- [ ] Both candidates reviewed and decision documented
- [ ] Actions taken (offload, .gitignore, or keep with justification)
- [ ] Monitoring script updated to reflect decisions
- [ ] Repository size impact measured

---

### Task 3: Implement Configuration File for Monitoring

**Objective**: Make offload criteria configurable without code changes

**Actions**:
1. Create `.codex/repository_health/config.json`:
   ```json
   {
     "criteria": {
       "temp_files_age_days": 90,
       "deprecated_reports_age_days": 180,
       "large_file_size_mb": 1.0,
       "unused_file_age_days": 180
     },
     "exclude_patterns": [
       "*.md",
       "README.*",
       ".git/*",
       ".venv/*"
     ],
     "categories": {
       "temp": ["temp/", "tmp/", "output/"],
       "logs": ["*.log", "logs/"],
       "coverage": ["coverage_", "*.coverage"],
       "artifacts": ["artifacts/gates/"],
       "reports": ["_codex_reports/", "reports/"]
     }
   }
   ```

2. Update `monitor_offload_candidates.py` to read from config file

3. Add `--config` parameter to allow custom config path

4. Document configuration in dashboard and agent spec

**Success Criteria**:
- [ ] Configuration file created
- [ ] Monitor script reads from config
- [ ] Criteria customizable without code changes
- [ ] Documentation updated

---

### Task 4: Add Automated Tests for Scripts

**Objective**: Ensure reliability with test coverage

**Actions**:
1. Create `tests/repository_organization/test_monitor.py`:
   - Test candidate identification
   - Test category classification
   - Test JSON report generation
   - Test action log integration

2. Create `tests/repository_organization/test_restore.py`:
   - Test category listing
   - Test file restoration (with mocking)
   - Test dry-run mode
   - Test error handling

3. Create `tests/repository_organization/test_compress.py`:
   - Test compression logic
   - Test compression ratio calculation
   - Test original file removal
   - Test error handling

4. Add tests to CI/CD pipeline:
   - Update test workflow to include repository_organization tests
   - Ensure tests run before monitoring workflow

**Success Criteria**:
- [ ] Test suite created with >80% coverage
- [ ] All tests passing
- [ ] Tests integrated into CI/CD
- [ ] Test documentation added

---

### Task 5: Enhanced Dashboard with Trend Analysis

**Objective**: Add historical tracking and trend visualization

**Actions**:
1. Create `.codex/repository_health/history.jsonl`:
   - NDJSON format for historical snapshots
   - Track: date, size, offload_size, candidates_count
   - Append on each monitoring run

2. Update dashboard generation script:
   - Read historical data from `history.jsonl`
   - Generate trend charts (text-based or data for visualization)
   - Show 30 iteration, 90 iteration, and all-time trends

3. Add trend analysis to dashboard:
   - Size reduction over time
   - Offload frequency
   - Average candidate size
   - Compliance trends

4. Create visualization script (optional):
   - Generate SVG charts from historical data
   - Embed in dashboard or link to separate page

**Success Criteria**:
- [ ] Historical tracking implemented
- [ ] Trend data collected on each run
- [ ] Dashboard shows trends (at least text-based)
- [ ] 30 iteration trend visible

---

### Task 6: Production Hardening

**Objective**: Add safety mechanisms and error handling

**Actions**:
1. **Multi-approval workflow for large offloads**:
   - Add confirmation step in workflow for offloads >10MB
   - Require manual approval via GitHub environment protection
   - Document approval process

2. **Automated rollback on errors**:
   - Add try-catch-rollback logic to scripts
   - Preserve pre-operation state
   - Auto-restore on failure

3. **Integrity verification**:
   - Add checksum verification for file moves
   - Verify file existence before deletion
   - Log all operations with checksums

4. **Enhanced error messages**:
   - Add detailed error context
   - Suggest remediation steps
   - Link to documentation

**Success Criteria**:
- [ ] Approval workflow for large operations
- [ ] Rollback mechanism tested
- [ ] Integrity checks in place
- [ ] Error messages comprehensive

---

## Files to Create/Update

**New Files**:
- `tests/repository_organization/test_monitor.py`
- `tests/repository_organization/test_restore.py`
- `tests/repository_organization/test_compress.py`
- `.codex/repository_health/config.json`
- `.codex/repository_health/history.jsonl`
- `.codex/repository_health/generate_dashboard.py` (optional)

**Update Files**:
- `scripts/repository_organization/monitor_offload_candidates.py` (read config)
- `scripts/repository_organization/restore_offloaded_files.py` (handle compressed)
- `.codex/repository_health/DASHBOARD.md` (add trends)
- `.codex/cognitive_brain/PHASE_22_2_COMPLETE.md` (new)
- `.github/workflows/repository-health-monitoring.yml` (add approval gates)
- `.gitignore` (potentially add validation logs pattern)
- `misc/repo-owner-review/*/README.md` (add decompression instructions)

---

## Success Criteria

### Phase 22.2 Complete When:
- [ ] Compression executed and verified (3-5MB savings)
- [ ] Current candidates reviewed and actions taken
- [ ] Configuration file implemented
- [ ] Automated tests added (>80% coverage)
- [ ] Trend analysis in dashboard
- [ ] Production hardening complete
- [ ] All actions logged to `.codex/action_log.ndjson`
- [ ] Cognitive brain updated with Phase 22.2 status
- [ ] Reusable patterns documented

---

## Expected Impact

### Repository Optimization
- **Additional 3-5MB** reduction through compression
- **Potential 12.35MB** reduction if github-secrets-cli removed
- **Total: 20-24MB** savings (15-18% of original size)

### Automation Maturity
- Configuration-driven (no code changes needed)
- Comprehensive test coverage (reliability)
- Historical trend analysis (insights)
- Production-grade safety (multi-approval, rollback)

### Developer Experience
- Faster restoration with decompression
- Clear configuration customization
- Trend visibility for planning
- Robust error handling

---

## Timeline
**Estimated**: 4-7 iterations  
**Priority**: P1 (High - completes production-ready automation)

---

## Dependencies
- Phase 22.1 complete ✅
- Scripts operational ✅
- Workflow deployed ✅
- Documentation comprehensive ✅

---

**Instructions for GitHub Copilot**:
1. Execute compression on historical files
2. Review and address 2 current candidates (13.4MB)
3. Implement configuration file for customizable criteria
4. Add comprehensive test suite (>80% coverage)
5. Enhance dashboard with trend analysis
6. Add production hardening (approval, rollback, integrity)
7. Update cognitive brain with Phase 22.2 completion
8. Document all reusable patterns

**Follow AI Agency Policy**: Address all issues found, iterate until complete, update cognitive brain, document patterns.

---

*This prompt continues the systematic improvement with focus on production readiness and advanced automation.*
