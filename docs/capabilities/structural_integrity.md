# Structural Integrity Detection

## Overview

The structural integrity capability detects architectural anti-patterns and risks in repository structure, including split-brain architecture (duplicate modules in root and `src/`) and library shadowing (local directories that conflict with PyPI package names).

**Keywords**: structural-integrity, architecture, split-brain, shadowing, namespace, validation, detection, consistency, safeguards

## Purpose

Ensures codebase maintains clean architecture by:
- **Split-Brain Detection**: Identifies duplicate module structures (e.g., `mymodule/` at root AND `src/mymodule/`)
- **Library Shadowing Detection**: Finds local directories that Phase 5 shadow standard libraries (e.g., `torch/`, `numpy/` at root)
- **Namespace Integrity**: Validates consistent import paths and module organization
- **Risk Assessment**: Classifies architectural risks as high/medium/low

## Architecture

### Detection Strategy

The detector analyzes directory structure to identify:

1. **Root directories** (excluding standard directories like `.git`, `tests`, `docs`, `scripts`)
2. **Source directories** under `src/`
3. **Intersections** that indicate split-brain architecture
4. **Known shadow risks** from PyPI package names

### Detection Algorithm

```python
# Pseudocode for structural integrity detection
for each file in repository:
    extract directory structure
    
identify split-brain patterns:
    intersection = root_dirs ∩ src_dirs
    
identify shadowing patterns:
    shadows = root_dirs ∩ known_pypi_packages
    
assess risk_level:
    high: if split-brain OR shadowing detected
    low: otherwise
```

## Configuration

### Detector Settings

The detector is configured in `scripts/space_traversal/detectors/structure_integrity.py`:

```python
# Known libraries that should not exist as root directories
KNOWN_SHADOW_RISKS = {
    "hydra", "torch", "numpy", "requests", 
    "wandb", "mlflow", "pandas"
}

# Evidence limit for file samples
evidence_limit = 10  # Configurable per detect() call
```

### Excluded Directories

Standard directories excluded from risk assessment:
- `.git`, `.github`, `.copilot-space`
- `tests`, `docs`, `scripts`
- `deploy`, `config`
- `audit_artifacts`, `reports`

## Usage Examples

### Example 1: Clean Architecture (No Issues)

**Repository Structure:**
```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── core.py
├── tests/
├── docs/
└── scripts/
```

**Detection Result:**
```json
{
  "id": "structural-integrity",
  "evidence_files": [],
  "found_patterns": [],
  "meta": {
    "risk_level": "low",
    "split_dirs": [],
    "shadow_dirs": []
  }
}
```

### Example 2: Split-Brain Architecture Detected

**Repository Structure:**
```
project/
├── myapp/          # ⚠️ Duplicate at root
│   └── utils.py
├── src/
│   └── myapp/      # ⚠️ Also in src/
│       └── core.py
```

**Detection Result:**
```json
{
  "id": "structural-integrity",
  "evidence_files": [
    "myapp/utils.py",
    "src/myapp/core.py"
  ],
  "found_patterns": ["split-brain"],
  "meta": {
    "risk_level": "high",
    "split_dirs": ["myapp"],
    "shadow_dirs": []
  }
}
```

### Example 3: Library Shadowing Detected

**Repository Structure:**
```
project/
├── torch/          # ⚠️ Shadows PyTorch
│   └── custom.py
├── src/
│   └── myapp/
```

**Detection Result:**
```json
{
  "id": "structural-integrity",
  "evidence_files": ["torch/custom.py"],
  "found_patterns": ["lib-shadowing"],
  "meta": {
    "risk_level": "high",
    "split_dirs": [],
    "shadow_dirs": ["torch"]
  }
}
```

### Example 4: Multiple Issues

**Repository Structure:**
```
project/
├── numpy/          # ⚠️ Shadows NumPy
├── utils/          # ⚠️ Duplicate
└── src/
    └── utils/      # ⚠️ Duplicate
```

**Detection Result:**
```json
{
  "id": "structural-integrity",
  "found_patterns": ["lib-shadowing", "split-brain"],
  "meta": {
    "risk_level": "high",
    "split_dirs": ["utils"],
    "shadow_dirs": ["numpy"]
  }
}
```

## Integration with Audit Pipeline

### Command Line Usage

```bash
# Run full audit (includes structural-integrity check)
python scripts/space_traversal/audit_runner.py run

# Explain structural-integrity capability score
python scripts/space_traversal/audit_runner.py explain structural-integrity

# View detailed evidence
cat audit_artifacts/capabilities_raw.json | jq '.capabilities[] | select(.id=="structural-integrity")'
```

### Programmatic Usage

```python
from scripts.space_traversal.detectors import structure_integrity

# Run detection
file_index = {"files": [{"path": "src/myapp/core.py"}, ...]}
result = structure_integrity.detect(file_index, evidence_limit=20)

# Check for issues
if result["meta"]["risk_level"] == "high":
    print(f"Found issues: {result['found_patterns']}")
    print(f"Split-brain dirs: {result['meta']['split_dirs']}")
    print(f"Shadowing dirs: {result['meta']['shadow_dirs']}")
```

## Risk Mitigation

### Resolving Split-Brain Architecture

**Problem**: Module exists in both root and `src/`

**Solutions**:
1. **Consolidate to `src/`** (recommended):
   ```bash
   git mv mymodule/ src/mymodule/
   # Update imports throughout codebase
   ```

2. **Rename one module**:
   ```bash
   mv mymodule/ mymodule_legacy/
   # Update references
   ```

