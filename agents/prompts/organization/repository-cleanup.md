# Repository Organization and Cleanup

## Purpose
Analyze repository structure, archive old files, organize root directory, and generate organization reports to maintain a clean, navigable codebase.

## Prerequisites
- Python 3.9+ installed
- Write access to repository
- Git configured for commits

## Commands

### 1. Analyze Repository Structure
```bash
cd /home/runner/work/_codex_/_codex_
python -m scripts.space_traversal.audit_runner analyze-structure --output structure_report.md
```

### 2. Archive Old Status/Report Files
```bash
# Create archive directory
mkdir -p archive/status_reports_$(date +%Y%m%d)

# Move old status files
find . -maxdepth 1 -name "*STATUS*.md" -o -name "*REPORT*.md" | \
  xargs -I {} mv {} archive/status_reports_$(date +%Y%m%d)/

# Move old achievement files
find . -maxdepth 1 -name "ACHIEVEMENT*.md" -o -name "*COMPLETE*.md" | \
  xargs -I {} mv {} archive/status_reports_$(date +%Y%m%d)/
```

### 3. Generate Organization Guide
```bash
python -c "
from pathlib import Path
import json

# Scan repository structure
root = Path('.')
structure = {
    'core_modules': list(root.glob('src/**/*.py')),
    'tests': list(root.glob('tests/**/*.py')),
    'docs': list(root.glob('docs/**/*.md')),
    'configs': list(root.glob('**/*.yaml')) + list(root.glob('**/*.yml')),
    'scripts': list(root.glob('scripts/**/*.py')),
}

# Generate report
with open('REPOSITORY_ORGANIZATION.md', 'w') as f:
    f.write('# Repository Organization\n\n')
    for category, files in structure.items():
        f.write(f'## {category.replace(\"_\", \" \").title()}\n')
        f.write(f'Total: {len(files)} files\n\n')
        for file in sorted(files)[:10]:  # Show first 10
            f.write(f'- {file}\n')
        if len(files) > 10:
            f.write(f'- ... and {len(files) - 10} more\n')
        f.write('\n')

print('Generated: REPOSITORY_ORGANIZATION.md')
"
```

### 4. Clean Root Directory
```bash
# Move status/summary files to archive
mkdir -p archive/historical_docs

# Archive old markdown files (preserve key docs)
for file in $(find . -maxdepth 1 -name "*.md" -type f); do
    filename=$(basename "$file")
    # Skip key documentation
    if [[ ! "$filename" =~ ^(README|AGENTS|CONTRIBUTING|SECURITY|CODE_OF_CONDUCT|GOVERNANCE)\.md$ ]]; then
        if [[ "$filename" =~ (STATUS|SUMMARY|REPORT|COMPLETE|ACHIEVEMENT) ]]; then
            echo "Archiving: $filename"
            mv "$file" archive/historical_docs/
        fi
    fi
done
```

## Validation

1. **Check Archive Created**: `ls -la archive/`
2. **Verify Key Docs Preserved**: Ensure README.md, AGENTS.md, etc. still exist
3. **Review Organization Report**: `cat REPOSITORY_ORGANIZATION.md`
4. **Check Git Status**: `git status` - should show moved files

## Expected Output

### Directory Structure After Cleanup
```
/home/runner/work/_codex_/_codex_/
├── README.md              # Preserved
├── AGENTS.md              # Preserved
├── CONTRIBUTING.md        # Preserved
├── SECURITY.md            # Preserved
├── src/                   # Source code
├── tests/                 # Test files
├── scripts/               # Utility scripts
├── agents/                # Agent tools and prompts
├── archive/               # Archived files
│   ├── historical_docs/   # Old markdown files
│   └── status_reports_*/  # Status reports by date
└── ...
```

### Organization Report Structure
```markdown
# Repository Organization

## Core Modules
Total: 234 files
- src/codex/cli.py
- src/codex/logging/session_logger.py
...

## Tests
Total: 1,208 files
- tests/test_cli.py
- tests/logging/test_session_logger.py
...
```

## Archive Strategy

### Files to Archive
- **Status Reports**: `*STATUS*.md`, `*REPORT*.md`
- **Achievement Logs**: `ACHIEVEMENT*.md`, `*COMPLETE*.md`
- **Old Summaries**: `*SUMMARY*.md`, `*PROGRESS*.md`
- **Temporary Docs**: `PHASE*.md`, `WAVE*.md`

### Files to Preserve
- **Core Documentation**: `README.md`, `AGENTS.md`, `CONTRIBUTING.md`
- **Security**: `SECURITY.md`, `CODE_OF_CONDUCT.md`
- **Governance**: `GOVERNANCE.md`, `LICENSE`
- **Current Status**: Most recent status update files

## Troubleshooting

### Issue: Accidentally archived key file
**Solution**: Restore from archive
```bash
cp archive/historical_docs/IMPORTANT_FILE.md ./
```

### Issue: Too many files to process
**Solution**: Process in batches
```bash
find . -maxdepth 1 -name "*STATUS*.md" | head -20 | xargs -I {} mv {} archive/
```

### Issue: Permission denied
**Solution**: Check file permissions
```bash
chmod +w file_to_move.md
```

## Integration with GitHub Actions

Automate organization with scheduled workflow:

```yaml
name: Repository Organization

on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly
  workflow_dispatch:

jobs:
  organize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Organization
        run: |
          bash scripts/organize_repository.sh
          
      - name: Commit Changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .
          git commit -m "chore: Archive old status reports" || echo "No changes"
          git push
```

## AI Query Interface

Files in archive remain queryable by AI Agents:

```bash
# Generate searchable index
find archive/ -name "*.md" > archive/INDEX.txt

# Create metadata
python -c "
import os
from pathlib import Path
import json

archive = Path('archive')
metadata = {}
for file in archive.rglob('*.md'):
    stat = file.stat()
    metadata[str(file)] = {
        'size': stat.st_size,
        'modified': stat.st_mtime,
        'relative_path': str(file.relative_to(archive))
    }

with open('archive/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
"
```

## Related Prompts
- [analyze-dependencies.md](analyze-dependencies.md) - Dependency analysis
- [generate-repo-map.md](generate-repo-map.md) - Repository mapping
- [cleanup-workflows.md](cleanup-workflows.md) - GitHub Actions cleanup
