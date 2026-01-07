# Guide: Authoring the `_codex_` Daily Status Update (v1.1)
> Generated: 2025-11-02 11:32:31 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Authoring Guide Maintainer], [Secondary: QA Reviewer] ⚡ Energy: 5  
⚛️ Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️

This guide explains how to produce the daily report using codex_status_template_v1.1.md.

## 1. Cadence and Storage
- Frequency: Daily (one comprehensive document).
- Location:
  - Template: docs/templates/status/codex_status_template_v1.1.md
  - Reports: reports/daily/<YYYY‑MM‑DD>.md
- Retention:
  - Keep last 30 reports (rolling window).
  - Optional: archive older than 90 days into zip/tar.gz.

## 2. Title and Metadata
- Title (H1): "📍 `_codex_` : Status Update <YYYY‑MM‑DD‑HH:mm:z‑UTC>"
- Timestamp: Use UTC ISO8601.
- Record author(s) and reviewer(s).
- Note the Template Version used (v1.1).

## 3. Full Snapshot vs Delta
- Always produce a full snapshot.
- Then compute a Delta from the previous report:
  - Compare coverage % (Δ), high-signal findings, issues/PRs, performance metrics, changed modules/files, and capability catalog changes (adds/removals/updates).
  - If previous report missing: mark "Delta N/A (reason)".

## 4. Scoring Rubric
- Severity 1–5, Confidence 1–5 must be present on:
  - Capability entries (Core table and Extended Catalog)
  - High‑Signal Findings
  - Atomic Patch Diffs
  - Reproducibility Registry entries (recommended)

## 5. Dynamic Capabilities
- Use the Core Capability Table for common areas.
- Add ANY additional capabilities in the Extended Capability Catalog:
  - Create a new CAP‑ID (e.g., CAP‑017).
  - Fill Category, Tags, Owner, ETA as applicable.
  - Reference CAP‑IDs within related Atomic Patch Diffs.
- Log discoveries in the Capability Discovery Log with evidence and rationale.

## 6. Reproducibility (Extensible)
- Fill Core Controls for baseline coverage.
- Add new controls in the Reproducibility Registry:
  - Create REPRO‑IDs (e.g., REPRO‑006).
  - Include severity/confidence when a gap or risk is present.
  - Set Next Audit to ensure continuous verification.

## 7. Atomic Patch Diffs
- Use canonical Begin/End Patch markers and unified diff format.
- Each patch must include:
  - Why, Risk (1–5), Confidence (1–5), Rollback, Tests/Docs, Validation Checklist.
  - CAP‑IDs and REPRO‑IDs impacted (when applicable).
- Prefer feature flags for risky changes and chunk large patches.

## 8. Automation Inputs (Daily)
- Populate:
  - Issues (full list, no truncation) in a list code block:
    ```list type="issue"
    data:
    # do not truncate entries returned by tools
    ```
  - PRs (full list, no truncation) in a list code block:
    ```list type="pr"
    data:
    # do not truncate entries returned by tools
    ```
  - Coverage %, dependency audit, security scan, performance snapshot.
  - Optional: Capability Auto‑Discovery notes.

## 9. Tokenization Insights
- Report tokenizer(s), settings (padding/truncation), max sequence policy, special tokens, caching/parity, offline considerations (local vocabs/models), and actionable recommendations.

## 10. Secret‑Masking
- Redact secret-like tokens as "[REDACTED:<class>]".
- Avoid quoting .env or secrets files.
- If exposure suspected: remove content, rotate secret, document incident separately.

## 11. Review and DoD
- Before publishing:
  - Lint/typecheck summaries provided
  - Tests updated and passing
  - Coverage recorded (and Δ computed)
  - Security scans summarized
  - All Severity/Confidence fields present
  - Secret-masking verified
  - Patches validated with checklist
  - CAP‑IDs/REPRO‑IDs cross‑linked where applicable

## 12. Template Updates
- Update template version and embedded CHANGELOG when structure changes.
- Keep JSON/YAML schemas aligned with any new fields.
