# Ensure config artifacts exist for CI and local runs
.PHONY: config
config:
	@echo ">> Ensuring config/ directory and config files exist"
	@if [ -d config ]; then \
	  echo " - config/ directory already exists"; \
	else \
	  echo " - creating config/ directory"; \
	  mkdir -p config; \
	fi
	@if [ -x scripts/generate-config.sh ]; then \
	  echo " - running scripts/generate-config.sh"; \
	  scripts/generate-config.sh; \
	elif [ ! -f config/sample-sbom-config.yaml ]; then \
	  echo " - creating config/sample-sbom-config.yaml"; \
	  printf 'apiVersion: v1\nsbom:\n  output: sbom.json\n  format: cyclonedx\n' > config/sample-sbom-config.yaml; \
	  echo "   created config/sample-sbom-config.yaml"; \
	else \
	  echo " - sample-sbom-config.yaml found"; \
	fi
	@echo ">> config target completed"

.PHONY: status quick test lint env perf scan deps actions-serve actions-health actions-branches actions-search actions-cli-branches actions-cli-search actions-cli-cite

# =============================================================================
# Docker Test Environment Targets
# =============================================================================
# These targets provide a production-ready Docker-based test environment.
# Use docker-test to run pytest inside a container with coverage reporting.
#
# Configuration variables:
#   IMAGE       - Docker image name/tag (default: codex-test:latest)
#   DOCKERFILE  - Path to Dockerfile (default: Dockerfile)
#   ARTIFACTS_DIR - Directory for coverage reports (default: ./artifacts)
#
# Examples:
#   make docker-build              # Build the test image
#   make docker-test               # Build and run tests
#   make docker-clean              # Remove artifacts and image
#   IMAGE=my-test:v1 make docker-test  # Use custom image name
# =============================================================================

.PHONY: docker-build docker-test docker-clean docker-test-prod

# Docker configuration with defaults
IMAGE ?= codex-test:latest
DOCKERFILE ?= Dockerfile
ARTIFACTS_DIR ?= ./artifacts

docker-build:
	@echo "Building Docker test image: $(IMAGE)"
	docker build -f $(DOCKERFILE) -t $(IMAGE) .

docker-test: docker-build
	@echo "Running tests in Docker container..."
	@mkdir -p $(ARTIFACTS_DIR)
	docker run --rm \
		-v $(abspath $(ARTIFACTS_DIR)):/workspace/artifacts \
		-e COVERAGE_DIR=/workspace/artifacts \
		$(IMAGE)
	@echo "Coverage reports written to $(ARTIFACTS_DIR)/"

docker-test-prod:
	@echo "Running tests with production Dockerfile..."
	$(MAKE) docker-test DOCKERFILE=Dockerfile.prod IMAGE=codex-test-prod:latest

docker-clean:
	@echo "Cleaning Docker test artifacts..."
	-@rm -rf $(ARTIFACTS_DIR)/htmlcov $(ARTIFACTS_DIR)/coverage.xml 2>/dev/null || true
	-@docker image rm -f $(IMAGE) 2>/dev/null || true
	-@docker image rm -f codex-test-prod:latest 2>/dev/null || true
	@echo "Docker cleanup complete"

# =============================================================================
# End Docker Targets
# =============================================================================

status:
	python tools/status/codex_status_cli.py

quick:
	nox -s status

test:
	pytest -q

# HFIX-001 Step 2: Local coverage baseline.
# Generates coverage.json + coverage.xml so agents can read accurate numbers.
# Use: make coverage
# Output: coverage-report.txt, coverage.json, coverage.xml
.PHONY: coverage
coverage:
	pip install -e ".[dev]" -q
	python -m pytest tests/ -m "not slow and not integration" \
	  --cov=src --cov-report=term-missing --cov-report=json \
	  --cov-report=xml --no-header -q 2>&1 | tee coverage-report.txt
	@echo "Coverage JSON → coverage.json | XML → coverage.xml"

lint:
	nox -s lint

# ── Codebase-wide error discovery ─────────────────────────────────────────
# `make check`  — run ALL static checks, report every error found.
# `make fix`    — auto-fix everything possible, then recheck.
# `make ci`     — full local CI simulation (mirrors GitHub Actions exactly).
# `make check-fast` — skip slow mypy pass (ruff + isort + auto-fix only).

