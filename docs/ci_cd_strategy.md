# CI/CD Strategy — Manual-First, Offline-Capable

**Last Updated:** 2026-06-22

Phase 4 confirms that the Codex delivery model relies on local quality gates
instead of hosted CI, keeping the workflow compliant with the repository
restrictions in `AGENTS.md`.

## Design rationale

* **No GitHub Actions** — `.github/workflows/` remains disabled.
* **Manual gates** — Contributors run `pre-commit` and `nox` locally before
  pushing changes.
* **Offline compliance** — Test sessions and coverage can execute without
  network access, backed by the new `offline_check` nox session.
* **Future-ready** — A non-activated workflow template can live under
  `.github/workflows/ci-template.yml` if needed later.

## Local workflow

1. **Pre-commit hooks**
   ```bash
   pre-commit run --all-files
   ```
2. **Focused linting / type checking**
   ```bash
   nox --noxfile configs/development/noxfile.py -s lint typecheck
   ```
3. **Full unit tests**
   ```bash
   nox --noxfile configs/development/noxfile.py -s tests
   ```
4. **Coverage audit**
   ```bash
   nox --noxfile configs/development/noxfile.py -s coverage
   ```
5. **Offline verification**
   ```bash
   nox --noxfile configs/development/noxfile.py -s offline_check
   ```

## Offline assumptions

* No external downloads at runtime — model artefacts must be staged locally
  (see `docs/docker_guide.md`).
* Optional dependencies are guarded with `pytest.importorskip` and documented in
  `docs/optional_dependencies.md`.
* Environment variables such as `CODEX_OFFLINE=1` prevent accidental HTTP calls.

## Evidence logging

* Phase 4 sessions emit JSONL entries under `.codex/evidence/` describing the
  manual gates that were executed.
* Developers should append new records when they run bespoke validation flows.

## Future consideration

* If centralised CI becomes necessary, reuse the local workflow commands in a
  template but obtain explicit approval before activating any workflow files.
