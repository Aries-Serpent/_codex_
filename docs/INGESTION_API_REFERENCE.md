# Ingestion Pipeline API Reference

**Last Updated:** 2026-06-22

## Overview

The ingestion pipeline provides a unified interface for processing multiple file formats (CSV, JSON, JSONL, TXT, MD) with comprehensive validation, transformation, and streaming support.

**Module**: `src.ingestion.pipeline`
**Version**: 1.0
**Status**: Production Ready

## Core Components

### 1. PipelineConfig

Configuration dataclass for the ingestion pipeline.

```python
from src.ingestion.pipeline import PipelineConfig

config = PipelineConfig(
    encoding='auto',           # File encoding detection
    batch_size=1000,          # Records per batch
    max_file_size_mb=100,     # Maximum file size
    shuffle=False,            # Shuffle records
    shuffle_seed=42,          # Random seed
    lowercase=False,          # Lowercase text
    strip_whitespace=True,    # Strip whitespace
    skip_empty=True,          # Skip empty records
    timeout_seconds=300,      # Operation timeout
    validate_utf8=True        # Validate UTF-8
)
```

**Attributes:**
- `encoding` (str): File encoding. Use 'auto' for auto-detection
- `batch_size` (int): Records per batch for streaming (default: 1000)
- `max_file_size_mb` (int): Maximum file size in MB (default: 100)
- `shuffle` (bool): Whether to shuffle records (default: False)
- `shuffle_seed` (int): Random seed for reproducibility (default: 42)
- `lowercase` (bool): Convert text to lowercase (default: False)
- `strip_whitespace` (bool): Strip leading/trailing whitespace (default: True)
- `skip_empty` (bool): Skip empty records (default: True)
- `timeout_seconds` (int): Operation timeout in seconds (default: 300)
- `validate_utf8` (bool): Validate UTF-8 encoding (default: True)

### 2. PipelineResult

Result of a pipeline operation.

```python
from src.ingestion.pipeline import PipelineResult

result = pipeline.ingest_file('data.csv')

# Access results
print(result.success)               # bool
print(result.records_processed)     # int
print(result.records_skipped)       # int
print(result.errors)                # List[str]
print(result.duration_seconds)      # float
print(result.output_path)           # str
print(result.metadata)              # dict
```

**Attributes:**
- `success` (bool): Whether operation succeeded
- `records_processed` (int): Number of records processed
- `records_skipped` (int): Number of records skipped
- `errors` (List[str]): List of error messages
- `duration_seconds` (float): Operation duration
- `output_path` (str): Output file path (if applicable)
- `metadata` (dict): Additional metadata

## 3. IngestionPipeline

Main pipeline class for data ingestion.

```python
from src.ingestion.pipeline import IngestionPipeline, PipelineConfig

config = PipelineConfig(batch_size=500)
pipeline = IngestionPipeline(config)
```

### Methods

#### `ingest_file()`

Process a single file.

```python
result = pipeline.ingest_file(
    input_path='data/input.csv',
    output_path='data/output.jsonl',
    transform_fn=None
)
```

**Parameters:**
- `input_path` (str|Path): Path to input file
- `output_path` (str|Path, optional): Path to output file
- `transform_fn` (Callable, optional): Custom transformation function

**Returns:** `PipelineResult`

**Raises:** 
- `FileNotFoundError`: If input file not found
- `ValueError`: If file exceeds max size
- `TimeoutError`: If operation exceeds timeout

**Example:**

```python
# Process with transformation
def transform(record):
    return {
        'text': record.get('text', '').lower(),
        'label': int(record.get('label', 0))
    }

result = pipeline.ingest_file(
    'raw_data.csv',
    'processed_data.jsonl',
    transform_fn=transform
)

if result.success:
    print(f"Processed {result.records_processed} records")
else:
    print(f"Errors: {result.errors}")
```

## `ingest_directory()`

Process all files in a directory.

```python
result = pipeline.ingest_directory(
    input_dir='data/raw',
    output_dir='data/processed',
    pattern='*.csv'
)
```

**Parameters:**
- `input_dir` (str|Path): Input directory path
- `output_dir` (str|Path): Output directory path
- `pattern` (str): File pattern to match (default: '*')

**Returns:** `PipelineResult` (aggregated)

**Example:**

```python
result = pipeline.ingest_directory(
    'data/raw',
    'data/processed',
    pattern='*.{csv,json}'
)

print(f"Total: {result.records_processed}")
print(f"Failed: {len(result.errors)}")
```

### `stream_records()`

Stream records from a file (memory-efficient).

