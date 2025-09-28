# Deprecated: Python Variant (FastAPI) — Reference Only

This repository standardizes on the **Node/Express** bridge (`.codex/copilot_bridge/bridge/server.js`) as the canonical implementation.

If you previously tested a Python/FastAPI variant, consider it **archived**. The Node bridge:
- Aligns with `.codex/` confinement policy,
- Uses the same API contract (`POST /copilot/run`),
- Returns both **CLI** and **bridge** manifest paths + SHA-256,
- Enforces the same default **allow/deny** policy.

> Use this folder only for notes or future comparisons. No Python code is shipped here.

