# Open Questions & Next Steps — Run 3 (2025-09-22)

## Menu Items Covered This Run
- ✅ **Docs polish (7)** — Replaced the audit prompt with the offline-first template and documented deterministic artefacts.
- ✅ **Quality gates (3)** — Added `codex_local_audit.sh` to exercise pre-commit, fence validation, and the audit shim offline.
- ✅ **Self-management (8)** — Published the offline audit validation guide and prompt copy workflow for repeatable runs.

## Proposed Menu Focus for Run 4
1. **Repo map (1)** — Execute the refreshed audit runner to populate `reports/audit.json` and validate inventory coverage.
2. **Fix folder (2)** — Apply the audit outputs to harden a high-churn path using the new deterministic workflow.
3. **Performance (6)** — Profile identified hotspots once inventory results surface (e.g., heavy CLI modules).

## Outstanding Questions
- What lightweight Python module should back `scripts/codex-audit` so the shim resolves without installing the full stack?
- How should we snapshot large-file hashes (>5MB) without bloating reports while maintaining reproducibility guarantees?
- Which follow-up automation keeps `reports/prompt_copy.md` synchronized during successive runs without manual copies?
- Should the evaluation NDJSON schema mirror the training metrics schema (run id,
  step, split) for downstream ingestion parity?

---

## Historical Snapshot
### Run 2 (2025-09-22)
- Covered Menu items: Security (4), Observability (5), Self-management (8).
- Added security sweep and observability templates plus shared audit artefact library.
- Outstanding automation and reproducibility questions rolled forward above.

### Run 1 (2025-09-22)
- Covered Menu items: Repo map (1), Quality gates (3), Docs polish (7).
- Seeded foundational audit reports, fence validator, and prompt refresh.
- Pending investigations captured above remain relevant until resolved.
