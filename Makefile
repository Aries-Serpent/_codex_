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
.PHONY: docker-build docker-run docker-smoke docker-health docker-sbom docker-scan docker-push \
        docker-gpu-build docker-gpu-run

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

# --- Owner approval convenience (local-only; writes .github/OWNER_APPROVAL.yml) ---
.PHONY: owner-approve-24h owner-approve-clear owner-approve-status owner-approve-extend-24h

owner-approve-24h:
	@mkdir -p .github
	@echo "# Effective owner-approval window (local 24h test)" > .github/OWNER_APPROVAL.yml
	@echo "enabled: true" >> .github/OWNER_APPROVAL.yml
	@echo 'reason: "24h test window for cost-incurring workflows"' >> .github/OWNER_APPROVAL.yml
	@echo 'approved_by: "'$(USER)'"' >> .github/OWNER_APPROVAL.yml
	@echo 'mode: "duration"' >> .github/OWNER_APPROVAL.yml
	@echo 'duration: "24h"' >> .github/OWNER_APPROVAL.yml
	@echo 'until: ""' >> .github/OWNER_APPROVAL.yml
	@echo "cost_workflows:" >> .github/OWNER_APPROVAL.yml
	@echo "  - docker-build-push" >> .github/OWNER_APPROVAL.yml
	@echo 'created_at: "'$$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' >> .github/OWNER_APPROVAL.yml
	@echo "[owner-approve-24h] Wrote .github/OWNER_APPROVAL.yml"

owner-approve-clear:
	@mkdir -p .github
	@echo "# Effective owner-approval window (disabled)" > .github/OWNER_APPROVAL.yml
	@echo "enabled: false" >> .github/OWNER_APPROVAL.yml
	@echo 'reason: ""' >> .github/OWNER_APPROVAL.yml
	@echo 'approved_by: ""' >> .github/OWNER_APPROVAL.yml
	@echo 'mode: "duration"' >> .github/OWNER_APPROVAL.yml
	@echo 'duration: "0h"' >> .github/OWNER_APPROVAL.yml
	@echo 'until: ""' >> .github/OWNER_APPROVAL.yml
	@echo "cost_workflows:" >> .github/OWNER_APPROVAL.yml
	@echo "  - docker-build-push" >> .github/OWNER_APPROVAL.yml
	@echo 'created_at: "'$$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' >> .github/OWNER_APPROVAL.yml
	@echo "[owner-approve-clear] Wrote .github/OWNER_APPROVAL.yml"

owner-approve-status:
	@bash scripts/ci/owner_approval_status.sh docker-build-push || true

owner-approve-extend-24h:
	@test -f .github/OWNER_APPROVAL.yml || { echo "Missing .github/OWNER_APPROVAL.yml"; exit 1; }
	@cp .github/OWNER_APPROVAL.yml .github/OWNER_APPROVAL.yml.bak
	@if grep -qE '^[[:space:]]*created_at:' .github/OWNER_APPROVAL.yml; then \
	  sed -i -E 's/^[[:space:]]*created_at:.*/created_at: "'$$'(date -u +%Y-%m-%dT%H:%M:%SZ)"/' .github/OWNER_APPROVAL.yml; \
	else \
	  echo 'created_at: "'$$'(date -u +%Y-%m-%dT%H:%M:%SZ)"' >> .github/OWNER_APPROVAL.yml; \
	fi
	@rm -f .github/OWNER_APPROVAL.yml.bak
	@echo "[owner-approve-extend-24h] Refreshed created_at"

DOCKER_GPU_IMAGE ?= codex-gpu:local

docker-gpu-build:
	@AUTO_BUILD_METADATA=1 bash scripts/ci/build_image.sh $(DOCKER_GPU_IMAGE) Dockerfile.gpu --load

docker-gpu-run:
	@echo "Note: requires NVIDIA Container Toolkit on host"
	@docker run --rm --gpus all -p $(HOST_PORT):8000 $(DOCKER_GPU_IMAGE)
