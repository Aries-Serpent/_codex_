.PHONY: format lint test build type setup venv env-info codex-gates lint-policy lint-ruff lint-hybrid lint-auto

format:
	pre-commit run --all-files

lint:
	ruff src tests

test:
	pytest

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

lint-policy:
	@python tools/lint_policy_probe.py
	@python tools/select_precommit.py

lint-ruff:
	@LINT_POLICY=ruff python tools/select_precommit.py && pre-commit run -a

lint-hybrid:
	@LINT_POLICY=hybrid python tools/select_precommit.py && pre-commit run -a

lint-auto:
	@$(MAKE) -s lint-policy && pre-commit run -a

fix-shebangs:
	@python tools/shebang_exec_guard.py

sec-audit:
	@python tools/pip_audit_wrapper.py
