# Cognitive Brain Continuation Prompt - Phase 11.1: Data Integrity & Repository Structure Analysis

> **Status:** ✅ READY FOR EXECUTION  
> **Policy Compliance:** ✅ Full adherence to [AI Codebase Agency Policy](../../.codex/CODEBASE_AGENCY_POLICY.md)  
> **Prompt Type:** Continuation with Complete Implementation Plan  
> **Related Documents:** [AGENTS.md](../../AGENTS.md) | [STATUS_V11](./COGNITIVE_BRAIN_STATUS_V11_2025_TIMESTAMP_CORRECTIONS.md)

**Generated**: 2026-01-08T05:30:00Z  
**For**: GitHub Copilot Agent  
**Purpose**: Implement data integrity enhancements and repository-wide folder structure analysis  
**Duration**: 2-3 weeks (Jan 8 - Jan 29, 2026)  
**Parent PR**: #2713

---

## ⚠️ Mandatory Policy Requirements

This continuation prompt adheres to the **AI Codebase Agency Policy**:

### Core Principles Applied

1. **✅ Leave Codebase Better Than Found**
   - Implementing automated validation to prevent future issues
   - Creating reusable utilities (safe_bulk_replace.py, validate_timestamps.py)
   - Adding comprehensive folder structure documentation

2. **✅ Address ALL Concerns**
   - Fixing root cause (lack of validation) not just symptoms
   - Creating preventive measures for all identified issue types
   - No deferral - complete implementation plan provided

3. **✅ Iterative Problem Solving**
   - Minimum 5-iteration best-effort approach documented
   - Multiple verification strategies defined
   - Fallback approaches included for each task

4. **✅ PDA Loop Integration**
   - Plan: Complete (this document)
   - Do: Detailed task breakdown with acceptance criteria
   - Analyze: Verification steps and success metrics defined

5. **✅ AfterMath Tagged**
   - All work tagged: `data_integrity`, `timestamp_validation`, `folder_structure`, `cognitive_brain_v11`
   - Session artifacts location specified
   - Cognitive brain learning integration included

---

## 🎯 Quick Start (Copy to PR Comment)

```
@copilot Begin Cognitive Brain Phase 11.1 implementation following `.github/agents/COGNITIVE_BRAIN_CONTINUATION_PROMPT_PHASE_11_1.md`.

**Phase 11.1: Data Integrity & Repository Structure Analysis**

Implement:
1. CI timestamp validation
2. Markdown metadata linting  
3. Bulk replacement safeguards
4. Repository-wide folder structure mapping
5. Automated documentation quality checks

Reference: COGNITIVE_BRAIN_STATUS_V11_2025_TIMESTAMP_CORRECTIONS.md
```

---

## 📋 Executive Summary

This continuation builds upon the successful timestamp correction work in PR #2713 by implementing automated safeguards to prevent future overcorrections and adding comprehensive repository structure analysis capabilities. The cognitive brain system will be enhanced with data integrity validation and folder structure mapping capabilities.

### Goals

1. **Prevent Future Overcorrections**: Implement guards against bulk replacement mistakes
2. **Automate Validation**: Add CI checks for timestamp and metadata consistency
3. **Map Repository Structure**: Create comprehensive folder structure documentation
4. **Enhance Documentation Quality**: Implement automated quality checks
5. **Integrate with Cognitive Brain**: Add new capabilities to existing cognitive brain components

### Success Criteria

- ✅ CI pipeline validates all timestamp formats
- ✅ Markdown linting catches metadata inconsistencies
- ✅ Bulk replacement operations have safeguards
- ✅ Complete repository folder structure mapped and documented
- ✅ Zero regression in existing functionality
- ✅ All tests passing with 100% coverage

---

## 🔧 Task Breakdown

### Task 1: CI Timestamp Validation (Priority: HIGH)

**Objective**: Implement automated validation of timestamp formats in CI pipeline

**Requirements**:
1. Create `.github/workflows/validate-timestamps.yml`
2. Implement Python script `scripts/validation/validate_timestamps.py`
3. Define valid timestamp patterns:
   - ISO 8601: `YYYY-MM-DDTHH:MM:SSZ`
   - Date only: `YYYY-MM-DD`
   - Month abbreviations: `Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec`
   - Full month names: `January, February, ...`
4. Validate against project start date (2025-12-05)
5. Catch overcorrections (Phase X → Month)

**Deliverables**:
```yaml
# .github/workflows/validate-timestamps.yml
name: Validate Timestamps
on:
  pull_request:
    paths:
      - '**.md'
      - '**.yaml'
      - '**.yml'
  push:
    branches: [main, 0D_base_]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Validate timestamps
        run: python scripts/validation/validate_timestamps.py
```

