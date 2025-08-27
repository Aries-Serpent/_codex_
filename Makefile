.PHONY: format lint test build type setup venv env-info

format:
	pre-commit run --all-files

lint:
	ruff src tests

test:
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

.PHONY: archive-gha-workflows archive-other-ci archive-paths

archive-gha-workflows:
	@mkdir -p archive/removed
	@set -e; files=$$(ls .github/workflows/*.{yml,yaml} 2>/dev/null || true); \
	if [ -z "$$files" ]; then echo "No workflow files found. Nothing to archive."; \
	else echo "Archiving: $$files"; mv $$files archive/removed/; git add archive/removed/; git rm -r $$files; fi

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
	else echo "Archiving: $$found"; mv $$found archive/removed/; git add archive/removed/; git rm -r $$found; fi

archive-paths:
	@test -n "$$P" || (echo "Usage: make archive-paths P='<path1> <path2> ...>'" && exit 2)
	mv $$P archive/removed/; git add archive/removed/; git rm -r $$P
