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

.PHONY: status quick test lint env perf scan deps

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
