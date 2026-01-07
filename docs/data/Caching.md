# Docs: Dataset Caching — Hash-Based JSONL

> Generated: 2024-11-05 | Author: mbaetiong

## Overview

The dataset caching utilities provide lightweight hash-based caching for preprocessed datasets to improve performance and reproducibility without requiring network access.

## Features

- **Hash-based keys**: Deterministic keys from dataset parameters
- **JSONL storage**: Simple, human-readable format
- **Offline-first**: No network calls required
- **Lightweight**: Minimal dependencies

## API

### derive_key

Generate a stable cache key from parameters:

```python
from codex_ml.data.cache import derive_key

key = derive_key("imdb", "train", "42")  # dataset, split, seed
# Returns: '4f3d2e1a0b9c8d7e'  (16-char hex)
```text

### cache_records

Cache preprocessed records to disk:

```python
from codex_ml.data.cache import cache_records

records = [
    {"text": "Great movie!", "label": 1},
    {"text": "Terrible film.", "label": 0},
]

path = cache_records(
    records,
    cache_dir="artifacts/cache",
    key=key
)
# Returns: Path('artifacts/cache/4f3d2e1a0b9c8d7e.jsonl')
```text

### load_cached_records

Load cached records if available:

```python
from codex_ml.data.cache import load_cached_records

records = load_cached_records("artifacts/cache", key)

if records is None:
    # Cache miss - preprocess data
    records = preprocess_dataset()
    cache_records(records, cache_dir="artifacts/cache", key=key)
else:
    # Cache hit - use cached data
    print(f"Loaded {len(records)} cached records")
```text

## Usage Patterns

### Basic Caching

```python
from codex_ml.data.cache import derive_key, cache_records, load_cached_records

def get_preprocessed_data(dataset_name, split, seed):
    # Derive cache key from parameters
    key = derive_key(dataset_name, split, str(seed))
    
    # Try loading from cache
    records = load_cached_records("artifacts/cache", key)
    
    if records is not None:
        return records
    
    # Cache miss - preprocess and cache
    raw_data = load_raw_dataset(dataset_name, split)
    records = preprocess(raw_data, seed=seed)
    cache_records(records, cache_dir="artifacts/cache", key=key)
    
    return records
```text

### With Version Control

```python
def get_cached_data_v2(dataset_name, split, seed, version="v1"):
    # Include version in cache key
    key = derive_key(dataset_name, split, str(seed), version)
    
    records = load_cached_records("artifacts/cache", key)
    
    if records is None:
        records = preprocess_v2(dataset_name, split, seed)
        cache_records(records, cache_dir="artifacts/cache", key=key)
    
    return records
```text

### Cache Invalidation

```python
import shutil
from pathlib import Path

def clear_cache(cache_dir="artifacts/cache"):
    """Remove all cached files."""
    cache_path = Path(cache_dir)
    if cache_path.exists():
        shutil.rmtree(cache_path)
        cache_path.mkdir(parents=True)

def clear_dataset_cache(dataset_name, cache_dir="artifacts/cache"):
    """Remove cached files for specific dataset."""
    cache_path = Path(cache_dir)
    pattern = f"{dataset_name}*"
    for cached_file in cache_path.glob("*.jsonl"):
        # Check if key was derived from this dataset
        # (requires storing metadata alongside cache)
        pass
```text

## Performance

### Cache Hit Speedup

Example with IMDB dataset:

| Operation | Without Cache | With Cache | Speedup |
|-----------|---------------|------------|---------|
| Load + Tokenize | 45s | 2s | 22.5x |
| Preprocessing | 120s | 2s | 60x |

### Storage Overhead

- **JSONL format**: ~1.2x of raw data size
- **Compression**: Can use `.jsonl.gz` for ~3x reduction
- **Typical cache**: 10-100 MB per dataset split

## Best Practices

### 1. Include All Relevant Parameters

