# Phase 4 Changes — Build System & CI/CD Optimisation

## Highlights

1. **Hydra plugin hardening** — Coverage sessions run `_check_hydra_plugin()` to
   stage `hydra-core[hydra_plugins]>=1.3` automatically when missing.
2. **Optional dependency audit** — Documented fallbacks and new extras in
   `pyproject.toml`, with an offline test matrix for quick reference.
3. **CI/CD strategy** — Manual-first workflow captured in `docs/ci_cd_strategy.md`
   plus a new `offline_check` nox session.
4. **Docker hardening** — Multi-stage builds for CPU/GPU images, offline wheel
   caching, and GPU-ready docker-compose profiles.
5. **Documentation refresh** — Quickstart, testing guide, and README updated to
   reflect the new layout and offline-first defaults.

## Developer checklist

* Run `nox --noxfile configs/development/noxfile.py -s offline_check` before submitting a PR.
* Install extras as required:
  * `pip install -e '.[test-core]'` — minimal pytest + Hydra stack.
  * `pip install -e '.[test,tracking,ml]'` — full feature set with optional deps.
* Review `docs/docker_guide.md` when building containers or running GPU tests.

## Evidence

Structured JSONL records are written to `.codex/evidence/phase4_*.jsonl` for
Hydra hardening, dependency audits, CI/CD strategy, Docker work, documentation,
and the overall phase sign-off.
