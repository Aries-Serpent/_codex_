# Codex CLI Modules

This directory consolidates the legacy root-level automation scripts into a
single importable package. Each module exposes a `main` entry point registered
through `pyproject.toml` so the commands are available once the project is
installed.

## Available Commands

| Module | Console Script | Purpose |
| ------ | -------------- | ------- |
| `setup.py` | `codex-setup` | Bootstraps the `.codex/` directory and provides append-only helpers for change logs, error logs, and result summaries. |
| `patch_runner.py` | `codex-patch-runner` | Applies pending patches, captures local validation output, and records failures for follow-up. |
| `update_runner.py` | `codex-update-runner` | Drives sequential remediation phases that apply configuration updates and hardening tasks. |
| `script_polish.py` | `codex-script` | Hydra-powered stack polishing orchestration that can apply modifications, install dependencies, and run validation gates. |
| `workflow.py` | `codex-workflow` | End-to-end automation workflow that inventories the repository, applies staged fixes, and writes audit logs. |
| `task_sequence.py` | `codex-task-sequence` | Offline execution of the Codex task sequence with logging, provenance capture, and optional dry-run support. |
| `ast_upgrade.py` | `codex-ast-upgrade` | Offline AST upgrade pipeline that emits code mods, diagnostics, and best-effort remediation patches. |
| `audit_runner_root.py` | `codex-audit-runner` | Backward-compatible shim that delegates to `scripts/space_traversal/audit_runner.py` for audit workflows. |

## Usage

All commands accept the standard `--help` flag:

```bash
codex-setup --help
codex-patch-runner --help
codex-update-runner --help
codex-workflow --help
codex-task-sequence --help
codex-ast-upgrade --help
```text

`codex-script` continues to rely on Hydra for configuration loading, so it
honours the original configuration tree under `configs/`.

## Development Notes

* Modules compute the repository root via `Path(__file__).resolve().parents[1]`
  so they work regardless of the current working directory.
* Console scripts are declared under `[project.scripts]` in `pyproject.toml` and
  the `cli` package is included in the distribution metadata and MANIFEST.
* The legacy locations have been removed; update imports to use `cli.*`
  modules directly.