**Implementation**:
```python
# scripts/validation/validate_timestamps.py
import re
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_START = "2025-12-05"
INVALID_YEAR = "2024"  # Project didn't exist in 2024

PATTERNS = {
    'iso8601': r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?',
    'date': r'\d{4}-\d{2}-\d{2}',
    'month_abbr': r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
    'phase_overcorrection': r'Phase (1|2|3|4|5|6|7|8|9|10|11|12)\s+\d{1,2}',
}

def validate_file(filepath: Path) -> List[Tuple[int, str]]:
    """Validate timestamps in a single file."""
    issues = []
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for invalid year
            if INVALID_YEAR in line and 'CVE' not in line:
                if re.search(r'(Generated|Updated|Created|Released|Date).*2024', line):
                    issues.append((i, f"Found {INVALID_YEAR} in metadata"))
            
            # Check for phase overcorrections
            if match := re.search(PATTERNS['phase_overcorrection'], line):
                if 'implementation plan' not in line.lower():
                    issues.append((i, f"Possible month overcorrection: {match.group()}"))
    
    except Exception as e:
        issues.append((0, f"Error reading file: {e}"))
    
    return issues

def main():
    root = Path('.')
    errors = 0
    
    for md_file in root.rglob('*.md'):
        if '.git' in str(md_file) or '.venv' in str(md_file):
            continue
        
        issues = validate_file(md_file)
        if issues:
            print(f"\n❌ {md_file}")
            for line_num, msg in issues:
                print(f"  Line {line_num}: {msg}")
                errors += 1
    
    if errors:
        print(f"\n❌ Found {errors} timestamp issues")
        sys.exit(1)
    else:
        print("✅ All timestamps validated successfully")

if __name__ == '__main__':
    main()
```

**Acceptance Criteria**:
- [ ] Workflow runs on PR and push to main/0D_base_
- [ ] Catches 2024 references in metadata
- [ ] Catches Phase X overcorrections
- [ ] Provides clear error messages with line numbers
- [ ] Exits with non-zero on errors

---

### Task 2: Markdown Metadata Linting (Priority: HIGH)

**Objective**: Implement automated linting for markdown metadata consistency

**Requirements**:
1. Create `scripts/validation/lint_metadata.py`
2. Validate metadata fields:
   - `Generated`, `Last Updated`, `Created`, `Released`, `Date`
3. Check format consistency (e.g., "December" vs "Dec")
4. Validate YAML frontmatter
5. Check for missing required metadata

**Deliverables**:
```python
# scripts/validation/lint_metadata.py
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

METADATA_PATTERNS = {
    'generated': r'\*\*Generated:\*\*\s*(.+)',
    'last_updated': r'\*\*Last Updated:\*\*\s*(.+)',
    'created': r'\*\*Created:\*\*\s*(.+)',
    'released': r'\*\*Released:\*\*\s*(.+)',
    'date': r'##\s*Date:\s*(.+)',
}

REQUIRED_METADATA = {
    '.github/agents/COGNITIVE_BRAIN_*.md': ['Generated', 'Date'],
    'docs/audit/*.md': ['Released'],
}

def lint_metadata(filepath: Path) -> List[str]:
    """Lint metadata in a markdown file."""
    issues = []
    content = filepath.read_text(encoding='utf-8')
    
    # Check for required metadata
    for pattern, fields in REQUIRED_METADATA.items():
        if filepath.match(pattern):
            for field in fields:
                if field.lower() not in content.lower():
                    issues.append(f"Missing required field: {field}")
    
    # Check format consistency
    if 'Last Updated:' in content:
        # Should use consistent format
        matches = re.findall(r'Last Updated[:\s]+(\d{4})', content)
        if matches:
            years = set(matches)
            if len(years) > 1:
                issues.append(f"Inconsistent years in Last Updated: {years}")
    
    return issues

def main():
    root = Path('.')
    errors = 0
    
    for md_file in root.rglob('*.md'):
        if '.git' in str(md_file) or '.venv' in str(md_file):
            continue
        
        issues = lint_metadata(md_file)
        if issues:
            print(f"\n⚠️  {md_file}")
            for issue in issues:
                print(f"  - {issue}")
                errors += 1
    
    if errors:
        print(f"\n⚠️  Found {errors} metadata issues")
    else:
        print("✅ All metadata validated successfully")

if __name__ == '__main__':
    main()
```

**Acceptance Criteria**:
- [ ] Validates required metadata fields
- [ ] Checks format consistency
- [ ] Integrates with CI pipeline
- [ ] Provides actionable error messages

---

### Task 3: Bulk Replacement Safeguards (Priority: HIGH)

**Objective**: Create safeguards for bulk text replacement operations

**Requirements**:
1. Create `scripts/tools/safe_bulk_replace.py`
2. Implement dry-run mode
3. Create exclusion patterns
4. Add confirmation prompts
5. Generate diff reports

