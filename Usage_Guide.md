# Space Traversal Audit System - Usage Guide

**Roles:** [Audit Orchestrator], [Capability Cartographer]  
**Energy:** 5  
**Version:** 1.1.0

> **NOTE:** For technical workflow details and formulas, see `Traversal_Workflow.md`

## Table of Contents
1. [Quick Start](#1-quick-start)
2. [Key Commands](#2-key-commands)
3. [Configuration](#3-configuration-workflowyaml)
4. [Adding Detectors](#4-adding-detectors)
5. [Understanding Outputs](#5-understanding-outputs)
6. [Diff & Explain](#6-diff--explain)
7. [Quality Gates](#7-quality-gates)
8. [Pre-Commit Workflow](#8-pre-commit-workflow)
9. [Troubleshooting](#9-troubleshooting)
10. [Advanced Usage](#10-advanced-usage)

## 1. Quick Start

### Prerequisites
- Python 3.8+
- Dependencies: `pip install pyyaml jinja2`

### First Run
```bash
# Full audit pipeline (all stages S1-S7)
python scripts/space_traversal/audit_runner.py run

# Or use Makefile shortcut
make space-audit
```

### What Gets Generated
```
audit_artifacts/
├── context_index.json           # S1: File inventory
├── facets.json                  # S2: Domain groupings
├── capabilities_raw.json        # S3: Detected capabilities
├── capabilities_scored.json     # S4: Scored with components
└── gaps.json                    # S5: Low-maturity capabilities

reports/
└── capability_matrix_<timestamp>.md  # S6: Human-readable report

audit_run_manifest.json          # S7: Integrity manifest
```

## 2. Key Commands

### Full Pipeline
```bash
# Python direct
python scripts/space_traversal/audit_runner.py run

# Makefile (recommended)
make space-audit
```
**Executes:** S1 → S2 → S3 → S4 → S5 → S6 → S7  
**Duration:** ~30-60 seconds on typical codebase  
**Output:** All artifacts, report, and manifest

### Fast Path (Skip S2, S5, S7)
```bash
make space-audit-fast
```
**Executes:** S1 → S3 → S4 → S6  
**Duration:** ~15-30 seconds  
**Use Case:** Quick iteration during development  
**Note:** No gaps.json or manifest generated

### Single Stage Execution
```bash
# Run specific stage
python scripts/space_traversal/audit_runner.py stage S4

# Examples for each stage
python scripts/space_traversal/audit_runner.py stage S1  # Index
python scripts/space_traversal/audit_runner.py stage S2  # Facets
python scripts/space_traversal/audit_runner.py stage S3  # Capabilities
python scripts/space_traversal/audit_runner.py stage S4  # Scoring
python scripts/space_traversal/audit_runner.py stage S5  # Gaps
python scripts/space_traversal/audit_runner.py stage S6  # Render
python scripts/space_traversal/audit_runner.py stage S7  # Manifest
```
**Requirements:** Previous stages' outputs must exist  
**Use Case:** Re-run specific stage after configuration change

### Explain Capability Score
```bash
# Python direct
python scripts/space_traversal/audit_runner.py explain checkpointing

# Makefile with parameter
make space-explain cap=logging-tracking
```
**Output:**
```
Explain: checkpointing
  functionality  value=0.8750 weight=0.250 contribution=0.2188
  consistency    value=0.6667 weight=0.200 contribution=0.1333
  tests          value=0.5000 weight=0.250 contribution=0.1250
  safeguards     value=0.4545 weight=0.150 contribution=0.0682
  documentation  value=0.6000 weight=0.150 contribution=0.0900
  Total score: 0.6353
```

### Compare Two Audit Runs (Diff)
```bash
# Python direct
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/capabilities_scored_baseline.json \
  --new audit_artifacts/capabilities_scored.json

# Makefile with parameters
make space-diff old=scored_baseline.json new=scored_current.json
```
**Output (CSV format):**
```
ID,OLD,NEW,DELTA
checkpointing,0.6353,0.6800,+0.0447
logging-tracking,0.7200,0.6950,-0.0250
tokenization,0.8100,0.8100,+0.0000
```
**Exit Codes:**
- 0: No regressions
- 3: Score regression exceeds threshold (if `fail_on_score_regression: true`)

### Cleanup
```bash
make space-clean
```
**Removes:**
- `audit_artifacts/` directory
- `audit_run_manifest.json`
- `reports/capability_matrix_*.md`
- `reports/codex_status_update_*.md`

## 3. Configuration (workflow.yaml)

### Location
`.copilot-space/workflow.yaml`

### Structure

#### Basic Info
```yaml
version: 1.4.0    # Specification version
```

#### Stage Definitions
```yaml
stages:
  - id: index
    script: audit_runner.py
    entry: stage
    args: ["S1"]
  # ... S2-S7 similarly defined
```
**Note:** Rarely needs modification unless adding custom stages

#### Component Weights
```yaml
weights:
  functionality: 0.25   # Pattern coverage
  consistency: 0.20     # Code duplication
  tests: 0.25           # Test depth
  safeguards: 0.15      # Security keywords
  documentation: 0.15   # Doc coverage
```
**Rules:**
- Must sum to 1.0 (auto-normalized with warning if not)
- All values must be ≥ 0
- Higher weight = more important to final score

**Example Adjustment (prioritize tests):**
```yaml
weights:
  functionality: 0.20
  consistency: 0.15
  tests: 0.35        # Increased from 0.25
  safeguards: 0.15
  documentation: 0.15
```

#### Scoring Thresholds
```yaml
scoring:
  thresholds:
    low: 0.70      # Below this = gap (needs remediation)
    medium: 0.85   # Informational (not enforced)
```
**Use Cases:**
- `low`: CI/CD gate threshold
- `medium`: Stretch goal for high-quality capabilities

#### Duplication Heuristic
```yaml
scoring:
  dup:
    heuristic: simple  # or "token_similarity"
```
**Options:**
- `simple`: File stem counting (default, fast)
- `token_similarity`: Token-level comparison (experimental, requires dup_similarity.py)

#### Capability Map
```yaml
capability_map:
  dynamic: true    # Enable detector auto-discovery
  overrides:
    training-engine: ["train_loop", "functional_training"]
    mcp-protocol-surface: ["FastAPI", "jsonrpc", "endpoint"]
    # Add custom aliases here
```
**dynamic:** When `true`, loads detectors from `scripts/space_traversal/detectors/`  
**overrides:** Synonym lists for capability pattern matching

#### Output Paths
```yaml
output:
  reports_dir: reports
  artifacts_dir: audit_artifacts
  matrix_template: templates/audit/capability_matrix.md.j2
```
**Customization:** Change paths to organize outputs differently

#### Quality Gates
```yaml
options:
  fail_on_score_regression: true      # Diff fails on score drops
  regression_delta_threshold: 0.02    # Max allowed drop
  fail_on_low_maturity: true          # Fail if any score < low threshold
  fail_on_missing_detector: true      # Fail if override ID not found
```
**CI/CD Integration:** Set to `true` for strict gates, `false` for informational runs

#### Safeguard Keywords
```yaml
safeguards:
  keywords:
    - sha256
    - checksum
    - rng
    - seed
    - offline
    - WANDB_MODE
    - confirm
    - dry_run
    - RateLimitExceeded
    - Unauthorized
    - ValidationError
```
**Customization:** Add project-specific security/reproducibility keywords

### Editing Best Practices
1. **Backup:** `cp .copilot-space/workflow.yaml{,.bak}`
2. **Validate:** `python -c "import yaml; yaml.safe_load(open('.copilot-space/workflow.yaml'))"`
3. **Test:** Run `make space-audit-fast` after changes
4. **Review warnings:** Check `audit_run_manifest.json` for issues

### Common Configurations

#### Strict CI/CD Gate
```yaml
options:
  fail_on_score_regression: true
  regression_delta_threshold: 0.01    # Very strict
  fail_on_low_maturity: true
  fail_on_missing_detector: true

scoring:
  thresholds:
    low: 0.80    # Higher bar
```

#### Permissive Development
```yaml
options:
  fail_on_score_regression: false
  fail_on_low_maturity: false
  fail_on_missing_detector: false

scoring:
  thresholds:
    low: 0.60    # Lower bar for exploration
```

## 4. Adding Detectors

### Detector File Structure
Create `scripts/space_traversal/detectors/<capability_id>.py`:

```python
"""
Detector for <capability_name> capability.

Identifies evidence of <what this capability does>.
"""

def detect(file_index: dict) -> dict:
    """
    Detect <capability_name> capability from file index.
    
    Args:
        file_index: Dict with 'files' list, each item:
                    {'path': str, 'ext': str, 'size': int, 'sha': str}
    
    Returns:
        Dict with required fields:
        {
            "id": "capability-kebab-case",
            "evidence_files": [str, ...],     # Sorted relative paths
            "found_patterns": [str, ...],     # Sorted detected patterns
            "required_patterns": [str, ...],  # Expected patterns list
            "meta": {}                        # Optional metadata
        }
    """
    evidence_files = []
    found_patterns = []
    required_patterns = ["pattern1", "pattern2", "pattern3"]
    
    # Example: Filter Python files in specific directory
    for file_meta in file_index["files"]:
        if file_meta["ext"] == ".py" and file_meta["path"].startswith("src/my_module/"):
            evidence_files.append(file_meta["path"])
            
            # Optional: Lazy load content for pattern matching
            # (be mindful of performance)
    
    # Detect patterns in evidence files
    for pattern in required_patterns:
        if any(pattern in f for f in evidence_files):
            found_patterns.append(pattern)
    
    return {
        "id": "my-new-capability",
        "evidence_files": sorted(set(evidence_files)),
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": required_patterns,
        "meta": {"detector_version": "1.0", "notes": "Initial implementation"}
    }
```

### Step-by-Step Guide

#### Step 1: Create Detector File
```bash
# Create new detector
touch scripts/space_traversal/detectors/my_capability.py

# Edit with your favorite editor
vim scripts/space_traversal/detectors/my_capability.py
```

#### Step 2: Implement Detector Logic
Use template above, filling in:
- **id:** Unique kebab-case identifier
- **evidence_files:** List of relevant file paths
- **found_patterns:** Patterns detected in codebase
- **required_patterns:** Patterns expected for full implementation
- **meta:** Optional metadata (version, notes, etc.)

#### Step 3: Test Import
```bash
python -c "
from scripts.space_traversal.detectors import my_capability
import json
# Minimal test
result = my_capability.detect({'files': []})
print(json.dumps(result, indent=2))
"
```

#### Step 4: Run Capability Extraction
```bash
python scripts/space_traversal/audit_runner.py stage S3
```
**Check output:**
```bash
jq '.capabilities[] | select(.id=="my-capability")' audit_artifacts/capabilities_raw.json
```

#### Step 5: Score the Capability
```bash
python scripts/space_traversal/audit_runner.py stage S4
```
**Inspect score:**
```bash
python scripts/space_traversal/audit_runner.py explain my-capability
```

#### Step 6: Full Pipeline
```bash
make space-audit
```
**Verify in report:**
```bash
# Find capability in markdown report
grep "my-capability" reports/capability_matrix_*.md
```

### Detector Examples

#### Example 1: Simple Path Filter
```python
def detect(file_index):
    """Detect MCP protocol surface capability."""
    mcp_files = [
        f["path"] for f in file_index["files"]
        if f["path"].startswith("mcp/") and f["ext"] == ".py"
    ]
    
    found = []
    required = ["FastAPI", "jsonrpc", "endpoint"]
    # Pattern matching would go here
    
    return {
        "id": "mcp-protocol-surface",
        "evidence_files": sorted(mcp_files),
        "found_patterns": sorted(found),
        "required_patterns": required,
        "meta": {}
    }
```

#### Example 2: Content Matching
```python
from pathlib import Path

def detect(file_index):
    """Detect rate limiting capability."""
    repo_root = Path(__file__).resolve().parents[3]
    evidence = []
    found = set()
    required = ["RateLimiter", "throttle", "rate_limit"]
    
    for f in file_index["files"]:
        if f["ext"] == ".py":
            try:
                content = (repo_root / f["path"]).read_text(
                    encoding="utf-8", errors="ignore"
                )[:200_000]  # Truncate for determinism
                
                for pattern in required:
                    if pattern in content:
                        found.add(pattern)
                        if f["path"] not in evidence:
                            evidence.append(f["path"])
            except Exception:
                pass  # Defensive: skip unreadable files
    
    return {
        "id": "rate-limiting",
        "evidence_files": sorted(evidence),
        "found_patterns": sorted(found),
        "required_patterns": required,
        "meta": {"max_read_bytes": 200_000}
    }
```

#### Example 3: Multi-Directory Search
```python
def detect(file_index):
    """Detect testing infrastructure capability."""
    test_dirs = ["tests/", "test/", "testing/"]
    test_files = [
        f["path"] for f in file_index["files"]
        if any(f["path"].startswith(d) for d in test_dirs)
    ]
    
    # Check for test frameworks
    found = []
    required = ["pytest", "unittest", "coverage"]
    
    for pattern in required:
        if any(pattern in f for f in test_files):
            found.append(pattern)
    
    return {
        "id": "testing-infrastructure",
        "evidence_files": sorted(set(test_files)),
        "found_patterns": sorted(found),
        "required_patterns": required,
        "meta": {"test_dirs": test_dirs}
    }
```

### Detector Best Practices
- ✅ **Do:** Sort all list returns for determinism
- ✅ **Do:** Use `set()` to deduplicate before sorting
- ✅ **Do:** Truncate file reads to 200KB max
- ✅ **Do:** Handle exceptions defensively (skip bad files)
- ✅ **Do:** Use meaningful pattern names
- ❌ **Don't:** Make network calls
- ❌ **Don't:** Write to filesystem
- ❌ **Don't:** Depend on execution order of other detectors
- ❌ **Don't:** Use mutable global state

## 5. Understanding Outputs

### Artifact Files

#### context_index.json (S1)
```json
{
  "generated": 1700000000.0,
  "count": 1234,
  "version": "1.1.0",
  "files": [
    {
      "path": "src/main.py",
      "ext": ".py",
      "size": 5432,
      "sha": "abc123..."
    }
  ]
}
```
**Use:** File inventory snapshot, input to all other stages

#### facets.json (S2)
```json
{
  "generated": 1700000000.0,
  "version": "1.1.0",
  "facets": {
    "checkpoint": ["src/checkpoint.py", "tests/test_checkpoint.py"],
    "logging": ["src/logging.py", "docs/logging.md"]
  }
}
```
**Use:** Domain-grouped files, input to baseline capability rules

#### capabilities_raw.json (S3)
```json
{
  "generated": 1700000000.0,
  "version": "1.1.0",
  "capabilities": [
    {
      "id": "checkpointing",
      "evidence_files": ["src/checkpoint.py", "tests/test_checkpoint.py"],
      "found_patterns": ["save_checkpoint", "load"],
      "required_patterns": ["save_checkpoint", "load", "resume"]
    }
  ]
}
```
**Use:** Detected capabilities with pattern matches, input to scoring

#### capabilities_scored.json (S4)
```json
{
  "generated": 1700000000.0,
  "version": "1.1.0",
  "capabilities": [
    {
      "id": "checkpointing",
      "score": 0.6353,
      "components": {
        "functionality": 0.8750,
        "consistency": 0.6667,
        "tests": 0.5000,
        "safeguards": 0.4545,
        "documentation": 0.6000
      },
      "evidence_files": ["src/checkpoint.py", "tests/test_checkpoint.py"],
      "found_patterns": ["save_checkpoint", "load"]
    }
  ]
}
```
**Use:** Scored capabilities with component breakdowns, primary audit output

#### gaps.json (S5)
```json
{
  "generated": 1700000000.0,
  "version": "1.1.0",
  "low_maturity": [
    {
      "id": "safeguards",
      "score": 0.45,
      "components": {...}
    }
  ]
}
```
**Use:** Capabilities below threshold, prioritization for improvements

### Report Files

#### capability_matrix_<timestamp>.md (S6)
```markdown
# Capability Audit Report

Generated: 2025-11-19 12:34:56 UTC

## Capabilities

| ID | Score | Func | Cons | Test | Safe | Docs |
|----|-------|------|------|------|------|------|
| checkpointing | 0.635 | 0.875 | 0.667 | 0.500 | 0.455 | 0.600 |
| logging-tracking | 0.720 | 0.900 | 0.800 | 0.600 | 0.600 | 0.650 |

## Gaps (Low Maturity)

- safeguards (0.450)
- documentation (0.550)
```
**Use:** Human-readable audit summary for reports, PRs, documentation

### Manifest File

#### audit_run_manifest.json (S7)
```json
{
  "timestamp": 1700000000.0,
  "version": "1.1.0",
  "repo_root_sha": "def456...",
  "artifacts": [
    {"name": "context_index.json", "sha": "abc123..."},
    {"name": "capabilities_scored.json", "sha": "ghi789..."}
  ],
  "template_hash": "jkl012...",
  "weights": {
    "functionality": 0.25,
    "consistency": 0.20,
    "tests": 0.25,
    "safeguards": 0.15,
    "documentation": 0.15
  },
  "normalized_weights": {
    "functionality": 0.256,
    "consistency": 0.205,
    "tests": 0.256,
    "safeguards": 0.154,
    "documentation": 0.154
  },
  "warnings": ["weights_normalized_from:0.975"]
}
```
**Use:** Integrity chain, configuration snapshot, reproducibility verification

## 6. Diff & Explain

### Diff: Compare Two Runs

#### Use Cases
- Detect capability maturity regressions between branches
- Track improvements over time
- Validate refactoring didn't degrade capabilities

#### Workflow
```bash
# Baseline (e.g., main branch)
git checkout main
make space-audit
cp audit_artifacts/capabilities_scored.json baseline.json

# Feature branch
git checkout feature-branch
make space-audit

# Compare
python scripts/space_traversal/audit_runner.py diff \
  --old baseline.json \
  --new audit_artifacts/capabilities_scored.json
```

#### Output Format (CSV)
```
ID,OLD,NEW,DELTA
checkpointing,0.6353,0.6800,+0.0447
logging-tracking,0.7200,0.6950,-0.0250
tokenization,NA,0.8100,NA
safeguards,0.4500,NA,NA
```

#### Interpreting Results
- **Positive DELTA:** Capability improved ✅
- **Negative DELTA:** Capability regressed ⚠️
- **NA in OLD:** New capability added
- **NA in NEW:** Capability removed (detector disabled or renamed)

#### Exit Codes
- `0`: No regressions (or regressions within threshold)
- `3`: Score regression exceeds `regression_delta_threshold`

### Explain: Score Breakdown

#### Use Cases
- Understand why a capability has low score
- Identify which component needs improvement
- Debug unexpected score changes

#### Workflow
```bash
# Explain specific capability
python scripts/space_traversal/audit_runner.py explain checkpointing

# Or use Makefile
make space-explain cap=checkpointing
```

#### Output Format
```
Explain: checkpointing
  functionality  value=0.8750 weight=0.250 contribution=0.2188
  consistency    value=0.6667 weight=0.200 contribution=0.1333
  tests          value=0.5000 weight=0.250 contribution=0.1250
  safeguards     value=0.4545 weight=0.150 contribution=0.0682
  documentation  value=0.6000 weight=0.150 contribution=0.0900
  Total score: 0.6353
```

#### Interpreting Components
- **functionality (0.875):** 7 of 8 required patterns found → High ✅
- **consistency (0.667):** Some file duplication → Medium ⚠️
- **tests (0.500):** Half of evidence files have tests → Medium ⚠️
- **safeguards (0.455):** Only 5 of 11 keywords found → Low ❌
- **documentation (0.600):** Moderate doc coverage → Medium ⚠️

**Action Items from this example:**
1. Add missing safeguard keywords to codebase (biggest impact: 15% weight)
2. Add tests for untested modules (25% weight)
3. Reduce code duplication (20% weight)

#### Pro Tips
- Run explain on all gaps: `jq -r '.low_maturity[].id' audit_artifacts/gaps.json | xargs -I{} make space-explain cap={}`
- Compare explain output before/after changes to validate improvements
- Focus on high-weight, low-value components for maximum impact

## 7. Quality Gates

### Overview
Quality gates enforce minimum standards for capability maturity, preventing regressions.

### Gate Types

#### 1. Low Maturity Fail
**Configuration:**
```yaml
options:
  fail_on_low_maturity: true
scoring:
  thresholds:
    low: 0.70
```

**Behavior:**
- Non-zero exit if **any** capability score < 0.70
- Useful for CI/CD to block merging low-quality capabilities

**Example CI Integration:**
```bash
#!/bin/bash
set -e
make space-audit
# Exits non-zero if any capability < 0.70
```

#### 2. Score Regression Fail
**Configuration:**
```yaml
options:
  fail_on_score_regression: true
  regression_delta_threshold: 0.02
```

**Behavior:**
- `diff` command exits non-zero if any score drops > 0.02
- Prevents accidental capability degradation

**Example CI Integration:**
```bash
#!/bin/bash
# Baseline from main branch
git show main:audit_artifacts/capabilities_scored.json > baseline.json

# Current branch
make space-audit

# Diff with gate
python scripts/space_traversal/audit_runner.py diff \
  --old baseline.json \
  --new audit_artifacts/capabilities_scored.json
# Exits 3 if regression > 0.02
```

#### 3. Missing Detector Fail
**Configuration:**
```yaml
options:
  fail_on_missing_detector: true
capability_map:
  overrides:
    my-capability: ["alias1", "alias2"]
```

**Behavior:**
- Non-zero exit if any `overrides` ID not found in capabilities_raw.json
- Catches configuration drift (detector disabled but override remains)

#### 4. Hash Drift Warning
**Automatic:** Always computed in manifest

**Behavior:**
- `template_hash` field changes if `templates/audit/*.j2` files modified
- Warning in manifest if hash differs from previous run

**Action:**
- Review git diff for template files
- Regenerate baseline if templates intentionally changed
- Investigate if change was accidental

### Bypassing Gates (Development)
For local development iterations, temporarily disable gates:

```yaml
options:
  fail_on_score_regression: false
  fail_on_low_maturity: false
  fail_on_missing_detector: false
```

**Remember:** Re-enable before pushing to CI/CD pipeline!

### Custom Gates
To add custom gates:
1. Edit `audit_runner.py` (or create plugin)
2. Load condition from `workflow.yaml`
3. Check after relevant stage
4. Call `sys.exit(code)` on failure
5. Add warning to manifest

## 8. Pre-Commit Workflow

### Standard Checklist

#### 1. Run Full Audit
```bash
make space-audit
```
**Expected:** Completes successfully, no errors

#### 2. Check Warnings
```bash
jq '.warnings' audit_run_manifest.json
```
**Expected:** Empty array `[]` or acceptable warnings

**Common Warnings:**
- `"weights_normalized_from:0.98"` → Fix workflow.yaml weights to sum to 1.0

#### 3. Review Gaps
```bash
jq '.low_maturity[] | .id' audit_artifacts/gaps.json
```
**Expected:** No new gaps introduced by changes

**If gaps increased:**
- Run `make space-explain cap=<gap_id>` for each new gap
- Determine if gap is acceptable (e.g., new capability not yet fully implemented)
- Document in commit message if intentional

#### 4. Verify No Regressions
```bash
# Get baseline (e.g., from main branch)
git show main:audit_artifacts/capabilities_scored.json > /tmp/baseline.json

# Compare
make space-diff old=/tmp/baseline.json new=audit_artifacts/capabilities_scored.json
```
**Expected:** No negative deltas or deltas within acceptable threshold

**If regressions found:**
- Investigate with `make space-explain cap=<regressed_capability>`
- Fix issue or document intentional regression in commit message

#### 5. Add/Update Documentation
For new capabilities:
```bash
# Add documentation mentioning capability token
echo "## New Capability: my-feature" >> docs/features.md
echo "The my-feature capability enables..." >> docs/features.md
```

For detector changes:
```bash
# Update detector docstring
vim scripts/space_traversal/detectors/my_capability.py
```

#### 6. Test Detectors (if modified)
```bash
# Run detector tests
python -m pytest tests/space_traversal/ -v

# Or run full test suite
nox -s tests
```

#### 7. Update Configuration (if needed)
```bash
# Add capability override
vim .copilot-space/workflow.yaml

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.copilot-space/workflow.yaml'))"
```

#### 8. Commit Artifacts
```bash
# Add manifest and latest report
git add audit_run_manifest.json
git add reports/capability_matrix_$(ls -t reports/capability_matrix_* | head -1 | xargs basename)

# Or add all audit outputs
git add audit_run_manifest.json reports/
```

#### 9. Write Descriptive Commit Message
```bash
git commit -m "feat: Add MCP rate-limiting capability

- Implemented RateLimiter class in mcp/rate_limit.py
- Added rate_limiting detector
- Score: 0.75 (medium maturity)
- Gap in documentation addressed with docs/mcp/rate-limiting.md

Audit results:
- No regressions
- 1 new capability: mcp-rate-limiting
- Manifest warnings: none"
```

### Automated Pre-Commit Hook
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
set -e

echo "Running space traversal audit..."
make space-audit

echo "Checking for warnings..."
warnings=$(jq '.warnings | length' audit_run_manifest.json)
if [ "$warnings" -gt 0 ]; then
    echo "⚠️  Warnings found in manifest:"
    jq '.warnings' audit_run_manifest.json
    echo "Fix warnings before committing."
    exit 1
fi

echo "Checking for new gaps..."
gap_count=$(jq '.low_maturity | length' audit_artifacts/gaps.json)
echo "Gaps: $gap_count"

echo "✅ Audit passed!"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## 9. Troubleshooting

### Common Issues

#### Issue: "Missing dependencies. Install via: pip install pyyaml jinja2"
**Solution:**
```bash
pip install pyyaml jinja2
```

#### Issue: "context_index.json missing for dynamic detectors"
**Cause:** Running stage S3 without S1 output
**Solution:**
```bash
python scripts/space_traversal/audit_runner.py stage S1
python scripts/space_traversal/audit_runner.py stage S3
```
Or run full pipeline:
```bash
make space-audit
```

#### Issue: "Capability X not found" (explain command)
**Cause:** Typo in capability ID or capability not detected
**Solution:**
```bash
# List all capability IDs
jq -r '.capabilities[].id' audit_artifacts/capabilities_scored.json

# Use exact ID from list
make space-explain cap=<exact-id>
```

#### Issue: "One of the diff paths does not exist"
**Cause:** File path incorrect or file not generated
**Solution:**
```bash
# Check file exists
ls -l audit_artifacts/capabilities_scored.json

# Use absolute or relative path
make space-diff old=/path/to/old.json new=/path/to/new.json
```

#### Issue: All safeguards scores are 0
**Cause:** Safeguard keywords not found in codebase
**Solution:**
1. Review keyword list: `jq '.safeguards.keywords' .copilot-space/workflow.yaml`
2. Add relevant keywords to codebase (or)
3. Customize keyword list in workflow.yaml with project-specific terms

#### Issue: High duplication ratio (consistency component low)
**Cause:** Over-broad facet regex matching unrelated files
**Solution:**
1. Check evidence files: `jq '.capabilities[] | select(.id=="<cap>") | .evidence_files' audit_artifacts/capabilities_raw.json`
2. Narrow DOMAIN_PATTERNS in audit_runner.py (or)
3. Create specialized detector with precise file filtering

#### Issue: Zero documentation score
**Cause:** No doc files mention capability token
**Solution:**
1. Check token: capability ID first word (e.g., "logging" in "logging-tracking")
2. Add documentation: `echo "## <Token>" >> docs/<topic>.md`
3. Re-run S4-S7: `make space-audit-fast`

#### Issue: Template hash mismatch warning
**Cause:** Template files modified between runs
**Solution:**
```bash
# Review changes
git diff templates/audit/*.j2

# If intentional, regenerate baseline
make space-audit
git add audit_run_manifest.json
```

#### Issue: Score regression on diff
**Cause:** Code changes reduced pattern matches or increased duplication
**Solution:**
1. Explain affected capability: `make space-explain cap=<id>`
2. Identify low component (e.g., tests=0.3)
3. Address gap (add tests, reduce duplication, etc.)
4. Re-run audit: `make space-audit`
5. Verify improvement: `make space-diff old=<baseline> new=audit_artifacts/capabilities_scored.json`

#### Issue: Detector not found (dynamic loading)
**Cause:** File naming or import error
**Solution:**
1. Check filename: Must be `<id>.py` in `scripts/space_traversal/detectors/`
2. Test import: `python -c "from scripts.space_traversal.detectors import <name>"`
3. Check function signature: Must be `def detect(file_index: dict) -> dict:`
4. Review stderr during S3 for import errors

#### Issue: Non-deterministic scores (different on repeated runs)
**Cause:** Floating point precision or unsorted lists
**Solution:**
1. Check detector implementation: Ensure all lists are sorted
2. Add rounding: `round(score, 4)` in detector
3. Use `sorted(Path.rglob())` for file traversal
4. Verify no external state (time, random, network)

### Debug Mode
Add print statements in audit_runner.py:
```python
def stage_s4_scoring(cfg, raw_caps):
    print(f"[DEBUG] Scoring {len(raw_caps)} capabilities")
    for cap in raw_caps:
        print(f"[DEBUG] Scoring: {cap['id']}")
        # ... existing code
```

Run with Python unbuffered:
```bash
python -u scripts/space_traversal/audit_runner.py run 2>&1 | tee audit_debug.log
```

## 10. Advanced Usage

### Custom Templates
Modify `templates/audit/capability_matrix.md.j2`:

```jinja2
# Custom Audit Report

Generated: {{ timestamp }}

{% for cap in capabilities %}
## {{ cap.id }}
Score: {{ cap.score }}
- Functionality: {{ cap.components.functionality }}
- Needs improvement: {% if cap.score < 0.70 %}Yes{% else %}No{% endif %}
{% endfor %}
```

Re-render:
```bash
python scripts/space_traversal/audit_runner.py stage S6
```

### Multiple Configurations
Maintain multiple workflow.yaml variants:
```bash
# Strict CI config
cp .copilot-space/workflow.yaml{,.strict}

# Permissive dev config
vim .copilot-space/workflow.yaml  # Lower thresholds

# Switch configs
cp .copilot-space/workflow.yaml.strict .copilot-space/workflow.yaml
make space-audit
```

### Baseline Management
Track baselines in git:
```bash
# Create baseline branch
git checkout -b audit-baseline
make space-audit
git add audit_artifacts/capabilities_scored.json audit_run_manifest.json
git commit -m "Baseline audit"
git push origin audit-baseline

# Compare feature branch to baseline
git checkout feature-branch
make space-audit
git show audit-baseline:audit_artifacts/capabilities_scored.json > /tmp/baseline.json
make space-diff old=/tmp/baseline.json new=audit_artifacts/capabilities_scored.json
```

### Batch Explain
Explain all gaps at once:
```bash
# Bash loop
for cap in $(jq -r '.low_maturity[].id' audit_artifacts/gaps.json); do
    echo "=== $cap ==="
    make space-explain cap=$cap
    echo
done

# Or with xargs
jq -r '.low_maturity[].id' audit_artifacts/gaps.json | \
    xargs -I{} sh -c 'echo "=== {} ===" && make space-explain cap={}'
```

### Integration with CI/CD

#### GitHub Actions Example
```yaml
name: Capability Audit
on: [pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Need history for diff
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install pyyaml jinja2
      
      - name: Get baseline
        run: |
          git show origin/main:audit_artifacts/capabilities_scored.json > baseline.json || echo "{}" > baseline.json
      
      - name: Run audit
        run: make space-audit
      
      - name: Check for regressions
        run: |
          python scripts/space_traversal/audit_runner.py diff \
            --old baseline.json \
            --new audit_artifacts/capabilities_scored.json
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: capability-audit
          path: |
            audit_run_manifest.json
            reports/capability_matrix_*.md
```

#### GitLab CI Example
```yaml
capability-audit:
  stage: test
  script:
    - pip install pyyaml jinja2
    - git show origin/main:audit_artifacts/capabilities_scored.json > baseline.json || echo "{}" > baseline.json
    - make space-audit
    - python scripts/space_traversal/audit_runner.py diff --old baseline.json --new audit_artifacts/capabilities_scored.json
  artifacts:
    paths:
      - audit_run_manifest.json
      - reports/capability_matrix_*.md
    expire_in: 30 days
```

### Scheduled Audits
Run periodic audits to track trends:

```bash
#!/bin/bash
# scheduled_audit.sh

DATE=$(date +%Y-%m-%d)
BASELINE_DIR="baselines/$DATE"

mkdir -p "$BASELINE_DIR"

make space-audit

cp audit_artifacts/capabilities_scored.json "$BASELINE_DIR/"
cp audit_run_manifest.json "$BASELINE_DIR/"
cp reports/capability_matrix_*.md "$BASELINE_DIR/"

echo "Audit completed for $DATE"
ls -l "$BASELINE_DIR"
```

Add to crontab:
```bash
# Run weekly on Sundays at 2 AM
0 2 * * 0 cd /path/to/repo && ./scheduled_audit.sh
```

### Export to Other Formats

#### JSON to CSV
```bash
# Convert capabilities_scored to CSV
jq -r '.capabilities[] | [.id, .score, .components.functionality, .components.consistency, .components.tests, .components.safeguards, .components.documentation] | @csv' \
    audit_artifacts/capabilities_scored.json > capabilities.csv
```

#### JSON to HTML
```python
# convert_to_html.py
import json
import sys

with open('audit_artifacts/capabilities_scored.json') as f:
    data = json.load(f)

print('<html><body><table>')
print('<tr><th>ID</th><th>Score</th><th>Functionality</th><th>Tests</th></tr>')
for cap in data['capabilities']:
    print(f"<tr><td>{cap['id']}</td><td>{cap['score']:.3f}</td>"
          f"<td>{cap['components']['functionality']:.3f}</td>"
          f"<td>{cap['components']['tests']:.3f}</td></tr>")
print('</table></body></html>')
```

Run:
```bash
python convert_to_html.py > audit_report.html
```

---

## Appendix: Quick Reference Card

### One-Line Commands
```bash
# Full audit
make space-audit

# Fast path
make space-audit-fast

# Explain score
make space-explain cap=<id>

# Compare runs
make space-diff old=<path> new=<path>

# Clean artifacts
make space-clean

# List capabilities
jq -r '.capabilities[].id' audit_artifacts/capabilities_scored.json

# List gaps
jq -r '.low_maturity[].id' audit_artifacts/gaps.json

# Check warnings
jq '.warnings' audit_run_manifest.json

# Show component scores
jq '.capabilities[] | select(.id=="<id>") | .components' audit_artifacts/capabilities_scored.json
```

### File Locations
```
.copilot-space/workflow.yaml                  # Configuration
scripts/space_traversal/audit_runner.py       # Main orchestrator
scripts/space_traversal/detectors/*.py        # Capability detectors
templates/audit/capability_matrix.md.j2       # Report template
audit_artifacts/*.json                        # Stage outputs
reports/capability_matrix_*.md                # Human-readable reports
audit_run_manifest.json                       # Integrity manifest
```

### Exit Codes
- `0`: Success
- `1`: Usage error (wrong arguments)
- `2`: File not found or invalid input
- `3`: Score regression detected (diff command)

### Support
- **Documentation:** `Traversal_Workflow.md` (technical details)
- **Repository:** `https://github.com/Aries-Serpent/_codex_`
- **Issues:** Report bugs via GitHub Issues

---

**Last Updated:** 2025-11-19  
**Version:** 1.1.0  
**Maintained By:** Codex Audit Orchestrator Team
