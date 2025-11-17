# [Playbook]: Detector Lifecycle and Quality
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

Contract:
```python
def detect(file_index: dict) -> dict:
    return {
      "id":"new-cap",
      "evidence_files":[...],
      "found_patterns":[...],
      "required_patterns":[...],
      "meta":{}
    }
```text

Quality checks:
- Deterministic: no random ordering; sort outputs.
- Minimal reads: rely on file_index (paths/sha/size); lazy text reads if needed.
- Unit tests: Provide fixtures based on audit_artifacts/context_index.json.
- Overrides: Keep canonical IDs stable; configure aliases in capability_map.overrides.

Troubleshooting:
- Detector missing: Confirm dynamic loading enabled; fix import errors.
- Too many false hits: Tighten patterns; restrict to relevant facets.
