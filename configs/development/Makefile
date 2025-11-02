MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
NOXFILE := $(MAKEFILE_DIR)noxfile.py

.PHONY: help setup fmt lint type test cover sast track cli clean sbom env-snapshot

MAKEFILE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
NOX := nox --noxfile $(MAKEFILE_DIR)noxfile.py

help:
	@echo "Targets: setup fmt lint type test cover sast track cli clean env-snapshot"

setup:
	@if [ ! -f requirements/lock.txt ]; then \
		echo "requirements/lock.txt missing; generate the lock before running make setup."; \
		exit 1; \
	fi
	pip install -r requirements/lock.txt
	pip install -r requirements/dev.txt --no-deps

fmt:
	black src tests
	isort src tests

lint:
	flake8 src tests

type:
	mypy src

test:
        pytest -q --cov=src/codex_ml --cov-fail-under=3.5

cover:
        pytest -q --cov=src/codex_ml --cov-report=term-missing --cov-fail-under=3.5

sast:
	bandit -q -r src
	semgrep scan --config=p/ci src
	@if [ -f requirements/lock.txt ]; then \
		pip-audit -r requirements/lock.txt || true; \
	else \
		pip-audit -r requirements/base.txt || true; \
	fi

track:
	$(NOX) -s tracking_smoke

cli:
	$(NOX) -s cli

sbom:
	python ../scripts/sbom_cyclonedx.py --lock ../requirements/lock.txt --lock ../uv.lock --output ../dist/sbom.json

clean:
	rm -rf .pytest_cache .mypy_cache .nox .coverage coverage.xml mlruns .checkpoints artifacts

env-snapshot:
	@mkdir -p artifacts
	python scripts/env/export_env_json.py artifacts/env_snapshot.json

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

# ==== Self-hosted runner helpers (Codex-aware; require GH_PAT or _CODEX_BOT_RUNNER) ====
.PHONY: runner-docker-install runner-binfmt runner-bootstrap runner-remove runner-status runner-vars
.PHONY: vars-list vars-delete

# Usage: make runner-docker-install USER=runner
runner-docker-install:
	@if [ -z "$$USER" ]; then echo "Usage: make runner-docker-install USER=<runner-user>"; exit 2; fi
	sudo bash scripts/runner/install_docker.sh $$USER

# Optional multi-arch (requires privileged Docker)
runner-binfmt:
	bash scripts/runner/install_binfmt.sh

# Usage:
#  make runner-bootstrap URL=https://github.com/Aries-Serpent/_codex_ LABELS="self-hosted,linux,docker" SVC=systemd
runner-bootstrap:
	@if [ -z "$$URL" ]; then echo "Usage: make runner-bootstrap URL=<org_or_repo_url> [LABELS=...] [SVC=systemd]"; exit 2; fi
	bash scripts/runner/actions_runner_bootstrap.sh --url "$$URL" --labels "$${LABELS:-self-hosted,linux}" --version "2.329.0" --svc "$${SVC:-systemd}"

# Usage: make runner-remove URL=https://github.com/Aries-Serpent/_codex_
runner-remove:
	@if [ -z "$$URL" ]; then echo "Usage: make runner-remove URL=<org_or_repo_url>"; exit 2; fi
	bash scripts/runner/actions_runner_remove.sh --url "$$URL"

# Usage:
#  make runner-status ORG=Aries-Serpent
#  make runner-status OWNER=Aries-Serpent REPO=_codex_
runner-status:
	@if [ -n "$$ORG" ]; then bash scripts/runner/runner_status.sh --org "$$ORG" --format pretty; fi
	@if [ -n "$$OWNER" ] && [ -n "$$REPO" ]; then bash scripts/runner/runner_status.sh --owner "$$OWNER" --repo "$$REPO" --format pretty; fi
	@if [ -z "$$ORG" ] && [ -z "$$OWNER$$REPO" ]; then echo "Usage: make runner-status ORG=<org> | OWNER=<owner> REPO=<repo>"; exit 2; fi

