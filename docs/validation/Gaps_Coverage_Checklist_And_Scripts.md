# [Validation]: Gaps Coverage Checklist and Scripts
Roles: [Audit Orchestrator], [Capability Cartographer] Energy: 5

Run after full S1–S7:

1) Completeness: low set equality
```bash
python - << 'PY'
import json, sys, yaml
scored = json.load(open("audit_artifacts/capabilities_scored.json"))
gaps = json.load(open("audit_artifacts/gaps.json"))
cfg = yaml.safe_load(open(".copilot-space/workflow.yaml"))
low_thr = cfg["scoring"]["thresholds"]["low"]
calc_low = {c["id"] for c in scored["capabilities"] if c["score"] < low_thr}
low = {c["id"] for c in gaps["low_maturity"]}
print("Missing in gaps:", sorted(calc_low - low))
print("Unexpected in gaps:", sorted(low - calc_low))
sys.exit(1 if (calc_low - low) or (low - calc_low) else 0)
PY
```text

2) Primary deficit sanity
```bash
python - << 'PY'
import json, sys
gaps = json.load(open("audit_artifacts/gaps.json"))
mismatch = []
for g in gaps["low_maturity"]:
    comps = g["components"]
    if min(comps, key=lambda k: comps[k]) not in comps:
        mismatch.append(g["id"])
print("Primary deficit mismatches:", mismatch)
sys.exit(1 if mismatch else 0)
PY
```text

3) Zero-component inventory
```bash
python - << 'PY'
import json
zeros = json.load(open("audit_artifacts/component_gaps.json"))
print(json.dumps(zeros, indent=2))
PY
```text

4) Missing required patterns
```bash
python - << 'PY'
import json
scored = json.load(open("audit_artifacts/capabilities_scored.json"))
for c in scored["capabilities"]:
    req = set(c.get("required_patterns", []))
    found = set(c.get("found_patterns", []))
    miss = sorted(req - found)
    if miss:
        print(c["id"], "missing:", ", ".join(miss))
PY
```text

5) Missing detectors (overrides)
```bash
python - << 'PY'
import json, yaml
cfg = yaml.safe_load(open(".copilot-space/workflow.yaml"))
over = (cfg.get("capability_map", {}) or {}).get("overrides") or {}
scored = json.load(open("audit_artifacts/capabilities_scored.json"))
have = {c["id"] for c in scored["capabilities"]}
missing = sorted(set(over.keys()) - have)
print("Missing detectors:", missing)
exit(1 if missing else 0)
PY
```text

Checklist:
- [ ] gaps.json matches threshold logic
- [ ] component_gaps.json present and reasonable
- [ ] missing_patterns populated for low entries
- [ ] validate gate fails when expected
- [ ] manifest includes thresholds and missing_detectors
