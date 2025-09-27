.PHONY: codex-setup-dev codex-install-hooks codex-precommit-all codex-autoformat \
	codex-audit codex-audit-clean codex-secrets-baseline codex-block-gha \
	codex-image codex-image-gpu codex-run codex-run-gpu \
	archive-gha-workflows archive-other-ci archive-paths

SHELL := /bin/bash
PY ?= python3
CODEx_SEMGREP_DIR := semgrep_rules
CODEx_AUDIT_DIR := .codex_audit
CODEx_PIP_PKGS := pre-commit ruff black isort bandit semgrep detect-secrets mdformat yamllint shellcheck-py

codex-setup-dev:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install --upgrade $(CODEx_PIP_PKGS)
	@echo "✔ Codex local toolchain installed."

codex-install-hooks:
	pre-commit install -t pre-commit -t pre-push
	@echo "✔ pre-commit hooks installed (pre-commit + pre-push)."

codex-precommit-all:
	pre-commit run --all-files

codex-autoformat:
	isort --profile black --filter-files .
	black .

$(CODEx_SEMGREP_DIR):
	mkdir -p $(CODEx_SEMGREP_DIR)

codex-audit: $(CODEx_SEMGREP_DIR)
	mkdir -p $(CODEx_AUDIT_DIR)
	@echo "==> Repo stats (tokei|scc|cloc)"
	@if command -v tokei >/dev/null 2>&1; then tokei . | tee $(CODEx_AUDIT_DIR)/stats.txt; \
	elif command -v scc >/dev/null 2>&1; then scc . | tee $(CODEx_AUDIT_DIR)/stats.txt; \
	elif command -v cloc >/dev/null 2>&1; then cloc . | tee $(CODEx_AUDIT_DIR)/stats.txt; \
	else echo "Install tokei/scc/cloc for LOC stats" | tee $(CODEx_AUDIT_DIR)/stats.txt; fi
	@echo "==> File list"
	@if command -v fd >/dev/null 2>&1; then fd -H -t f -E venv -E .venv -E node_modules > $(CODEx_AUDIT_DIR)/filelist.txt; \
	else find . -type f -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./node_modules/*" > $(CODEx_AUDIT_DIR)/filelist.txt; fi
	@echo "==> Debt scan (TODO/FIXME/NotImplemented/pass)"
	@if command -v rg >/dev/null 2>&1; then rg -n --hidden -S --pcre2 "(TODO|FIXME|HACK|XXX|NotImplementedError|^\s*pass\s*$)" -g '!venv' -g '!.venv' -g '!node_modules' > $(CODEx_AUDIT_DIR)/debt.txt || true; \
	else grep -RInE "(TODO|FIXME|HACK|XXX|NotImplementedError|^[[:space:]]*pass[[:space:]]*$$)" --exclude-dir=.git --exclude-dir=venv --exclude-dir=.venv --exclude-dir=node_modules . > $(CODEx_AUDIT_DIR)/debt.txt || true; fi
	@echo "==> Symbols (ctags)"
	@if command -v ctags >/dev/null 2>&1; then ctags -R --fields=+n --extras=+q -f $(CODEx_AUDIT_DIR)/tags .; else echo "Install ctags for symbol index" > $(CODEx_AUDIT_DIR)/tags; fi
	@echo "==> Semgrep (offline, local rules)"
	@if command -v semgrep >/dev/null 2>&1; then semgrep --error --config $(CODEx_SEMGREP_DIR)/ --disable-version-check | tee $(CODEx_AUDIT_DIR)/semgrep.txt || true; else echo "Install semgrep for policy scan" > $(CODEx_AUDIT_DIR)/semgrep.txt; fi
	@echo "==> Done. Outputs in $(CODEx_AUDIT_DIR)/"

codex-audit-clean:
	rm -rf $(CODEx_AUDIT_DIR)

codex-secrets-baseline:
	@echo "Creating/refreshing .secrets.baseline ..."
	@detect-secrets scan > .secrets.baseline
	@echo "✔ Baseline written to .secrets.baseline. Review & commit it."

codex-image:
	docker build -t codex-ml:cpu .

codex-image-gpu:
	docker build -t codex-ml:gpu -f Dockerfile.gpu .

codex-run:
	docker run --rm -it -v $(PWD):/app codex-ml:cpu --help

codex-run-gpu:
	docker run --rm -it --gpus all -v $(PWD):/app codex-ml:gpu --help

codex-block-gha:
	@mkdir -p .git/info
	@grep -qxF '.github/workflows/' .git/info/exclude 2>/dev/null || echo '.github/workflows/' >> .git/info/exclude
	@echo "✔ Locally ignoring .github/workflows/* (pre-commit also blocks staging)."

archive-gha-workflows:
	@mkdir -p archive/removed
	@echo "Scanning for .github/workflows/*.yml(yaml) ..."
	@set -e; \
	files=$$(ls .github/workflows/*.{yml,yaml} 2>/dev/null || true); \
	if [ -z "$$files" ]; then echo "No workflow files found. Nothing to archive."; \
	else echo "Archiving: $$files"; scripts/archive_paths.sh $$files; fi

archive-other-ci:
	@mkdir -p archive/removed
	@set -e; found=""; \
	for p in \
	  .circleci \
	  .gitlab-ci.yml \
	  .gitlab/ci.yml \
	  .travis.yml \
	  .drone.yml \
	  azure-pipelines.yml \
	  bitbucket-pipelines.yml \
	  .woodpecker.yml \
	  .buildkite/pipeline.yml \
	  Jenkinsfile \
	  .teamcity \
	  appveyor.yml \
	; do \
	  if [ -e "$$p" ]; then found="$$found $$p"; fi; \
	done; \
	if [ -z "$$found" ]; then echo "No non-Codex CI files found."; \
	else echo "Archiving: $$found"; scripts/archive_paths.sh $$found; fi

archive-paths:
	@test -n "$$P" || (echo "Usage: make archive-paths P='<path1> <path2> ...>'" && exit 2)
	@scripts/archive_paths.sh $$P
