<!-- BEGIN: CODEX_HYDRA_DISTRIBUTED_OVERRIDES -->
# Hydra Distributed Overrides

## torchrun (single node)
```

torchrun --nproc_per_node=8 train.py trainer.gpus=8

```

## multi-node
```

torchrun --nnodes=2 --nproc_per_node=8 --rdzv_backend=c10d --rdzv_endpoint=$HOST:29400 train.py

```

## tokenizer swap
```

tokenizer.backend=sentencepiece tokenizer.vocab_size=32000

```
