<!-- BEGIN: CODEX_HYDRA_DISTRIBUTED_OVERRIDES -->

# Hydra Distributed Overrides

## torchrun (single node)

```text
torchrun --nproc_per_node=8 train.py trainer.gpus=8

```
## multi-node

```text
torchrun --nnodes=2 --nproc_per_node=8 --rdzv_backend=c10d --rdzv_endpoint=$HOST:29400 train.py

```
## tokenizer swap

```text
tokenizer.backend=sentencepiece tokenizer.vocab_size=32000

```