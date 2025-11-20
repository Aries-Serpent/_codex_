# Copilot Space Audit Workflow Makefile (v1.2.0)

SPACE_PY ?= python
RUNNER ?= scripts/space_traversal/audit_runner.py
SPACE_DECODE ?= scripts/space_traversal/decode_validate_and_extract.py
SPACE_STABLE ?= --stable-output

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

.PHONY: space-validate
space-validate:
        $(SPACE_PY) $(RUNNER) validate

.PHONY: space-decode
space-decode:
        $(SPACE_PY) $(SPACE_DECODE) $(SPACE_STABLE) --generate-baseline

.PHONY: space-status
space-status:
	$(SPACE_PY) scripts/space_traversal/status_update_report.py

.PHONY: space-status-delta
space-status-delta:
	@if [ -z "$(base)" ]; then echo "Usage: make space-status-delta base=<baseline_scored.json>"; exit 2; fi
	$(SPACE_PY) scripts/space_traversal/status_update_report.py --base $(base)

.PHONY: space-clean
space-clean:
	rm -rf audit_artifacts audit_run_manifest.json reports/capability_matrix_*.md reports/codex_status_update_*.md

space-decode-validate:
	@echo "Decoding committed Phase-A artifacts..."
	@mkdir -p artifacts/extracted_local
	@for f in artifacts/*.json.gz.b64; do \
		[ -f $$f ] || continue; \
		base=$$(basename $$f .json.gz.b64); \
		python3 scripts/space_traversal/decode_validate_and_extract.py --input $$f --out-dir artifacts/extracted_local/$$base --stable-output || exit 1; \
	done
	@echo "Done. Extracted artifacts under artifacts/extracted_local/"
