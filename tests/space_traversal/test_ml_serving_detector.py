"""
Tests for ml_serving detector (v1.4.0)
"""

from scripts.space_traversal.detectors.ml_serving import detect


def test_ml_serving_detector_basic():
    """Test basic ML serving detection."""
    file_index = {
        "files": [
            {"path": "src/api/serve.py", "ext": ".py"},
            {"path": "src/inference/predict.py", "ext": ".py"},
            {"path": "src/models/fastapi_server.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "ml-serving", "Result must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"
    assert "serve" in result["found_patterns"] or "predict" in result["found_patterns"], "Result must not be empty"
    assert result["required_patterns"] == ["serve", "predict", "api"]
    assert result["meta"]["layer"] == "inference", "Result must not be empty"


def test_ml_serving_detector_no_evidence():
    """Test ML serving detector with no evidence."""
    file_index = {"files": [{"path": "src/utils/helper.py", "ext": ".py"}]}

    result = detect(file_index)

    assert result["id"] == "ml-serving", "Result must not be empty"
    assert len(result["evidence_files"]) == 0, "Collection must not be empty"
    assert len(result["found_patterns"]) == 0, "Collection must not be empty"


def test_ml_serving_detector_api_patterns():
    """Test ML serving detector with API patterns."""
    file_index = {
        "files": [
            {"path": "src/api/fastapi_routes.py", "ext": ".py"},
            {"path": "src/api/flask_app.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "ml-serving", "Result must not be empty"
    assert "api" in result["found_patterns"], "Result must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"


def test_ml_serving_detector_sorted_output():
    """Test that detector returns sorted results."""
    file_index = {
        "files": [
            {"path": "z_serve.py", "ext": ".py"},
            {"path": "a_api.py", "ext": ".py"},
            {"path": "m_predict.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    # Check that evidence files are sorted
    assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"
    # Check that found patterns are sorted
    assert result["found_patterns"] == sorted(result["found_patterns"]), "Result must not be empty"
