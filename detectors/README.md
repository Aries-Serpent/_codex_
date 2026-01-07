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
- Ensure ordering is deterministic: sort any lists you emit in results so downstream capability scoring remains stable across runs.
- Keep outputs small and text-only; audit_runner enforces `SAFE_TEXT_EXT` and size limits for deterministic hashing.

Best Practices:
- Keep detectors minimal and deterministic.
- Document detector id and intent in module-level docstring.
- Add a corresponding unit test under tests/detectors/ to validate expected outputs for sample file_index.
- When adding new detectors, request code review.
- If a detector depends on configuration files, validate their presence explicitly and provide actionable error messages so
  `codex-status-audit --skip-audit` can surface missing prerequisites quickly.

Pipeline integration & verification:
- Runtime wiring: detectors are imported by `scripts/space_traversal/audit_runner.py` during the capability-audit pipeline invoked via `codex-status-audit`.
- Schema + template alignment: outputs feed the status templates in `docs/templates/status/` (see `codex_status_template_v1.2.md` and schema files) and must remain deterministic for reproducible reports.
- Tests: run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/detectors tests/cli/test_status_audit.py` to validate detector contracts, CLI orchestration, and downstream template presence. Add fixture-specific tests in `tests/detectors/fixtures` when introducing new heuristics.
- Edge cases: handle empty `file_index`, missing optional evidence fields, and ensure no network or filesystem writes occur during import or detection.

Example:
```python
def detect(file_index: dict) -> dict:
    # analyze file_index["files"] and return capability dict
    pass
```
