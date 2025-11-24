# Orchestrator Prompt — Golden Harness: RED

The golden harness reports **RED**. Stop non-essential automation and remediate immediately.

- Inspect `golden_harness_status.json` to locate failing signals (RA policies, honesty metadata, tool trace mismatches).
- Re-run required gates locally with tracing to regenerate evidence.
- Provide a concise incident note summarizing failures and remediation steps before resuming.
- Do not proceed to rollout, promotion, or external publication until the status returns to green or a risk waiver is approved.
