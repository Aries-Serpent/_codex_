# App Package Download Workflow

## Overview

The App Package Download workflow produces a repo-local, downloadable archive for the Offline ZIP Keymaster application. The primary artifact is a self-contained ZIP package that contains the runnable app files and launcher scripts, so it can be extracted and used without any additional repo checkout or network fetch. It packages only the files required to run the air-gapped ZIP generator and extractor, stores build staging under tracked workspace directories, and uploads both the runnable package and the minimal source bundle as workflow artifacts.

This workflow intentionally avoids `/tmp` staging. All packaging work happens under repo-local directories such as `package_staging/`, `release/`, and `build_bundle/` inside the GitHub Actions checkout.

## Why this workflow exists

The ZIP keymaster app is the canonical downloadable executable package for the repo’s secure local archive workflow. It includes:

- the standalone `offline_zip_keymaster` Python package
- the CLI entry point used for `generate-key`, `encrypt`, and `unpack`
- the GUI wrapper for local use
- a minimal build-support bundle for reproducible packaging
- a manifest describing exactly which files were bundled

## Workflow inputs

| Input | Type | Required | Default | Description |
|---|---|---:|---|---|
| `app_name` | choice | yes | `offline_zip_keymaster` | Target package to build |
| `branch` | choice | yes | `main` | Package source branch |
| `package_format` | choice | yes | `zip` | Output archive format |
| `include_dependencies` | boolean | no | `true` | Include dependency metadata in the bundle |
| `include_build_bundle` | boolean | no | `true` | Add the minimal source archive used to reconstruct the package |

## Supported package targets

- `offline_zip_keymaster`
- `offline-zip-keymaster`
- `all`

The workflow validates the target app name and the allowed branch values before creating any archives.

## Package output

The workflow creates a repo-local package directory, then archives it into a single downloadable file.

Example contents of the final archive:

```text
offline_zip_keymaster/
├── offline_zip_keymaster/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── gui.py
│   └── README.md
├── scripts/
│   └── security/
│       └── offline_zip_keymaster.py
├── README.md
├── pyproject.toml
├── package_manifest.json
├── run_offline_zip_keymaster.py
├── run_offline_zip_keymaster.sh
└── requirements*.txt (when enabled)
```

The workflow also emits a second archive containing only the minimal source bundle used to reconstruct the package.

## Artifact behavior

After a run completes, the GitHub Actions summary includes the generated archive names and the workflow uploads the artifacts with a 30-day retention window.

Artifacts are named like:

```text
offline-zip-keymaster-<run_id>
```

and include:

- the runnable app package archive
- the minimal source bundle archive (when enabled)

## Usage

1. Open GitHub Actions.
2. Select `App Package Download`.
3. Choose the package target and archive format.
4. Click `Run workflow`.
5. Download the artifact from the run summary when the job completes.

## Repository-local packaging constraints

This workflow follows the repository’s packaging guardrails:

- checkout is local to the GitHub Actions workspace
- all build artifacts are stored under repo-local directories
- no transient staging is left under `/tmp`
- only the exact app sources needed to build the project are copied into the archive
- the package manifest records the content list for download verification

## Local validation example

The packaged app is designed to run from the extracted bundle without a repository checkout:

```bash
python -m offline_zip_keymaster generate-key --key-out ./offline_key.key
python -m offline_zip_keymaster encrypt --input-dir ./source_data --zip-out ./payloads/archive.zip --key-file ./offline_key.key
python -m offline_zip_keymaster unpack --zip-path ./payloads/archive.zip --key-file ./offline_key.key --output-dir ./output
```

## Workflow files

- `.github/workflows/app-package-download.yml`
- `.github/workflows/app-package-download.md`
- `.github/workflows/app-package-download-quick-ref.md`
