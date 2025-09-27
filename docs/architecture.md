# Architecture Overview

This page sketches the core components and their relationships.

```mermaid
classDiagram
    class TrainingEngine {
      +run(cfg)
      +evaluate()
    }
    class DataHandling {
      +iter_jsonl(path)
      +deterministic_split(items, seed)
    }
    class Metrics {
      +batch_metrics(outputs, batch)
    }
    class Checkpointing {
      +save_checkpoint(...)
      +load_checkpoint(...)
    }
    class Logging {
      +TBWriter
      +maybe_wandb
    }
    class Safety {
      +sanitize_prompt(text, policy)
    }
    TrainingEngine --> DataHandling
    TrainingEngine --> Metrics
    TrainingEngine --> Checkpointing
    TrainingEngine --> Logging
    TrainingEngine --> Safety
```

## Runtime flow

```mermaid
flowchart LR
    A[Ingestion] --> B[Tokenizer]
    B --> C[Datasets]
    C --> D[Model Loader]
    D --> E{Training Engine}
    E --> F[Metrics]
    F --> G[Logging]
    G --> H[Experiment Tracking]
    E --> I[Checkpoint Manager]
```

**Legend**

- Solid nodes are required.
- Dashed arrows/nodes (not shown) can represent optional components such as LoRA/PEFT adapters, offline trackers (TensorBoard, MLflow, W&B), and the async NDJSON writer.

The flow begins with raw data ingestion, followed by tokenization and dataset creation. A model loader prepares either a tiny in-repo model or a cached Hugging Face checkpoint. The training engine (HF Trainer or a custom loop) consumes datasets and produces metrics. Metrics feed into logging and optional experiment tracking backends while checkpoints enable resume and evaluation.
