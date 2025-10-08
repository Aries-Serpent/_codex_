# Manifest Integrity

Use canonical JSON for reproducible hashing/signing.
- Deterministic property order and compact separators (RFC 8785 / JCS).
- SHA-256 digest over the canonical bytes.

CLI:
```bash
python -m codex_ml.cli.manifest hash --path path/to/manifest.json
```
