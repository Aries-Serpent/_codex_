# Troubleshooting Guide

**Last Updated:** 2026-06-22

## Common Issues and Solutions

### Installation & Setup

#### 1. Python Version Incompatibility

**Error**: `ModuleNotFoundError: No module named 'codex_ml'`

**Cause**: Python version < 3.11 or incorrect environment

**Solution**:
```bash
# Check Python version
python --version  # Should be 3.11+

# Create fresh virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. CUDA/GPU Not Detected

**Error**: `cuda is not available` or `No CUDA devices found`

**Causes**:
- PyTorch installed without CUDA support
- NVIDIA drivers not installed
- CUDA not in PATH

**Solution**:
```bash
# Verify NVIDIA drivers
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA availability in Python
python -c "import torch; print(torch.cuda.is_available())"
```

## 3. Dependency Conflicts

**Error**: `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed`

**Solution**:
```bash
# Use exact requirements-lock file if available
pip install -r requirements/requirements-lock.txt

# Or install minimal requirements first
pip install -r requirements-minimal.txt
pip install -r requirements-ml-lite.txt
```

## Data Processing

### 4. Encoding Detection Failures

**Error**: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x...`

**Cause**: File has non-UTF-8 encoding

**Solution**:
```python
from src.ingestion.pipeline import PipelineConfig, IngestionPipeline

# Specify encoding explicitly
config = PipelineConfig(encoding='latin-1')  # or 'iso-8859-1', 'cp1252'
pipeline = IngestionPipeline(config)
result = pipeline.ingest_file('data.csv')

# Or use auto-detection with validation disabled
config = PipelineConfig(encoding='auto', validate_utf8=False)
pipeline = IngestionPipeline(config)
```

## 5. File Size Exceeds Maximum

**Error**: `ValueError: File size exceeds maximum (100 MB)`

**Cause**: Input file larger than max_file_size_mb

**Solution**:
```python
# Option 1: Increase limit (careful with memory)
config = PipelineConfig(max_file_size_mb=500)
pipeline = IngestionPipeline(config)

# Option 2: Stream large files (memory-efficient)
for batch in pipeline.stream_records('large_file.csv'):
    process_batch(batch)

# Option 3: Split file first
from src.ingestion.split import split_file
split_file('large_file.csv', 'split_output/', chunk_size=50_000)
```

## 6. Empty Records After Processing

**Error**: All records skipped; `result.records_skipped == input_size`

**Cause**: Transformation function returns None or skip conditions too strict

**Solution**:
```python
def transform(record):
    # Ensure you return a record, not None
    return {
        'text': record.get('text', ''),
        'label': int(record.get('label', 0))
    }

config = PipelineConfig(skip_empty=False)  # Don't skip empty
pipeline = IngestionPipeline(config)
result = pipeline.ingest_file('data.csv', transform_fn=transform)
```

### Model Training

#### 7. Out of Memory (OOM) During Training

**Error**: `RuntimeError: CUDA out of memory. Tried to allocate 2.00 GB`

**Solutions** (in order of preference):

```bash
# 1. Reduce batch size
python train.py training.batch_size=16

# 2. Enable gradient accumulation
python train.py training.batch_size=32 \
               training.gradient_accumulation_steps=2

# 3. Enable mixed precision (16-bit)
python train.py training.mixed_precision=fp16

# 4. Enable gradient checkpointing
python train.py training.gradient_checkpointing=true

# 5. Use smaller model
python train.py model.name=distilbert-base-uncased

# 6. Clear cache
python -c "import torch; torch.cuda.empty_cache()"
```

## 8. Training Diverges (Loss becomes NaN)

**Error**: `loss: nan`, training unstable

**Causes**: Learning rate too high, exploding gradients, bad data

**Solutions**:
```bash
# 1. Reduce learning rate
python train.py training.learning_rate=1e-6

# 2. Increase warmup
python train.py training.warmup_steps=2000 \
               training.warmup_ratio=0.5

# 3. Clip gradients
python train.py training.max_grad_norm=0.5

# 4. Check data quality
python scripts/validate_data.py data/train.jsonl

# 5. Use smaller batch size for stability
python train.py training.batch_size=16
```

## 9. Model Not Improving

**Error**: Validation loss plateaus, no improvement

**Solutions**:
```bash
# 1. Increase learning rate (if too small)
python train.py training.learning_rate=5e-5

# 2. Adjust scheduler
python train.py scheduler.type=cosine \
               scheduler.num_cycles=1.0

# 3. Use different optimizer
python train.py optimizer.type=adamw \
               optimizer.betas=[0.8,0.99]

# 4. Add regularization
python train.py training.weight_decay=0.1 \
               training.dropout=0.3

# 5. Train longer
python train.py training.num_epochs=5
```

## RAG & Retrieval

### 10. Slow Retrieval Performance

**Error**: Each query takes >5 seconds

**Cause**: Large index size, inappropriate index type