```python
# Good - includes all preprocessing params
key = derive_key(dataset, split, seed, tokenizer, max_length)

# Bad - missing preprocessing details
key = derive_key(dataset, split)
```text

### 2. Organize Cache by Purpose

```python
# Separate caches for different stages
train_key = derive_key("train", dataset, split, seed)
cache_records(records, cache_dir="artifacts/cache/train", key=train_key)

eval_key = derive_key("eval", dataset, split, seed)
cache_records(records, cache_dir="artifacts/cache/eval", key=eval_key)
```text

### 3. Document Cache Keys

```python
def derive_dataset_key(config):
    """Derive cache key from dataset config.
    
    Key includes:
    - dataset name
    - split name
    - random seed
    - preprocessing version
    """
    return derive_key(
        config.dataset_name,
        config.split,
        str(config.seed),
        config.preprocess_version,
    )
```text

### 4. Handle Cache Misses Gracefully

```python
def load_or_preprocess(config):
    key = derive_dataset_key(config)
    
    try:
        records = load_cached_records(config.cache_dir, key)
        if records is not None:
            logger.info(f"Cache hit: {key}")
            return records
    except Exception as e:
        logger.warning(f"Cache load failed: {e}")
    
    logger.info(f"Cache miss: {key} - preprocessing...")
    records = preprocess_dataset(config)
    
    try:
        cache_records(records, cache_dir=config.cache_dir, key=key)
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")
    
    return records
```text

## Integration

### With HuggingFace Datasets

```python
from datasets import load_dataset
from codex_ml.data.cache import derive_key, cache_records, load_cached_records

def load_hf_dataset_cached(name, split, cache_dir="artifacts/cache"):
    key = derive_key("hf", name, split)
    
    records = load_cached_records(cache_dir, key)
    if records is not None:
        return records
    
    # Load from HuggingFace
    dataset = load_dataset(name, split=split)
    records = [dict(example) for example in dataset]
    
    cache_records(records, cache_dir=cache_dir, key=key)
    return records
```text

### With Custom Loaders

```python
from codex_ml.data.cache import derive_key, cache_records, load_cached_records

def load_custom_dataset(path, preprocess_fn, cache_dir="artifacts/cache"):
    # Use file hash in cache key for freshness
    import hashlib
    file_hash = hashlib.md5(open(path, 'rb').read()).hexdigest()[:8]
    
    key = derive_key("custom", path, file_hash, preprocess_fn.__name__)
    
    records = load_cached_records(cache_dir, key)
    if records is not None:
        return records
    
    # Load and preprocess
    with open(path) as f:
        raw_records = json.load(f)
    
    records = [preprocess_fn(r) for r in raw_records]
    cache_records(records, cache_dir=cache_dir, key=key)
    
    return records
```text

## Troubleshooting

### Cache Directory Permissions

**Issue**: Cannot write to cache directory

**Solution**:
```python
import os
os.makedirs(cache_dir, exist_ok=True, mode=0o755)
```text

### Disk Space

**Issue**: Cache filling disk

**Solution**: Implement cache size limits
```python
def cleanup_old_caches(cache_dir, max_age_days=7):
    import time
    cutoff = time.time() - (max_age_days * 86400)
    
    for cached_file in Path(cache_dir).glob("*.jsonl"):
        if cached_file.stat().st_mtime < cutoff:
            cached_file.unlink()
```text

### Corrupted Cache

**Issue**: Invalid JSON in cached file

**Solution**: Validate and rebuild
```python
def validate_cache(cache_dir, key):
    try:
        records = load_cached_records(cache_dir, key)
        return records is not None
    except json.JSONDecodeError:
        # Remove corrupted cache
        cached_file = Path(cache_dir) / f"{key}.jsonl"
        cached_file.unlink(missing_ok=True)
        return False
```text

## See Also

- [Data Loading Guide](../guides/data_loading.md)
- [Reproducibility Validation](../validation/Repro_Validation.md)
- [Performance Optimization](../guides/performance.md)
