# Smoke tests

Run hermetic, network-free smoke tests locally:

```bash
pytest -q -m smoke
```
CI runs these by default on PRs unless area labels (e.g. `tokenizer`, `training`, `eval`) are added; in that case, CI narrows the selection to the labeled areas.

To validate a config without running:

```bash
codex-validate-config file path/to/config.yaml
```