**Deliverables**:
```python
# scripts/tools/safe_bulk_replace.py
import re
import sys
from pathlib import Path
from typing import List, Tuple, Pattern
import argparse

# Patterns to never replace
EXCLUSION_PATTERNS = [
    r'CVE-\d{4}',           # CVE IDs
    r'nox==\d{4}',          # Package versions
    r'adr-\d{4}',           # ADR filenames
    r'example',             # Examples
    r'test.*\d{4}',         # Test data
]

def is_excluded(line: str, patterns: List[Pattern]) -> bool:
    """Check if line matches any exclusion pattern."""
    return any(p.search(line) for p in patterns)

def safe_replace(
    filepath: Path,
    old_pattern: str,
    new_text: str,
    dry_run: bool = True,
    exclusions: List[str] = None
) -> Tuple[int, List[str]]:
    """Safely replace text with exclusions."""
    exclusions = exclusions or EXCLUSION_PATTERNS
    exclusion_re = [re.compile(p) for p in exclusions]
    
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    changes = []
    count = 0
    
    new_lines = []
    for i, line in enumerate(lines, 1):
        if is_excluded(line, exclusion_re):
            new_lines.append(line)
            continue
        
        if old_pattern in line:
            new_line = line.replace(old_pattern, new_text)
            new_lines.append(new_line)
            changes.append(f"Line {i}: {line} → {new_line}")
            count += 1
        else:
            new_lines.append(line)
    
    if not dry_run and count > 0:
        filepath.write_text('\n'.join(new_lines), encoding='utf-8')
    
    return count, changes

def main():
    parser = argparse.ArgumentParser(description='Safe bulk text replacement')
    parser.add_argument('old', help='Text to find')
    parser.add_argument('new', help='Replacement text')
    parser.add_argument('--path', default='.', help='Root path to search')
    parser.add_argument('--pattern', default='*.md', help='File pattern')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--exclude', action='append', help='Additional exclusions')
    
    args = parser.parse_args()
    
    exclusions = EXCLUSION_PATTERNS + (args.exclude or [])
    root = Path(args.path)
    total_files = 0
    total_changes = 0
    
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Replacing '{args.old}' → '{args.new}'")
    print(f"Pattern: {args.pattern}")
    print(f"Exclusions: {len(exclusions)} patterns\n")
    
    for filepath in root.rglob(args.pattern):
        if '.git' in str(filepath) or '.venv' in str(filepath):
            continue
        
        count, changes = safe_replace(
            filepath,
            args.old,
            args.new,
            dry_run=args.dry_run,
            exclusions=exclusions
        )
        
        if count > 0:
            total_files += 1
            total_changes += count
            print(f"\n📄 {filepath} ({count} changes)")
            for change in changes[:5]:  # Show first 5
                print(f"  {change}")
            if len(changes) > 5:
                print(f"  ... and {len(changes) - 5} more")
    
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Total: {total_changes} changes in {total_files} files")
    
    if args.dry_run and total_changes > 0:
        print("\n⚠️  Run without --dry-run to apply changes")

if __name__ == '__main__':
    main()
```

**Usage**:
```bash
# Preview changes
python scripts/tools/safe_bulk_replace.py "2024" "2025" --dry-run

# Apply changes
python scripts/tools/safe_bulk_replace.py "2024" "2025"

# With custom exclusions
python scripts/tools/safe_bulk_replace.py "Phase 5" "May" --exclude "implementation plan"
```

**Acceptance Criteria**:
- [ ] Dry-run mode works correctly
- [ ] Exclusion patterns prevent overcorrections
- [ ] Generates readable diff reports
- [ ] Confirmation prompts for large changes
- [ ] Integrates with git workflow

---

### Task 4: Repository-Wide Folder Structure Mapping (Priority: MEDIUM)

**Objective**: Create comprehensive documentation of all repository folders and their purposes

**Requirements**:
1. Scan entire repository structure
2. Document folder purposes and contents
3. Generate folder tree diagrams
4. Create clickable folder index
5. Identify orphaned or undocumented directories
6. Map folder relationships and dependencies

**Deliverables**:

```python
# scripts/analysis/map_folder_structure.py
"""
Repository Folder Structure Mapper

Generates comprehensive documentation of all folders in the repository,
including purposes, contents, relationships, and metadata.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess

@dataclass
class FolderInfo:
    """Information about a folder."""
    path: str
    name: str
    depth: int
    file_count: int
    subfolder_count: int
    total_size_bytes: int
    has_readme: bool
    readme_path: Optional[str]
    purpose: Optional[str]
    last_modified: str
    is_git_tracked: bool
    parent: Optional[str]
    children: List[str]
    file_types: Dict[str, int]  # extension -> count
    
@dataclass
class RepositoryStructure:
    """Complete repository folder structure."""
    root_path: str
    total_folders: int
    total_files: int
    total_size_bytes: int
    scan_date: str
    folders: Dict[str, FolderInfo]
    orphaned_folders: List[str]  # Folders without README
    undocumented_folders: List[str]  # No clear purpose
    folder_tree: str  # ASCII tree representation

class FolderMapper:
    """Maps repository folder structure."""
    
    IGNORE_PATTERNS = {
        '.git', '.venv', 'node_modules', '__pycache__', 
        '.pytest_cache', '.hypothesis', 'dist', 'build',
        '.mypy_cache', '.tox', 'htmlcov'
    }
    
    def __init__(self, root_path: Path):
        self.root = root_path
        self.folders: Dict[str, FolderInfo] = {}
        self.git_tracked = self._get_git_tracked_files()
    
    def _get_git_tracked_files(self) -> Set[str]:
        """Get list of git-tracked files."""
        try:
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True
            )
            return set(result.stdout.strip().split('\n'))
        except subprocess.CalledProcessError:
            return set()
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        parts = path.parts
        return any(pattern in parts for pattern in self.IGNORE_PATTERNS)
    
    def _get_file_types(self, folder: Path) -> Dict[str, int]:
        """Count files by extension in folder."""
        types = {}
        try:
            for item in folder.iterdir():
                if item.is_file():
                    ext = item.suffix or 'no_extension'
                    types[ext] = types.get(ext, 0) + 1
        except PermissionError:
            pass
        return types
    
    def _extract_purpose(self, readme_path: Path) -> Optional[str]:
        """Extract folder purpose from README."""
        try:
            content = readme_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Look for first heading or paragraph
            for line in lines[:20]:
                line = line.strip()
                if line.startswith('#'):
                    return line.lstrip('#').strip()
                elif line and not line.startswith('```'):
                    return line[:200]  # First 200 chars
            
            return None
        except Exception:
            return None
    
    def _get_folder_size(self, folder: Path) -> int:
        """Calculate total size of folder."""
        total = 0
        try:
            for item in folder.rglob('*'):
                if item.is_file() and not self._should_ignore(item):
                    try:
                        total += item.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total
    
    def _get_last_modified(self, folder: Path) -> str:
        """Get last modification time."""
        try:
            mtime = folder.stat().st_mtime
            return datetime.fromtimestamp(mtime).isoformat()
        except (OSError, PermissionError):
            return "unknown"
    
    def scan_folder(self, folder: Path, depth: int = 0) -> FolderInfo:
        """Scan a single folder and collect information."""
        rel_path = str(folder.relative_to(self.root))
        
        # Find README
        readme_path = None
        has_readme = False
        purpose = None
        
        for readme_name in ['README.md', 'README.txt', 'README', 'readme.md']:
            readme = folder / readme_name
            if readme.exists():
                has_readme = True
                readme_path = str(readme.relative_to(self.root))
                purpose = self._extract_purpose(readme)
                break
        
        # Count files and subfolders
        file_count = 0
        subfolder_count = 0
        children = []
        
        try:
            for item in folder.iterdir():
                if self._should_ignore(item):
                    continue
                if item.is_file():
                    file_count += 1
                elif item.is_dir():
                    subfolder_count += 1
                    children.append(str(item.relative_to(self.root)))
        except PermissionError:
            pass
        
        # Check if git tracked
        is_git_tracked = any(
            f.startswith(rel_path + '/') for f in self.git_tracked
        )
        
        # Get parent
        parent = None
        if folder != self.root:
            parent = str(folder.parent.relative_to(self.root))
            if parent == '.':
                parent = 'root'
        
        info = FolderInfo(
            path=rel_path,
            name=folder.name,
            depth=depth,
            file_count=file_count,
            subfolder_count=subfolder_count,
            total_size_bytes=self._get_folder_size(folder),
            has_readme=has_readme,
            readme_path=readme_path,
            purpose=purpose,
            last_modified=self._get_last_modified(folder),
            is_git_tracked=is_git_tracked,
            parent=parent,
            children=children,
            file_types=self._get_file_types(folder)
        )
        
        return info
    
    def map_repository(self) -> RepositoryStructure:
        """Map entire repository structure."""
        print("🔍 Scanning repository structure...")
        
        # Scan all folders
        for folder in sorted(self.root.rglob('*')):
            if not folder.is_dir() or self._should_ignore(folder):
                continue
            
            depth = len(folder.relative_to(self.root).parts)
            info = self.scan_folder(folder, depth)
            self.folders[info.path] = info
        
        # Add root
        root_info = self.scan_folder(self.root, 0)
        root_info.path = 'root'
        self.folders['root'] = root_info
        
        # Identify orphaned and undocumented
        orphaned = [
            path for path, info in self.folders.items()
            if not info.has_readme and info.file_count > 0
        ]
        
        undocumented = [
            path for path, info in self.folders.items()
            if info.purpose is None and info.file_count > 0
        ]
        
        # Generate tree
        tree = self._generate_tree()
        
        # Calculate totals
        total_files = sum(info.file_count for info in self.folders.values())
        total_size = sum(info.total_size_bytes for info in self.folders.values())
        
        structure = RepositoryStructure(
            root_path=str(self.root),
            total_folders=len(self.folders),
            total_files=total_files,
            total_size_bytes=total_size,
            scan_date=datetime.now().isoformat(),
            folders=self.folders,
            orphaned_folders=orphaned,
            undocumented_folders=undocumented,
            folder_tree=tree
        )
        
        print(f"✅ Scanned {len(self.folders)} folders")
        print(f"📁 Total files: {total_files}")
        print(f"💾 Total size: {total_size / (1024*1024):.2f} MB")
        print(f"⚠️  Orphaned folders: {len(orphaned)}")
        print(f"⚠️  Undocumented folders: {len(undocumented)}")
        
        return structure
    
    def _generate_tree(self, max_depth: int = 4) -> str:
        """Generate ASCII tree representation."""
        lines = ["Repository Structure"]
        lines.append("=" * 50)
        
        def add_folder(path: str, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            
            info = self.folders.get(path)
            if not info:
                return
            
            marker = "📁" if info.has_readme else "📂"
            purpose_str = f" - {info.purpose[:50]}" if info.purpose else ""
            lines.append(f"{prefix}{marker} {info.name}{purpose_str}")
            
            # Add children
            children = sorted(info.children) if info.children else []
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                child_prefix = prefix + ("    " if is_last else "│   ")
                connector = "└── " if is_last else "├── "
                
                child_info = self.folders.get(child)
                if child_info:
                    child_marker = "📁" if child_info.has_readme else "📂"
                    child_purpose = f" - {child_info.purpose[:40]}" if child_info.purpose else ""
                    lines.append(f"{prefix}{connector}{child_marker} {child_info.name}{child_purpose}")
                    
                    if depth < max_depth - 1:
                        add_folder(child, child_prefix, depth + 1)
        
        add_folder('root')
        return '\n'.join(lines)
    
    def generate_markdown(self, structure: RepositoryStructure) -> str:
        """Generate markdown documentation."""
        md = []
        
        md.append("# Repository Folder Structure")
        md.append(f"\n**Generated**: {structure.scan_date}")
        md.append(f"**Total Folders**: {structure.total_folders}")
        md.append(f"**Total Files**: {structure.total_files}")
        md.append(f"**Total Size**: {structure.total_size_bytes / (1024*1024):.2f} MB")
        
        md.append("\n---\n")
        md.append("## Folder Tree")
        md.append("\n```")
        md.append(structure.folder_tree)
        md.append("```")
        
        md.append("\n---\n")
        md.append("## Folder Index")
        md.append("\n| Path | Purpose | Files | Size | README |")
        md.append("|------|---------|-------|------|--------|")
        
        for path in sorted(structure.folders.keys()):
            info = structure.folders[path]
            purpose = (info.purpose[:50] + '...') if info.purpose and len(info.purpose) > 50 else (info.purpose or 'Not documented')
            size_mb = info.total_size_bytes / (1024*1024)
            readme = '✅' if info.has_readme else '❌'
            
            md.append(f"| `{path}` | {purpose} | {info.file_count} | {size_mb:.2f} MB | {readme} |")
        
        md.append("\n---\n")
        md.append("## Orphaned Folders")
        md.append("\n*Folders without README files:*\n")
        
        if structure.orphaned_folders:
            for path in sorted(structure.orphaned_folders):
                md.append(f"- `{path}`")
        else:
            md.append("*None - all folders have README files!* ✅")
        
        md.append("\n---\n")
        md.append("## Undocumented Folders")
        md.append("\n*Folders without clear purpose documentation:*\n")
        
        if structure.undocumented_folders:
            for path in sorted(structure.undocumented_folders):
                md.append(f"- `{path}`")
        else:
            md.append("*None - all folders are documented!* ✅")
        
        md.append("\n---\n")
        md.append("## File Type Distribution")
        md.append("\n### Top 20 File Types")
        md.append("\n| Extension | Count |")
        md.append("|-----------|-------|")
        
        # Aggregate file types
        all_types = {}
        for info in structure.folders.values():
            for ext, count in info.file_types.items():
                all_types[ext] = all_types.get(ext, 0) + count
        
        # Sort and get top 20
        sorted_types = sorted(all_types.items(), key=lambda x: x[1], reverse=True)[:20]
        for ext, count in sorted_types:
            md.append(f"| `{ext}` | {count} |")
        
        return '\n'.join(md)
    
    def save_results(self, structure: RepositoryStructure):
        """Save results to files."""
        output_dir = self.root / '.codex' / 'repository_structure'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_file = output_dir / 'folder_structure.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            # Convert to serializable format
            data = {
                'metadata': {
                    'root_path': structure.root_path,
                    'total_folders': structure.total_folders,
                    'total_files': structure.total_files,
                    'total_size_bytes': structure.total_size_bytes,
                    'scan_date': structure.scan_date,
                },
                'folders': {
                    path: asdict(info) 
                    for path, info in structure.folders.items()
                },
                'orphaned_folders': structure.orphaned_folders,
                'undocumented_folders': structure.undocumented_folders,
            }
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved JSON: {json_file}")
        
        # Save Markdown
        md_file = output_dir / 'FOLDER_STRUCTURE.md'
        md_content = self.generate_markdown(structure)
        md_file.write_text(md_content, encoding='utf-8')
        
        print(f"📝 Saved Markdown: {md_file}")
        
        # Save tree
        tree_file = output_dir / 'folder_tree.txt'
        tree_file.write_text(structure.folder_tree, encoding='utf-8')
        
        print(f"🌳 Saved tree: {tree_file}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Map repository folder structure'
    )
    parser.add_argument(
        '--root',
        type=Path,
        default=Path('.'),
        help='Repository root path'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output directory (default: .codex/repository_structure)'
    )
    
    args = parser.parse_args()
    
    mapper = FolderMapper(args.root.resolve())
    structure = mapper.map_repository()
    mapper.save_results(structure)
    
    print("\n✅ Repository folder structure mapping complete!")
    print(f"📁 Results saved to: .codex/repository_structure/")

if __name__ == '__main__':
    main()
```

**Usage**:
```bash
# Map entire repository
python scripts/analysis/map_folder_structure.py

# Map specific directory
python scripts/analysis/map_folder_structure.py --root ./docs

# Custom output location
python scripts/analysis/map_folder_structure.py --output ./reports
```

**Output Files**:
1. `.codex/repository_structure/folder_structure.json` - Machine-readable structure data
2. `.codex/repository_structure/FOLDER_STRUCTURE.md` - Human-readable documentation
3. `.codex/repository_structure/folder_tree.txt` - ASCII tree visualization

**Acceptance Criteria**:
- [ ] Scans entire repository structure
- [ ] Identifies all folders and their purposes
- [ ] Generates clickable index in markdown
- [ ] Creates ASCII tree visualization
- [ ] Identifies orphaned/undocumented folders
- [ ] Exports to JSON and Markdown formats
- [ ] Runs in < 30 seconds for typical repository
- [ ] Respects .gitignore patterns

---

### Task 5: Integrate with Cognitive Brain (Priority: MEDIUM)

**Objective**: Add data integrity and structure mapping capabilities to cognitive brain

**Requirements**:
1. Update `.github/agents/core/cognitive_brain.py`
2. Add `DataIntegrityValidator` component
3. Add `RepositoryStructureAnalyzer` component
4. Integrate with self-improvement engine
5. Add automated quality checks

**Deliverables**:
```python
# .github/agents/core/cognitive_brain.py (additions)

class DataIntegrityValidator:
    """Validates data integrity across repository."""
    
    def __init__(self):
        self.validators = [
            TimestampValidator(),
            MetadataValidator(),
            FormatValidator(),
        ]
    
    def validate_all(self) -> Dict[str, List[str]]:
        """Run all validators."""
        issues = {}
        for validator in self.validators:
            validator_issues = validator.validate()
            if validator_issues:
                issues[validator.name] = validator_issues
        return issues
    
    def auto_fix(self, issues: Dict[str, List[str]]) -> Dict[str, int]:
        """Attempt to auto-fix issues."""
        fixed = {}
        for validator_name, validator_issues in issues.items():
            validator = next(v for v in self.validators if v.name == validator_name)
            count = validator.auto_fix(validator_issues)
            fixed[validator_name] = count
        return fixed

class RepositoryStructureAnalyzer:
    """Analyzes repository structure."""
    
    def __init__(self):
        self.mapper = FolderMapper(Path('.'))
    
    def analyze(self) -> RepositoryStructure:
        """Analyze repository structure."""
        return self.mapper.map_repository()
    
    def identify_issues(self, structure: RepositoryStructure) -> List[str]:
        """Identify structure issues."""
        issues = []
        
        if structure.orphaned_folders:
            issues.append(f"{len(structure.orphaned_folders)} folders without README")
        
        if structure.undocumented_folders:
            issues.append(f"{len(structure.undocumented_folders)} folders without purpose")
        
        # Check for deep nesting
        max_depth = max(info.depth for info in structure.folders.values())
        if max_depth > 6:
            issues.append(f"Deep folder nesting detected: {max_depth} levels")
        
        return issues
    
    def suggest_improvements(self, structure: RepositoryStructure) -> List[str]:
        """Suggest structure improvements."""
        suggestions = []
        
        # Suggest README additions
        for path in structure.orphaned_folders[:5]:
            suggestions.append(f"Add README to {path}")
        
        # Suggest consolidation
        small_folders = [
            path for path, info in structure.folders.items()
            if info.file_count <= 2 and info.subfolder_count == 0
        ]
        if len(small_folders) > 10:
            suggestions.append(f"Consider consolidating {len(small_folders)} small folders")
        
        return suggestions
```

**Acceptance Criteria**:
- [ ] Data integrity validator integrated
- [ ] Structure analyzer integrated
- [ ] Auto-fix capabilities functional
- [ ] Suggestions generated automatically
- [ ] Tests passing with 100% coverage

---

## 📊 Progress Tracking

### Task Status Matrix

| Task | Priority | Status | Assignee | ETA |
|------|----------|--------|----------|-----|
| CI Timestamp Validation | HIGH | 🔵 Not Started | Copilot | Week 1 |
| Markdown Metadata Linting | HIGH | 🔵 Not Started | Copilot | Week 1 |
| Bulk Replacement Safeguards | HIGH | 🔵 Not Started | Copilot | Week 1 |
| Folder Structure Mapping | MEDIUM | 🔵 Not Started | Copilot | Week 2 |
| Cognitive Brain Integration | MEDIUM | 🔵 Not Started | Copilot | Week 2-3 |

### Milestones

- **Week 1**: Complete all HIGH priority tasks
- **Week 2**: Complete MEDIUM priority tasks
- **Week 3**: Testing, documentation, and deployment

---

## 🎯 Success Metrics

### Quantitative Metrics

- ✅ 100% test coverage maintained
- ✅ CI pipeline passes all checks
- ✅ Zero regression in existing functionality
- ✅ All timestamps validated automatically
- ✅ Complete folder structure documented

### Qualitative Metrics

- ✅ Improved documentation quality
- ✅ Better repository understanding
- ✅ Reduced risk of future overcorrections
- ✅ Enhanced cognitive brain capabilities
- ✅ Team confidence in automation

---

## 🔄 PDA Loop Integration

### Plan Phase
- [x] Identify data integrity issues
- [x] Design validation solutions
- [x] Plan folder structure mapping
- [x] Define integration approach

### Do Phase
- [ ] Implement CI validation
- [ ] Implement metadata linting
- [ ] Create safe replacement tool
- [ ] Build folder mapper
- [ ] Integrate with cognitive brain

### Analyze Phase
- [ ] Run all validators
- [ ] Review folder structure
- [ ] Identify patterns
- [ ] Generate insights
- [ ] Update cognitive brain

---

## 🏷️ AfterMath Tag Integration

All work in this phase should be tagged for AfterMath processing:

```yaml
aftermath_tags:
  - data_integrity
  - timestamp_validation
  - folder_structure
  - cognitive_brain_v11
  - automation_safeguards
```

Session artifacts will be stored in:
- `.codex/sessions/phase_11_1/`
- `.codex/repository_structure/`
- `scripts/validation/`
- `scripts/analysis/`

---

## 📚 References

- Parent Status: `.github/agents/COGNITIVE_BRAIN_STATUS_V11_2025_TIMESTAMP_CORRECTIONS.md`
- CI Testing Agent: `.github/agents/ci-testing-agent/`
- Previous Phases: `.github/agents/COGNITIVE_BRAIN_STATUS_V9_COMPLETE.md`
- Repository Guidelines: `AGENTS.md`

---

## 🚀 Getting Started

1. **Review this document thoroughly**
2. **Check out branch from PR #2713**
3. **Start with Task 1 (CI Timestamp Validation)**
4. **Use TDD approach - tests first**
5. **Run validation after each task**
6. **Report progress frequently**
7. **Update cognitive brain status**

---

## ⚠️ Important Notes

- **Do not skip validation**: Every change must pass CI
- **Preserve existing functionality**: Zero regression tolerance
- **Follow PDA loop**: Plan → Do → Analyze for each task
- **Tag for AfterMath**: All sessions must be tagged
- **Document learnings**: Update cognitive brain with insights
- **Test thoroughly**: 100% coverage required

---

**Status**: READY FOR EXECUTION  
**Next Action**: Begin Task 1 - CI Timestamp Validation  
**Contact**: @mbaetiong for questions or clarifications

---

*End of Continuation Prompt*

---

## 📋 ADDENDUM: Complete Folder Links List

### Additional Requirement: Generate Simple Folder Links List

**Objective**: Create a comprehensive, simple list of all folder paths in the repository for quick reference and navigation.

**Output Format**: Plain text file with one folder path per line, relative to repository root.

**Implementation**:

```python
# scripts/analysis/list_all_folders.py
"""
Simple script to list all folder paths in the repository.
Outputs a plain text file with one folder path per line.
"""

from pathlib import Path
import sys

IGNORE_PATTERNS = {
    '.git', '.venv', 'node_modules', '__pycache__', 
    '.pytest_cache', '.hypothesis', 'dist', 'build',
    '.mypy_cache', '.tox', 'htmlcov', '.eggs'
}

def should_ignore(path: Path) -> bool:
    """Check if path should be ignored."""
    parts = path.parts
    return any(pattern in parts for pattern in IGNORE_PATTERNS)

def list_all_folders(root: Path) -> list[str]:
    """Get list of all folders in repository."""
    folders = []
    
    # Add root
    folders.append('.')
    
    # Find all subdirectories
    for item in sorted(root.rglob('*')):
        if item.is_dir() and not should_ignore(item):
            rel_path = item.relative_to(root)
            folders.append(str(rel_path))
    
    return sorted(folders)

def generate_markdown_links(folders: list[str], root: Path) -> str:
    """Generate markdown with clickable folder links."""
    lines = []
    lines.append("# Repository Folder Links")
    lines.append(f"\nTotal Folders: {len(folders)}\n")
    lines.append("---\n")
    lines.append("## All Folders (Alphabetical)\n")
    
    for folder in folders:
        # Create relative link
        if folder == '.':
            lines.append(f"- [`.` (root)](./)")
        else:
            lines.append(f"- [`{folder}`](./{folder})")
    
    return '\n'.join(lines)

def generate_categorized_links(folders: list[str]) -> str:
    """Generate categorized folder links."""
    lines = []
    lines.append("# Repository Folder Links (Categorized)")
    lines.append(f"\nTotal Folders: {len(folders)}\n")
    lines.append("---\n")
    
    # Categorize by top-level directory
    categories = {}
    for folder in folders:
        if folder == '.':
            categories.setdefault('root', []).append(folder)
        else:
            parts = folder.split('/')
            top_level = parts[0]
            categories.setdefault(top_level, []).append(folder)
    
    for category in sorted(categories.keys()):
        lines.append(f"\n## {category.upper()}\n")
        for folder in sorted(categories[category]):
            if folder == '.':
                lines.append(f"- [`.` (root)](./)")
            else:
                lines.append(f"- [`{folder}`](./{folder})")
    
    return '\n'.join(lines)

def generate_tree_with_links(folders: list[str], max_depth: int = 10) -> str:
    """Generate tree structure with links."""
    lines = []
    lines.append("# Repository Folder Tree (with Links)")
    lines.append(f"\nTotal Folders: {len(folders)}\n")
    lines.append("---\n")
    
    # Build tree structure
    tree = {}
    for folder in folders:
        if folder == '.':
            continue
        parts = folder.split('/')
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    
    def render_tree(node: dict, prefix: str = "", path: str = ".", depth: int = 0):
        if depth > max_depth:
            return
        
        items = sorted(node.items())
        for i, (name, children) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            current_path = f"{path}/{name}" if path != "." else name
            
            # Add link
            lines.append(f"{prefix}{connector}[`{name}`](./{current_path})")
            
            if children:
                child_prefix = prefix + ("    " if is_last else "│   ")
                render_tree(children, child_prefix, current_path, depth + 1)
    
    lines.append("[`.` (root)](./)\n")
    render_tree(tree)
    
    return '\n'.join(lines)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='List all folders in repository'
    )
    parser.add_argument(
        '--root',
        type=Path,
        default=Path('.'),
        help='Repository root path'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('.codex/repository_structure'),
        help='Output directory'
    )
    parser.add_argument(
        '--format',
        choices=['plain', 'markdown', 'categorized', 'tree', 'all'],
        default='all',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    root = args.root.resolve()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Scanning folders in: {root}")
    folders = list_all_folders(root)
    print(f"✅ Found {len(folders)} folders")
    
    # Generate outputs based on format
    if args.format in ['plain', 'all']:
        # Plain text list
        plain_file = output_dir / 'ALL_FOLDERS.txt'
        plain_file.write_text('\n'.join(folders), encoding='utf-8')
        print(f"📝 Saved plain list: {plain_file}")
    
    if args.format in ['markdown', 'all']:
        # Markdown with links
        md_file = output_dir / 'ALL_FOLDERS_LINKS.md'
        md_content = generate_markdown_links(folders, root)
        md_file.write_text(md_content, encoding='utf-8')
        print(f"📝 Saved markdown links: {md_file}")
    
    if args.format in ['categorized', 'all']:
        # Categorized markdown
        cat_file = output_dir / 'ALL_FOLDERS_CATEGORIZED.md'
        cat_content = generate_categorized_links(folders)
        cat_file.write_text(cat_content, encoding='utf-8')
        print(f"📝 Saved categorized links: {cat_file}")
    
    if args.format in ['tree', 'all']:
        # Tree with links
        tree_file = output_dir / 'ALL_FOLDERS_TREE.md'
        tree_content = generate_tree_with_links(folders)
        tree_file.write_text(tree_content, encoding='utf-8')
        print(f"📝 Saved tree with links: {tree_file}")
    
    print(f"\n✅ Complete! All outputs saved to: {output_dir}/")
    print(f"\nGenerated files:")
    if args.format in ['plain', 'all']:
        print(f"  - ALL_FOLDERS.txt (plain text list)")
    if args.format in ['markdown', 'all']:
        print(f"  - ALL_FOLDERS_LINKS.md (alphabetical with links)")
    if args.format in ['categorized', 'all']:
        print(f"  - ALL_FOLDERS_CATEGORIZED.md (grouped by top-level)")
    if args.format in ['tree', 'all']:
        print(f"  - ALL_FOLDERS_TREE.md (tree structure with links)")

if __name__ == '__main__':
    main()
```

**Usage Examples**:

```bash
# Generate all formats (default)
python scripts/analysis/list_all_folders.py

# Generate only plain text list
python scripts/analysis/list_all_folders.py --format plain

# Generate only markdown with links
python scripts/analysis/list_all_folders.py --format markdown

# Generate categorized list
python scripts/analysis/list_all_folders.py --format categorized

# Generate tree structure
python scripts/analysis/list_all_folders.py --format tree

# Custom output location
python scripts/analysis/list_all_folders.py --output-dir ./reports/folders
```

**Output Files**:

1. **`ALL_FOLDERS.txt`** - Simple plain text list:
   ```
   .
   .codex
   .codex/archive
   .codex/cognitive_brain
   .codex/plans
   .codex/prompts
   .codex/reports
   ...
   ```

2. **`ALL_FOLDERS_LINKS.md`** - Markdown with clickable links:
   ```markdown
   # Repository Folder Links
   
   Total Folders: 250
   
   ---
   
   ## All Folders (Alphabetical)
   
   - [`.` (root)](./)
   - [`.codex`](./.codex)
   - [`.codex/archive`](./.codex/archive)
   - [`.codex/cognitive_brain`](./.codex/cognitive_brain)
   ...
   ```

3. **`ALL_FOLDERS_CATEGORIZED.md`** - Grouped by top-level directory:
   ```markdown
   # Repository Folder Links (Categorized)
   
   ## .CODEX
   
   - [`.codex`](./.codex)
   - [`.codex/archive`](./.codex/archive)
   - [`.codex/cognitive_brain`](./.codex/cognitive_brain)
   
   ## .GITHUB
   
   - [`.github`](./.github)
   - [`.github/actions`](./.github/actions)
   - [`.github/agents`](./.github/agents)
   ...
   ```

4. **`ALL_FOLDERS_TREE.md`** - Tree structure with links:
   ```markdown
   # Repository Folder Tree (with Links)
   
   [`.` (root)](./)
   
   ├── [`.codex`](./.codex)
   │   ├── [`archive`](./.codex/archive)
   │   ├── [`cognitive_brain`](./.codex/cognitive_brain)
   │   └── [`plans`](./.codex/plans)
   ├── [`.github`](./.github)
   │   ├── [`actions`](./.github/actions)
   │   └── [`agents`](./.github/agents)
   ...
   ```

**Quick Reference Command**:

```bash
# Run immediately to get all folder lists
python scripts/analysis/list_all_folders.py && \
  echo "Results available at:" && \
  ls -lh .codex/repository_structure/ALL_FOLDERS*
```

**Integration with Task 4**:

The folder structure mapper (`map_folder_structure.py`) will now also call `list_all_folders.py` automatically to generate all four list formats as part of the comprehensive mapping process.

**Acceptance Criteria**:
- [ ] Generates plain text list of all folders
- [ ] Creates markdown with clickable GitHub links
- [ ] Groups folders by top-level directory
- [ ] Creates tree structure with links
- [ ] Ignores standard directories (.git, .venv, etc.)
- [ ] Runs in < 5 seconds
- [ ] Output files are properly formatted
- [ ] Links work in GitHub UI

