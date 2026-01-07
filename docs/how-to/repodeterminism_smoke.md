# [How-to]: Repo Determinism Smoke (CPU-only)  
> Generated: 2025-10-09 20:26:25 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Provide a minimal CPU-only smoke to assert seed handling and checkpoint round-trip integrity.

Checklist
| Item | Command | Expected |
|------|---------|----------|
| Seed behavior | `pytest -q tests/training/test_checkpoint_rng_restore.py` | Next RNG value matches pre-saved sequence |
| Checkpoint round-trip | `pytest -q tests/training/test_checkpoint_integrity.py::test_roundtrip_and_integrity` | State equal; checksum verified |
| Best‑k retention | `pytest -q tests/training/test_checkpoint_integrity.py::test_best_k_retention` | Only top_k files remain; best metric selected |
| Offline guards | `pytest -q tests/tracking/test_tracking_guards.py` | MLflow coerced to file://; W&B offline |

Notes
- All tests run without network; optional libs (torch, numpy) are import-guarded.
- For CI: tag these as a fast subset (e.g., -k "rng_restore or roundtrip or best_k or tracking_guards").

*End*