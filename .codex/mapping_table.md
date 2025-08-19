| task | candidate_assets | rationale |
|---|---|---|
| add optional SQLite pool | python files importing sqlite3 | non-invasive monkey-patch via import hook |
| modify log_event/log_message | defs if present | inherit pooled connect via patched sqlite3.connect |
| benchmark throughput | create scripts/benchmark_logging.py | self-contained baseline vs. pooled |
