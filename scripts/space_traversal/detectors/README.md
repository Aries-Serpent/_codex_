# Detectors README — Safe Detector Guidelines

Detectors are small analysis modules loaded dynamically by the audit pipeline.

Key points:
- Location: scripts/space_traversal/detectors/
- Required function(s): `detect(file_index: dict) -> dict` and/or `detect_v2(file_index: dict) -> dict`
- Detector contract:
  - Return a dict with keys:
    - id: str (unique capability id)
    - evidence_files: List[str] OR evidence: List[object] (v2)
    - found_patterns: List[str]
    - required_patterns: List[str]
    - meta: optional dict
- detect_v2: Phase 5 return `evidence` objects including path, ranges, confidence, excerpt.

Security & Safety:
- Detectors execute at import-time. DO NOT write files, make network calls, or perform heavy computation during module import.
- Implement detectors as side-effect free. Only examine the provided `file_index` argument.
- Wrap any heavy parsing in functions invoked by the detect function (not on import).
- Add unit tests for detector behavior and ensure deterministic outputs (no random order).
- Use defensive coding: validate input, return canonical types, and raise descriptive exceptions.

Best Practices:
- Keep detectors minimal and deterministic.
- Document detector id and intent in module-level docstring.
- Add a corresponding unit test under tests/detectors/ to validate expected outputs for sample file_index.
- When adding new detectors, request code review.

Example:
```python
def detect(file_index: dict) -> dict:
    # analyze file_index["files"] and return capability dict
    pass
```

---

## Detector: structure_integrity.py

**Purpose**: Detects "Split Brain" architecture and library shadowing risks.

**ID**: `structural-integrity`

**Detection Logic**:

1. **Split-Brain Detection**:
   - Identifies directories that exist in both root and `src/`
   - Examples: `training/` and `src/training/`, `tokenization/` and `src/tokenization/`
   - Evidence: Balanced sample of files from both locations (5 from root + 5 from src)

2. **Library Shadowing Detection**:
   - Identifies root directories that Phase 5 shadow PyPI packages
   - Known shadow risks: `hydra`, `torch`, `numpy`, `requests`, `wandb`, `mlflow`, `pandas`
   - Evidence: Sample files from shadowing directory

**Configuration**:
- `EVIDENCE_LIMIT`: 10 files (configurable)
- Balanced sampling ensures representation from both root and src

**Meta Fields**:
- `risk_level`: "high" if issues found, "low" otherwise
- `description`: Detector purpose
- `split_dirs`: List of split-brain directories
- `shadow_dirs`: List of shadowing directories
- `evidence_limit`: Evidence cap value

**Integration**:
```bash
# Test detector
python scripts/space_traversal/audit_runner.py stage S3

# View results
cat audit_artifacts/capabilities_raw.json | jq '.capabilities[] | select(.id=="structural-integrity")'
```

**Related**:
- `scripts/remediation/verify_conflicts.py`: Runtime verification
- `tests/validation/test_shadowing.py`: Automated test for shadowing
