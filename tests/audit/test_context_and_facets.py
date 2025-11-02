from pathlib import Path
import json
import pytest

CTX = Path("audit_artifacts/context_index.json")
FAC = Path("audit_artifacts/facets.json")

@pytest.mark.skipif(not CTX.exists(), reason="context index missing")
def test_context_index_has_files():
    data = json.loads(CTX.read_text(encoding="utf-8"))
    assert "files" in data and isinstance(data["files"], list)
    assert all("path" in f and "sha256" in f for f in data["files"])

@pytest.mark.skipif(not FAC.exists(), reason="facets file missing")
def test_facets_has_groups():
    data = json.loads(FAC.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    # At least one non-empty facet
    assert any(isinstance(v, list) and len(v) > 0 for v in data.values())
