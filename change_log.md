# Change Log

- Added `src/modeling.py` with model/tokenizer loaders and optional LoRA support.
- Implemented `src/training/trainer.py` for the extended training loop with evaluation and checkpoint retention.
- Introduced `src/logging_utils.py` and `src/data/datasets.py` to centralise logging and dataset helpers.
- Updated Hydra configs (`configs/default.yaml`, `configs/model/base.yaml`, `configs/training/base.yaml`, `configs/data/tiny.yaml`) to use defaults lists and preserve legacy keys.
- Documented the new training stack and reproducibility steps in `README.md` and ensured GitHub Actions remain disabled in this environment.
- Added focused pytest suites for modeling, datasets, logging, and the extended trainer alongside a supporting `nox` session.
- Created `error_log.md` per audit guidance and captured an illustrative authentication failure for follow-up analysis.
- Restored CRM legacy helpers by adding flow builders, Power Automate/ZAF compatibility shims, and diagram exports (`src/codex_crm/diagram/__init__.py`, `src/codex_crm/diagram/flows.py`, `src/codex_crm/pa_legacy/reader.py`, `src/codex_crm/zaf_legacy/reader.py`).
- Hardened security tests by making semgrep config discovery absolute and importing required utilities (`tests/security/test_semgrep_rules.py`).
