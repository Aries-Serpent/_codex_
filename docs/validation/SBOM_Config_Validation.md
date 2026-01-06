# [Validation]: SBOM Config and Workflow
> Generated: Previous Cycle-10-30 23:34:52 | Author: mbaetiong

## Local validation
1. Clean and prepare
   - `rm -rf config sbom.json`
2. Run config
   - `make config`
   - Expect: `config/` exists; `config/sample-sbom-config.yaml` or `config/sbom-config.yaml` created.
3. Generate SBOM (placeholder)
   - `jq -n '{ "sbom": "placeholder" }' > sbom.json` or use your actual SBOM tool.

## CI validation
- Push to `0D_base_` or open a PR targeting `0D_base_`.
- Inspect job "Generate SBOM":
  - Diagnostic step lists files and Makefile header.
  - "Ensure config artifacts" step succeeds even without a `config` target.
  - Artifact `sbom` contains `sbom.json`.

## Troubleshooting
- If your SBOM tool expects different paths/filenames, update:
  - Makefile `config` target
  - `.github/workflows/sbom.yml` steps
