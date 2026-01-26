# Historical Log Extracts

**Purpose**: Archived log extracts from previous sessions and troubleshooting  
**Retention**: Permanent (for historical reference)  
**Active Files**: See `logs/` in main repository

## Contents

This directory contains historical log extracts that have been offloaded from the main repository. These logs represent completed sessions, resolved issues, and historical troubleshooting data.

### Files

- `extracted_log_59387658652.md` - Session log extract
- `extracted_log_60269597152.md` - Session log extract
- `extracted_log_60562804384.md` - Session log extract
- `extracted_log_60557908501.md` - Session log extract
- `extracted_log_59387344823.md` - Session log extract
- `extracted_chatgptcodex-v2.md` - ChatGPT Codex integration log
- `extracted_patch_chatgpt-codex.md` - Patch application log

## Usage

### For Historical Troubleshooting
Reference these logs when investigating patterns or recurring issues:
```bash
# Search across all historical logs
grep -r "error_pattern" .

# View specific session
cat extracted_log_[session_id].md
```

### For Session Recovery
If investigating a past issue, cross-reference session IDs with commit history.

## Current Logging

For current/active logs, see:
- `logs/error_captures.log` (main repo - active error tracking)
- `.codex/action_log.ndjson` (main repo - agent actions)

## Retrieval Instructions

### For Compressed Files (.gz)

All historical log files are now compressed with gzip to save space (**71% reduction achieved**).

**To decompress and view**:
```bash
# Decompress to stdout for viewing
gunzip -c misc/repo-owner-review/historical-logs/extracted_log_59387658652.md.gz | less

# Or decompress to file
gunzip -c misc/repo-owner-review/historical-logs/extracted_log_59387658652.md.gz > extracted_log_59387658652.md
```

**To restore to main repository**:
```bash
# Option 1: Decompress and copy manually
gunzip -c misc/repo-owner-review/historical-logs/FILE.md.gz > logs/FILE.md

# Option 2: Use automated restoration script
python scripts/repository_organization/restore_offloaded_files.py --file historical-logs/FILE.md.gz
```

---
**Offloaded**: 2026-01-26  
**Compressed**: 2026-01-26 (71% reduction)  
**Maintained by**: QA Walkthrough Agent
