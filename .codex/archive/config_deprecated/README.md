# config
This directory holds configuration files used by the SBOM generation workflow.

- sample-sbom-config.yaml — an example SBOM config used by the Makefile and CI.
- sbom-config.yaml — a generated file when `scripts/generate-config.sh` is available.

Update the Makefile and `.github/workflows/sbom.yml` if your SBOM tooling requires different filenames or formats.
