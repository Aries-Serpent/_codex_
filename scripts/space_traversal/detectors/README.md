# Detectors — Dynamic Capability Extraction
> Generated: 2025-10-10 03:27:51 UTC | Author: mbaetiong

Purpose
- Add pluggable capability detectors without editing the core audit runner.

How it works
- Any Python module in this directory exposing `def detect(file_index: dict) -> dict` will be discovered when `capability_map.dynamic: true` in .copilot-space/workflow.yaml.
- The runner passes the S1 context index payload; your detector returns a capability object.

Contract (return value)
```python
{
  "id": "my-capability",
  "evidence_files": ["path/relative/to/repo.py"],
  "found_patterns": ["keyword1", "keyword2"],
  "required_patterns": ["keyword1"],
  "meta": {"layer":"core"}
}
```

Tips
- Keep results deterministic (avoid random ordering).
- Prefer stable filename/pattern signals; open files only when necessary (respect offline operation).
- Add tests under tests/ if you introduce non-trivial logic.

Activation
- This repo ships without active detectors in this folder by default.
- Create a new `<name>.py` here to add your detector; it will be auto-loaded on next S3 run.
