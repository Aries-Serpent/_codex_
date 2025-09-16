# Example Training Configurations

The following configurations pair with the scripts under `examples/`:

* [`configs/training/base.yaml`](../../configs/training/base.yaml) – default
  configuration used by the CLI.
* [`examples/train_toy.py`](../../examples/train_toy.py) – inline config for a
  two-sample toy dataset.
* [`examples/chat_finetune.py`](../../examples/chat_finetune.py) – overrides the
  trainer registry to simulate chat fine-tuning.

Reference these from your own modules to keep docs, registries, and configs in
sync.
