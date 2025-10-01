# Hydra overrides: the fast track

Codex uses a minimal **defaults list** so you can compose configs and tweak
parameters straight from the command line. The root defaults live in
`conf/config.yaml`:

```yaml
# conf/config.yaml (root defaults list)
defaults:
  - override hydra/job_logging: disabled   # silence Hydra's verbose logging
  - trainer: base                         # pull in conf/trainer/base.yaml
  - _self_                                # keep the current file last
```

What each entry provides:

| Default | Purpose |
| --- | --- |
| `override hydra/job_logging: disabled` | Keeps Hydra job logs quiet so our structured logging stays readable. |
| `trainer: base` | Seeds runtime values (seed, deterministic toggle, log formats) from `conf/trainer/base.yaml`. |
| `_self_` | Ensures inline keys in `config.yaml` win over group defaults. |

The `trainer/base` preset expands to:

```yaml
# conf/trainer/base.yaml
seed: 42
deterministic: false
log:
  dir: logs
  formats:
    - ndjson
```

### Fresh override examples

```bash
# change seed and enable deterministic mode (mirrors the trainer defaults list)
codex-train trainer.seed=1234 trainer.deterministic=true

# switch metrics sink to both NDJSON and CSV without editing YAML
codex-train trainer.log.formats='["ndjson","csv"]'

# disable MLflow explicitly when running air-gapped
codex-train logging.mlflow_uri=null logging.mlflow_enable=false

# compose the offline sweep preset and keep epochs at one
python -m codex_ml.cli.hydra_main --config-path conf/examples --config-name sweep_offline \
  training.max_epochs=1
```

Hydra understands `dot.path=value` for single values, `node=[a,b]` for lists, and
`foo.bar='{json:1}'` when you need structured overrides. See the Hydra docs for
the full grammar; the snippets above map 1:1 to our defaults list.

> **Tip**: combine overrides with `--config-name` to swap entire component trees,
> then override individual leaves as needed.

***
ENDNOTES: Hydra defaults list & override syntax
***
