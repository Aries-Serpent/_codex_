# High-Signal Findings — Run 4 (2025-10-05)

1. **Gap/Risk register established.** The new `reports/gap_risk_resolution.md` distils the 2025-10-05 status update into a closed/open tracker so future runs can prioritise remaining mitigations without re-triaging the audit surface.【F:reports/gap_risk_resolution.md†L1-L15】
2. **Telemetry hardening landed.** Training configuration now exposes `log_system_metrics` and a resilient collector, closing the observability gap flagged in the October status update.【F:reports/_codex_status_update-2025-10-05.md†L57-L57】【F:src/codex_ml/training/__init__.py†L90-L156】
3. **Advanced modeling remains a priority.** Heavy-model support and LoRA validation are still pending; they stay “open” in the tracker to drive a focused follow-up run.【F:reports/gap_risk_resolution.md†L13-L15】【F:reports/_codex_status_update-2025-10-05.md†L53-L53】
4. **Security and deployment gaps still open.** SBOM generation, moderation adapters, and container tooling need dedicated follow-up, carried forward in the register for planning purposes.【F:reports/gap_risk_resolution.md†L14-L15】【F:reports/_codex_status_update-2025-10-05.md†L60-L62】
