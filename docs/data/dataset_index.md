# Dataset Index Tool

`tools/codex_dataset_index.py` scans a data directory (default: `data`) and
produces two artifacts:

- `codex_dataset_index.json`: structured listing of files with type and size
- `codex_dataset_index.md`: Markdown table for quick review

The tool classifies files by extension (`csv`, `json`, `ndjson`, `parquet`,
`unknown`) and records relative paths so indexes remain portable across
machines.

Usage:

```bash
python tools/codex_dataset_index.py --data-root data \
  --json-out codex_dataset_index.json --md-out codex_dataset_index.md
```

The command is safe to run on empty directories (outputs will contain empty
file lists) and can be rerun after dataset updates to refresh the index.
