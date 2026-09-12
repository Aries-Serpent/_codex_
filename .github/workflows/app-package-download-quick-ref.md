# App Package Download - Quick Reference

## Active workflow

Use the restored active workflow: `.github/workflows/app-package-download.yml`

This workflow builds a self-contained archive for the offline ZIP keymaster app and uploads it as a workflow artifact using repo-local staging directories only.

## Workflow inputs

| Input | Options | Default |
|---|---|---|
| `app_name` | `offline_zip_keymaster`, `offline-zip-keymaster`, `all` | `offline_zip_keymaster` |
| `branch` | `main`, `0D_base_` | `main` |
| `package_format` | `zip`, `tar.gz` | `zip` |
| `include_dependencies` | `true`, `false` | `true` |
| `include_build_bundle` | `true`, `false` | `true` |

## Standalone package contract

The primary artifact is a self-contained ZIP application bundle. It includes the runnable package plus helper launchers so the extracted app can run without pulling anything else from the network or the repo checkout.

```text
offline_zip_keymaster_<branch>_<run_id>.zip
├── offline_zip_keymaster/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── gui.py
│   └── README.md
├── scripts/security/offline_zip_keymaster.py
├── README.md
├── package_manifest.json
├── run_offline_zip_keymaster.py
├── run_offline_zip_keymaster.sh
├── pyproject.toml
└── requirements*.txt (if enabled)
```

## Local post-download usage

```bash
# Extract the ZIP
unzip offline_zip_keymaster_*.zip
cd offline_zip_keymaster_*/

# Run the packaged CLI directly
python run_offline_zip_keymaster.py generate-key --key-out ./offline_key.key
python run_offline_zip_keymaster.py encrypt --input-dir ./source_data --zip-out ./payloads/archive.zip --key-file ./offline_key.key
python run_offline_zip_keymaster.py unpack --zip-path ./payloads/archive.zip --key-file ./offline_key.key --output-dir ./output
```

## Notes

- The workflow uses repo-local `package_staging/`, `release/`, and `build_bundle/` directories.
- No useful staging files are left in `/tmp`.
- The build-support bundle is uploaded alongside the runnable app archive for reproducibility.
