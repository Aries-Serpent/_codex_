# Codex Implementation Plan: Track A (Atomic Diffs)

This plan enumerates the key diffs to be implemented for track A. Each bullet is a discrete change to be applied to the repository. All modifications must avoid enabling GitHub Actions or any cost-incurring pipelines.

- **Tokenizer Loader & API**: Replace the placeholder tokenizer loader in `tokenization/loader.py` with a proper loader using `tokenizers` and `transformers`. Accept a model name or vocab path from the config, and return a `PreTrainedTokenizerFast`. Update the FastAPI `/predict` endpoint in `src/codex/api/app.py` to call the model's `generate` with proper tokenization, instead of echoing input.

- **Training CLI & Checkpointing**: Create `cli/train_codex.py` that wraps the HuggingFace `Trainer`. Add config-driven arguments for model, dataset, hyperparameters, precision (fp16/bf16), gradient accumulation, and LoRA/PEFT toggles. Implement checkpoint saving and resuming via `codex_ml/training/checkpoint.py`.

- **Security Enforcement**: Add a runtime denylist loader (e.g., `codex_ml/security/denylist.py`) that loads blocked terms from `policies/denylist.yaml` and checks user prompts before passing them to the model. Integrate this check into the FastAPI layer.

- **Local Tests & Nox**: Add pytest tests in `tests/atomic_diffs/` covering tokenizer loading, API inference, checkpoint save/resume, and denylist enforcement. Update `nox_sessions/audit.py` to run these tests offline.

All changes must run locally and pass existing and new tests. After implementing these, update documentation accordingly.
