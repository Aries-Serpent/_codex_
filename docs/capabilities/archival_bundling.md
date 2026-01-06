# Archival & Bundling Capability Guide

## Overview

The **archival-bundling** capability provides comprehensive functionality for packaging, versioning, and archiving ML artifacts including models, datasets, configurations, and experiment results. This system ensures reproducibility by creating self-contained archives that capture all dependencies and metadata needed to recreate experimental conditions.

See [Bundle Builder Spec](bundle_builder_spec.md) for the formal bundle model,
manifest schema, and UI projection map used by Create Agent workflows.

### Purpose

- **Reproducibility**: Bundle all artifacts needed to reproduce experiments
- **Version Control**: Track artifact versions with metadata
- **Portability**: Create self-contained packages for sharing
- **Compliance**: Meet data retention and audit requirements
- **Efficiency**: Compress and deduplicate artifacts

### Key Components

1. **Artifact Bundler**: Packages models, configs, data
2. **Version Tracker**: Maintains artifact lineage
3. **Compression Engine**: Efficient storage with deduplication
4. **Metadata Manager**: Captures provenance and dependencies
5. **Archive Store**: Organized storage with retrieval

---

## Architecture

### Bundling Pipeline

```
┌─────────────┐
│   Source    │
│  Artifacts  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Metadata   │◄── Environment Info
│ Collection  │◄── Dependency List
└──────┬──────┘◄── Git Info
       │
       ▼
┌─────────────┐
│  Packaging  │
│   Engine    │──► Compression
└──────┬──────┘──► Deduplication
       │
       ▼
┌─────────────┐
│   Archive   │
│   Storage   │──► Local/Remote
└─────────────┘
```

### Bundle Structure

```
experiment_bundle_v1.0.0.tar.gz
├── manifest.json          # Bundle metadata
├── models/
│   ├── model.pkl
│   └── model_config.json
├── data/
│   ├── train_dataset.parquet
│   └── validation_dataset.parquet
├── configs/
│   ├── hyperparameters.yaml
│   └── training_config.yaml
├── environment/
│   ├── requirements.txt
│   ├── environment.yaml
│   └── system_info.json
├── code/
│   ├── training_script.py
│   └── preprocessing.py
└── logs/
    ├── training.log
    └── metrics.json
```

---

## API Reference

### Core Functions

#### `bundle_experiment()`
Create a complete experiment bundle with all artifacts.

```python
from codex.archival import bundle_experiment

# Bundle current experiment
bundle = bundle_experiment(
    experiment_id="exp_2025_01_15",
    include_data=True,
    include_code=True,
    include_environment=True,
    compression="gzip",
    dedup=True
)

# Returns: BundleMetadata
# bundle.path: "/artifacts/bundles/exp_2025_01_15_v1.0.0.tar.gz"
# bundle.size: 1024567890  # bytes
# bundle.checksum: "sha256:abc123..."
```

#### `create_bundle()`
Create a custom bundle with specific artifacts.

```python
from codex.archival import create_bundle

# Custom bundle
bundle = create_bundle(
    name="model_deployment_v2",
    artifacts=[
        {"type": "model", "path": "model.pkl"},
        {"type": "config", "path": "config.yaml"},
        {"type": "preprocessor", "path": "preprocessor.pkl"}
    ],
    metadata={
        "purpose": "production_deployment",
        "version": "2.0.0",
        "approved_by": "ml_team"
    }
)
```

#### `extract_bundle()`
Extract and restore artifacts from a bundle.

```python
from codex.archival import extract_bundle

# Extract bundle
artifacts = extract_bundle(
    bundle_path="exp_2025_01_15_v1.0.0.tar.gz",
    output_dir="/restored/exp_2025_01_15",
    verify_checksums=True
)

# Access extracted artifacts
model = artifacts.models["model.pkl"]
config = artifacts.configs["hyperparameters.yaml"]
```

#### `list_bundles()`
Query available bundles with filtering.

```python
from codex.archival import list_bundles

# List recent bundles
bundles = list_bundles(
    experiment_pattern="exp_2025_*",
    min_date="Previous Cycle-01-01",
    max_date="Previous Cycle-01-31",
    sort_by="created",
    limit=10
)

for bundle in bundles:
    print(f"{bundle.name}: {bundle.size_mb}MB, {bundle.created}")
```

