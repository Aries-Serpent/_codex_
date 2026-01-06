# Resume workflow and resume_manifest.json

This document describes the resume manifest format, the precedence rules used by the CLI, and examples of how to resume training deterministically.

Manifest schema
---------------
The resume manifest (`run_dir/resume_manifest.json`) contains the following top-level fields:

- manifest_version: (int) optional version stamp for future schema evolution.
- checkpoint_dir: (string|null) path to checkpoint directory (Phase 5 be inside run dir)
- last_checkpoint: (string|null) last saved checkpoint path
- best_checkpoint: (string|null) best model checkpoint path
- global_step: (int) training step at manifest write time
- resume_from: (string|null) path that was used to resume training for the current write
- config_path: (string|null) the path the caller (if any) provided to `run_hf_trainer`
- copied_config_path: (string|null) location of the copied config placed beside the manifest
- config: (object|null) a JSON-serialisable snapshot of the resolved configuration (preferred)

Precedence rules used by the CLI
--------------------------------
When resuming, the CLI uses the following deterministic precedence to obtain the configuration that will be used to reconstruct the original run:

1. `manifest["config"]` — Highest priority. If present, the embedded configuration snapshot is the canonical source of truth.
2. `run_dir/resume_config.json` or `run_dir/resume_config.yaml` (or `.yml`) — A copied file written at training completion. Prefer the copied file to any external path.
3. `manifest["config_path"]` — Fall back to the recorded path in the original environment. The CLI attempts to read this path as absolute, then relative to the run directory.
4. If none of the above are available, the CLI will error and refuse to resume to avoid silently using defaults.

Why we prefer the snapshot
--------------------------
Callers historically omitted passing `config_path` to `run_hf_trainer`, causing manifests to contain null `config_path`. To guarantee reproducibility, we persist either the resolved `hydra_cfg` snapshot into `manifest["config"]` or copy the original config into the run directory (`resume_config.*`). The resume command prefers the embedded snapshot because it is self-contained and not dependent on external files.

Examples
--------
Example 1: Resume using embedded snapshot
- `resume_manifest.json` contains:
  ```json
  {
    "manifest_version": 1,
    "config": {
      "model_name": "gpt2",
      "training": { "lr": 0.0002, "batch_size": 8 }
    }
  }
  ```
- The CLI will print the snapshot and exit success. Example command:
  `codex resume /path/to/run_dir`

Example 2: Resume using copied config file
- `run_dir/resume_config.yaml` exists (written at training completion).
- `resume_manifest.json` contains `"config": null` but `"config_path": "configs/training/base.yaml"`
- The CLI will detect `run_dir/resume_config.yaml`, print content, and exit success.

Example 3: Failure — neither snapshot nor path
- `resume_manifest.json` has `"config": null` and no usable `config_path`.
- The CLI will refuse to resume and exit with a non-zero code, printing an error describing how to fix the situation.

Recommended resume pseudocode
-----------------------------
1. Read `resume_manifest.json`
2. If `manifest.get("config")` is not `None`: use `manifest["config"]`
3. Else if `run_dir/resume_config.*` exists: use its content
4. Else if `manifest.get("config_path")` exists and is readable: use that file
5. Else: raise an error and refuse to resume

Notes and best practices
------------------------
- Training wrappers should attempt to pass `config_path` and/or `hydra_cfg` to `run_hf_trainer`. When neither is available, the manifest will not contain enough information to resume safely.
- CI and reproducibility workflows should archive `run_dir` entirely (including `resume_config.*` and `resume_manifest.json`).
- Adding `manifest_version` to `resume_manifest.json` is recommended for future schema evolution.
