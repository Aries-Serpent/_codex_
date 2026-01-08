# Repository Structure Generator

This tool generates comprehensive lists of all folders and files in the repository with multiple output formats.

## Features

- **Multiple Output Formats**: Plain text, Markdown with links, categorized by directory, tree structure, JSON, and JSONL
- **File Listing**: Optionally include all files within each folder
- **Compression**: Support for Gzip, Brotli, and Zstandard compression formats
- **GitHub Actions Integration**: Manual trigger workflow with dropdown options
- **Summary Comments**: Optional metadata about folder contents

## Quick Start

### Command Line Usage

```bash
# Generate all formats (default)
python scripts/analysis/list_all_folders.py

# Generate only plain text list
python scripts/analysis/list_all_folders.py --format plain

# Generate markdown with links
python scripts/analysis/list_all_folders.py --format markdown

# Include files within folders
python scripts/analysis/list_all_folders.py --include-files

# Generate JSON with compression
python scripts/analysis/list_all_folders.py --format json --compress gzip

# Generate all formats with files and summaries
python scripts/analysis/list_all_folders.py --format all --include-files --include-summaries
```

### GitHub Actions Workflow

1. Go to **Actions** tab in GitHub
2. Select **Generate Repository Structure** workflow
3. Click **Run workflow**
4. Configure options:
   - **Branch**: Select branch to analyze
   - **Include files**: Toggle file listing
   - **Include summaries**: Add metadata comments
   - **Format**: Choose output format(s)
   - **Compress**: Select compression method for JSON
5. Download artifacts after workflow completes

## Output Files

### Plain Text (`ALL_FOLDERS.txt`)
Simple list of all folders, one per line:
```
.
.codex
.codex/archive
.codex/cognitive_brain
...
```

### Markdown with Links (`ALL_FOLDERS_LINKS.md`)
Alphabetical list with clickable GitHub links:
```markdown
# Repository Folder Links

Total Folders: 250

---

## All Folders (Alphabetical)

- [`.` (root)](.)
- [`.codex`](.codex)
- [`.codex/archive`](.codex/archive)
...
```

### Categorized (`ALL_FOLDERS_CATEGORIZED.md`)
Grouped by top-level directory:
```markdown
# Repository Folder Links (Categorized)

## .CODEX

- [`.codex`](.codex)
- [`.codex/archive`](.codex/archive)

## .GITHUB

- [`.github`](.github)
- [`.github/actions`](.github/actions)
...
```

### Tree Structure (`ALL_FOLDERS_TREE.md`)
Hierarchical tree with links:
```markdown
# Repository Folder Tree (with Links)

[`.` (root)](.)

├── [`.codex`](.codex)
│   ├── [`archive`](.codex/archive)
│   ├── [`cognitive_brain`](.codex/cognitive_brain)
│   └── [`plans`](.codex/plans)
├── [`.github`](.github)
│   ├── [`actions`](.github/actions)
│   └── [`agents`](.github/agents)
...
```

### Files by Folder (`ALL_FILES_BY_FOLDER.md`)
Lists all files in each folder (requires `--include-files`):
```markdown
# Repository Files by Folder

## `.codex`

**Files**: 15

- [`change_log.md`](.codex/change_log.md)
- [`results.md`](.codex/results.md)
...
```

### JSON Format (`repository_structure.json`)
Machine-readable JSON:
```json
{
  "total_folders": 250,
  "folders": [".", ".codex", ...],
  "files_by_folder": {
    ".": ["README.md", "pyproject.toml", ...],
    ".codex": ["change_log.md", ...]
  },
  "total_files": 1500
}
```

### JSON Lines (`repository_structure.jsonl`)
One folder per line:
```json
{"folder": ".", "files": ["README.md", "pyproject.toml"]}
{"folder": ".codex", "files": ["change_log.md", "results.md"]}
...
```

### Compressed Formats
- `repository_structure.gz` (Gzip)
- `repository_structure.br` (Brotli)
- `repository_structure.zst` (Zstandard)

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--root` | Repository root path | Current directory |
| `--output-dir` | Output directory | `.codex/repository_structure` |
| `--format` | Output format: `plain`, `markdown`, `categorized`, `tree`, `files`, `json`, `jsonl`, `all` | `all` |
| `--include-files` | Also list files within folders | `False` |
| `--compress` | Compress JSON: `gzip`, `brotli`, `zstd`, `all` | None |
| `--include-summaries` | Add summary comments in JSON | `False` |

## Use Cases

### 1. Quick Navigation Reference
Generate a plain text list for quick copy-paste:
```bash
python scripts/analysis/list_all_folders.py --format plain
cat .codex/repository_structure/ALL_FOLDERS.txt
```

### 2. Documentation
Generate markdown for wiki or documentation:
```bash
python scripts/analysis/list_all_folders.py --format markdown
```

### 3. Automated Analysis
Generate JSON for scripts and tools:
```bash
python scripts/analysis/list_all_folders.py --format json --include-files
```

### 4. Archive/Backup Metadata
Generate compressed archive of repository structure:
```bash
python scripts/analysis/list_all_folders.py --format json --include-files --compress all
```

### 5. CI/CD Integration
Use in GitHub Actions to track repository structure changes over time.

## Installation

### Required Dependencies
None - uses only Python standard library

### Optional Dependencies
For compression support:
```bash
# Brotli compression
pip install brotli

# Zstandard compression
pip install zstandard
```

## Performance

- **Scanning**: Processes ~1000 folders in <5 seconds
- **File Listing**: Adds ~5-10 seconds for ~5000 files
- **Output Generation**: All formats in <2 seconds
- **Total Runtime**: Typically <15 seconds for large repositories

## Ignored Directories

The following directories are automatically excluded:
- `.git`, `.venv`, `venv`, `node_modules`
- `__pycache__`, `.pytest_cache`, `.hypothesis`
- `dist`, `build`, `.mypy_cache`, `.tox`
- `htmlcov`, `.eggs`, `.nox`, `.codex_cache`
- `target`, `bin`, `obj`

## Examples

### Example 1: Quick Reference
```bash
# Generate simple list
python scripts/analysis/list_all_folders.py --format plain
```

### Example 2: Complete Documentation
```bash
# All formats with files
python scripts/analysis/list_all_folders.py --format all --include-files
```

### Example 3: Compressed Archive
```bash
# JSON with all compression formats
python scripts/analysis/list_all_folders.py --format json --include-files --compress all
```

### Example 4: Custom Output Location
```bash
# Save to custom directory
python scripts/analysis/list_all_folders.py --output-dir ./reports/structure
```

## Integration with Other Tools

### Task 4: Folder Structure Mapper
The comprehensive folder structure mapper can call this script automatically:
```python
from scripts.analysis.list_all_folders import list_all_folders, list_all_files
folders = list_all_folders(Path('.'))
files = list_all_files(Path('.'))
```

### CI/CD Pipelines
Include in your workflow:
```yaml
- name: Generate Structure
  run: python scripts/analysis/list_all_folders.py --format all --include-files
```

## Troubleshooting

### Permission Errors
If you encounter permission errors, ensure the output directory is writable:
```bash
mkdir -p .codex/repository_structure
chmod 755 .codex/repository_structure
```

### Missing Compression Libraries
If compression fails:
```bash
pip install brotli zstandard
```

### Memory Issues
For very large repositories (>100k files), use streaming formats:
```bash
python scripts/analysis/list_all_folders.py --format jsonl
```

## License

Part of the Aries-Serpent/_codex_ repository.
