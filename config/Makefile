# SBOM generation Makefile for config/ directory
# This Makefile is invoked by the CI workflow with: make -C config sbom

.PHONY: sbom
sbom:
	@echo "Generating CycloneDX SBOM..."
	python ../scripts/sbom_cyclonedx.py --lock ../requirements/lock.txt --lock ../uv.lock --output ../dist/sbom.json --project-name codex-ml --packages-output ../artifacts/sbom/packages.txt
	@echo "✅ SBOM generated at dist/sbom.json"
