.PHONY: format lint test build type

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