# Usage examples:
#  make runner-vars OWNER=Aries-Serpent REPO=_codex_ RUNS_ON='["self-hosted","linux"]'
#  make runner-vars OWNER=Aries-Serpent REPO=_codex_ APPROVAL_DURATION=24h
#  make runner-vars OWNER=Aries-Serpent REPO=_codex_ APPROVAL_UNTIL=2025-10-21T00:00:00Z
#  make runner-vars OWNER=Aries-Serpent REPO=_codex_ PUSH_PLATFORMS="linux/amd64,linux/arm64"
#  make runner-vars OWNER=Aries-Serpent REPO=_codex_ SETS="FOO=bar NEW_FLAG=1"
#  make runner-vars OWNER=Aries-Serpent REPO=_codex_ DELETE="FOO NEW_FLAG"
runner-vars:
	@if [ -z "$$OWNER" ] || [ -z "$$REPO" ]; then echo "Usage: make runner-vars OWNER=<owner> REPO=<repo> [RUNS_ON='[\"self-hosted\",\"linux\"]'] [APPROVAL_DURATION=24h|APPROVAL_UNTIL=...] [PUSH_PLATFORMS=...] [SETS='NAME=VALUE ...'] [DELETE='NAME ...']"; exit 2; fi
	@OWNER="$$OWNER" REPO="$$REPO" RUNS_ON="$$RUNS_ON" APPROVAL_DURATION="$$APPROVAL_DURATION" APPROVAL_UNTIL="$$APPROVAL_UNTIL" PUSH_PLATFORMS="$$PUSH_PLATFORMS" SETS="$$SETS" DELETE="$$DELETE" \
	sh -c '
	  set -euo pipefail;
	  cmd=(bash scripts/runner/configure_repo_vars.sh --owner "$$OWNER" --repo "$$REPO");
	  if [ -n "$$RUNS_ON" ]; then cmd+=(--runs-on "$$RUNS_ON"); fi;
	  if [ -n "$$APPROVAL_DURATION" ]; then cmd+=(--approval-duration "$$APPROVAL_DURATION"); fi;
	  if [ -n "$$APPROVAL_UNTIL" ]; then cmd+=(--approval-until "$$APPROVAL_UNTIL"); fi;
	  if [ -n "$$PUSH_PLATFORMS" ]; then cmd+=(--push-platforms "$$PUSH_PLATFORMS"); fi;
	  # Parse SETS="NAME=VALUE NAME2=VALUE2"
	  if [ -n "$${SETS:-}" ]; then
	    for kv in $$SETS; do
	      cmd+=(--set "$$kv");
	    done;
	  fi;
	  # Parse DELETE="NAME1 NAME2"
	  if [ -n "$${DELETE:-}" ]; then
	    for name in $$DELETE; do
	      cmd+=(--delete "$$name");
	    done;
	  fi;
	  "${cmd[@]}"
	'

# List repository variables (pretty by default)
# Usage: make vars-list OWNER=Aries-Serpent REPO=_codex_ [FORMAT=json]
vars-list:
	@if [ -z "$$OWNER" ] || [ -z "$$REPO" ]; then echo "Usage: make vars-list OWNER=<owner> REPO=<repo> [FORMAT=json|pretty]"; exit 2; fi
	@bash scripts/runner/list_repo_vars.sh --owner "$$OWNER" --repo "$$REPO" --format "$${FORMAT:-pretty}"

# Delete variables by name (space-delimited)
# Usage: make vars-delete OWNER=Aries-Serpent REPO=_codex_ NAMES="FOO BAR"
vars-delete:
	@if [ -z "$$OWNER" ] || [ -z "$$REPO" ] || [ -z "$$NAMES" ]; then echo "Usage: make vars-delete OWNER=<owner> REPO=<repo> NAMES=\"NAME1 NAME2\""; exit 2; fi
	@for n in $$NAMES; do \
	  echo "Deleting $$n"; \
	  bash scripts/runner/configure_repo_vars.sh --owner "$$OWNER" --repo "$$REPO" --delete "$$n"; \
	done
