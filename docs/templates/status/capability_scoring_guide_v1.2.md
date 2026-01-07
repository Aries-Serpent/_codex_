# Guide: Capability Scoring & Gaps (v1.2)
> Generated: 2024-11-02 15:21:24 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Capability Scoring Lead], [Secondary: Auditor] ⚡ Energy: 5

Scoring Heuristic
- Base score = severity × confidence (1–5 each)
- Normalized weight = score / sum(scores)

Artifacts
- Input: audit_artifacts/capabilities_raw.json
- Output: audit_artifacts/capabilities_scored.json

Commands
- python tools/capability_autodiscover.py
- python tools/capability_score.py

Thresholds (example)
- High‑priority: weight ≥ 0.15
- Low maturity: severity ≥ 4 and confidence ≤ 3
