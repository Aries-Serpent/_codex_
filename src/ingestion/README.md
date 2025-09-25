# Ingestion

Utilities for reading text files.

## Parameters

- `path: Union[str, Path]` – file to read.
- `encoding: str = "utf-8"` – decoding used when opening the file. Pass
  `"auto"` to attempt deterministic encoding detection.
- `chunk_size: Optional[int] = None` – if `None`, returns the entire file as a
  single string; if a positive integer, yields chunks of at most that length.

## Examples

```python
from ingestion import ingest

# Full read
text = ingest("data/sample.txt")

# Chunked streaming
for chunk in ingest("data/sample.txt", encoding="utf-8", chunk_size=4096):
    process(chunk)
```