.PHONY: check fix ci check-fast

check:
	@echo "$(BOLD)🔍 Running codebase-wide scanner…$(RESET)"
	python scripts/ci/scan_all.py

check-fast:
	@echo "$(BOLD)🔍 Fast scan (ruff + isort + auto-fix, no mypy)…$(RESET)"
	python -m ruff check . --statistics
	python -m isort . --check-only --quiet
	python scripts/ci/auto_fix_common_issues.py --check-only

fix:
	@echo "$(BOLD)🔧 Auto-fixing all fixable issues…$(RESET)"
	python -m ruff check . --fix
	python -m isort .
	python scripts/ci/auto_fix_common_issues.py
	@echo "$(BOLD)🔍 Rechecking after fixes…$(RESET)"
	python scripts/ci/scan_all.py

ci:
	@echo "$(BOLD)🏗  Running full local CI simulation…$(RESET)"
	bash scripts/ci/simulate_ci_locally.sh

ci-fix:
	@echo "$(BOLD)🏗  Running full local CI simulation with auto-fix…$(RESET)"
	bash scripts/ci/simulate_ci_locally.sh --fix

env:
	nox -s env-snapshot

perf:
	CODEX_ENABLE_PERF_SAMPLER=1 python -c "from tools.perf.sampler import PerfSampler as S; S().run(steps=3)"

scan:
	python tools/security/scan_repo.py

deps:
	python tools/security/license_audit.py || true
	python tools/security/dep_snapshot.py || true

actions-serve:
	@echo "[+] Starting local Actions server on :8010"
	@python tools/actions_server.py

actions-health:
	@curl -s http://localhost:8010/healthz | jq .

actions-branches:
	@curl -s "http://localhost:8010/repo/branches?owner=$${CODEX_GH_OWNER:-Aries-Serpent}&repo=$${CODEX_GH_REPO:-_codex_}" | jq .

actions-search:
	@if [ -z "$$Q" ]; then echo "Usage: make actions-search Q=tokenization"; exit 1; fi
	@curl -s "http://localhost:8010/repo/search?owner=$${CODEX_GH_OWNER:-Aries-Serpent}&repo=$${CODEX_GH_REPO:-_codex_}&q=$$Q&ref=$${REF:-main}" | jq .

actions-cli-branches:
	@python tools/actions_cli.py branches

actions-cli-search:
	@if [ -z "$$Q" ]; then echo "Usage: make actions-cli-search Q=tokenization REF=0D_base_"; exit 1; fi
	@python tools/actions_cli.py search --q "$$Q" --ref "$${REF:-main}"

actions-cli-cite:
	@if [ -z "$$PATH" ] || [ -z "$$REF" ] || [ -z "$$NOTE" ]; then echo "Usage: make actions-cli-cite PATH=... REF=... NOTE=..."; exit 1; fi
	@python tools/actions_cli.py cite --path "$$PATH" --ref "$$REF" --note "$$NOTE"

# Include Space audit targets
-include space.mk

SKIP_OPTIONAL ?= 1
FAIL_ON_MISSING ?= 0

.PHONY: docs-build
docs-build:
	@SKIP_OPTIONAL="$(SKIP_OPTIONAL)" FAIL_ON_MISSING="$(FAIL_ON_MISSING)" bash scripts/docs_build.sh

.PHONY: docs-build-strict
docs-build-strict:
	@SKIP_OPTIONAL=0 FAIL_ON_MISSING=1 bash scripts/docs_build.sh

.PHONY: capture-baseline
capture-baseline:
	bash scripts/baseline/capture_baseline.sh

.PHONY: rotate-baselines
rotate-baselines:
	python scripts/baseline/rotate_baselines.py 5

.PHONY: filter-run
filter-run:
	@echo "[INFO] Running content filter (mode=$${CONTENT_FILTER_MODE:-allowlist})"
	python scripts/content_filter/apply_filter.py

.PHONY: archive-run
archive-run:
	@echo "[INFO] Running archival & pointer (fmt=$${ARCHIVE_FORMAT:-tar.gz}, style=$${ARCHIVE_POINTER_STYLE:-both})"
	python scripts/archive/select_and_compress.py --root $${RAW_ROOT:-audit_artifacts/raw}
