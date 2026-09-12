# Legacy app-package download workflow

This page is intentionally kept as a historical reference only.

The repository's restored active workflow is `.github/workflows/offline-zip-unpack.yml`, and the live packaging contract is defined by `scripts/security/offline_zip_keymaster.py` plus `src/offline_zip_keymaster/cli.py`.

The file `.github/workflows/app-package-download.yml.disabled` is not part of the active workflow baseline and should not be treated as the live user-facing workflow path.

## Current active workflow

### `offline-zip-unpack.yml`

This workflow is the active packaging/unpack workflow in the repository baseline.

- Trigger: `workflow_dispatch` or `workflow_call`
- Inputs:
  - `zip_url`: optional URL to download and unpack
  - `zip_path`: repo-relative path to a ZIP to unpack
  - `output_dir`: parent directory for the extracted self-titled output folder
  - `artifact_name`: artifact name to upload after extraction
- Behavior:
  1. resolves either a URL or a repo-local ZIP path
  2. validates archive readability and safety
  3. extracts into a self-titled folder under `output_dir`
  4. uploads the extracted directory as a workflow artifact
- Security controls:
  - rejects empty / absolute / escaping zip paths
  - validates the ZIP before extraction
  - calls `scripts.security.offline_zip_keymaster._safe_extract_members` for safe member extraction
  - prevents path traversal and symlink extraction

### Example usage

```bash
# Trigger via GitHub CLI
gh workflow run offline-zip-unpack.yml \
  --field zip_url=https://example.com/archive.zip \
  --field output_dir=output \
  --field artifact_name=release-archive

# Or unpack a repo-local archive
gh workflow run offline-zip-unpack.yml \
  --field zip_path=dist/release.zip \
  --field output_dir=output \
  --field artifact_name=release-archive
```

## Offline ZIP keymaster contract

The active packaging contract is the offline ZIP keymaster package.

### CLI contract

```bash
python -m offline_zip_keymaster generate-key --key-out ./offline_key.key
python -m offline_zip_keymaster encrypt --input-dir ./source_data --zip-out ./payloads/archive.zip --key-file ./offline_key.key
python -m offline_zip_keymaster unpack --zip-path ./payloads/archive.zip --key-file ./offline_key.key --output-dir ./output
```

The implementation encrypts a directory into a ZIP archive containing:

- `manifest.json` — archive metadata including the payload name, member names, and key fingerprint
- `encrypted_payload.bin` — the encrypted archive payload

The unpack path validates:

- key fingerprint matches the manifest
- archive HMAC matches the key
- member names are safe and remain inside the target directory
- nested archive recursion and file counts remain within safety caps

This is the documented local-only packaging workflow; it is not the disabled `app-package-download` workflow.

## Legacy note

The old app package download flow built downloadable bundles from `apps/` but it was intentionally disabled from the live workflow baseline. Its docs are preserved for audit history only and should not be used as the live operational path.

Use the offline ZIP workflow and keymaster contract when the user-facing requirement is to package or unpack a ZIP securely and locally in a repository-controlled environment.
