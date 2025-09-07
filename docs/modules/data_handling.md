# Data Handling

The data loader in `codex_ml.data.loader` supports loading datasets from plain
text (`.txt`/`.md`), NDJSON (`.jsonl`/`.ndjson`), and CSV files with a `text`
column. Loaded texts can be cached by setting a cache directory which stores a
hash of the original file for quick reloads. A simple safety filter is available
via `apply_safety_filter` to redact sensitive content when enabled.

Example:

```python
from pathlib import Path
from codex_ml.data.loader import load_dataset, apply_safety_filter

texts = load_dataset(Path("data/sample.jsonl"))
texts = apply_safety_filter(texts, enabled=True)
```
