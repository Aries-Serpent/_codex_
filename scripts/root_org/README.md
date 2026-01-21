# Root Organization Scripts

Automated tools for safe, incremental root folder reorganization with zero-break guarantee.

## Overview

This directory contains 4 core scripts that work together to safely reorganize the repository root:

1. **validate_references.py** - Scan for all references to a file
2. **update_links_atomic.py** - Atomically update all references
3. **organize_root_incremental.py** - Execute controlled file moves
4. **rollback_move.py** - Rollback on failure

## Physics Model (Energy=5)

These scripts implement the Physics Model directives:

- **Path🛤️**: Minimize churn with incremental batched moves
- **Fields🔄**: Track all metadata (timestamps, refs, hashes) in NDJSON logs
- **Patterns👁️**: Enforce repository conventions (.github/, .codex/, docs/)
- **Redundancy🔀**: Provide rollback capability for all operations
- **Balance⚖️**: Prioritize zero-break guarantees over speed

## Scripts

### 1. validate_references.py

Scans the codebase for all references to a file before moving it.

**Usage:**
```bash
# Basic validation
python validate_references.py README.md

# Dry run (no logging)
python validate_references.py AGENTS.md --dry-run

# JSON output
python validate_references.py QUICKSTART.md --json > refs.json
```

**Risk Levels:**
- **LOW** (0 refs): Safe to move
- **MEDIUM** (1-5 refs): Automated with validation
- **HIGH** (>5 refs): Requires manual review

**Exit Codes:**
- `0`: LOW risk
- `1`: MEDIUM risk
- `2`: HIGH risk

### 2. update_links_atomic.py

Atomically updates all references when a file is moved. Transaction-like behavior with automatic rollback on failure.

**Usage:**
```bash
# Dry run (preview changes)
python update_links_atomic.py --old README.md --new docs/README.md --dry-run

# Execute update
python update_links_atomic.py --old AGENTS.md --new .github/agents/AGENTS.md
```

**Features:**
- Transaction-like updates (all or nothing)
- Automatic backup before changes
- Rollback on any error
- Validates updates after execution

**Patterns Updated:**
- Markdown links: `[text](path)`
- HTML links: `href="path"`
- YAML paths: `path: path`
- Direct text references

### 3. organize_root_incremental.py

Main orchestrator for moving files. Integrates validation and reference updating.

**Usage:**
```bash
# Move files according to plan (10 at a time, dry run)
python organize_root_incremental.py \
    --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json \
    --batch 10 \
    --dry-run

# Move only LOW risk files
python organize_root_incremental.py \
    --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json \
    --risk LOW

# Move a single file
python organize_root_incremental.py \
    --file QUICKSTART.md \
    --target docs/QUICKSTART.md \
    --dry-run
```

**Workflow:**
1. Validate move (scan references, assess risk)
2. Execute `git mv` (atomic file system operation)
3. Update references (transaction-like)
4. Verify changes

**Safety Features:**
- Manual approval required for HIGH risk moves
- Validates before and after
- Updates references automatically
- Logs all operations

### 4. rollback_move.py

Rollback mechanism for recovering from failures.

**Usage:**
```bash
# Rollback single file to previous commit
python rollback_move.py --file docs/README.md

# Rollback to specific commit
python rollback_move.py --file docs/README.md --commit abc123

# Rollback last operation
python rollback_move.py --last-operation

# Rollback batch from file
python rollback_move.py --batch --commits rollback_list.txt
```

**Recovery Options:**
- Git history restore (`git checkout`)
- Last commit reset (`git reset --soft HEAD~1`)
- Batch rollback from file list
- Action log inspection

## Typical Workflow

### Phase 2: Low-Risk Moves (136 files with 0 references)

```bash
# Step 1: Validate plan
python validate_references.py QUICKSTART.md --dry-run

# Step 2: Execute moves in batch (dry run first)
python organize_root_incremental.py \
    --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json \
    --risk LOW \
    --batch 10 \
    --dry-run

# Step 3: Execute for real
python organize_root_incremental.py \
    --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json \
    --risk LOW \
    --batch 10

# Step 4: Verify (run validation suite, check links)
# ... validation steps ...

# Step 5: If issues, rollback
python rollback_move.py --last-operation
```

### Phase 3: Medium-Risk Moves (15 files with 1-5 references)

