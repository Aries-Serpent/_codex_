task: unfinished-code-harvest -> candidates: [src, tests, scripts, tools, codex] -> rationale: primary Python modules, test harness, helper scripts, developer tools

| candidate | C_code | H_hints | T_tests | R_risk | Score | rationale |
| --- | --- | --- | --- | --- | --- | --- |
| tests | 1.0 | 0.125 | 1 | 0 | 1.262 | tests |
| tools | 1.0 | 0.5 | 0 | 0 | 1.25 | tools |
| src | 1.0 | 0.0 | 0 | 0 | 1.0 | primary source |
| scripts | 1.0 | 0.0 | 0 | 0 | 1.0 | scripts |
| codex | 1.0 | 0.0 | 0 | 0 | 1.0 | helper modules |
# Mapping Table
Generated: 2025-08-18T23:40:38.367402Z
## Task → Candidate Assets → Rationale
| Rank | File | Score F | Signal S | Rationale |
|---:|---|---:|---:|---|
| 1 | `tools/codex_workflow_session_query.py` | 1.57 | 2 | High unfinished markers; central path weight. |
| 2 | `tools/codex_logging_workflow.py` | 1.57 | 2 | High unfinished markers; central path weight. |
| 3 | `scripts/apply_session_logging_workflow.py` | 1.57 | 2 | High unfinished markers; central path weight. |
| 4 | `tools/git_patch_parser_complete.py` | 0.87 | 1 | High unfinished markers; central path weight. |

## Session Log DB Path Unification
- `src/codex/logging/export.py` – defines `_DEFAULT_DB` and env override
- `src/codex/logging/session_logger.py` – logging API honoring env/default
- `src/codex/logging/viewer.py` – viewer CLI using env or autodetect
- `tools/codex_log_viewer.py` – helper viewer defaulting to `.codex/session_logs.db`
- `README.md` and `documentation/end_to_end_logging.md` – document default path and `CODEX_LOG_DB_PATH`
