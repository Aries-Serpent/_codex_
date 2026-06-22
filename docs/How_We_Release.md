# How We Release

**Last Updated:** 2026-06-22

This repository uses **small, reviewable changes** and local-only checks. We do not enable any CI or paid services by default.

## Release steps (human-driven)
1. Create a feature branch from `main`.
2. Make atomic commits with clear WHY, risk, rollback, and tests/docs notes in the message.
3. Run local gates:
   - `pre-commit run --all-files`
   - `python3 validate_fences.py docs/` (or the paths you changed)
   - `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` (if tests exist locally)
4. Open a PR and request review.
5. Squash-merge with a CHANGELOG entry.
6. Tag a release if applicable.

## Policy
- **No GitHub Actions** without explicit maintainer approval.
- Keep changes reversible and low-risk.
