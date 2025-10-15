# [Guide]: Hydra Quickstart — Defaults and Sweeps
> Generated: 2025-10-14 21:10:31 UTC | Author: mbaetiong
🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Baseline run (defaults)
- Config file: configs/default.yaml (safe, offline)
- Example:
```bash
python -m codex_ml.cli.hydra_main --config-path configs --config-name default
```

## Override examples
- Change learning rate and epochs:
```bash
python -m codex_ml.cli.hydra_main --config-path configs --config-name default learning_rate=3e-5 epochs=2
```

## Multirun (sweep) examples
- Sweep learning rate and batch size (offline):
```bash
python -m codex_ml.cli.hydra_main --multirun \
  --config-path configs --config-name default \
  learning_rate=1e-5,3e-5,5e-5 \
  batch_size=2,4
```

- Sweep LoRA flags (if PEFT available; otherwise ignored gracefully):
```bash
python -m codex_ml.cli.hydra_main --multirun \
  --config-path configs --config-name default \
  use_lora=true,false \
  lora_rank=4,8
```

## Tips
- Determinism: configs/default.yaml sets seed and deterministic=true. Keep PYTHONHASHSEED=0 and pytest-randomly for tests.
- Offline: tracking backends disabled by default; re-enable by setting logging.* to true.
- GPU runs: set device=cuda and ensure torch with CUDA is available locally.

*End*