**Solutions**:
```python
from src.rag.pipelines.retrieval import RetrieverPipeline

# 1. Use HNSW (faster) instead of flat
retriever = RetrieverPipeline(
    index_type='hnsw',
    ef_construction=400
)

# 2. Reduce k (return fewer results)
results = retriever.retrieve(query, k=3)  # Instead of k=10

# 3. Add similarity threshold
retriever = RetrieverPipeline(
    similarity_threshold=0.5  # Ignore low-similarity results
)

# 4. Use approximate search
results = retriever.retrieve(query, ef_search=20)  # Faster but less accurate
```

## 11. Irrelevant Retrieval Results

**Error**: Retrieved documents don't match query

**Causes**: Poor embeddings, suboptimal chunking, wrong similarity metric

**Solutions**:
```python
from src.rag.pipelines.chunking import ChunkingPipeline
from src.rag.pipelines.embedding import EmbeddingPipeline

# 1. Improve chunking
chunker = ChunkingPipeline(
    chunk_size=256,  # Smaller chunks
    overlap=100,     # More overlap
    split_method='sentence'
)

# 2. Use better embeddings
embedder = EmbeddingPipeline(
    model_name='sentence-transformers/all-mpnet-base-v2'  # Better model
)

# 3. Increase k to see more options
results = retriever.retrieve(query, k=20)
# Users can choose better matches

# 4. Re-rank results
from src.rag.reranker import CrossEncoderReranker
reranker = CrossEncoderReranker()
reranked = reranker.rerank(query, results)
```

## Configuration

### 12. Config Errors

**Error**: `KeyError: 'training'` or invalid config

**Cause**: Missing or malformed YAML

**Solution**:
```bash
# Validate config
python -c "from omegaconf import OmegaConf; \
          cfg = OmegaConf.load('config.yaml'); \
          print(OmegaConf.to_yaml(cfg))"

# Use provided configs
python train.py --config-name default

# Override with basic values
python train.py +training.batch_size=32 +training.learning_rate=2e-5
```

## 13. Interpolation Issues

**Error**: `MissingMandatoryValue` or unresolved references

**Cause**: Referenced key doesn't exist

**Solution**:
```yaml
# Bad
output_dir: ${model.name}/${experiment}
# Error if 'experiment' not defined

# Good
output_dir: ${model.name}/${experiment:default_exp}
# Uses 'default_exp' if 'experiment' not defined

# Or define explicitly
experiment: exp_001
output_dir: ${model.name}/${experiment}
```

## Performance

### 14. Slow Data Loading

**Error**: Training bottlenecked by I/O

**Causes**: Too many workers, slow storage, unoptimized format

**Solutions**:
```bash
# 1. Increase number of workers
python train.py data.num_workers=16

# 2. Pre-load data to RAM (if fits)
python preload_data.py data/train.jsonl data/train_cached.bin

# 3. Use faster format (Parquet instead of JSONL)
python convert_to_parquet.py data/train.jsonl data/train.parquet

# 4. Enable prefetching
python train.py data.prefetch_factor=4
```

## 15. Slow Inference

**Error**: Model prediction takes too long

**Cause**: Batch size too small, inefficient code

**Solution**:
```python
# Batch predictions
texts = ["text1", "text2", "text3"]
predictions = model.predict(texts)  # Batch of 3

# Instead of
for text in texts:
    pred = model.predict([text])  # 3 separate calls

# Use quantization
model = quantize_model(model)  # 4x faster
```

## Debugging

### Getting Help

**Before reporting issues:**
```bash
# 1. Collect system info
python scripts/collect_debug_info.py > debug_info.txt

# 2. Check logs
tail -100 logs/train.log

# 3. Reproduce with minimal example
python minimal_example.py

# 4. Check GitHub issues
# https://github.com/Aries-Serpent/_codex_/issues

# 5. Join discussions
# https://github.com/Aries-Serpent/_codex_/discussions
```

## Enabling Verbose Logging

```text
import logging

# Set to DEBUG for detailed information
logging.basicConfig(level=logging.DEBUG)

# Or via config
logging:
  level: DEBUG
  log_dir: ./logs_debug
```

## Common Warning Messages

**Warning**: `Some weights of BertForSequenceClassification were not initialized`

- Normal when fine-tuning
- Uninitialized layers get random weights
- Safe to ignore if you're training

**Warning**: `Gradients not accumulating correctly`

- Check gradient_accumulation_steps configuration
- Ensure optimizer.zero_grad() called correctly

## Performance Benchmarks

### Typical Performance

| Task | GPU | Time | Notes |
|------|-----|------|-------|
| Ingest 100K CSV | CPU | ~30s | Depends on encoding |
| Generate embeddings (100K docs) | V100 | ~2m | Model: all-MiniLM-L6-v2 |
| Retrieve with HNSW | CPU | 5-10ms | Per query |
| Train BERT epoch | 4x A100 | ~1h | 500K samples, batch 128 |
| Inference batch (1K) | V100 | ~2s | Seq length 512 |

## Getting More Help

- **Documentation**: https://aries-serpent.github.io/_codex_/
- **Issues**: https://github.com/Aries-Serpent/_codex_/issues
- **Discussions**: https://github.com/Aries-Serpent/_codex_/discussions
- **Email**: support@codex-ml.dev

## See Also

- [Quickstart Guide](./QUICKSTART.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
