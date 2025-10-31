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
