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
- detect_v2: may return `evidence` objects including path, ranges, confidence, excerpt.

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
