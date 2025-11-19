from scripts.space_traversal import audit_runner


def sample_cap(cap_id, evidence, patterns):
    return {
        "id": cap_id,
        "evidence_files": evidence,
        "found_patterns": patterns,
        "required_patterns": patterns,
        "meta": {},
    }


def test_apply_overrides_merges_aliases():
    capabilities = [
        sample_cap("train_loop", ["src/train.py"], ["train", "loop"]),
        sample_cap("training-engine", ["README.md"], ["train"]),
    ]
    overrides = {"training-engine": ["train_loop"]}

    merged, missing = audit_runner.apply_overrides(capabilities, overrides, False)

    assert missing == []
    assert len(merged) == 1
    entry = merged[0]
    assert entry["id"] == "training-engine"
    assert sorted(entry["evidence_files"]) == ["README.md", "src/train.py"]
    assert set(entry["found_patterns"]) == {"train", "loop"}
    assert "override_aliases" in entry["meta"]


def test_apply_overrides_missing_alias_strict_exit():
    capabilities = [sample_cap("training-engine", ["README.md"], ["train"])]
    overrides = {"training-engine": ["train_loop"]}

    try:
        audit_runner.apply_overrides(capabilities, overrides, True)
    except SystemExit as exc:
        assert exc.code == 5
    else:
        raise AssertionError("SystemExit expected")
