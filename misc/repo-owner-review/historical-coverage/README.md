# Historical Coverage Reports

**Purpose**: Archived coverage reports from previous testing phases  
**Retention**: Permanent (for trend analysis)  
**Active Files**: See `coverage_reports/` in main repository

## Contents

This directory contains historical coverage analysis reports that have been offloaded from the main repository to reduce size while preserving historical data for trend analysis and QA walkthrough purposes.

### Files

- `phase1_iteration1.json` - Phase 1 initial coverage baseline
- `phase1_iteration2.json` - Phase 1 iteration 2 coverage
- `phase2_iter.json` - Phase 2 iteration coverage
- `coverage_iteration2.json` - Historical iteration 2 snapshot
- `coverage_agents.json` - Agent-specific coverage snapshot
- `coverage_agents_full.json` - Full agent coverage analysis
- `coverage_working_tests.json` - Working tests coverage snapshot
- `coverage_analysis_static.md` - Static analysis of coverage

## Usage

### For Trend Analysis
Access these files to analyze coverage progression across phases:
```bash
# View phase progression
jq '.summary.percent_covered' phase*.json

# Compare iterations
diff <(jq . phase1_iteration1.json) <(jq . phase1_iteration2.json)
```

### For QA Walkthrough
These files complement `.codex/qa_walkthrough/coverage_analysis.json` for comprehensive coverage tracking.

## Current Coverage

For current/active coverage data, see:
- `coverage_reports/current_coverage.json` (main repo)
- `coverage_reports/coverage.json` (main repo)
- `.codex/qa_walkthrough/coverage_analysis.json` (QA analysis)

## Retrieval Instructions

### For Compressed Files (.gz)

All historical coverage files are now compressed with gzip to save space (**71% reduction achieved** - 5.6MB → 1.6MB).

**To decompress and view**:
```bash
# Decompress a specific file to stdout
gunzip -c misc/repo-owner-review/historical-coverage/phase1_iteration1.json.gz > phase1_iteration1.json

# Or decompress in-place (removes .gz file)
gunzip misc/repo-owner-review/historical-coverage/phase1_iteration1.json.gz
```

**To restore to main repository**:
```bash
# Option 1: Decompress and copy manually
gunzip -c misc/repo-owner-review/historical-coverage/phase1_iteration1.json.gz > coverage_reports/phase1_iteration1.json

# Option 2: Use automated restoration script (handles decompression automatically)
python scripts/repository_organization/restore_offloaded_files.py --file historical-coverage/phase1_iteration1.json.gz
```

---
**Offloaded**: 2026-01-26  
**Compressed**: 2026-01-26 (71% reduction)  
**Maintained by**: QA Walkthrough Agent
