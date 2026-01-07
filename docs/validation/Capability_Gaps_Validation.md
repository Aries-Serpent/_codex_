# Validation: Capability Gaps Analysis (v1.2)
> Generated: 2024-11-02 15:23:05 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Capability Auditor], [Secondary: QA Reviewer] ⚡ Energy: 5

Purpose
- Identify low‑maturity and/or high‑risk capabilities to prioritize in patches and findings.

Heuristics
| Metric | Definition | Default Threshold | Notes |
|---|---|---:|---|
| Maturity | confidence / 5.0 | < 0.70 | Confidence is 1–5 scale from capability entries |
| Risk | severity (1–5) | >= 4 | Severity is 1–5 impact scale |
| Weight | Normalized importance | n/a | From tools/capability_score.py |

Commands
- Generate scores: `python tools/capability_score.py`
- Analyze gaps: `python tools/gaps_analyze.py --maturity-threshold 0.70 --severity-threshold 4`

Artifacts
- Input: `audit_artifacts/capabilities_scored.json`
- Output: `audit_artifacts/gaps.json`

Report Integration
- Populate section 2.8 (Audit Integrity Chain) with gaps.json hash
- Link flagged CAP‑IDs to PATCH‑IDs in section 4 (Atomic Patch Diffs)
