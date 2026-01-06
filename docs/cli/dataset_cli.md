# [Guide]: Dataset CLI (validate & metadata)
> Generated: Previous Cycle-11-19 04:26:35 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5  
Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️

## Overview
Small, offline-safe CLI for quick checks on dataset files using the unified loader registry.

## Commands
```bash
# Validate a dataset file can be loaded
python -m src.codex_ml.data.cli validate path/to/file.jsonl

# Emit metadata (format-aware)
python -m src.codex_ml.data.cli metadata path/to/file.parquet
```

## Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Path not found |
| 3 | Load failed |

## Notes
- Parquet/Arrow/HDF5 metadata uses native loader metadata for rich details.
- JSONL/CSV fall back to simple counts and file size.
- No network calls; safe for offline environments.
