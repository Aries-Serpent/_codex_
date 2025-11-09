# [Guide]: Dynamic Detectors — scripts/space_traversal/detectors
> Updated: 2025-11-09 | Author: mbaetiong  
> Version: 1.4.0

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

## Available Detectors (v1.4.0)

### Core Infrastructure
- **ci_cd_pipeline.py** - CI/CD workflows and automation
- **code_quality_tooling.py** - Linters, formatters, static analysis
- **deployment_infrastructure.py** - Deployment configs and orchestration
- **documentation_system.py** - Sphinx, MkDocs, documentation builds
- **testing_infrastructure.py** - Test frameworks and fixtures

### ML-Specific (v1.4.0)
- **ml_serving.py** - ML serving and inference endpoints (NEW)
- **inference_serving.py** - FastAPI/Flask serving infrastructure
- **unified_training.py** - Training orchestration
- **experiment_management.py** - Experiment tracking (MLflow, W&B)
- **detector_peft.py** - PEFT/LoRA hooks

### Data & Reproducibility
- **reproducibility.py** - Deterministic configs, seed management
- **detector_safeguards.py** - Safety checks and validation
- **vector_store_detector.py** - Vector database integrations
- **detector_duplication.py** - Duplication detection utilities

### Operations (v1.4.0)
- **status_reporting.py** - Status updates and audit reporting (NEW)
- **archival_bundling.py** - Archive creation and validation (NEW)

## Creating New Detectors

1. Create file in this directory: `my_capability.py`
2. Implement `detect(file_index: dict) -> dict` function
3. Return dict with required fields: id, evidence_files, found_patterns, required_patterns
4. Add override to `.copilot-space/workflow.yaml` if needed
5. Run: `python scripts/space_traversal/audit_runner.py run`

Example:
```python
def detect(file_index: dict) -> dict:
    files = file_index.get("files", [])
    evidence = [f["path"] for f in files if "my_pattern" in f["path"].lower()]
    return {
        "id": "my-capability",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": ["pattern1", "pattern2"],
        "required_patterns": ["pattern1", "pattern2", "pattern3"],
        "meta": {"layer": "infrastructure", "priority": "medium"}
    }
```

*End*
