from codex_crm.zaf_legacy.reader import _normalize_manifest


def test_manifest_placeholder() -> None:
    manifest = _normalize_manifest({})
    parameters = manifest["parameters"]
    assert any(param["name"] == "API_BASE" for param in parameters)
