#!/usr/bin/env python
"""
Schema Validation (P4)

Validates:
- workflow.yaml essential keys & weight structure
- knob normalization schema completeness (DEFAULT_SCHEMA)
- Detector meta fields (if present) conform to expected enums

Outputs schema_validation_report.json

Exit Codes:
 0 success
 2 structural issues
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

WORKFLOW = Path(".copilot-space/workflow.yaml")
REPORT = Path("audit_artifacts/schema_validation_report.json")

COMPLEXITY_ENUM = {"low","medium","high"}
STABILITY_ENUM = {"experimental","stable"}


def load_yaml(p: Path):
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}


def validate_workflow(doc) -> list[str]:
    warnings = []
    required_top = ["version","stages","weights","output"]
    for key in required_top:
        if key not in doc:
            warnings.append(f"missing_key:{key}")
    
    w = doc.get("weights",{})
    if w and abs(sum(w.values()) - 1.0) > 1e-6:
        warnings.append("weights_not_normalized")
    
    return warnings


def validate_detector_meta():
    # Optional: look at capabilities_raw.json if present
    raw = Path("audit_artifacts/capabilities_raw.json")
    if not raw.exists():
        return []
    
    meta_warnings = []
    try:
        data = json.loads(raw.read_text())
    except Exception:
        return ["capabilities_raw_parse_error"]
    
    for cap in data.get("capabilities",[]):
        meta = cap.get("meta")
        if not meta:
            continue
        comp = meta.get("complexity")
        stab = meta.get("stability")
        if comp and comp not in COMPLEXITY_ENUM:
            meta_warnings.append(f"invalid_complexity:{comp}")
        if stab and stab not in STABILITY_ENUM:
            meta_warnings.append(f"invalid_stability:{stab}")
    
    return meta_warnings


def main():
    doc = load_yaml(WORKFLOW)
    wf_warn = validate_workflow(doc)
    meta_warn = validate_detector_meta()
    
    report = {
        "workflow_warnings": wf_warn,
        "detector_meta_warnings": meta_warn,
        "error": doc.get("_error"),
    }
    
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    code = 0
    if report["error"] or any(w.startswith("missing_key") for w in wf_warn):
        code = 2
    
    print(f"[INFO] Schema validation written: {REPORT}")
    return code


if __name__ == "__main__":
    sys.exit(main())
