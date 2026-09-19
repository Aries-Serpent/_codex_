# App package download quick reference

## Active workflow

Use the active workflow: `.github/workflows/app-package-download.yml`

This workflow packages the offline ZIP keymaster as a native Windows GUI app using a Wine-backed Windows container on `ubuntu-latest`. The generated runtime zip contains the bundled `run_offline_zip_keymaster.exe` and is the default user-facing artifact.

### Trigger inputs

- `app_name`: `offline_zip_keymaster`, `offline-zip-keymaster`, or `all`
- `branch`: `main` or `0D_base_`
- `package_format`: `zip` (the self-contained GUI runtime is shipped as a ZIP archive)
- `include_dependencies`: include dependency metadata
- `include_build_bundle`: include the minimal build-support bundle
- `offline_wheelhouse`: generate a local wheelhouse for offline support

### Primary artifact

```text
release/run_offline_zip_keymaster_self_contained.zip
```

This zip is the user-facing download and contains:

- `run_offline_zip_keymaster.exe`
- `README.txt`
- `manifest.json`

### Secondary artifact

```text
release/offline_zip_keymaster_build_bundle.zip
```

This build bundle contains the source files and packaging metadata used to construct the runtime app bundle.

## Local app usage

```bash
python -m offline_zip_keymaster generate-key --key-out ./offline_key.key
python -m offline_zip_keymaster encrypt --input-dir ./source_data --zip-out ./payloads/archive.zip --key-file ./offline_key.key
python -m offline_zip_keymaster unpack --zip-path ./payloads/archive.zip --key-file ./offline_key.key --output-dir ./output
```

To open the GUI directly:

```bash
python -m offline_zip_keymaster.gui
```

After extraction, the packaged Windows app should be launched by double-clicking `run_offline_zip_keymaster.exe`.
