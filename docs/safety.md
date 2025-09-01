<!-- BEGIN: CODEX_DOCS_SAFETY -->

# Safety

- Blocklist/Allowlist, regex heuristics.
- Logits masking helper.
- Sandboxed subprocess execution (best-effort).
- Limitations and red-team considerations.
- API layer masks strings resembling API keys (e.g. `sk-...`) unless `DISABLE_SECRET_FILTER=1`.

> **Note to Codex:** Expand with concrete red-team datasets & tests.
