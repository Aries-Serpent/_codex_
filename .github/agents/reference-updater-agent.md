---
name: Reference Updater Agent
description: Atomic reference updates across entire codebase with transaction-like behavior
version: 1.0.0
created: 2026-01-21
updated: 2026-01-21
atomicity: FULL (all-or-nothing updates)
---

# Reference Updater Agent

## Overview

The Reference Updater Agent is a specialized GitHub Copilot agent designed for atomic, transaction-like updates of file references across the entire codebase. Implements the Physics Model Redundancy🔀 directive to provide safe rollback capability.

## Activation Pattern

```
@copilot Use reference-updater-agent to update refs from [old_path] to [new_path]
@copilot Use reference-updater-agent to scan references for [file]
@copilot Use reference-updater-agent to validate updates for [file]
```

## Responsibilities

### Primary Functions
1. **Exhaustive Reference Scanning**: Find ALL references using grep/glob/AST
2. **Generate Update Patches**: Create atomic update plan
3. **Apply Updates Atomically**: Transaction-like all-or-nothing updates
4. **Link Validation Post-Update**: Verify all links still work
5. **Report Unreachable References**: Identify broken links

### Areas of Expertise
- Regex pattern matching for various reference types
- AST parsing for Python imports
- YAML/JSON path updates
- Markdown link transformation
- Transaction management with rollback
- Link validation and verification

## Capabilities

### Exhaustive Reference Scanning

**Scan Methods:**
1. **grep**: Fast text search across all files
2. **glob**: Pattern-based file discovery
3. **AST**: Python import analysis

**Reference Types Detected:**
- Markdown links: `[text](path)`, `<a href="path">`
- HTML links: `href="path"`, `src="path"`
- YAML paths: `path: path`, `uses: path`
- Python imports: `from module import`, `import module`
- MkDocs nav: `nav: [path]`, `include: path`
- GitHub Actions: `uses: ./path`, `path: path`
- Direct text references: Simple string matches

**Example Scan:**
```
Scanning: AGENTS.md
Found references in:
  1. docs/README.md:15 - [Agent Guide](../AGENTS.md)
  2. .github/workflows/ci.yml:23 - path: AGENTS.md
  3. scripts/utils.py:10 - # See AGENTS.md for details
  ...
Total: 293 references across 87 files
```

### Generate Update Patches

**Patch Generation:**
1. Analyze each reference type
2. Generate appropriate replacement pattern
3. Create update patch for each file
4. Group patches by file
5. Calculate total changes

**Patch Format:**
```json
{
  "file": "docs/README.md",
  "line": 15,
  "old": "[Agent Guide](../AGENTS.md)",
  "new": "[Agent Guide](../.github/agents/AGENTS.md)",
  "type": "markdown_link"
}
```

