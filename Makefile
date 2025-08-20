.PHONY: format lint test build

format:
	pre-commit run --all-files

lint:
	ruff src tests

test:
	pytest

build:
	python -m build
