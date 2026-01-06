# Workflow Caching Implementation Plan

**Created:** Current Cycle-01-05  
**Status:** Planning Phase  
**Target:** Phase 2-5 implementation across multiple pre-commit cycles

## Overview

This document outlines the comprehensive plan for implementing intelligent caching mechanisms across GitHub Actions workflows to skip non-security scans when files haven't changed.

## Phase 1: Aggregate Checksum Caching (IMPLEMENTED)

### Status: ✅ COMPLETE

**Implementation:** `documentation-link-checker.yml`

### Features
- Computes SHA1 checksum across all tracked documentation files (paths + contents)
- Uses GitHub Actions cache with checksum as key
- Skips link checking when cache hit occurs
- Stores success marker (`.link-check-success`) for validation
- Includes checksum in workflow reports

### Benefits
- **Fast skip**: 10-15 seconds vs 2-5 minutes for full check
- **Deterministic**: Same files = same checksum = guaranteed skip
- **Simple**: Single cache key, minimal complexity
- **Cache-friendly**: Small marker file, no size limits

### Limitations
- All-or-nothing: One changed file triggers full recheck
- No granular reporting on what changed
- Cache eviction affects all files equally

---

## Phase 2: Per-Folder Granular Caching

### Timeline: Pre-commit cycles 1-4 (estimated)

### Objective
Enable folder-level granularity so only changed directories trigger rescans.

### Technical Design

#### 2.1 Folder Checksum Structure
```bash
# Compute per-folder checksums
docs/admin/         -> checksum_abc123
docs/agent/         -> checksum_def456
.codex/             -> checksum_ghi789
scripts/            -> checksum_jkl012
```

#### 2.2 Cache Key Strategy
- **Primary key:** `link-check-folders-v1-${{ matrix.folder }}-${{ checksum }}`
- **Restore keys:** `link-check-folders-v1-${{ matrix.folder }}-`
- **Matrix strategy:** Parallel jobs per folder

#### 2.3 Workflow Structure
```yaml
jobs:
  compute-checksums:
    runs-on: ubuntu-latest
    outputs:
      folders: ${{ steps.scan.outputs.folders }}
      checksums: ${{ steps.scan.outputs.checksums }}
    steps:
      - name: Scan folders and compute checksums
        id: scan
        run: |
          # Generate folder list with checksums
          # Output as JSON for matrix strategy

  check-links-per-folder:
    needs: compute-checksums
    runs-on: ubuntu-latest
    strategy:
      matrix:
        folder: ${{ fromJson(needs.compute-checksums.outputs.folders) }}
    steps:
      - name: Check cache for folder
        uses: actions/cache@v4
        with:
          key: link-check-folders-v1-${{ matrix.folder }}-${{ checksums[matrix.folder] }}
      
      - name: Run link check if cache miss
        if: steps.cache.outputs.cache-hit != 'true'
        run: |
          # Check only files in ${{ matrix.folder }}
```

#### 2.4 Implementation Files
- `.github/workflows/documentation-link-checker-granular.yml` (new)
- `.github/scripts/compute-folder-checksums.sh` (new helper)
- `.github/scripts/check-links-folder.sh` (new helper)

#### 2.5 Success Criteria
- [ ] Folders checked in parallel (max 4 concurrent)
- [ ] Cache hit on unchanged folders (skip check)
- [ ] Cache miss only on changed folders (targeted check)
- [ ] Report shows per-folder status
- [ ] Total runtime < 50% of current for partial changes
- [ ] Maintains 100% link validation accuracy

---

## Phase 3: Per-File Granular Caching

### Timeline: Pre-commit cycles 5-8 (estimated)

### Objective
Enable file-level granularity for maximum efficiency on single-file changes.

### Technical Design

#### 3.1 File Checksum Database
```json
{
  "version": "1.0",
  "generated": "Current Cycle-01-05T21:32:00Z",
  "files": {
    "docs/admin/GENESIS_SETUP_GUIDE.md": {
      "checksum": "a1b2c3d4e5f6",
      "last_checked": "Current Cycle-01-05T20:00:00Z",
      "last_status": "pass",
      "link_count": 42
    },
    "README.md": {
      "checksum": "f6e5d4c3b2a1",
      "last_checked": "Current Cycle-01-05T20:00:00Z",
      "last_status": "pass",
      "link_count": 15
    }
  }
}
```

#### 3.2 Changed File Detection
```bash
# Detect changed files
git diff --name-only ${{ github.event.before }}..${{ github.sha }} -- '*.md'

# For each changed file:
#   1. Compute new checksum
#   2. Compare with database
#   3. Add to check list if different or missing
```

#### 3.3 Incremental Update Strategy
- Store checksum database as artifact (30-day retention)
- Restore database at workflow start
- Check only files with changed checksums
- Update database with new checksums on success
- Upload updated database as artifact

#### 3.4 Cache Strategy
- **Database cache key:** `link-check-db-v1-${{ github.ref }}`
- **Per-file cache key:** `link-check-file-v1-${{ file_path }}-${{ checksum }}`
- **Fallback:** If no database, check all files (cold start)

