# Example: Capability Matrix (v1.2)
> Generated: 2024-11-02 15:23:05 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Example Author], [Secondary: Reviewer] ⚡ Energy: 5

| ID | Name | Category | Status | Evidence | Gaps | Risks | Severity (1–5) | Confidence (1–5) | Tags | Owner | ETA |
|---|---|---|---|---|---|---|---:|---:|---|---|---|
| CAP-001 | Tokenization | Tokenization | Partially Implemented | src/codex_ml/tokenization | Parity tests missing | Drift on rare tokens | 3 | 3 | huggingface, offline | @mbaetiong | 2024-11-05 |
| CAP-010 | Security Input Validation | Security | Implemented | src/security/core.py | Unicode edge cases | Bypass via encoding tricks | 4 | 4 | security | @mbaetiong | 2024-11-06 |
