# Offline ZIP Keymaster

This package exposes the air-gapped ZIP key generation and extraction workflow as a standalone Python app stored inside the repository.

## Local-only usage

Generate a key:

```bash
python -m offline_zip_keymaster generate-key --key-out ./offline_key.key
```

Encrypt a directory:

```bash
python -m offline_zip_keymaster encrypt --input-dir ./source_data --zip-out ./payloads/archive.zip --key-file ./offline_key.key
```

Unpack into a self-titled output folder:

```bash
python -m offline_zip_keymaster unpack --zip-path ./payloads/archive.zip --key-file ./offline_key.key --output-dir ./output
```

## GUI

```bash
python -m offline_zip_keymaster.gui
```

The GUI delegates to the same internal backend used by the CLI and does not bypass the local-only validation or extraction safeguards.
