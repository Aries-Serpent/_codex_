# Example Training Configurations

The following configurations pair with the scripts under `examples/`:

* [`configs/training/base.yaml`](https://github.com/Aries-Serpent/_codex_/blob/main/configs/training/base.yaml) – default
  configuration used by the CLI.
* [`examples/train_toy.py`](https://github.com/Aries-Serpent/_codex_/blob/main/examples/train_toy.py) – inline config for a
  two-sample toy dataset.
* [`examples/chat_finetune.py`](https://github.com/Aries-Serpent/_codex_/blob/main/examples/chat_finetune.py) – overrides the
  trainer registry to simulate chat fine-tuning.

Reference these from your own modules to keep docs, registries, and configs in
sync.
