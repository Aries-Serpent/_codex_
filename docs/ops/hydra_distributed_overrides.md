<!-- BEGIN: CODEX_HYDRA_DISTRIBUTED_OVERRIDES -->

# Hydra Distributed Overrides

**Last Updated:** 2026-06-22

## torchrun (single node)

```text
torchrun --nproc_per_node=8 train.py trainer.gpus=8

```text
## multi-node

```text
torchrun --nnodes=2 --nproc_per_node=8 --rdzv_backend=c10d --rdzv_endpoint=$HOST:29400 train.py

```text
## tokenizer swap

```text
tokenizer.backend=sentencepiece tokenizer.vocab_size=32000

```text
