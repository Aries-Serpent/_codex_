.PHONY: format lint test build type setup venv env-info codex-gates

format:
pre-commit run --all-files

lint:
ruff src tests

test:
@nox -s tests

quality:
pre-commit run --all-files
pytest

build:
python -m build

type:
mypy src

setup:
bash scripts/env/setup_ubuntu.sh

venv:
bash scripts/env/create_venv.sh

env-info:
python scripts/env/print_env_info.py

include codex.mk

## Run local gates with the exact same entrypoint humans and bots use
codex-gates:
@bash ci_local.sh

.PHONY: wheelhouse
wheelhouse:
@tools/bootstrap_wheelhouse.sh

.PHONY: fast-tests
fast-tests:
@PIP_CACHE_DIR=.cache/pip nox -r -s tests

.PHONY: sys-tests
sys-tests:
@nox --no-venv -s tests_sys

.PHONY: ssp-tests
ssp-tests:
@nox -s tests_ssp

.PHONY: sec-scan
sec-scan:
@nox -s sec_scan

.PHONY: sec-audit
sec-audit:
	@python tools/pip_audit_wrapper.py

.PHONY: lock-refresh
lock-refresh:
@bash tools/uv_lock_refresh.sh

.PHONY: ci-local coverage gates
ci-local:
@nox -s ci_local
coverage:
@nox -s ci_local
gates:
@bash tools/run_quality_gates.sh
lint-policy:
	@python tools/lint_policy_probe.py
	@python tools/select_precommit.py
lint-ruff:
	@LINT_POLICY=ruff python tools/select_precommit.py && pre-commit run -a || true
lint-hybrid:
	@LINT_POLICY=hybrid python tools/select_precommit.py && pre-commit run -a || true
lint-auto:
	@make -s lint-policy && pre-commit run -a || true
