# Phase 8: CLI & Workflow Integration

**Status**: Pending Phase 7 Completion  
**Dependencies**: Phase 1-7  
**Estimated Time**: 2-3 hours  
**Branch**: `copilot/fix-strict-conflicts-detected`

---

## 🎯 Objective

Create comprehensive CLI and integrate with GitHub Actions:
- Full-featured command-line interface
- Configuration file support
- GitHub Actions workflow
- Integration with nightly audit
- Progress reporting and logging

---

## 📋 Tasks

### Task 8.1: Comprehensive CLI

**File**: `scripts/analysis/cli.py`

**Requirements**:
- Use argparse or click for CLI
- Support all detection modes
- Configuration file option
- Output directory option
- Progress indicators
- Verbose/quiet modes
- Filtering options
- Exit codes for CI integration

**CLI Interface**:
```bash
python scripts/analysis/cli.py [REPO_PATH] [OPTIONS]

Options:
  --output-dir PATH           Output directory (default: ./duplicate_analysis)
  --modes MODE[,MODE]         Detection modes: exact,normalized,ast,semantic (default: all)
  --config FILE               Configuration file path
  --threshold FLOAT           Similarity threshold (default: 0.75)
  --exclude PATTERN           Exclude patterns (can be repeated)
  --include-intentional       Include intentional duplicates in output
  --no-git                    Skip git integration
  --verbose, -v               Verbose output
  --quiet, -q                 Quiet mode (errors only)
  --format FORMAT             Output format: yaml,json,csv,all (default: all)
  --report-only               Generate markdown report only
  --help, -h                  Show help message
```

**Enhanced Implementation**:
```python
def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive duplicate detection for codebases"
    )
    # Add all arguments
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config) if args.config else {}
    
    # Initialize scanner
    scanner = DuplicateScanner(args.repo_path, config)
    
    # Run scan with progress
    with Progress() as progress:
        inventory = scanner.scan(modes=args.modes)
    
    # Write outputs
    scanner.write_outputs(inventory, args.output_dir)
    
    # Exit with appropriate code
    sys.exit(0 if inventory.metadata.total_violations == 0 else 1)
```

### Task 8.2: Configuration File Support

**File**: `scripts/analysis/config.py`

**Requirements**:
- YAML configuration file format
- Override CLI defaults
- Support all options
- Include/exclude patterns
- Detection thresholds
- Output preferences

**Config File Format** (`.duplicate-scan.yml`):
```yaml
# Duplicate detection configuration
scan:
  modes:
    - exact
    - normalized
    - ast
    - semantic
  
  thresholds:
    normalized: 1.0
    ast: 0.85
    semantic: 0.75
  
  exclude_patterns:
    - "*.min.js"
    - "vendor/**"
    - "node_modules/**"
    - ".git/**"
  
  include_dirs:
    - "src/"
    - "scripts/"
    - "lib/"
  
output:
  directory: "./duplicate_analysis"
  formats:
    - yaml
    - json
    - csv
    - markdown
  include_intentional: false
  
git:
  enabled: true
  churn_window_days: 90
  
shim:
  inventory_path: ".github/SHIM_INVENTORY.yaml"
  cross_reference: true
```

**Interface**:
```python
class Config:
    """Configuration manager."""
    
    @staticmethod
    def load(path: Path) -> Dict:
        """Load configuration from file."""
        pass
    
    @staticmethod
    def merge(config: Dict, args: argparse.Namespace) -> Dict:
        """Merge config file with CLI args (CLI wins)."""
        pass
    
    @staticmethod
    def validate(config: Dict) -> List[str]:
        """Validate configuration, return errors."""
        pass
```

### Task 8.3: Progress Reporting

**File**: `scripts/analysis/progress.py`

**Requirements**:
- Show scanning progress
- Display file count
- Show current file being processed
- Estimate time remaining
- Work in both verbose and quiet modes
- Use tqdm or similar for progress bars

**Interface**:
```python
class ProgressReporter:
    """Reports scan progress."""
    
    def __init__(self, verbose: bool = False):
        """Initialize reporter."""
        pass
    
    def start_scan(self, total_files: int):
        """Start progress tracking."""
        pass
    
    def update(self, current_file: Path):
        """Update progress."""
        pass
    
    def finish(self):
        """Finish progress reporting."""
        pass
```

### Task 8.4: GitHub Actions Workflow

