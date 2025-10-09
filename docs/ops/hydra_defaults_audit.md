# Hydra Defaults Audit

Audit Hydra YAML configs for defaults hygiene:

- Verify `_self_` is present (and warn when it appears mid-list).
- Flag defaults entries that point to non-existent YAML targets.
- Detect unresolved interpolations (`${...}`) to catch configuration debt early.

```bash
python -m codex_ml.cli hydra \
  defaults-audit \
  --config-root configs \
  --out-json .codex/reports/hydra_audit.json \
  --out-md .codex/reports/hydra_audit.md
```

Recommendations
---------------

- Keep `_self_` either first (preferable) or last for predictable override order.
- When optional defaults are used (`?group: option`), ensure fallbacks exist or document the missing dependency.
- Use Hydra's `--info defaults` flag during development to confirm the composed list matches expectations.

The JSON payload mirrors the CLI stdout to simplify automation pipelines. The Markdown report is optimised for
lightweight status dashboards in Markdown-based wikis.
