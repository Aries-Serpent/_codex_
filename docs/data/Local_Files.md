# Docs: Local Files — CSV/JSON/JSONL Loaders

> Generated: 2024-11-05 | Author: mbaetiong

## Overview

Simple utilities for loading and saving local CSV, JSON, and JSONL files without requiring network access.

## Features

- **Format Support**: CSV, JSON, JSONL
- **Offline-first**: No network calls required
- **Simple API**: Consistent interface across formats
- **Type Hints**: Full type annotations
- **Encoding Support**: UTF-8 by default, configurable

## Loading Data

### load_jsonl

Load JSONL file line-by-line:

```python
from codex_ml.data.local_files import load_jsonl

records = load_jsonl("data/train.jsonl")
# Returns: [{"text": "...", "label": 0}, ...]
```text

### load_json

Load single JSON object or array:

```python
from codex_ml.data.local_files import load_json

# Load object
config = load_json("config.json")
# Returns: {"model": "gpt2", "lr": 0.001}

# Load array
data = load_json("data.json")
# Returns: [{"id": 1}, {"id": 2}]
```text

### load_csv

Load CSV as list of dictionaries:

```python
from codex_ml.data.local_files import load_csv

records = load_csv("data/dataset.csv")
# Returns: [{"text": "...", "label": "1"}, ...]

# Custom delimiter (TSV)
records = load_csv("data/dataset.tsv", delimiter='\t')
```text

## Saving Data

### save_jsonl

Save records to JSONL file:

```python
from codex_ml.data.local_files import save_jsonl

records = [
    {"text": "hello", "label": 0},
    {"text": "world", "label": 1},
]

save_jsonl(records, "output.jsonl")
```text

### save_json

Save data to JSON file:

```python
from codex_ml.data.local_files import save_json

config = {"model": "gpt2", "lr": 0.001}
save_json(config, "config.json")

# Custom indentation
save_json(config, "config.json", indent=4)
```text

### save_csv

Save records to CSV file:

```python
from codex_ml.data.local_files import save_csv

records = [
    {"text": "hello", "label": "1"},
    {"text": "world", "label": "0"},
]

save_csv(records, "output.csv")

# Custom fieldnames order
save_csv(records, "output.csv", fieldnames=["label", "text"])

# TSV format
save_csv(records, "output.tsv", delimiter='\t')
```text

## Usage Patterns

### Data Pipeline

```python
from codex_ml.data.local_files import load_jsonl, save_jsonl

# Load raw data
raw_data = load_jsonl("data/raw.jsonl")

# Process
processed_data = [
    {
        "text": record["text"].lower(),
        "label": int(record["label"])
    }
    for record in raw_data
]

# Save processed
save_jsonl(processed_data, "data/processed.jsonl")
```text

### Format Conversion

```python
from codex_ml.data.local_files import load_csv, save_jsonl

# Convert CSV to JSONL
records = load_csv("data/input.csv")
save_jsonl(records, "data/output.jsonl")
```text

### Configuration Management

```python
from codex_ml.data.local_files import load_json, save_json

# Load base config
base_config = load_json("configs/base.json")

# Override settings
run_config = {**base_config, "lr": 0.0001, "epochs": 20}

# Save run-specific config
save_json(run_config, "runs/exp_001/config.json")
```text

## Best Practices

### 1. Handle Missing Files

```python
from pathlib import Path
from codex_ml.data.local_files import load_jsonl

def load_data_safe(path):
    if not Path(path).exists():
        print(f"Warning: {path} not found")
        return []
    return load_jsonl(path)
```text

### 2. Validate Data Structure

```python
from codex_ml.data.local_files import load_jsonl

records = load_jsonl("data.jsonl")

# Validate required fields
for i, record in enumerate(records):
    if "text" not in record or "label" not in record:
        raise ValueError(f"Record {i} missing required fields")
```text

### 3. Use Type Conversion

```python
from codex_ml.data.local_files import load_csv

records = load_csv("data.csv")

# CSV values are strings - convert as needed
processed = [
    {
        "text": r["text"],
        "label": int(r["label"]),  # Convert to int
        "score": float(r["score"]) if r["score"] else None
    }
    for r in records
]
```text

### 4. Create Parent Directories

```python
from codex_ml.data.local_files import save_jsonl

# save_* functions create parent directories automatically
save_jsonl(records, "deep/nested/path/output.jsonl")
# Creates 'deep/nested/path' if it doesn't exist
```text

## Integration Examples

### With HuggingFace Datasets

```python
from datasets import load_dataset
from codex_ml.data.local_files import save_jsonl

# Download and cache locally
dataset = load_dataset("imdb", split="train")

# Convert to JSONL for offline use
records = [dict(example) for example in dataset]
save_jsonl(records, "cache/imdb_train.jsonl")

# Later: load from local cache
from codex_ml.data.local_files import load_jsonl
records = load_jsonl("cache/imdb_train.jsonl")
```text

### With Pandas

```python
import pandas as pd
from codex_ml.data.local_files import load_csv, save_csv

# Load as pandas DataFrame
records = load_csv("data.csv")
df = pd.DataFrame(records)

# Process
df["text_length"] = df["text"].str.len()

# Save back to CSV
save_csv(df.to_dict("records"), "data_processed.csv")
```text

### With Caching

```python
from pathlib import Path
from codex_ml.data.local_files import load_jsonl, save_jsonl

def load_or_process(input_path, cache_path):
    if Path(cache_path).exists():
        return load_jsonl(cache_path)
    
    # Process and cache
    raw_data = load_jsonl(input_path)
    processed = process_data(raw_data)
    save_jsonl(processed, cache_path)
    
    return processed
```text

## Performance Considerations

### Memory Usage

- **JSONL**: Loads all records into memory at once
- **Large Files**: Consider streaming for files > 1GB

### Streaming Alternative

For very large files, use generators:

```python
import json

def stream_jsonl(path):
    """Stream JSONL file line-by-line."""
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# Use with for loop
for record in stream_jsonl("large_file.jsonl"):
    process(record)
```text

## Troubleshooting

### UnicodeDecodeError

**Issue**: Cannot decode file

**Solution**: Specify encoding
```python
# Try different encoding
records = load_csv("data.csv", encoding='latin-1')
```text

### JSONDecodeError

**Issue**: Invalid JSON in file

**Solution**: Validate JSON first
```python
import json

def validate_jsonl(path):
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Line {i}: {e}")
```text

### Empty CSV Records

**Issue**: CSV has extra empty columns

**Solution**: Filter empty values
```python
records = load_csv("data.csv")
cleaned = [
    {k: v for k, v in record.items() if v}
    for record in records
]
```text

## See Also

- [Data Caching Guide](Caching.md)
- [Dataset Loading Guide](../guides/data_loading.md)
- [Performance Optimization](../guides/performance.md)
