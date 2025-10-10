from __future__ import annotations

from scripts.space_traversal.detectors.inference_serving import detect


def test_inference_serving_detector_basic_path_signals():
    file_index = {
        "files": [
            {"path": "src/api/server_fastapi.py"},
            {"path": "src/training/train_loop.py"},
        ]
    }
    result = detect(file_index)
    assert result["id"] == "inference-serving"
    assert any("server" in p for p in result["evidence_files"])
    # signals detected from filename tokens
    assert "server" in result["found_patterns"]
    assert "fastapi" in result["found_patterns"]
    # required patterns declared
    assert set(result["required_patterns"]) == {"server", "fastapi"}
