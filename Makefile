.PHONY: format lint test build type setup venv env-info codex-gates

format:
	pre-commit run --all-files

lint:
	ruff src tests

test:
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