---

## Configuration

### Bundle Settings

```yaml
# configs/archival.yaml (canonical location; example schema)
archival:
  # Storage location
  storage:
    local: /data/artifacts/bundles
    remote: s3://ml-artifacts/bundles
    
  # Compression settings
  compression:
    algorithm: gzip  # gzip, bzip2, xz, lz4
    level: 6         # 1-9 for gzip
    
  # Deduplication
  deduplication:
    enabled: true
    block_size: 4096
    hash_algorithm: sha256
    
  # Metadata
  metadata:
    include_git_info: true
    include_environment: true
    include_dependencies: true
    include_system_info: true
    
  # Retention policy
  retention:
    keep_latest: 10
    keep_days: 90
    cleanup_interval: 86400  # seconds
```

### Environment Variables

```bash
# Storage paths
export CODEX_BUNDLE_DIR="/data/artifacts/bundles"
export CODEX_REMOTE_STORE="s3://ml-artifacts/bundles"

# Compression
export CODEX_COMPRESSION="gzip"
export CODEX_COMPRESSION_LEVEL="6"

# Deduplication
export CODEX_DEDUP_ENABLED="true"
```

---

## Usage Examples

### Example 1: Bundle Training Experiment

```python
from codex.archival import bundle_experiment
from codex.training import Trainer

# Train model
trainer = Trainer(config="config.yaml")
results = trainer.train()

# Bundle everything
bundle = bundle_experiment(
    experiment_id=trainer.experiment_id,
    include_data=True,          # Include datasets
    include_code=True,          # Include training scripts
    include_environment=True,   # Include dependencies
    include_logs=True,          # Include training logs
    compression="gzip",
    metadata={
        "model_type": "transformer",
        "dataset": "wikitext-103",
        "final_loss": results.final_loss,
        "training_time": results.elapsed_time
    }
)

print(f"Bundle created: {bundle.path}")
print(f"Size: {bundle.size_mb:.2f} MB")
print(f"Checksum: {bundle.checksum}")
```

### Example 2: Version Comparison Bundle

```python
from codex.archival import create_bundle, compare_bundles

# Bundle model v1
bundle_v1 = create_bundle(
    name="model_comparison",
    version="1.0.0",
    artifacts=[
        {"type": "model", "path": "model_v1.pkl"},
        {"type": "metrics", "path": "metrics_v1.json"}
    ]
)

# Bundle model v2
bundle_v2 = create_bundle(
    name="model_comparison",
    version="2.0.0",
    artifacts=[
        {"type": "model", "path": "model_v2.pkl"},
        {"type": "metrics", "path": "metrics_v2.json"}
    ]
)

# Compare bundles
diff = compare_bundles(bundle_v1, bundle_v2)
print(f"Size delta: {diff.size_delta_mb:.2f} MB")
print(f"Metric improvement: {diff.metric_delta}")
```

### Example 3: Restore from Archive

```python
from codex.archival import extract_bundle, validate_bundle

# Validate bundle integrity
validation = validate_bundle("exp_2025_01_15_v1.0.0.tar.gz")
if not validation.valid:
    print(f"Bundle corrupted: {validation.errors}")
    exit(1)

# Extract bundle
artifacts = extract_bundle(
    bundle_path="exp_2025_01_15_v1.0.0.tar.gz",
    output_dir="/tmp/restored",
    verify_checksums=True,
    restore_environment=True  # Recreate conda env
)

# Use restored artifacts
from codex.models import load_model

model = load_model(artifacts.models["model.pkl"])
config = artifacts.configs["training_config.yaml"]

# Resume training from checkpoint
trainer = Trainer(config=config)
trainer.load_checkpoint(artifacts.checkpoints["latest.ckpt"])
trainer.resume_training()
```

### Example 4: Automated Archival Pipeline