#### 3.5 Implementation Files
- `.github/workflows/documentation-link-checker-incremental.yml` (new)
- `.github/scripts/manage-link-check-db.py` (new Python helper)
- `.github/scripts/check-links-incremental.sh` (new helper)
- `.link-check-db.json` (generated, stored as artifact)

#### 3.6 Success Criteria
- [ ] Single file change triggers single file check
- [ ] Database persists across runs (artifact)
- [ ] Database auto-repairs on corruption
- [ ] Cold start (no database) checks all files
- [ ] Report shows per-file status with change detection
- [ ] Total runtime < 20 seconds for single file changes
- [ ] Maintains 100% link validation accuracy

---

## Phase 4: Extended Scope - Other Workflows

### Timeline: Pre-commit cycles 9-12 (estimated)

### Target Workflows

#### 4.1 `pr-checks.yml`
- **Current behavior:** Runs all checks on every PR
- **Optimization:** Skip linting/formatting if no code changes
- **Implementation:** Per-file checksums for Python files

#### 4.2 `github_connector_check.yml` - REMOVED
- **Status:** ❌ Workflow removed due to missing dependencies
- **Original plan:** Cache last successful check (1 hour TTL)
- **Issue:** Referenced non-existent `tools/connectors/github_connector_check.py`
- **Resolution:** Workflow deleted; if needed in future, create script first

#### 4.3 Security Workflows
- **Note:** Security scans (CodeQL, secrets) should NOT be skipped
- **Reason:** Security vulnerabilities can emerge from dependency updates
- **Action:** Exclude from caching scope

#### 4.4 Test Workflows
- **Current behavior:** Run all tests on every commit
- **Optimization:** Test selection based on changed files
- **Implementation:** Dependency graph + file checksums
- **Example:** Change to `agents/quantum_game_theory.py` triggers only related tests

### Implementation Files
- `.github/workflows/pr-checks-cached.yml` (enhanced)
- `.github/scripts/smart-test-selection.py` (new)
- `.github/scripts/workflow-cache-manager.sh` (shared utility)

---

## Phase 5: Monitoring and Metrics

### Objective
Track cache efficiency and cost savings

### Metrics to Collect
- Cache hit rate (per workflow, per folder, per file)
- Runtime savings (baseline vs cached)
- Cache storage usage
- False positive rate (skipped checks that should have run)

### Implementation
- Add telemetry step to each workflow
- Store metrics in workflow artifacts
- Generate per-commit-cycle summary report
- Dashboard in `.codex/metrics/` directory

### Files
- `.github/scripts/collect-cache-metrics.py` (new)
- `.codex/metrics/CACHE_PERFORMANCE.md` (generated per commit cycle)

---

## Configuration Options

### Environment Variables

```yaml
env:
  # Enable/disable caching globally
  WORKFLOW_CACHE_ENABLED: true
  
  # Cache TTL for time-based caching (in hours)
  CACHE_TTL_HOURS: 1
  
  # Maximum parallel jobs for folder-based caching
  MAX_PARALLEL_FOLDERS: 4
  
  # Minimum file age before considering for caching (in minutes)
  MIN_FILE_AGE_MINUTES: 5
```

### Per-Workflow Configuration

```yaml
# .github/workflow-cache-config.yml
workflows:
  documentation-link-checker:
    strategy: aggregate-checksum
    enabled: true
    
  documentation-link-checker-granular:
    strategy: per-folder
    enabled: true
    max_parallel: 4
    
  documentation-link-checker-incremental:
    strategy: per-file
    enabled: true
    database_retention_days: 30
```

---

## Migration Plan

### Pre-commit 1: Phase 1 (Aggregate) ✅
- [x] Implement aggregate checksum for link checker
- [x] Test on sample PRs
- [x] Monitor for false negatives
- [x] Document in this plan

### Pre-commit 2-5: Phase 2 (Per-Folder)
- [ ] Design folder matrix strategy
- [ ] Implement helper scripts
- [ ] Create parallel workflow
- [ ] A/B test against aggregate version
- [ ] Measure performance improvement
- [ ] Deploy if >30% faster on partial changes

### Pre-commit 6-9: Phase 3 (Per-File)
- [ ] Design checksum database schema
- [ ] Implement Python helper for DB management
- [ ] Create incremental workflow
- [ ] Test with various change scenarios
- [ ] Benchmark against Phase 2
- [ ] Deploy if >50% faster on single file changes

### Pre-commit 10-12: Phase 4 (Other Workflows)
- [ ] Audit all workflows for caching candidates
- [ ] Prioritize by runtime impact
- [ ] Implement caching for top 3 workflows
- [ ] Document exclusions (security scans)

### Pre-commit 13-15: Phase 5 (Monitoring)
- [ ] Implement metrics collection
- [ ] Create dashboard template
- [ ] Generate first per-phase report
- [ ] Set up alerts for cache issues

---

## Rollback Strategy

### If Caching Causes Issues

1. **Immediate:** Set `WORKFLOW_CACHE_ENABLED=false` in workflow
2. **Temporary:** Revert to original workflow file from git history
3. **Investigation:** Analyze cache key collision, false positives
4. **Fix:** Adjust checksum algorithm or cache key strategy
5. **Re-deploy:** Test fix on non-critical branch first

