.PHONY: help setup fmt lint type test cover sast track cli clean

help:
	@echo "Targets: setup fmt lint type test cover sast track cli clean"

setup:
	@if [ -f requirements.lock ]; then \\
		pip install -r requirements.lock && \\
		pip install -r requirements-dev.txt; \\
	else \\
		pip install -r requirements.txt -r requirements-dev.txt; \\
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

# --- Docker convenience targets (local-only; CI remains gated) ---
.PHONY: docker-build docker-run docker-smoke docker-health docker-sbom docker-scan docker-push

DOCKER_IMAGE ?= codex:local
DOCKERFILE ?= Dockerfile
HOST_PORT ?= 8000
SMOKE_HOST_PORT ?= 18000
PUSH_IMAGE ?= ghcr.io/OWNER/REPO:tag

docker-build:
	@bash scripts/ci/build_image.sh $(DOCKER_IMAGE) $(DOCKERFILE) --load

docker-run:
	@docker run --rm -p $(HOST_PORT):8000 $(DOCKER_IMAGE)

docker-smoke:
	@bash scripts/ci/container_smoke.sh $(DOCKER_IMAGE) 8000 $(SMOKE_HOST_PORT)

docker-health:
	@SMOKE_ENFORCE_HEALTH=1 bash scripts/ci/container_smoke.sh $(DOCKER_IMAGE) 8000 $(SMOKE_HOST_PORT)

docker-sbom:
	@bash scripts/ci/sbom_syft.sh $(DOCKER_IMAGE)

docker-scan:
	@bash scripts/ci/scan_trivy.sh $(DOCKER_IMAGE)

docker-push:
	@bash scripts/ci/push_image.sh $(PUSH_IMAGE)
