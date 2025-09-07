# Data Handling

The data handling helpers load plain text, NDJSON and CSV files.  Datasets are
cached on disk using a hash of the source file to avoid repeated parsing.
A small safety filter hook allows optional redaction of sensitive content.

```python
from pathlib import Path
from codex_ml.data.loader import load_dataset
texts = load_dataset(Path('corpus.jsonl'))
```
