# App package download workflow

This document describes the live app packaging flow for the offline ZIP keymaster distribution. The workflow must produce a ready-to-run Windows GUI application archive that can be downloaded and executed locally without the repository, GitHub variables, or network access.

## Live workflow

The active workflow path is `.github/workflows/app-package-download.yml`.

### Purpose

- build a native Windows GUI executable for the offline ZIP keymaster app
- create a self-contained runtime ZIP bundle containing `run_offline_zip_keymaster.exe`
- generate a minimal source/build-support bundle for packaging metadata and rebuild support
- keep all staging and release output in repo-local directories under `dist/`, `.artifacts/`, `release/`, and `packages/`

### Trigger

```yaml
workflow_dispatch
```

### Inputs

- `app_name` — `offline_zip_keymaster`, `offline-zip-keymaster`, or `all`
- `branch` — `main` or `0D_base_`
- `package_format` — `zip` only for the user-facing runtime bundle (self-contained GUI requirement)
- `include_dependencies` — include dependency metadata in the bundle
- `include_build_bundle` — include the minimal source build bundle
- `offline_wheelhouse` — build a local wheelhouse for offline installation support

### Runtime artifact contract

The primary downloadable artifact is:

- `release/run_offline_zip_keymaster_self_contained.zip`

The zip must contain:

- `run_offline_zip_keymaster.exe`
- `README.txt`
- `manifest.json`

The bundled executable is built from the GUI entrypoint:

- `src/offline_zip_keymaster/gui.py`

This is the default launch path for the packaged app, and the GUI is the canonical user experience.

### Build-support artifact contract

The second artifact is:

- `release/offline_zip_keymaster_build_bundle.zip`

It contains the minimal source package used to construct the downloadable app, plus metadata and checksums. It is intentionally smaller than the runtime bundle and excludes transient `.codex` session metadata.

## Packaging pipeline

1. Validate the selected app and safe target branch.
2. Prepare repo-local staging directories (`dist/`, `.artifacts/`, `release/`, `packages/`).
3. Build the Windows GUI app on `ubuntu-latest` inside a Wine-backed Windows container so a true Windows PE `.exe` can be produced without relying on a native Windows runner as the default path.
4. Create a self-contained zip archive from the finished `run_offline_zip_keymaster.exe` plus support files.
5. Generate a manifest with SHA-256 metadata, launch mode, and offline-only flags.
6. Upload the runtime bundle and the build-support bundle as GitHub Actions artifacts.

## Local offline usage

```bash
python -m offline_zip_keymaster generate-key --key-out ./offline_key.key
python -m offline_zip_keymaster encrypt --input-dir ./source_data --zip-out ./payloads/archive.zip --key-file ./offline_key.key
python -m offline_zip_keymaster unpack --zip-path ./payloads/archive.zip --key-file ./offline_key.key --output-dir ./output
```

The GUI entrypoint also supports the equivalent local actions:

```bash
python -m offline_zip_keymaster.gui
```

Double-click the packaged `run_offline_zip_keymaster.exe` to open the GUI directly after extraction.

## Security and offline requirements

- no GitHub variables or secrets are required at runtime
- no network access is required for the packaged GUI runtime
- workflow staging must remain repo-local only
- archive contents are restricted to the app runtime + minimal support files
- `.codex` session metadata and transient build artifacts are excluded from the runtime zip

## Build note

The packaged runtime artifact must be a native Windows executable; the Python source-only staging path does not satisfy the user-facing requirement. The active workflow therefore uses a Wine-backed Windows container build on `ubuntu-latest` for the Windows PE artifact, with the GUI entrypoint as the canonical target and the CLI kept secondary.
