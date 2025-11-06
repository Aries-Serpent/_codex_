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

status:
python tools/status/codex_status_cli.py

quick:
nox -s status

test:
pytest -q

lint:
nox -s lint

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

.PHONY: capture-baseline
capture-baseline:
	bash scripts/baseline/capture_baseline.sh

.PHONY: rotate-baselines
rotate-baselines:
	python scripts/baseline/rotate_baselines.py 5

