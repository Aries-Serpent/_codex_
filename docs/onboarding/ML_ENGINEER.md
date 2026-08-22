# ML engineer

## Where to start

Choose a dependency profile in the [profile quick start](../QUICKSTART_BY_PROFILE.md),
then review the ML/RAG layer in the
[repository explanation](../REPOSITORY_EXPLANATION.md#4-canonical-five-layer-architecture).

## Where the code lives

- `src/codex_ml/`: training, evaluation, data, models, inference, serving, and plugins
- `src/rag/`: retrieval, embedding, indexing, and evaluation
- `training/` and `tokenization/`: installed root packages explicitly mapped by
  `pyproject.toml`
- `configs/`: Hydra-compatible profiles and schemas
- `tests/`: unit and integration coverage for those packages

## What this role cares about

Reproducible configuration, offline-safe tests, deterministic evaluation, optional
dependency boundaries, checkpoint compatibility, and CPU-friendly validation.

## Key technologies

PyTorch, Transformers, Datasets, Accelerate, PEFT, scikit-learn,
SentenceTransformers, FAISS, ChromaDB, Hydra, OmegaConf, MLflow, and Ray Serve.

## Typical workflow

1. Use `runtime` for inference/RAG work or `full` for training and development.
2. Select or add configuration under `configs/`.
3. Work inside the relevant `src/` package and its focused tests.
4. Validate locally without requiring model downloads or network access in CI.
5. Run the relevant ML tests before broader project validation.

## Common gotchas

- Base dependencies are always installed; extras add capabilities rather than replacing
  the base set.
- `runtime` includes substantial ML and serving dependencies; it is not a minimal
  training-only profile.
- `full` is the profile that includes test and quality tooling.
- CI-facing ML components must not download models or data unless an explicit,
  documented opt-in permits network access.
