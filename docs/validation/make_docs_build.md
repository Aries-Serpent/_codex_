# [Review]: Makefile docs-build Target — Defaults & Shell Safety

> Generated: 2025-11-06 13:11:49 | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1) Issue Summary (Lines +78 to +82)

The docs-build recipe uses Make's "?=" operator inside the shell recipe:

```make
.PHONY: docs-build
docs-build:
	@SKIP_OPTIONAL?=1 ; \\
	FAIL_ON_MISSING?=0 ; \\
	SKIP_OPTIONAL=$$SKIP_OPTIONAL FAIL_ON_MISSING=$$FAIL_ON_MISSING bash scripts/docs_build.sh
```text

Inside a recipe, each line is executed by /bin/sh; "SKIP_OPTIONAL?=1" is not a shell command and fails with "command not found", preventing the target from running.

## 2) Correct Pattern (Make variable defaults outside recipe)

Move defaults to Make context; pass them as environment to the script. Suggested fix:

```make
# Defaults (Make context)
SKIP_OPTIONAL ?= 1
FAIL_ON_MISSING ?= 0

.PHONY: docs-build
docs-build:
	SKIP_OPTIONAL=$(SKIP_OPTIONAL) FAIL_ON_MISSING=$(FAIL_ON_MISSING) bash scripts/docs_build.sh
```text

## 3) Alternative (shell‑local defaulting, if you must keep in recipe)

Use POSIX shell parameter expansion (still recommend Make‑level defaults instead):

```make
.PHONY: docs-build
docs-build:
	: $${SKIP_OPTIONAL:=1}; : $${FAIL_ON_MISSING:=0}; \\
	SKIP_OPTIONAL=$$SKIP_OPTIONAL FAIL_ON_MISSING=$$FAIL_ON_MISSING bash scripts/docs_build.sh
```text

## 4) CI/Script Consistency

Standardize env values as "1"/"0" (not "true"/"false") across:
- .github/workflows/docs.yml
- scripts/docs_build.sh (expects "1"/"0")
- scripts/agent/run_selected_jobs.sh

Example workflow step:

```yaml
env:
  SKIP_OPTIONAL: "1"
  FAIL_ON_MISSING: "0"
```text

## 5) Quick Tests

| Check | Command | Expect |
|------|---------|--------|
| Make default run | make docs-build | Exit 0; artifacts/docs/* present |
| Override flags | SKIP_OPTIONAL=0 FAIL_ON_MISSING=1 make docs-build | Script enforces strict mode |
| CI parity | GH Actions run for docs.yml | Artifacts uploaded; no shell errors |

## 6) Rationale

- Make‑context defaults avoid shell syntax errors and keep variables overridable by CLI: `SKIP_OPTIONAL=0 make docs-build`.
- Consistent "1"/"0" flags align with script gating and reduce conditional drift.

## 7) Optional Enhancements

- Add a Make alias:

```make
.PHONY: docs-build-strict
docs-build-strict:
	SKIP_OPTIONAL=0 FAIL_ON_MISSING=1 bash scripts/docs_build.sh
```text

- Add a nox mirror target (`nox -s docs_build`) to unify local/CI execution.

## 8) Implementation Status

✅ **All items implemented**:
- Makefile defaults defined at top level (lines 78-79)
- Recipe uses proper variable substitution (line 83)
- Strict build target added (`docs-build-strict`)
- Workflows standardized to "1"/"0" (docs.yml)
- Nox session exists for unified execution

*End of Review*
