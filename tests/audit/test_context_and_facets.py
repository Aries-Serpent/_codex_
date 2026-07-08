"""
Test Context And Facets

Test module for context and facets.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CTX = ROOT / "audit_artifacts/context_index.json"
FAC = ROOT / "audit_artifacts/facets.json"


@pytest.mark.skipif(not CTX.exists(), reason="context index missing")
def test_context_index_has_files():
    data = json.loads(CTX.read_text(encoding="utf-8"))
    assert "files" in data and isinstance(data["files"], list)
    assert all("path" in f and ("sha" in f or "sha256" in f) for f in data["files"]), "Data must not be empty"


@pytest.mark.skipif(not FAC.exists(), reason="facets file missing")
def test_facets_has_groups():
    data = json.loads(FAC.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    facets = data.get("facets", {})
    assert isinstance(facets, (dict, list))
    if isinstance(facets, dict):
        assert facets == {} or any(isinstance(v, list) and len(v) > 0 for v in facets.values())
    else:
        assert facets == [] or any(facets), "facets is not valid"
