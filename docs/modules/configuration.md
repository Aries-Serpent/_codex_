# Configuration Hierarchy

`_codex_` uses [Hydra](https://hydra.cc) for configuration management.  The
root configuration file is `configs/config.yaml` which composes a series of
group configurations via its `defaults` list:

```yaml
defaults:
  - env: ubuntu
  - model: base
  - data: base
  - logging: base
  - training: base
  - tokenization: base
  - tracking: base
```

Each item corresponds to a directory under `configs/` containing one or more
YAML files.  For example, `configs/model/base.yaml` defines the default model
settings and can be overridden on the command line:

```bash
python -m codex_ml.cli.main model.name=MiniLM training.epochs=1
```

### Fallback Loader

Some lightweight scripts may operate without Hydra.  These call
`codex_ml.utils.config_loader.load_training_cfg`, which attempts to compose the
Hydra config but falls back to a minimal dictionary when Hydra is not
available.  This ensures offline operation while preserving a consistent
interface.

### Adding New Groups

To introduce a new configuration group:

1. Create a directory under `configs/<group_name>/` containing a `base.yaml`.
2. Reference the group in `configs/config.yaml`'s `defaults` list.
3. Document the available keys in this file.

Hydra's override syntax (`group.option=value`) allows experimentation without
editing YAML files directly.
