.PHONY: help setup fmt lint type test cover sast track cli clean

help:
	@echo "Targets: setup fmt lint type test cover sast track cli clean"

setup:
	@if [ -f requirements.lock ]; then \
		pip install -r requirements.lock; \
	else \
		pip install -r requirements.txt -r requirements-dev.txt; \
	fi

fmt:
	black src tests
	isort src tests

lint:
	flake8 src tests

type:
	mypy src

test:
	pytest -q

cover:
	pytest -q --cov=src --cov-report=term-missing

sast:
	bandit -q -r src
	semgrep scan --config=p/ci src
        @if [ -f requirements.lock ]; then \
		pip-audit -r requirements.lock || true; \
	else \
		pip-audit -r requirements.txt || true; \
	fi

track:
	nox -s tracking_smoke

cli:
	nox -s cli

clean:
	rm -rf .pytest_cache .mypy_cache .nox .coverage coverage.xml mlruns .checkpoints artifacts
