# High-Signal Findings — Run 1 (2025-09-22)

1. **Audit prompt drift** — `AUDIT_PROMPT.md` still references remote fetch instructions and lacks the new Menu/Phase framing. This creates confusion for offline operators. _Action_: rewrite prompt to match audit-first workflow and ensure all fences are language-tagged.
2. **Missing fence gate** — No automation blocked malformed Markdown before this run, leading to thousands of legacy issues (notably under `.codex/`). _Action_: introduce `tools/validate_fences.py` with a narrow default scope and stage cleanup iteratively.
3. **Reports directory absent** — Prior audits scattered outputs across `.codex/status/`. _Action_: establish a curated `reports/` tree (repo map, branch analysis, capability audit, etc.) to serve as the single source of truth going forward.

Future runs should expand into observability (Menu item 5) and security hygiene (Menu item 4) once the foundational audit scaffolding stabilises.
