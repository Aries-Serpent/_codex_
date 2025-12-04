# _codex_ Security & Safety Baseline (Scaffolding)

This document captures the initial security and safety posture for the
`_codex_` environment, focusing on **local developer workflows** rather
than production deployments.

It is intentionally conservative and will evolve over time.

## 1. Dependency Hygiene

Tools:

- `tools/codex_dependency_audit.py`
  - Aggregates dependencies from:
    - `pyproject.toml`
    - `requirements.txt`
    - `requirements-dev.txt`
  - Outputs:
    - `codex_dependency_report.json`
    - `codex_dependency_report.md`

Use it to:

- Check for unpinned or loosely pinned dependencies.
- Identify which files introduce each dependency.
- Inform future work on lockfiles or SBOM generation.

## 2. Secrets Hygiene (Stub)

Tools:

- `tools/codex_secret_scan_stub.py`
  - Lightweight, heuristic scan for:
    - Private key markers (`BEGIN PRIVATE KEY`)
    - Common cloud secret env var names
    - Token-like patterns for a few providers
  - Outputs:
    - `codex_secret_scan_report.json`
    - `codex_secret_scan_report.md`

Limitations:

- This is not a full secret scanner.
- False positives are acceptable; false negatives are possible.
- It is meant as a **local, low-friction check** when editing new code or
  preparing to share a branch.

Future extensions may:

- Add more patterns.
- Integrate with dedicated secret-scanning tools (still local only).

## 3. Environment & Security Health Check

Tool:

- `codex_ml.cli.env_check` (module)
- Entrypoint (recommended from repo root):

  ```bash
  python -m codex_ml.cli.env_check
  ```

What it does:
1. Runs tools/codex_env_snapshot.py to capture:
   - Python version & executable
   - Platform details
   - Selected environment variables (CODEX_, CUDA_, etc.)
2. Runs tools/codex_dependency_audit.py.
3. Runs tools/codex_secret_scan_stub.py.

The health check is designed as a pre-flight step before:
- Running the full gap/task sequence.
- Capturing a reproducibility bundle.
- Sharing a set of artifacts with others.

## 4. Relationship to Reproducibility

Security & safety are tied to reproducibility:
- Knowing which dependencies were installed and from where aids incident
  response and reproducible builds.
- A clean secret baseline helps ensure that reproducible artifacts can be
  safely shared without leaking credentials.

Related docs/tools:
- docs/reproducibility/reproducibility_checklist.md
- tools/codex_env_snapshot.py
- tools/codex_reproducibility_bundle.py

## 5. Next Steps (Future Work)
- Introduce optional hooks to enforce dependency pins for core paths.
- Add structured configuration for allowed/blocked dependencies.
- Expand secret-scan patterns and allow project-specific allowlists.
- Tie health-check results more directly into the gap registry or task
  sequence reports.
