# Offline ZIP packaging quick reference

## Active workflow

Use the restored active workflow: `.github/workflows/offline-zip-unpack.yml`

This workflow downloads or resolves a ZIP and extracts it into a self-titled folder without trusting unsafe member paths.

### Trigger inputs

- `zip_url`: remote ZIP URL
- `zip_path`: repo-relative ZIP path
- `output_dir`: output parent directory (default: `output`)
- `artifact_name`: workflow artifact name

### Examples

```bash
# Download a remote ZIP and unpack it
gh workflow run offline-zip-unpack.yml \
  --field zip_url=https://example.com/release.zip \
  --field output_dir=output \
  --field artifact_name=release-artifact

# Unpack a repo-local ZIP
gh workflow run offline-zip-unpack.yml \
  --field zip_path=dist/release.zip \
  --field output_dir=output \
  --field artifact_name=release-artifact
```

## Offline ZIP keymaster contract

The packaging contract used for secure ZIP handling is defined by the offline ZIP keymaster package.

```bash
python -m offline_zip_keymaster generate-key --key-out ./offline_key.key
python -m offline_zip_keymaster encrypt --input-dir ./source_data --zip-out ./payloads/archive.zip --key-file ./offline_key.key
python -m offline_zip_keymaster unpack --zip-path ./payloads/archive.zip --key-file ./offline_key.key --output-dir ./output
```

The archive includes a `manifest.json` and `encrypted_payload.bin` pair, and the unpack path validates the key fingerprint, HMAC, and safe member paths before extraction.

## Legacy note

`app-package-download.yml.disabled` is a historical workflow kept only for audit purposes. It is not active and does not represent the current packaging contract.
