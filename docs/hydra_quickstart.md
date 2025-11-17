# Hydra Quickstart (Codex)

## Run with defaults
```bash
python -m codex_ml hydra-train
```text
Show composed config:
```bash
CODEX_SHOW_CFG=1 python -m codex_ml hydra-train
```text

## Override on the CLI
```bash
python -m codex_ml hydra-train train.epochs=3 data.batch_size=16
```text

## Multirun sweeps
```bash
python -m codex_ml -m train.epochs=1,2 data.batch_size=8,16
```text
See Hydra docs for defaults lists and multirun syntax.
