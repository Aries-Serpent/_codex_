# Hydra overrides: the fast track

Codex uses a minimal **defaults list** so you can compose configs and tweak
parameters straight from the command line. The root defaults live in
`configs/base/hydra.yaml`:

```yaml
# configs/base/hydra.yaml (root defaults list)
defaults:
  - override hydra/job_logging: disabled   # silence Hydra's verbose logging
  - trainer: base                         # pull in configs/training/legacy/trainer_base.yaml
  - _self_                                # keep the current file last
```text

What each entry provides:

| Default | Purpose |
| --- | --- |
| `override hydra/job_logging: disabled` | Keeps Hydra job logs quiet so our structured logging stays readable. |
| `trainer: base` | Seeds runtime values (seed, deterministic toggle, log formats) from `configs/training/legacy/trainer_base.yaml`. |
| `_self_` | Ensures inline keys in `config.yaml` win over group defaults. |

The `trainer/base` preset expands to:

```yaml
# configs/training/legacy/trainer_base.yaml
seed: 42
deterministic: false
log:
  dir: logs
  formats:
    - ndjson
```text

### Fresh override examples

```bash
# change seed and enable deterministic mode (mirrors the trainer defaults list)
codex-train trainer.seed=1234 trainer.deterministic=true

# switch metrics sink to both NDJSON and CSV without editing YAML
codex-train trainer.log.formats='["ndjson","csv"]'

# disable MLflow explicitly when running air-gapped
codex-train logging.mlflow_uri=null logging.mlflow_enable=false

# compose the offline sweep preset and keep epochs at one
python -m codex_ml.cli.hydra_main --config-path configs/training/sweeps --config-name sweep_offline \
  training.max_epochs=1
```text

Hydra understands `dot.path=value` for single values, `node=[a,b]` for lists, and
`foo.bar='{json:1}'` when you need structured overrides. See the Hydra docs for
the full grammar; the snippets above map 1:1 to our defaults list.

> **Tip**: combine overrides with `--config-name` to swap entire component trees,
> then override individual leaves as needed.

### Offline reproducibility checklist

- Use `codex config --audit last` to ensure `_self_` sits at the end of the
  defaults list before shipping a preset. The helper surfaces unresolved
  interpolation or misplaced `_self_` markers so CI catches regressions early.
- When deploying via Helm, the default values now export `WANDB_MODE=offline`
  and `HF_HUB_OFFLINE=1` alongside `LOG_LEVEL=INFO` to guarantee detached
  telemetry and deterministic logging in air-gapped clusters.
- Pair runtime overrides such as `trainer.seed` and `trainer.deterministic`
  with the offline environment variables above to keep experiment runs
  reproducible across laptops and isolated build agents.

***
ENDNOTES: Hydra defaults list & override syntax
***
