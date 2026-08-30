# Documentation layer source-of-truth

**Last updated:** 2026-08-30
**Repository version:** v0.3.0

This file is the canonical classification for the repository's documentation, planset, and archive surfaces. It replaces ad hoc assumptions that treat plan files or archive roots as live documentation without checking whether they are active, historical, or compatibility-only.

## 1. Source-of-truth rule

Use the following precedence when deciding which files define current documentation state:

1. `README.md`, `docs/`, and `mkdocs.yml` are the active documentation layer.
2. `docs/archive/` and `docs/plans/archive/` are historical archive roots for superseded material.
3. `.codex/archive/` and `.github/workflows/_archived/` are operational historical records, not active documentation contracts.
4. `config_legacy/`, `yaml_legacy/`, `conf/`, and other compatibility shims are compatibility-only surfaces and should not be treated as the primary documentation source.

## 2. Active documentation layer

These are the current source-of-truth entries for the docs layer:

- `README.md` — project identity, release status, active runtime policy, and repository hygiene guidance.
- `docs/REPOSITORY_EXPLANATION.md` — evidence-based repository overview and status vocabulary.
- `docs/REPOSITORY_MAP.md` — primary navigation map for the repository.
- `docs/WORKFLOW_MAP.md` — active workflow and governance map.
- `docs/ROADMAP.md` — current high-level roadmap.
- `docs/` — active human-facing guidance, architecture, runbooks, and onboarding.
- `mkdocs.yml` — live documentation site configuration.
- `site/` — generated static output derived from the active doc source.

## 3. Historical plan and archive roots

These are historical or operational archives and must be treated as secondary evidence only:

### Historical plansets

- `.github/plans/` — branch remediation plansets for the `0D_base_` branch; historical and complete by status in `.github/plans/INDEX.md`.
- `.codex/plans/` — operational planset corpus that contains dated status, reinforcement, and remediation documents; treat as historical unless a file is directly referenced by current operational guidance.
- `docs/plans/archive/` — completed phase plans and consolidation records preserved for traceability.

### Historical archive roots

- `.codex/archive/` — operational archive of sessions, PR resolutions, coverage reports, and root-consolidation outputs.
- `.codex/archive/root-consolidation/` — archived root cleanup, temp outputs, and legacy phase histories.
- `.github/workflows/_archived/` — disabled legacy workflow definitions preserved for audit and reactivation review.
- `docs/archive/` — repository-level archive for superseded phase reports and validation dumps.
- `site/archive/` — generated static archive snapshots and older site output; not source-of-truth for current docs.

## 4. Compatibility-only surfaces

These are compatibility or bridge locations and are not the active source-of-truth for current docs or configuration:

- `conf/` — compatibility and split-root config surfaces; `configs/` is the primary configuration tree.
- `config_legacy/` — historical configuration compatibility layer.
- `yaml_legacy/` — legacy YAML compatibility layer.
- `cli/` — historical CLI surface; current CLI entry points live under `src/` and installed package names.
- `training/` and `tokenization/` — package mirrors retained for compatibility with the installed package boundary, not the canonical implementation location.
- `docs/archive/consolidated/` — generated historical snapshots kept only for audit; not an active doc source.

## 5. Stale references to treat as historical, not living docs

The following root causes create stale plan/archive references when documents are treated as if they were still active:

- Version drift: plan indexes carry older version labels (`v0.2.0`) while the live repository is `v0.3.0`.
- Branch-scoped history: `.github/plans/INDEX.md` is a completed branch remediation index, not an active repository roadmap.
- Archive roots being read as active: `.codex/archive/`, `docs/archive/`, and `site/archive/` are preserved for auditing and retrieval, not for current navigation.
- Historic operational status accidentally allowed to masquerade as current runtime policy: completed plans and archived workflows remain important, but they are not current source-of-truth files.

## 6. Corrected source-of-truth set

The canonical set for the documentation layer is:

- `README.md`
- `docs/REPOSITORY_EXPLANATION.md`
- `docs/REPOSITORY_MAP.md`
- `docs/WORKFLOW_MAP.md`
- `docs/ROADMAP.md`
- `docs/plans/README.md`
- `docs/archive/README.md`
- `.codex/archive/ARCHIVE_INDEX.md`
- `.github/plans/INDEX.md` (historical/complete, not active)
- `mkdocs.yml`

Use the archive roots only as historical evidence and retrieval targets, not as the primary navigation or status source for the active docs layer.

## 7. Canonical relationship summary

```text
Active docs source-of-truth:
  README.md
  docs/
  mkdocs.yml
  site/ (generated output)

Historical planning and archive evidence:
  .github/plans/
  .codex/plans/
  .codex/archive/
  docs/archive/
  docs/plans/archive/
  .github/workflows/_archived/
  site/archive/

Compatibility-only layers:
  conf/
  config_legacy/
  yaml_legacy/
  cli/
  training/
  tokenization/
```

This classification is intentionally conservative: when a plan or archive file is not directly tied to the active workflow or current repository guidance, it remains historical evidence rather than the current documentation contract.
