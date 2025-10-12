
.PHONY: format
.PHONY: install package clean

install:
	@pip install -e .

package:
	@if command -v nox >/dev/null 2>&1; then \
		nox -s package; \
	else \
		python -m nox -s package; \
	fi

clean:
	rm -rf build dist .nox *.egg-info artifacts/coverage.xml .pytest_cache

# --- Metrics utilities ---
metrics-csv:
	@echo "Usage: make metrics-csv IN=.codex/metrics/run.ndjson OUT=.codex/metrics/run.csv"
	@test -n "$(IN)" || (echo "IN variable is required"; exit 2)
	@test -n "$(OUT)" || (echo "OUT variable is required"; exit 2)
	. .venv/bin/activate && ndjson-to-csv "$(IN)" "$(OUT)"

mlflow-ui:
	. .venv/bin/activate && mlflow ui --backend-store-uri file:./mlruns

.PHONY: lint tests test build type setup venv env-info codex-gates wheelhouse fast-tests sys-tests ssp-tests sec-scan sec-audit lock-refresh ci-local coverage gates lint-policy lint-ruff lint-hybrid lint-auto quality fix-shebangs hooks integrity space-audit space-audit-fast space-explain space-diff space-clean data-pull data-push pipeline dvc-repro

format:
	pre-commit run --all-files

lint:
	ruff src tests

tests:
        @if command -v nox >/dev/null 2>&1; then \
                nox -s tests; \
        else \
                python -m nox -s tests; \
        fi

test: tests

quality:
	pre-commit run --all-files
	pytest

build:
	python -m build

type:
	mypy src

setup:
	bash scripts/env/setup_ubuntu.sh

venv:
	bash scripts/env/create_venv.sh

env-info:
	python scripts/env/print_env_info.py

data-pull:
	@. .venv/bin/activate && dvc pull -v

data-push:
	@. .venv/bin/activate && dvc push -v

dvc-repro:
	@. .venv/bin/activate && dvc repro -v

pipeline: dvc-repro
	@echo "Reproducing DVC pipeline..."

.PHONY: train eval

train:
	. .venv/bin/activate && python -m hhg_logistics.train train.enable=true

eval:
	. .venv/bin/activate && python -m hhg_logistics.eval.harness eval.enable=true

include codex.mk

.PHONY: space-audit space-audit-fast space-explain space-diff space-clean

space-audit:
	@$(MAKE) -f space.mk space-audit

space-audit-fast:
	@$(MAKE) -f space.mk space-audit-fast

space-explain:
	@$(MAKE) -f space.mk space-explain cap=$(cap)

space-diff:
	@$(MAKE) -f space.mk space-diff old=$(old) new=$(new)

space-clean:
	@$(MAKE) -f space.mk space-clean

## Run local gates with the exact same entrypoint humans and bots use
codex-gates:
@bash scripts/codex_local_gates.sh

.PHONY: repo-admin-dry-run repo-admin-apply

repo-admin-dry-run:
	python -m scripts.ops.codex_repo_admin_bootstrap --owner $(owner) --repo $(repo) --detect-default-branch

repo-admin-apply:
	python -m scripts.ops.codex_repo_admin_bootstrap --owner $(owner) --repo $(repo) --apply --detect-default-branch --dependabot-updates

wheelhouse:
	@tools/bootstrap_wheelhouse.sh

fast-tests:
	@PIP_CACHE_DIR=.cache/pip nox -r -s tests

sys-tests:
	@nox --no-venv -s tests_sys

ssp-tests:
	@nox -s tests_ssp

sec-scan:
	@nox -s sec_scan

sec-audit:
	@python tools/pip_audit_wrapper.py

sbom:
	@python scripts/sbom_cyclonedx.py

lock-refresh:
	@bash tools/uv_lock_refresh.sh

lock-hash:
	@pip-compile --generate-hashes -o requirements.txt requirements.in

# Legacy CI target removed; use codex-gates for full local checks

coverage:
	@nox -s ci_local

gates:
	@bash tools/run_quality_gates.sh

lint-policy:
	@python tools/lint_policy_probe.py
	@python tools/select_precommit.py

lint-ruff:
	@LINT_POLICY=ruff python tools/select_precommit.py && pre-commit run -a || true

lint-hybrid:
	@LINT_POLICY=hybrid python tools/select_precommit.py && pre-commit run -a || true

lint-auto:
	@make -s lint-policy && pre-commit run -a || true

fix-shebangs:
	@python tools/shebang_exec_guard.py

hooks:
        @if command -v pre-commit >/dev/null 2>&1; then \
                pre-commit run --all-files; \
        else \
                python -m pre_commit run --all-files; \
        fi
        @if [ "${CODEX_HEAVY_HOOKS:-0}" = "1" ]; then \
                echo "[hooks] running opt-in heavy checks"; \
                if command -v nox >/dev/null 2>&1; then \
                        nox -s sec_scan; \
                else \
                        python -m nox -s sec_scan; \
                fi; \
                python scripts/sbom_cyclonedx.py; \
        fi