```python
from codex.archival import BundleManager
from datetime import datetime, timedelta

# Create bundle manager
manager = BundleManager(storage_dir="/data/bundles")

# Auto-archive completed experiments
def archive_completed_experiments():
    experiments = manager.list_experiments(status="completed")
    
    for exp in experiments:
        # Bundle if not already bundled
        if not manager.has_bundle(exp.id):
            bundle = manager.bundle_experiment(
                experiment_id=exp.id,
                compression="gzip",
                dedup=True
            )
            print(f"Bundled {exp.id}: {bundle.size_mb:.2f}MB")

# Cleanup old bundles
def cleanup_old_bundles():
    cutoff_date = datetime.now() - timedelta(days=90)
    
    old_bundles = manager.list_bundles(max_date=cutoff_date)
    for bundle in old_bundles:
        if bundle.retention_policy == "delete":
            manager.delete_bundle(bundle.id)
            print(f"Deleted old bundle: {bundle.name}")

# Run archival pipeline
archive_completed_experiments()
cleanup_old_bundles()
```

---

## Best Practices

### Bundling Strategy

1. **Include Essential Artifacts**
   - Model files and weights
   - Training configurations
   - Preprocessing code
   - Environment specifications
   - Validation metrics

2. **Metadata Capture**
   - Git commit hash for code version
   - Dataset versions and checksums
   - Training timestamps
   - Hardware specifications
   - Hyperparameters used

3. **Deduplication**
   - Enable for large datasets
   - Use block-level dedup for efficiency
   - Store only deltas between versions

4. **Compression Balance**
   - Higher compression for archival
   - Lower compression for frequent access
   - Consider trade-offs (time vs space)

### Version Management

1. **Semantic Versioning**
   ```
   v<major>.<minor>.<patch>
   v1.0.0 - Initial model
   v1.1.0 - Added feature
   v2.0.0 - Architecture change
   ```

2. **Tagging Bundles**
   - Tag important milestones
   - Mark production deployments
   - Label baseline models

3. **Retention Policies**
   - Keep latest N versions
   - Archive after time period
   - Never delete production bundles

### Security & Compliance

1. **Access Control**
   - Restrict bundle access by role
   - Audit bundle access logs
   - Encrypt sensitive bundles

2. **Data Privacy**
   - Remove PII before bundling
   - Comply with data retention policies
   - Document data lineage

3. **Integrity Verification**
   - Always verify checksums
   - Sign bundles for authenticity
   - Detect tampering

---

## Troubleshooting

### Common Issues

#### Bundle Too Large

**Problem**: Bundle size exceeds storage limits.

**Solutions**:
- Enable deduplication
- Increase compression level
- Exclude large intermediate files
- Use remote storage

```python
# High compression for large bundles
bundle = bundle_experiment(
    experiment_id="large_exp",
    compression="xz",          # Better compression
    compression_level=9,        # Maximum
    dedup=True,                # Deduplicate
    exclude_patterns=["*.tmp", "cache/*"]
)
```

#### Extraction Failures

**Problem**: Bundle fails to extract completely.

**Solutions**:
- Check disk space
- Verify bundle integrity
- Check file permissions
- Use recovery mode

```python
# Extract with recovery
artifacts = extract_bundle(
    bundle_path="corrupted_bundle.tar.gz",
    output_dir="/tmp/recovery",
    verify_checksums=False,  # Skip if corrupt
    continue_on_error=True   # Extract what's possible
)
```

#### Missing Dependencies

**Problem**: Restored experiment missing dependencies.

**Solutions**:
- Include environment spec in bundle
- Use conda pack for environments
- Document external dependencies

```python
# Bundle with full environment
bundle = bundle_experiment(
    experiment_id="exp_001",
    include_environment=True,
    pack_environment=True,  # Include conda env
    freeze_pip=True         # Freeze pip deps
)
```

---

## Keywords

archival, bundling, packaging, versioning, artifacts, reproducibility, compression, deduplication, metadata, provenance, storage, backup, restore, snapshot, checkpoint, archive

---

## Related Capabilities

- **checkpointing**: Training checkpoint management
- **reproducibility**: Experiment reproducibility
- **experiment-management**: Experiment tracking
- **version-control**: Code and data versioning

---

## References

- [Artifact Management Reference](../reference/artifacts.md)
- [Artifact Bundle Specification](../ops/artifacts_bundle_spec.md)
- [Reproducibility Guide](reproducibility.md)
- [Experiment Management](experiment_management.md)
