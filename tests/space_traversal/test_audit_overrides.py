"""Tests for capability overrides functionality in audit_runner."""


def test_apply_overrides_basic():
    """Test basic override application merging aliases into canonical IDs."""
    from scripts.space_traversal.audit_runner import apply_overrides

    capabilities = [
        {
            "id": "training-engine",
            "evidence_files": ["train.py"],
            "found_patterns": ["train"],
            "required_patterns": ["train", "epoch"],
            "meta": {},
        },
        {
            "id": "train_loop",
            "evidence_files": ["loop.py"],
            "found_patterns": ["epoch"],
            "required_patterns": ["train", "epoch"],
            "meta": {"source": "detector"},
        },
    ]

    cfg = {
        "capability_map": {"overrides": {"training-engine": ["train_loop", "functional_training"]}}
    }

    result = apply_overrides(capabilities, cfg)

    # Should merge into single capability
    assert len(result) == 1, "Result must not be empty"
    assert result[0]["id"] == "training-engine", "Result must not be empty"
    assert set(result[0]["evidence_files"]) == {"train.py", "loop.py"}
    assert set(result[0]["found_patterns"]) == {"train", "epoch"}
    assert set(result[0]["required_patterns"]) == {"train", "epoch"}


def test_apply_overrides_no_config():
    """Test that overrides work when no config is provided."""
    from scripts.space_traversal.audit_runner import apply_overrides

    capabilities = [
        {
            "id": "cap1",
            "evidence_files": ["a.py"],
            "found_patterns": ["pat1"],
            "required_patterns": ["pat1"],
            "meta": {},
        },
    ]

    cfg = {}
    result = apply_overrides(capabilities, cfg)

    # Should return unchanged
    assert len(result) == 1, "Result must not be empty"
    assert result[0]["id"] == "cap1", "Result must not be empty"


def test_apply_overrides_multiple_aliases():
    """Test merging multiple aliases into one canonical ID."""
    from scripts.space_traversal.audit_runner import apply_overrides

    capabilities = [
        {
            "id": "serve",
            "evidence_files": ["serve.py"],
            "found_patterns": ["serve"],
            "required_patterns": ["serve", "api"],
            "meta": {},
        },
        {
            "id": "predict",
            "evidence_files": ["predict.py"],
            "found_patterns": ["api"],
            "required_patterns": ["serve", "api"],
            "meta": {},
        },
        {
            "id": "api",
            "evidence_files": ["api.py"],
            "found_patterns": ["api", "serve"],
            "required_patterns": ["serve", "api"],
            "meta": {},
        },
    ]

    cfg = {"capability_map": {"overrides": {"ml-serving": ["serve", "predict", "api"]}}}

    result = apply_overrides(capabilities, cfg)

    assert len(result) == 1, "Result must not be empty"
    assert result[0]["id"] == "ml-serving", "Result must not be empty"
    assert set(result[0]["evidence_files"]) == {"serve.py", "predict.py", "api.py"}
    assert set(result[0]["found_patterns"]) == {"serve", "api"}


def test_apply_overrides_preserves_unrelated():
    """Test that capabilities not in overrides are preserved."""
    from scripts.space_traversal.audit_runner import apply_overrides

    capabilities = [
        {
            "id": "train_loop",
            "evidence_files": ["loop.py"],
            "found_patterns": ["epoch"],
            "required_patterns": ["train", "epoch"],
            "meta": {},
        },
        {
            "id": "checkpointing",
            "evidence_files": ["ckpt.py"],
            "found_patterns": ["save"],
            "required_patterns": ["save", "load"],
            "meta": {},
        },
    ]

    cfg = {"capability_map": {"overrides": {"training-engine": ["train_loop"]}}}

    result = apply_overrides(capabilities, cfg)

    assert len(result) == 2, "Result must not be empty"
    ids = {cap["id"] for cap in result}
    assert ids == {"training-engine", "checkpointing"}


def test_validate_detector_output_valid():
    """Test detector validation with valid output."""
    from scripts.space_traversal.audit_runner import validate_detector_output

    det = {
        "id": "test-cap",
        "evidence_files": ["a.py"],
        "found_patterns": ["pat1"],
        "required_patterns": ["pat1", "pat2"],
    }

    assert validate_detector_output(det, "test_detector") is True


def test_validate_detector_output_missing_fields():
    """Test detector validation with missing required fields."""
    from scripts.space_traversal.audit_runner import validate_detector_output

    det = {
        "id": "test-cap",
        "evidence_files": ["a.py"],
        # missing found_patterns and required_patterns
    }

    assert validate_detector_output(det, "test_detector") is False


def test_validate_detector_output_wrong_type():
    """Test detector validation with wrong field types."""
    from scripts.space_traversal.audit_runner import validate_detector_output

    det = {
        "id": "test-cap",
        "evidence_files": "not-a-list",  # should be list
        "found_patterns": ["pat1"],
        "required_patterns": ["pat1"],
    }

    assert validate_detector_output(det, "test_detector") is False
