from codex_crm.zaf_legacy.reader import _normalise_manifest


def test_manifest_placeholder() -> None:
    manifest = _normalise_manifest({})
    assert any(param["name"] == "API_BASE" for param in manifest["parameters"])