### Fallback Mechanism Built Into Workflows

```yaml
- name: Check with fallback
  run: |
    if ! run_cached_check; then
      echo "⚠️ Cache check failed, falling back to full check"
      run_full_check
    fi
```

---

## Testing Plan

### Unit Tests
- Checksum computation accuracy
- Cache key generation correctness
- Database update logic

### Integration Tests
- Full workflow execution with cache hit
- Full workflow execution with cache miss
- Partial folder/file changes
- Cold start (no cache)
- Cache corruption recovery

### Performance Tests
- Baseline: Current runtime without caching
- Phase 1: Aggregate checksum (cache hit)
- Phase 2: Per-folder (partial change)
- Phase 3: Per-file (single change)
- Target: >50% reduction in median runtime

### Validation Tests
- Zero false positives (missed broken links)
- Zero false negatives (unnecessary checks)
- Consistency across parallel jobs

---

## Documentation Updates Required

- [ ] Update `.codex/AGENTS_GUIDE.md` with caching behavior
- [ ] Document cache debugging in `.codex/guardrails.md`
- [ ] Add caching metrics to `.codex/results.md` template
- [ ] Create `.github/CACHING_GUIDE.md` for contributors
- [ ] Update workflow README files

---

## Cost-Benefit Analysis

### Current State
- Documentation link check: ~3 minutes per run
- Runs on every doc change PR
- ~20 PRs per commit cycle = 60 minutes/cycle
- Annual: ~52 hours of CI time (assuming ~17 commit cycles/year)

### With Phase 1 (Aggregate)
- Cache hit: ~15 seconds
- Estimated hit rate: 30% (no changes after first check)
- Savings: ~18 minutes/cycle → ~15.6 hours/year

### With Phase 3 (Per-File)
- Single file change: ~20 seconds
- Estimated hit rate: 70% (single file changes)
- Savings: ~42 minutes/cycle → ~36.4 hours/year

### Additional Benefits
- Faster feedback for developers
- Reduced GitHub Actions quota usage
- Lower carbon footprint (less compute)
- Improved developer experience

---

## Future Enhancements

### Intelligent Cache Warming
- Pre-compute checksums on main branch
- Seed PR caches from main branch cache

### Cross-Workflow Cache Sharing
- Share checksums between related workflows
- Unified cache database

### ML-Based Prediction
- Predict which files likely to have broken links
- Prioritize those for checking even with cache hit

### Distributed Caching
- Use external cache service (Redis, etc.)
- Share cache across repository forks

---

## References

- GitHub Actions Caching: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
- SHA1 Checksums: https://en.wikipedia.org/wiki/SHA-1
- Matrix Strategy: https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs
- Artifact Actions: https://github.com/actions/upload-artifact

---

## Appendix A: Checksum Computation Algorithm

```bash
#!/bin/bash
# compute_checksum.sh - Compute aggregate checksum for files

compute_aggregate_checksum() {
  local pattern="$1"  # e.g., "*.md"
  local exclude_paths="$2"  # e.g., "./node_modules/*,./archive/*"
  
  # Build find command
  local find_cmd="find . -name '$pattern'"
  
  # Add exclusions
  IFS=',' read -ra EXCLUDES <<< "$exclude_paths"
  for excl in "${EXCLUDES[@]}"; do
    find_cmd="$find_cmd -not -path '$excl'"
  done
  
  # Execute find and compute checksums
  eval "$find_cmd" | sort | while read -r file; do
    if [ -f "$file" ]; then
      # Include file path and content hash
      echo "$file:$(sha1sum "$file" | cut -d' ' -f1)"
    fi
  done | sha1sum | cut -d' ' -f1
}

# Usage
CHECKSUM=$(compute_aggregate_checksum "*.md" "./node_modules/*,./archive/*")
echo "Aggregate checksum: $CHECKSUM"
```

---

## Appendix B: Database Schema (Phase 3)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$"
    },
    "generated": {
      "type": "string",
      "format": "date-time"
    },
    "repository": {
      "type": "string"
    },
    "branch": {
      "type": "string"
    },
    "files": {
      "type": "object",
      "patternProperties": {
        "^.+\\.md$": {
          "type": "object",
          "properties": {
            "checksum": {
              "type": "string",
              "pattern": "^[a-f0-9]{40}$"
            },
            "last_checked": {
              "type": "string",
              "format": "date-time"
            },
            "last_status": {
              "type": "string",
              "enum": ["pass", "fail", "error"]
            },
            "link_count": {
              "type": "integer",
              "minimum": 0
            },
            "broken_links": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          },
          "required": ["checksum", "last_checked", "last_status"]
        }
      }
    }
  },
  "required": ["version", "generated", "files"]
}
```

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| Current Cycle-01-05 | 1.0 | GitHub Copilot | Initial plan with Phases 1-5 |
| TBD | 1.1 | TBD | Updates after Phase 2 implementation |
| TBD | 2.0 | TBD | Complete plan after all phases deployed |

---

**End of Plan**
