# Hydra overrides: the fast track

Codex uses a minimal **defaults list** so you can compose configs and tweak
parameters straight from the command line.

```yaml
# conf/config.yaml
defaults:
  - override hydra/job_logging: disabled
  - trainer: base
  - _self_
```

Examples:

```bash
# change seed and enable deterministic mode
codex-train trainer.seed=1234 trainer.deterministic=true

# switch the metrics sink to both NDJSON and CSV
codex-train trainer.log.formats='[ndjson,csv]'
```

Hydra understands `dot.path=value` for single values, `node=[a,b]` for lists, and
`foo.bar='{json:1}'` when you need structured overrides. See the Hydra docs for
the full grammar; the snippets above map 1:1 to our defaults list.

> **Tip**: combine overrides with `--config-name` to swap entire component trees,
> then override individual leaves as needed.

***
ENDNOTES: Hydra defaults list & override syntax
***
