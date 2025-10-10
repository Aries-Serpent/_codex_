# [How-to]: Dataset Manifest & Shard Integrity  
> Generated: 2025-10-09 20:04:41 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Ensure reproducible dataset loading with per-shard SHA256 verification.

Schema (v1.0)
| Field | Type | Notes |
|-------|------|-------|
| schema_version | str | "1.0" |
| created_at | int | Epoch seconds |
| dataset_id | str? | Optional stable ID |
| shards[].path | str | Relative path |
| shards[].size | int | Bytes |
| shards[].sha256 | str | Hex digest |

Python API
```python
from src.data.manifest import DatasetManifest
man = DatasetManifest.build("data_root", ["splits/train.jsonl", "splits/val.jsonl"])
man.write("data_root/manifest.json")
man2 = DatasetManifest.load("data_root/manifest.json")
man2.verify("data_root")
```

Notes
- Verification raises ValueError on missing shard or checksum mismatch.
- Writing uses atomic IO (tmpfile→fsync→os.replace).

*End*