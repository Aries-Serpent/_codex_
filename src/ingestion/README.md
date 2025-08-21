# Ingestion Module

Provides a minimal :class:`Ingestor` utility for reading text from files. The
current implementation focuses solely on filesystem paths and is designed to be
extended with additional data sources in the future.

## Usage

```python
from ingestion import Ingestor

ingestor = Ingestor()
text = ingestor.ingest("path/to/file.txt")
```

## Expected Errors

- `FileNotFoundError` – raised when the supplied path does not exist or is not
  a file.

## Future Extensions

Potential future work includes support for streaming sources, remote URLs, or
data validation hooks.