```bash
# Step 1: Validate each file
python validate_references.py CHANGES.md

# Step 2: Move with automatic reference updating
python organize_root_incremental.py \
    --file CHANGES.md \
    --target docs/archive/misc/CHANGES.md

# Step 3: Verify references updated
python validate_references.py docs/archive/misc/CHANGES.md
```

## Logging

All operations are logged to `.codex/action_log.ndjson`:

```json
{"timestamp": "2026-01-21T...", "action": "validate_references", "target_file": "README.md", "risk_level": "LOW", "reference_count": 0}
{"timestamp": "2026-01-21T...", "action": "update_links_atomic", "old_path": "README.md", "new_path": "docs/README.md", "files_updated": 0}
{"timestamp": "2026-01-21T...", "action": "organize_root_incremental", "operation": "batch_move", "details": {...}}
{"timestamp": "2026-01-21T...", "action": "rollback_move", "file": "docs/README.md", "success": true}
```

## Testing

All scripts support `--dry-run` mode for safe testing:

```bash
# Test validation
python validate_references.py AGENTS.md --dry-run

# Test reference update
python update_links_atomic.py --old test.md --new docs/test.md --dry-run

# Test file move
python organize_root_incremental.py --file test.md --target docs/test.md --dry-run

# Test rollback
python rollback_move.py --file docs/test.md --dry-run
```

## Integration with CI/CD

These scripts integrate with the `root-org-validation.yml` workflow:

```yaml
- name: Validate references
  run: python scripts/root_org/validate_references.py ${{ matrix.file }}

- name: Execute move
  run: python scripts/root_org/organize_root_incremental.py --file ${{ matrix.file }} --target ${{ matrix.target }}

- name: Rollback on failure
  if: failure()
  run: python scripts/root_org/rollback_move.py --last-operation
```

## Error Handling

All scripts follow consistent error handling:

1. **Validate inputs** - Check file existence, paths, permissions
2. **Pre-operation backup** - Create restore point
3. **Execute atomically** - All or nothing operations
4. **Validate results** - Check expected state
5. **Log outcomes** - Record to NDJSON
6. **Rollback on error** - Automatic recovery

**Exit Codes:**
- `0`: Success
- `1`: Error (with rollback if applicable)
- `2`: High risk (validation only)

## Safety Guarantees

✅ **Zero-break guarantee:**
- All moves validated before execution
- References updated atomically
- Rollback on any failure
- Comprehensive logging for audit

✅ **Risk assessment:**
- LOW: 0 references → Safe automated move
- MEDIUM: 1-5 references → Automated with validation
- HIGH: >5 references → Manual approval required

✅ **Validation:**
- Pre-move: Reference scanning
- Post-move: Link checking, build verification
- Continuous: CI/CD integration

## Troubleshooting

### "File not found" error
- Ensure you're in the repository root
- Check file path is relative to root
- Verify file exists with `ls -la <file>`

### "Git mv failed" error
- File may have uncommitted changes: `git status`
- Target directory may not exist: `mkdir -p <dir>`
- File may not be tracked: `git add <file>`

### "Reference update failed" error
- Check file permissions: `ls -l <file>`
- Verify file encoding is UTF-8
- Review `.codex/action_log.ndjson` for details

### "Rollback failed" error
- Check git history: `git log --oneline -10`
- Verify commit exists: `git show <sha>`
- Try manual rollback: `git checkout HEAD~1 -- <file>`

## Future Enhancements

Planned improvements for Phase 1.1:

- [ ] Parallel processing for faster scanning
- [ ] AST-based Python import analysis
- [ ] MkDocs navigation automatic updates
- [ ] GitHub Actions workflow path updates
- [ ] Progress bar for long operations
- [ ] Dry-run diff preview
- [ ] Integration tests

## Contributing

When modifying these scripts:

1. Maintain backward compatibility
2. Add comprehensive docstrings
3. Test with `--dry-run` mode
4. Update this README
5. Follow Physics Model directives
6. Log all operations to NDJSON

## Support

For issues or questions:
- Check `.codex/action_log.ndjson` for operation history
- Review `.codex/reports/ROOT_ORG_PREFLIGHT_SELF_REVIEW.md`
- See `.codex/prompts/ROOT_ORG_PHASE_1_CONTINUATION.md` for full spec
- Contact: @mbaetiong

---

**Version:** 1.0.0  
**Last Updated:** 2026-01-21  
**Status:** ✅ Production Ready  
**Physics Model:** Energy=5 (Full compliance)
