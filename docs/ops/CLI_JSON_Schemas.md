# CLI JSON Schemas

Two CLIs surface machine-readable JSON and are validated against schemas stored in `schemas/cli/`:

- `python -m codex_ml.cli.list_plugins --format json`
- `python tools/github/gh_api.py --json-envelope ...`

## Validating Locally

Install `jsonschema` in your environment and run:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/cli/test_cli_schemas.py
```

This suite verifies that stdout contains exactly one JSON document and matches the corresponding schema.

## Envelope Mode

`tools/github/gh_api.py` supports `--json-envelope`, which wraps stdout in a normalized envelope:

```json
{ "ok": true, "data": <payload> }
{ "ok": false, "error": "message" }
```

This keeps stderr free for diagnostics while downstream tools consume predictable JSON.
