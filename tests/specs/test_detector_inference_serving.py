"""
Test Detector Inference Serving

Test module for detector inference serving.
"""

from __future__ import annotations

from scripts.space_traversal.detectors.inference_serving import detect


def test_inference_serving_detector_basic_path_signals():
    file_index = {
        "files": [
            {"path": "src/api/server_fastapi.py", "ext": ".py"},
            {"path": "src/training/train_loop.py"},
        ]
    }
    result = detect(file_index)
    assert result["id"] == "inference-serving", "Result must not be empty"
    assert any("server" in p for p in result["evidence_files"]), "Result must not be empty"
    # signals detected from path/content heuristics
    assert "serve" in result["found_patterns"], "Result must not be empty"
    # required patterns declared
    assert "fastapi" in result["required_patterns"], "Result must not be empty"
    assert "serve" in result["required_patterns"], "Result must not be empty"
