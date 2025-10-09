# Hydra Defaults & Sweeps

Codex ML relies on Hydra's [Defaults List](https://hydra.cc/docs/advanced/defaults_list/) to compose runtime configuration and supports Hydra's multirun sweeps.

Example defaults list:

```yaml
# configs/defaults.yaml
defaults:
  - data: tiny
  - model: toy
  - train: small
  - tracking: offline
  - _self_
```

Run with inline overrides:

```bash
python -m codex_ml.cli.hydra_main train.epochs=2 data.batch_size=32
```

Launch a grid sweep:

```bash
python -m codex_ml.cli.hydra_main -m train.epochs=1,2 data.batch_size=8,16
```

Inspect the composed defaults:

```bash
python -m codex_ml.cli.config --info defaults
```

Hydra documentation covers [configuration composition](https://hydra.cc/docs/advanced/defaults_list/) and [multirun syntax](https://hydra.cc/docs/intro/examples/compose_your_config/).