**File**: `.github/workflows/duplicate-detection.yml`

**Requirements**:
- Scheduled daily/weekly run
- Manual trigger option
- Run duplicate scanner
- Upload artifacts
- Comment on PRs if new duplicates
- Fail if violations exceed threshold

**Workflow**:
```yaml
name: Duplicate Detection Scan

on:
  schedule:
    - cron: '0 3 * * 0'  # Weekly on Sunday at 3 AM UTC
  workflow_dispatch:
    inputs:
      modes:
        description: 'Detection modes (comma-separated)'
        required: false
        default: 'exact,normalized'

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
      
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git metrics
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      
      - name: Install dependencies
        run: |
          pip install pyyaml gitpython
          # Install any other dependencies
      
      - name: Run duplicate detection
        run: |
          python scripts/analysis/cli.py . \
            --output-dir duplicate_analysis \
            --modes ${{ github.event.inputs.modes || 'exact,normalized' }} \
            --format all
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: duplicate-analysis-${{ github.run_id }}
          path: duplicate_analysis/
      
      - name: Check for new violations
        id: check
        run: |
          # Parse output and check for new violations
          python scripts/analysis/check_violations.py
      
      - name: Create issue if violations found
        if: steps.check.outputs.has_violations == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            // Create issue with violation details
            const fs = require('fs');
            const report = fs.readFileSync('duplicate_analysis/supplemental_duplicates.md', 'utf8');
            
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `[Duplicate Detection] New violations found - ${new Date().toISOString().split('T')[0]}`,
              body: report,
              labels: ['duplicate-detection', 'automated']
            });
```

### Task 8.5: Integration with Nightly Audit

**File**: `.github/workflows/nightly-audit.yml` (update)

**Requirements**:
- Add duplicate detection step
- Run after existing checks
- Upload combined artifacts
- Include in audit report

**Integration**:
```yaml
- name: Run duplicate detection
  run: |
    python scripts/analysis/cli.py . \
      --output-dir audit_artifacts/duplicates \
      --modes exact,normalized \
      --quiet
  
- name: Combine audit artifacts
  run: |
    # Merge duplicate detection results into audit report
```

---

## 🧪 Testing Requirements

### Test 8.1: CLI Tests

**File**: `tests/analysis/test_cli.py`

**Test Cases**:
- `test_cli_help` - Help message displays
- `test_cli_defaults` - Default options work
- `test_cli_modes` - Mode selection works
- `test_cli_output_dir` - Output directory created
- `test_cli_config_file` - Config file loaded
- `test_cli_exit_codes` - Correct exit codes

### Test 8.2: Config Tests

**File**: `tests/analysis/test_config.py`

**Test Cases**:
- `test_load_config` - Config file parsed
- `test_config_validation` - Invalid config rejected
- `test_cli_override` - CLI args override config
- `test_default_config` - Defaults work

### Test 8.3: Workflow Tests

**File**: `tests/analysis/test_workflow.py`

**Test Cases**:
- `test_workflow_syntax` - YAML syntax valid
- `test_workflow_steps` - All steps present
- `test_artifact_upload` - Artifacts configured

---

## ✅ Acceptance Criteria

- [ ] CLI fully functional with all options
- [ ] Configuration file support working
- [ ] Progress reporting implemented
- [ ] GitHub Actions workflow created
- [ ] Integration with nightly audit complete
- [ ] Exit codes appropriate for CI
- [ ] All tests passing
- [ ] Documentation complete (README, help text)
- [ ] Code formatted and linted

---

## 🔄 Self-Healing Checklist

1. [ ] Run: `pytest tests/analysis/test_cli.py -v`
2. [ ] Run: `pytest tests/analysis/test_config.py -v`
3. [ ] Run: `python scripts/analysis/cli.py --help`
4. [ ] Test: `python scripts/analysis/cli.py . --modes exact --output-dir /tmp/test`
5. [ ] Test with config file
6. [ ] Validate workflow YAML syntax
7. [ ] Run code_review tool
8. [ ] Address any issues
9. [ ] Commit with report_progress

---

## 📝 Notes

- CLI should be user-friendly and well-documented
- Configuration files reduce command-line complexity
- GitHub Actions integration enables automation
- Exit codes are critical for CI/CD integration

---

## 🔗 Next Phase

**Phase 9: Documentation & Examples** (`09_documentation.md`)
