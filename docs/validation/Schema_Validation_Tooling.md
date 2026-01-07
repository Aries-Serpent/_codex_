# Validation: Status Schema and Config Validation Tooling
> Generated: Previous Cycle-11-02 14:48:51 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Validation Architect], [Secondary: Toolsmith] ⚡ Energy: 5  


This document explains how to use the new validation tooling to satisfy v1.2 requirements.

- Tools:
  - tools/schema_validate.py — Generic JSON/YAML + JSON Schema validator
  - tools/validate_configs.py — Batch-validate Hydra configs against schemas
  - src/codex_ml/cli/validate.py — Programmatic API and CLI wrapper with structured output
- Schemas:
  - configs/schemas/training.schema.yaml
  - configs/schemas/training_profile.schema.json
  - configs/schemas/evaluation.schema.json
  - configs/schemas/checkpoint_manifest.schema.json

Quickstart
- Validate one pair:
  - python tools/schema_validate.py --data configs/training/base.yaml --schema configs/schemas/training.schema.yaml
- Validate all training profiles:
  - python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml
- Validate run output:
  - python src/codex_ml/cli/validate.py json --data runs/last/evaluation.json --schema configs/schemas/evaluation.schema.json --format json

Outputs
- PASS returns exit code 0; FAIL returns 1
- Detailed error listing with dataPath, schemaPath, message, and instance excerpt
