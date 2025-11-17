# [InstructionEnhancement]: SBOM Config and Makefile Target
> Generated: 2025-10-30 23:34:52 | Author: mbaetiong

## Objective
Prevent the CI failure:
```text
make: *** config: No such file or directory.  Stop.
```text
by ensuring `make config` succeeds and the SBOM workflow is resilient.

## References
- Failing run reference (Make uses missing target error): [sbom.yml @ ref 324e730e](https://github.com/Aries-Serpent/_codex_/blob/324e730e83438c93555a2c8d46ac8787b21964b1/.github/workflows/sbom.yml)

## Expected file/folder changes

### File matrix
| Action | Path | Purpose | Notes |
|---|---|---|---|
| Modify | Makefile | Add idempotent `config` target that creates `config/` and a sample config | Called by CI and local |
| Modify | .github/workflows/sbom.yml | Add diagnostics and guarded `make config` step | Uses ref 324e730e for traceability |
| Add | scripts/generate-config.sh | Optional generator using env vars (SBOM_OUTPUT, SBOM_FORMAT) | Executable script |
| Add | config/sample-sbom-config.yaml | Baseline SBOM config (CycloneDX -> sbom.json) | Used if generator absent |
| Add | config/README.md | Documents config directory contents and usage | Developer aid |

### Expected repo tree (relevant paths)
```text
.
├── Makefile
├── config/
│   ├── README.md
│   └── sample-sbom-config.yaml
├── scripts/
│   └── generate-config.sh
└── .github/
    └── workflows/
        └── sbom.yml
```text

## Resolution summary
- `make config` is now safe to run even if the repo lacks config files.
- The workflow prints diagnostics and falls back to creating a minimal config to avoid hard failures.
- Optional script supports environment-driven config.

## Usage
- Local: `make config`
- CI: triggered by pushes/PRs to `0D_base_`.

## Rollback
Revert the five files above if needed.
