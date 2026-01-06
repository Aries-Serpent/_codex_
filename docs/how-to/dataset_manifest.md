# [How-to]: Dataset Manifest & Shard Integrity  
> Generated: Previous Cycle-10-09 20:04:41 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Ensure reproducible dataset loading with per-shard SHA256 verification.

## Built-in loaders

The `codex_ml.data.registry` module now exposes ready-to-use JSONL and CSV
loaders that integrate with manifest generation and deterministic splitting.

- **JSONL** — `codex_ml.data.registry.load_jsonl(path, split=(0.8,0.1,0.1))`
  normalises each record into `{text,input,target}` entries, records the source
  checksum and optionally writes cache manifests under `artifacts/data_cache/`.
- **CSV** — `codex_ml.data.registry.load_csv(path, delimiter=",")` uses the
  header row to resolve columns and mirrors the JSONL deterministic splitting
  utilities. TSV files are supported by setting `delimiter="\t"`.

Both loaders accept `seed` and `shuffle` parameters, ensuring reproducible
train/validation/test splits that align with the manifest checksums described
below.

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
```text

Notes
- Verification raises ValueError on missing shard or checksum mismatch.
- Writing uses atomic IO (tmpfile→fsync→os.replace).

*End*