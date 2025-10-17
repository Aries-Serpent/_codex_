# Codebase Archival & Hygiene Policy

> Purpose: keep the working tree lean while preserving auditability and supply-chain integrity.

**Method:** remove live code/docs by replacing them with small *tombstone* stubs that include stable IDs and hashes which link to an **append-only evidence log** (JSONL). Reviewers verify provenance through the stub→log trail in pull requests. For repo-wide end-of-life, set the repository **read-only (Archived)**.
@-- References:
CODEOWNERS (GitHub): https://docs.github.com/articles/about-code-owners
Repo archival (GitHub): https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories
Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/
Keep a Changelog: https://keepachangelog.com/en/1.1.0/
ADRs: https://adr.github.io/
SLSA provenance: https://slsa.dev/provenance
in-toto: https://in-toto.io/docs/specs/
SBOM: SPDX https://spdx.github.io/ , CycloneDX https://cyclonedx.org/
git-filter-repo: https://github.com/newren/git-filter-repo
--

## 1. Governance & Traceability
- **Ownership:** Changes gated by **CODEOWNERS** and branch protection requiring “Require review from Code Owners.”
- **Decision record:** Every non-trivial archival has an **ADR** (`/docs/arch/adr-YYYYMMDD-<slug>.md`). Link ADRs from PRs.
- **Provenance:** Attach a lightweight **attestation** (who/when/inputs/digests) aligned with **SLSA/in-toto**.
- **Change log:** Use **Conventional Commits** for commits and **Keep a Changelog** for releases; record deprecations/removals.

## 2. Cadence
- Run “archive hygiene” each release cycle and **at least quarterly**: *plan → execute → summarize → vacuum*.
- Maintain a predictable deprecation window; publish outcomes in the CHANGELOG.

## 3. Identification (What is “dead/pruned”?)
A unit is a candidate when all are true:
1. **Age/Inactivity** ≥ τ days (default τ=180, configurable).
2. **Usage/Refs** == 0 (or below policy threshold) via dependency/usage scans.
3. **Coverage/Ownership** low or orphaned; or explicitly **deprecated**.
4. **Planner score** rates it in the removal band.

> Symbolic policy:  Candidate(p) = 𝟙{age(p)≥τ} · 𝟙{refs(p)≤r_min} · 𝟙{owner(p)∈CODEOWNERS}.
> Decision(p) = Archive with tombstone+attestation if Candidate and ADR approved; else Rescue with ADR + owner.

## 4. Evidence Log (append-only)
- File: `.codex/evidence/archive_ops.jsonl` (one line per archived unit).
- Append-only: new entries only; never rewrite prior lines.
- Each line includes: `id`, `path`, `sha256`, `removed_by`, `when`, `adr`, `reason`, `provenance`.
```json
{"id":"arch-2025-10-16-1234","path":"src/foo/bar.py","sha256":"…","removed_by":"@owner","when":"2025-10-16T19:44:00Z","adr":"docs/arch/adr-0421-archive-foo.md","reason":"orphaned, 0 refs, age>180d","provenance":"attestations/arch-2025-10-16-1234.intoto.jsonl"}
```

## 5. PR Checklist (must pass)
- CODEOWNERS approvals present.
- ADR linked in PR body (Context, Decision, Consequences).
- Conventional Commit message; **BREAKING CHANGE** if applicable.
- Evidence log entry added; tombstone file references `id`/digest.
- SBOM reverse-dep check is green (SPDX/CycloneDX).
- Provenance attestation present and well-formed.
- CHANGELOG updated (Deprecated/Removed).

## 6. Scheduled Hygiene
- Generate planner report; open issues for pending removals.
- Run **summary/vacuum** to prune stale tombstones, refresh summaries.
- Publish CHANGELOG updates (deprecations/removals).

## 7. Safe History Rewrite (exception-only)
If sensitive data leaked into history, use **git-filter-repo** (not `filter-branch`), then coordinate a forced push with stakeholders. Follow GitHub’s “Removing sensitive data” guide.

## 8. Repository-Level Archival
For fully deprecated projects, **archive the repository** (read-only). Update README with migration pointers.

## 9. Retention
Retain evidence logs and attestations per `docs/ops/retention.md`. ADRs are never deleted—only superseded.
