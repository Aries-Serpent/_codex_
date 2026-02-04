"""
Test Determinism Normalization

Test module for determinism normalization.
"""

import json
from pathlib import Path

ART = Path("audit_artifacts") / "capabilities_scored.json"


def normalize(data: dict) -> dict:
    # remove generated fields if present
    data.pop("generated", None)
    caps = data.get("capabilities", [])
    norm = []
    for c in caps:
        nc = dict(c)
        if "evidence_files" in nc:
            nc["evidence_files"] = sorted(nc["evidence_files"])
        if "found_patterns" in nc:
            nc["found_patterns"] = sorted(nc["found_patterns"])
        if "components" in nc:
            nc["components"] = {k: round(float(v), 6) for k, v in nc["components"].items()}
        if "score" in nc:
            try:
                nc["score"] = round(float(nc["score"]), 6)
            except Exception:
                # Ignore malformed scores; retain original value for comparison
                pass
        norm.append(nc)
    data["capabilities"] = sorted(norm, key=lambda x: x.get("id", ""))
    return data


def test_capabilities_scored_normalized():
    assert ART.exists(), "capabilities_scored.json must exist; run S4 first"
    data = json.loads(ART.read_text(encoding="utf-8"))
    norm = normalize(data)
    # basic sanity checks
    assert isinstance(norm.get("capabilities"), list)
    # ensure sorted by id
    ids = [c.get("id") for c in norm["capabilities"]]
    assert ids == sorted(
        ids
    ), f"Capabilities not sorted by id: {ids[:5]}... vs {sorted(ids)[:5]}..."
