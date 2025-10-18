# [Guide]: Dynamic Detectors — scripts/space_traversal/detectors
> Generated: 2025-10-18 07:50:35 UTC | Author: mbaetiong

Roles: [Primary: Audit Orchestrator], [Secondary: Capability Cartographer]  Energy: 5

## Contract
Implement a module with:
```python
def detect(file_index: dict) -> dict:
    return {
      "id":"<capability-id>",
      "evidence_files":[...],
      "found_patterns":[...],
      "required_patterns":[...],
      "meta":{}
    }
```

## Notes
- Autoloaded at S3 when `capability_map.dynamic: true` in .copilot-space/workflow.yaml
- Keep pure: no network I/O, deterministic output, sorted lists
- Use IDs unique across static and dynamic capabilities
- Prefer lightweight signals (path-level, simple token presence)

*End*