```python
for batch in pipeline.stream_records('data/large_file.csv'):
    # Process batch (list of dicts)
    process_batch(batch)
```

**Parameters:**
- `input_path` (str|Path): Path to input file

**Returns:** Iterator of record batches

**Example:**

```python
# Process large file in batches
batch_count = 0
for batch in pipeline.stream_records('data/large_file.csv'):
    batch_count += 1
    process_batch(batch)
    print(f"Processed batch {batch_count}")
```

## File Format Support

### CSV Format

Comma-separated values with headers.

```text
# Input: data.csv
id,text,label
1,Sample text,0
2,Another example,1

# Usage
result = pipeline.ingest_file('data.csv', 'data.jsonl')

# Output: data.jsonl
{"id": "1", "text": "Sample text", "label": "0"}
{"id": "2", "text": "Another example", "label": "1"}
```

## JSON Format

Single JSON object or array.

```python
# Input: data.json
{
  "data": [
    {"id": 1, "text": "Sample text", "label": 0},
    {"id": 2, "text": "Another example", "label": 1}
  ]
}

# Usage
result = pipeline.ingest_file('data.json', 'data.jsonl')
```

## JSONL Format

Newline-delimited JSON (one object per line).

```
# Input: data.jsonl
{"id": 1, "text": "Sample text", "label": 0}
{"id": 2, "text": "Another example", "label": 1}
```

## Text Format

Plain text, one record per line.

```
# Input: data.txt
Sample text
Another example

# Usage with transformation
def text_to_record(line):
    return {"text": line}

result = pipeline.ingest_file('data.txt')
```

## Custom Ingestors

### CSV Ingestor

```python
from src.ingestion.csv_ingestor import CSVIngestor

ingestor = CSVIngestor(
    encoding='utf-8',
    delimiter=',',
    quotechar='"'
)

records = ingestor.ingest('data.csv')
```

### JSON Ingestor

```python
from src.ingestion.json_ingestor import JSONIngestor

ingestor = JSONIngestor(encoding='utf-8')
records = ingestor.ingest('data.json')
```

### File Ingestor

```python
from src.ingestion.file_ingestor import FileIngestor

ingestor = FileIngestor(encoding='utf-8')
records = ingestor.ingest('data.txt')
```

## Error Handling

### Common Errors

**FileNotFoundError:**
```python
try:
    result = pipeline.ingest_file('nonexistent.csv')
except FileNotFoundError:
    print("Input file not found")
```

**EncodingError:**
```python
config = PipelineConfig(encoding='utf-8', validate_utf8=True)
pipeline = IngestionPipeline(config)
result = pipeline.ingest_file('data_with_encoding_issues.csv')
```

**SizeError:**
```python
config = PipelineConfig(max_file_size_mb=50)
pipeline = IngestionPipeline(config)
result = pipeline.ingest_file('large_file.csv')  # Will fail if > 50MB
```

**TimeoutError:**
```python
config = PipelineConfig(timeout_seconds=60)
pipeline = IngestionPipeline(config)
try:
    result = pipeline.ingest_file('data.csv')
except TimeoutError:
    print("Operation exceeded 60 second timeout")
```

## Performance Considerations

1. **Batch Size**: Larger batches = faster processing but higher memory
```python
config = PipelineConfig(batch_size=5000)  # Larger batches
```

2. **Streaming**: Use `stream_records()` for large files to save memory
```python
for batch in pipeline.stream_records('large_file.csv'):
    process_batch(batch)
```

3. **Parallel Processing**: Process multiple files simultaneously
```python
from concurrent.futures import ProcessPoolExecutor

files = ['file1.csv', 'file2.csv', 'file3.csv']
with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(pipeline.ingest_file, files)
```

4. **Encoding Detection**: Auto-detection is slower than specifying encoding
```python
config = PipelineConfig(encoding='utf-8')  # Faster
```

## Best Practices

1. **Always validate input files**
```python
from pathlib import Path
input_file = Path('data.csv')
assert input_file.exists(), f"{input_file} not found"
```

2. **Use deterministic shuffling for reproducibility**
```python
config = PipelineConfig(shuffle=True, shuffle_seed=42)
```

3. **Log pipeline results**
```python
result = pipeline.ingest_file('data.csv', 'output.jsonl')
logging.info(f"Processed: {result.records_processed}, "
             f"Skipped: {result.records_skipped}")
```

4. **Handle errors gracefully**
```python
if not result.success:
    logging.error(f"Pipeline errors: {result.errors}")
    # Implement fallback or retry logic
```

## See Also

- [RAG Pipeline API Reference](./RAG_API_REFERENCE.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)
- [Quickstart Guide](./QUICKSTART.md)