integrity:
        @rm -rf __pycache__ .pytest_cache site .ruff_cache
        @python tools/file_integrity_audit.py snapshot .codex/pre_manifest.json
        @${INTEGRITY_STEPS:-true}
        @python tools/file_integrity_audit.py snapshot .codex/post_manifest.json
        @python tools/file_integrity_audit.py compare .codex/pre_manifest.json .codex/post_manifest.json $$(python tools/allowlist_args.py)

.PHONY: uv-fix-lock torch-policy-check torch-repair-cpu precommit-migrate precommit-bootstrap hooks-prewarm hooks-manual

# Deterministic remediation for stale lockfiles:
# When "The lockfile at `uv.lock` needs to be updated, but `--locked` was provided."
uv-fix-lock:
	uv lock
	uv sync --locked
# Refs:
# - uv sync projects + --locked semantics: https://docs.astral.sh/uv/guides/sync/projects/
# - UV_LOCKED env (assert lock up-to-date): https://docs.astral.sh/uv/reference/environment/#uv_locked

# Print JSON status of Torch + policy outcome
torch-policy-check:
	python scripts/torch_policy_check.py

# Force reinstall Torch CPU wheel and re-check
torch-repair-cpu:
	bash scripts/torch_repair_cpu.sh

# Modernize pre-commit config (fix deprecated stage names)
precommit-migrate:
	pre-commit migrate-config  # https://pre-commit.com/#migrate-config

# Bootstrap hook environments once (reduce per-commit slowness)
precommit-bootstrap:
	pre-commit install --install-hooks  # https://pre-commit.com/#using

# Alias: pre-warm hook environments (same as precommit-bootstrap)
hooks-prewarm:
	@pre-commit install --install-hooks

# Run manual-stage hooks (security scanners, etc.) across the repo
hooks-manual:
	@pre-commit run --hook-stage manual --all-files
# ========================================
# Codex Capability Audit Targets
# Added: 2025-10-10 by mbaetiong
# ========================================

.PHONY: audit-full
audit-full:
	@echo "Running full space traversal audit (S1-S7)..."
	python scripts/space_traversal/audit_runner.py run
	python scripts/generate_capability_report.py

.PHONY: audit-fast
audit-fast:
	@echo "Running fast audit (S1, S3, S4, S6)..."
	bash scripts/run_space_audit_fast.sh

.PHONY: validate-all
validate-all:
	@echo "Running comprehensive validation suite..."
	bash scripts/validate_all_capabilities.sh

.PHONY: validate-security
validate-security:
	@echo "Running security validation..."
	bash scripts/validate_security.sh

.PHONY: audit-explain
audit-explain:
	@if [ -z "$(cap)" ]; then \
		echo "Usage: make audit-explain cap=<capability-id>"; \
		exit 1; \
	fi
	python scripts/space_traversal/audit_runner.py explain $(cap)

.PHONY: audit-diff
audit-diff:
	@if [ -z "$(old)" ] || [ -z "$(new)" ]; then \
		echo "Usage: make audit-diff old=<path> new=<path>"; \
		exit 1; \
	fi
	python scripts/space_traversal/audit_runner.py diff --old $(old) --new $(new)

.PHONY: format
format:
	@echo "Formatting code with Black..."
	black --line-length=100 src/ tests/ scripts/

.PHONY: lint
lint:
	@echo "Linting code with Ruff..."
	ruff check src/ tests/ scripts/

.PHONY: typecheck
typecheck:
	@echo "Type checking with mypy..."
	mypy src/security/ --config-file=pyproject.toml

.PHONY: test-quick
test-quick:
	@echo "Running quick tests..."
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/ -q -m "not slow"

.PHONY: test-security
test-security:
	@echo "Running security tests..."
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/security/ -v

.PHONY: clean-audit
clean-audit:
	@echo "Cleaning audit artifacts..."
	rm -rf audit_artifacts/ audit_run_manifest.json reports/capability_matrix_*.md reports/capability_summary.md

.PHONY: help-audit
help-audit:
	@echo "Codex Capability Audit Targets:"
	@echo "  audit-full        - Run complete audit pipeline (S1-S7)"
	@echo "  audit-fast        - Run fast audit (S1, S3, S4, S6)"
	@echo "  validate-all      - Run all validation checks"
	@echo "  validate-security - Run security validation only"
	@echo "  audit-explain     - Explain capability score (make audit-explain cap=checkpointing)"
	@echo "  audit-diff        - Compare two audit runs"
	@echo "  format            - Format code with Black"
	@echo "  lint              - Lint code with Ruff"
	@echo "  typecheck         - Type check with mypy"
	@echo "  test-quick        - Run quick test suite"
	@echo "  test-security     - Run security tests"
	@echo "  clean-audit       - Clean audit artifacts"