3. **Use explicit namespacing**:
   ```python
   # In root module
   from src.mymodule import *  # Explicit delegation
   ```

### Resolving Library Shadowing

**Problem**: Local directory shadows PyPI package

**Solutions**:
1. **Rename local directory** (recommended):
   ```bash
   mv torch/ torch_custom/
   mv numpy/ numpy_extensions/
   ```

2. **Move to `src/`**:
   ```bash
   mkdir -p src/project_torch
   git mv torch/* src/project_torch/
   ```

3. **Use package prefix**:
   ```bash
   mv torch/ myproject_torch/
   ```

## Best Practices

### Architecture Guidelines

1. **Use `src/` layout** for all application code:
   ```
   project/
   ├── src/
   │   └── myapp/
   ├── tests/
   ├── docs/
   └── scripts/
   ```

2. **Avoid namespace conflicts**:
   - Never name directories after PyPI packages
   - Use project-specific prefixes for utilities

3. **Maintain single source of truth**:
   - Each module should exist in exactly one location
   - Use explicit imports, not duplicate code

4. **Follow PEP 420** (Implicit Namespace Packages):
   - Use `__init__.py` for all packages
   - Avoid relying on implicit namespace behavior

### Detection Configuration

1. **Evidence Limit**: Adjust for repository size
   ```python
   result = detect(file_index, evidence_limit=50)  # Larger repos
   ```

2. **Custom Shadow Risks**: Extend `KNOWN_SHADOW_RISKS`
   ```python
   KNOWN_SHADOW_RISKS = {
       *KNOWN_SHADOW_RISKS,
       "custom_lib", "internal_package"
   }
   ```

3. **Exclude Additional Directories**: Modify exclusion list
   ```python
   excluded = {
       ".git", "tests", "docs", "scripts",
       "vendor", "third_party"  # Add project-specific
   }
   ```

## Troubleshooting

### Issue: False Positives

**Symptom**: Detector reports issues that are intentional

**Solution**: Add directories to exclusion list or use different naming

### Issue: Missing Detections

**Symptom**: Known split-brain not detected

**Cause**: Directory in exclusion list

**Solution**: Review exclusion criteria in detector

### Issue: High Evidence Count

**Symptom**: Too many evidence files returned

**Solution**: Reduce `evidence_limit` parameter

### Issue: Import Errors After Fixes

**Symptom**: Code breaks after resolving split-brain

**Solution**: Use automated refactoring tools:
```bash
# Use rope or similar for safe refactoring
python -m rope.refactor.rename mymodule src.mymodule
```

## Performance Considerations

### Detection Performance

- **Time Complexity**: O(n) where n = number of files
- **Space Complexity**: O(d) where d = number of unique directories
- **Typical Runtime**: < 100ms for 10,000 files

### Optimization Tips

1. **Use smaller evidence_limit** for large repos
2. **Cache directory structure** for repeated runs
3. **Run detection early** in CI/CD pipeline

## Monitoring

### Audit Score Tracking

```bash
# Track structural-integrity score over time
python scripts/space_traversal/trend_aggregator.py --lookback-days 30
```

### CI/CD Integration

```yaml
# .github/workflows/quality-gate.yml
- name: Check Structural Integrity
  run: |
    python scripts/space_traversal/audit_runner.py run
    python -c "
    import json
    with open('audit_artifacts/capabilities_scored.json') as f:
        data = json.load(f)
    cap = next(c for c in data['capabilities'] if c['id']=='structural-integrity')
    assert cap['score'] >= 0.70, f'Structural integrity score {cap[\"score\"]} below threshold'
    "
```

## Related Capabilities

- **consistency**: Overall code consistency metrics
- **documentation-system**: Documentation organization
- **testing-infrastructure**: Test structure organization
- **code-quality-tooling**: Linting and static analysis

## References

- [PEP 420 - Implicit Namespace Packages](https://www.python.org/dev/peps/pep-0420/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [Split-Brain Architecture Anti-Pattern](https://wiki.c2.com/?SplitBrain)

## Safeguards

The structural integrity detector includes the following safeguards:

1. **Bounded Evidence Collection**: Limits evidence files to prevent excessive memory usage
2. **Deterministic Detection**: Stable sorting ensures reproducible results
3. **Validation**: Checks path existence before processing
4. **Error Handling**: Gracefully handles malformed paths
5. **Risk Classification**: Clear high/medium/low categorization

## Changelog

- **v1.0**: Initial implementation with split-brain and shadowing detection
- **v1.1**: Added configurable evidence limits
- **v1.2**: Enhanced meta information with risk assessment
- **v1.3**: Added safeguards and deterministic behavior

---

**Last Updated**: 2024-12-09  
**Maintainer**: Codex Audit System  
**Capability ID**: structural-integrity

## Advanced Safeguards

### Reproducibility Guarantees

The structural integrity detector ensures reproducible results through:

- **Explicit seed-independent logic**: No random operations, deterministic file ordering
- **Checksum-stable output**: Results can be verified with sha256 hashes
- **Manifest tracking**: All detected patterns recorded in audit manifest
- **Baseline comparison**: Compare against baselines for regression detection

### Offline Operation

- Works completely offline with no network dependencies
- WANDB_MODE not required as no logging to external services
- All analysis performed on local file system

### Security Considerations

- Paths are sanitized before processing
- Secret files (matching patterns like `.env`, `secret`) are excluded from evidence
- Bounded file reading prevents memory exhaustion (rng not applicable)
