# Documentation Source-of-Truth and Archive Map

**Last Updated:** 2026-10-02  
**Version:** v0.3.0  
**Status:** Historical compatibility page; not the live product narrative

> This page is intentionally neutral. It exists to make the boundary between active documentation and archive evidence explicit. The live repo state remains in `README.md`, `docs/`, and `mkdocs.yml`.

## Current truth

Use the following as the active source of truth for repository status and guidance:

- `README.md` — project identity, release scope, active runtime policy, and current repo posture
- `docs/` — current human-facing documentation and operating guides
- `mkdocs.yml` — navigation and site settings for the public docs site
- `docs/status/GITHUB_PAGES_STATUS.md` — current status and evidence-backed dashboard
- `docs/archive/README.md` — archive retention policy and historical separation rules
- `docs/DOCUMENTATION_SOURCE_OF_TRUTH.md` — canonical classification of live vs historical docs

## Archive evidence

The following are not the active state of the repository and should not be treated as live operational truth unless explicitly labeled historical:

- `.codex/archive/`
- `docs/archive/`
- `site/archive/`
- older status pages, phase reports, completion memos, and stale deployment narratives

Keep historical backlog and remediation notes in archive roots for context, but do not use them as the primary navigation or status source.

## Public GitHub Pages narrative vs active repo truth

The repository's current documentation posture is evidence-based and branch-scoped.

- Current status docs are authoritative for the present branch and validation evidence.
- Historical pages remain available for audit and recovery, but they are not the product story.
- Deployment or site-status claims must be checked against the current branch evidence and the active status dashboard rather than older phase reports.

## Current references

- [README.md](../README.md)
- [docs/index.md](index.md)
- [docs/status/GITHUB_PAGES_STATUS.md](status/GITHUB_PAGES_STATUS.md)
- [docs/DOCUMENTATION_SOURCE_OF_TRUTH.md](DOCUMENTATION_SOURCE_OF_TRUTH.md)
- [docs/archive/README.md](archive/README.md)

## Archive reminder

This document is a compatibility/clarification page, not a roadmap or release narrative. If a file was produced during investigation or a historical phase, it should live in an archive location rather than being promoted into the active docs layer.