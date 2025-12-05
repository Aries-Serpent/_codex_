# Copilot Space Audit Workflow Makefile (v1.1.0) - corrected
SPACE_PY ?= python
RUNNER ?= scripts/space_traversal/audit_runner.py

.PHONY: space-audit
space-audit:
	$(SPACE_PY) $(RUNNER) run

.PHONY: space-audit-fast
space-audit-fast:
	$(SPACE_PY) $(RUNNER) stage S1
	$(SPACE_PY) $(RUNNER) stage S3
	$(SPACE_PY) $(RUNNER) stage S4
	$(SPACE_PY) $(RUNNER) stage S6

.PHONY: space-explain
space-explain:
	@if [ -z "$(cap)" ]; then echo "Usage: make space-explain cap=<capability_id>"; exit 2; fi
	$(SPACE_PY) $(RUNNER) explain $(cap)

.PHONY: space-diff
space-diff:
	@if [ -z "$(old)" ] || [ -z "$(new)" ]; then echo "Usage: make space-diff old=<old> new=<new>"; exit 2; fi
	$(SPACE_PY) $(RUNNER) diff --old $(old) --new $(new)

.PHONY: space-clean
space-clean:
	rm -rf audit_artifacts audit_run_manifest.json reports/capability_matrix_*.md

.PHONY: space-remediation
space-remediation:
	$(SPACE_PY) scripts/remediation/cleanup_root.py --dry-run
	@echo "Run with --yes to execute cleanup"

.PHONY: space-verify
space-verify:
	$(SPACE_PY) scripts/remediation/verify_conflicts.py --expect-site-packages
	$(SPACE_PY) scripts/remediation/analyze_legacy_usage.py

.PHONY: space-test
space-test:
	pytest tests/validation/ -v

# Inference pipeline helpers (deterministic, offline-first)
.PHONY: inference-run
inference-run:
	@echo "[INFO] Running deterministic inference (WANDB_MODE=offline)"
	@export WANDB_MODE=offline; \
	$(SPACE_PY) scripts/inference_pipeline.py --config .copilot-space/workflow.yaml --input scripts/config/sample_inference_input.json --output audit_artifacts/inference_output.json

.PHONY: inference-fast
inference-fast:
	@echo "[INFO] Running deterministic inference (explain) (WANDB_MODE=offline)"
	@export WANDB_MODE=offline; \
	$(SPACE_PY) scripts/inference_pipeline.py --config .copilot-space/workflow.yaml --input scripts/config/sample_inference_input.json --output audit_artifacts/inference_output.json --explain

.PHONY: inference-test
inference-test:
	@echo "[INFO] Running inference tests (WANDB_MODE=offline)"
	@export WANDB_MODE=offline; \
	pytest tests/inference/ -q