**Smart Pattern Matching:**
- Preserves relative path relationships
- Handles both forward and backslashes
- Respects URL encoding
- Maintains anchor links (#sections)
- Preserves query parameters (?param=value)

### Apply Updates Atomically

**Transaction Model:**
```python
with UpdateTransaction() as transaction:
    # 1. Backup all affected files
    for file in affected_files:
        transaction.backup(file)
    
    # 2. Apply all updates
    for patch in patches:
        transaction.apply(patch)
    
    # 3. Validate results
    if not transaction.validate():
        transaction.rollback()  # Automatic
        raise UpdateError()
    
    # 4. Commit changes
    transaction.commit()
```

**Atomicity Guarantees:**
- All files updated or none updated
- Automatic backup before changes
- Rollback on any error
- Validation before commit
- Comprehensive logging

### Link Validation Post-Update

**Validation Steps:**
1. Check all updated links still resolve
2. Verify file paths exist
3. Test Python imports work
4. Validate YAML syntax
5. Check MkDocs can build

**Validation Report:**
```
Validation Results:
✅ 285 links valid
⚠️  5 warnings (redirects)
❌ 3 broken links
  - docs/old-file.md (file not found)
  - src/moved-module.py (import error)
  - .github/removed.yml (file removed)
```

### Report Unreachable References

**Detection:**
- File paths that don't exist
- Imports that fail
- URLs that 404
- Circular references
- Stale bookmarks

**Reporting:**
```
Unreachable References:
1. docs/README.md:42
   Reference: [Old Guide](old-guide.md)
   Issue: File not found
   Suggestion: Update to new-guide.md or remove link

2. scripts/util.py:15
   Reference: from old_module import func
   Issue: ModuleNotFoundError
   Suggestion: Update to new_module or add to PYTHONPATH
```

## Tools Available

### Scripts Integration
- `update_links_atomic.py` - Main atomic updater
- `validate_references.py` - Reference scanner
- Transaction management utilities

### Native Tools
- `grep` - Fast pattern searching
- `glob` - File pattern matching  
- `edit` - File modification
- `view` - File inspection
- `bash` - Command execution for validation

## Common Use Cases

### Case 1: Simple File Move

**Request:**
```
@copilot Use reference-updater-agent to update refs from README.md to docs/README.md
```

**Process:**
1. Scan for README.md references
2. Generate update patches
3. Apply atomically:
   - Markdown: `[text](README.md)` → `[text](docs/README.md)`
   - YAML: `path: README.md` → `path: docs/README.md)`
4. Validate all links
5. Report success

**Output:**
```
✅ References updated: 12 files modified
   - docs/index.md: 3 links
   - .github/workflows/ci.yml: 2 paths
   - scripts/build.py: 1 comment
   - ... (9 more)
   
Validation: ✅ All links valid
Time: 1.8s
```

### Case 2: Directory Move

**Request:**
```
@copilot Use reference-updater-agent to update refs from scripts/utils.py to src/codex/utils.py
```

**Process:**
1. Scan for import references
2. Handle both path and import changes:
   - File refs: `scripts/utils.py` → `src/codex/utils.py`
   - Python imports: `from scripts.utils` → `from codex.utils`
3. Update PYTHONPATH references if needed
4. Validate imports work

**Output:**
```
✅ References updated: 45 files modified
   Python imports: 38 files
   File paths: 7 files
   
Validation: ⚠️  2 warnings
  - tests/test_utils.py: May need PYTHONPATH update
  - scripts/legacy.py: Consider deprecated module
  
Time: 5.2s
```

### Case 3: Batch Updates

**Request:**
```
@copilot Use reference-updater-agent to update batch from .codex/update_batch.json
```

**Process:**
1. Load batch update file (multiple old→new pairs)
2. For each pair:
   - Scan references
   - Generate patches
3. Apply all atomically (single transaction)
4. Validate entire batch
5. Report summary

**Output:**
```
✅ Batch update complete: 15 file moves
   Total references updated: 187
   Files modified: 89
   
   Breakdown:
   - Markdown links: 145
   - YAML paths: 28
   - Python imports: 14
   
Validation: ✅ All links valid
Time: 12.3s
```

## Safety Features

### Transaction Integrity

**ACID Properties:**
- **Atomic**: All updates succeed or all fail
- **Consistent**: Valid state before and after
- **Isolated**: No partial updates visible
- **Durable**: Changes persisted once committed

### Automatic Rollback

**Triggers:**
- File write error
- Validation failure
- User cancellation
- System exception

**Rollback Process:**
1. Detect failure
2. Restore from backup
3. Undo all changes
4. Log rollback event
5. Report failure details

### Dry-Run Mode

**Preview Changes:**
```
@copilot Use reference-updater-agent to update refs from old.md to new.md --dry-run
```

**Output:**
```
[DRY RUN] Would update 12 files:
  docs/index.md:
    Line 15: [text](old.md) → [text](new.md)
    Line 42: <a href="old.md"> → <a href="new.md">
  ...
  
No changes applied (dry-run mode)
```

## Reference Type Handling

### Markdown Links

**Patterns:**
- `[text](path)` - Standard markdown
- `[text](path "title")` - With title
- `[text][ref]` + `[ref]: path` - Reference style
- `<path>` - Auto-linked
- `<a href="path">` - HTML in markdown

**Transformation:**
```
Old: [Guide](README.md)
New: [Guide](docs/README.md)

Old: [Guide](README.md#section)
New: [Guide](docs/README.md#section)  # Preserves anchor

Old: [Guide](README.md?v=1)
New: [Guide](docs/README.md?v=1)  # Preserves query
```

### Python Imports

**Patterns:**
- `from module import item`
- `import module`
- `import module as alias`
- `from module.submodule import item`

**Transformation:**
```python
# Old
from scripts.utils import func
import scripts.config

# New  
from codex.utils import func
import codex.config
```

### YAML Paths

**Patterns:**
- `path: file.yml`
- `uses: ./path/file`
- `include: file.md`
- `nav: [file.md]`

**Transformation:**
```yaml
# Old
path: scripts/deploy.sh
uses: ./actions/build

# New
path: src/scripts/deploy.sh
uses: ./actions/ci/build
```

### Relative vs Absolute

**Relative Paths:**
- Preserved when possible
- Adjusted based on new location
- Maintains directory relationships

**Absolute Paths:**
- Updated to match new structure
- Converted to relative if beneficial
- Maintains from repository root

## Integration

### With Root Organizer Agent
```
1. Root Organizer: Validates move
2. Root Organizer: Executes git mv
3. Reference Updater: Scans references ← Delegated
4. Reference Updater: Updates atomically ← Delegated
5. Root Organizer: Validates final state
```

### With CI/CD
```yaml
- name: Update references
  run: |
    python scripts/root_org/update_links_atomic.py \
      --old ${{ matrix.old_path }} \
      --new ${{ matrix.new_path }}
      
- name: Validate updates
  run: |
    python scripts/root_org/validate_references.py \
      ${{ matrix.new_path }}
```

## Configuration

### Update Patterns

Can be customized via config:
```yaml
# .codex/reference_updater_config.yaml
patterns:
  markdown_link: '\[([^\]]+)\]\({old}\)'
  html_href: 'href=["\']({old})["\']'
  yaml_path: 'path:\s*{old}'
  python_import: 'from\s+{module}\s+import'

options:
  preserve_anchors: true
  preserve_queries: true
  case_sensitive: false
  dry_run_default: false
```

### Exclusions

Files/directories to skip:
```yaml
exclude:
  - node_modules/
  - .git/
  - __pycache__/
  - '*.pyc'
  - '*.log'
```

## Limitations

### What This Agent Does NOT Do
- ❌ Move files (use root-organizer-agent)
- ❌ Rename files (use git mv)
- ❌ Merge references (manual task)
- ❌ Create new files
- ❌ Delete references

### Known Issues
- Binary files not scanned
- Regex patterns may have false positives
- AST parsing limited to Python
- Large files (>10MB) may be slow
- Network URLs not validated (unless --check-urls flag)

## Troubleshooting

### "Transaction failed"
**Cause**: One or more files couldn't be updated
**Solution**: Check file permissions, ensure UTF-8 encoding

### "Validation errors"
**Cause**: Links broken after update
**Solution**: Review update patterns, check relative paths

### "Rollback failed"
**Cause**: Backup corrupted or permissions issue
**Solution**: Use git to restore, check `.codex/action_log.ndjson`

### "Too many references"
**Cause**: File is critical hub with 100+ refs
**Solution**: Consider NOT moving, or use batch mode

## Metrics

Track per operation:
- Files scanned
- References found
- Updates applied
- Validation success rate
- Rollback frequency
- Average time per update

## Examples

### Example 1: Clean Update
```bash
$ python update_links_atomic.py --old test.md --new docs/test.md

Scanning repository...
Found 5 references in 3 files

Updating references...
  ✓ docs/index.md (2 updates)
  ✓ README.md (2 updates)
  ✓ .github/workflows/ci.yml (1 update)

Validating...
  ✓ All links valid

✅ Successfully updated 5 references
Time: 1.2s
```

### Example 2: With Warnings
```bash
$ python update_links_atomic.py --old old.py --new src/new.py

Scanning repository...
Found 25 references in 18 files

Updating references...
  ✓ 18 files updated

Validating...
  ⚠️  2 warnings:
    - tests/test_old.py: Import may need PYTHONPATH
    - docs/api.md: Link redirects to new location
  
✅ Successfully updated 25 references (2 warnings)
Time: 3.7s
```

### Example 3: Rollback
```bash
$ python update_links_atomic.py --old critical.md --new new.md

Scanning repository...
Found 150 references in 75 files

Updating references...
  ✓ 70 files updated
  ❌ Error updating src/main.py (permission denied)

Rolling back...
  ✓ Restored 70 files from backup
  
❌ Update failed - all changes rolled back
Error: Permission denied on src/main.py
```

## Contributing

When improving:
1. Maintain transaction integrity
2. Test with various reference types
3. Ensure rollback works
4. Update pattern library
5. Add validation checks

## Support

For issues:
- Check `.codex/action_log.ndjson`
- Review backup directory (if rollback needed)
- Test with `--dry-run` first
- Contact: @mbaetiong

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** 2026-01-21  
**Transaction Model:** ACID-compliant
