# Copilot Space Audit Workflow Makefile (v1.1.0)

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
