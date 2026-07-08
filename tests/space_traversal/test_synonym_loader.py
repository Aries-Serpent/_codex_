"""
P6 Test: Synonym Loader

Validates:
- Synonym map loading and expansion
- map_hash computation
- Passthrough when no map present
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ART = Path("audit_artifacts")
SYNONYMS = Path("configs/synonyms/test_synonyms.json")


def setup():
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir()

    raw = {
        "capabilities": [
            {"id": "alpha", "found_patterns": ["train", "checkpoint"]},
            {"id": "beta", "found_patterns": ["unknown"]},
        ]
    }
    (ART / "capabilities_raw.json").write_text(json.dumps(raw), encoding="utf-8")

    # Create test synonym map
    SYNONYMS.parent.mkdir(parents=True, exist_ok=True)
    synonyms = {"train": ["training", "epoch"], "checkpoint": ["save_checkpoint"]}
    SYNONYMS.write_text(json.dumps(synonyms), encoding="utf-8")


def test_synonym_expansion():
    setup()
    env = os.environ.copy()
    env["SYNONYM_MAP_PATH"] = str(SYNONYMS)
    subprocess.run(
        [sys.executable, "scripts/space_traversal/synonym_loader.py"], check=True, env=env
    )

    out = ART / "capabilities_raw_expanded.json"
    assert out.exists(), "Condition must be true"
    data = json.loads(out.read_text())

    # Verify expansion
    alpha = next(c for c in data["capabilities"] if c["id"] == "alpha")
    assert "training" in alpha["found_patterns"], "Condition must be true"
    assert "epoch" in alpha["found_patterns"], "Condition must be true"
    assert alpha["synonym_expansion_count"] > 0, "Value must be greater than zero"

    # Verify map hash
    assert "synonym_map_hash" in data, "Data must not be empty"
    assert len(data["synonym_map_hash"]) == 16, "Collection must not be empty"


def test_synonym_passthrough():
    setup()
    # Remove synonym map
    if SYNONYMS.exists():
        SYNONYMS.unlink()

    subprocess.run([sys.executable, "scripts/space_traversal/synonym_loader.py"], check=True)

    out = ART / "capabilities_raw_expanded.json"
    assert out.exists(), "Condition must be true"
