"""
Test Inference Integration

Test module for inference integration.
"""

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # isort: skip

from codex_ml.serving.inference_server import ModelConfig, create_app


def _build_client():
    config = ModelConfig(model_type="local", model_name="toy-model")
    app = create_app(config=config)
    return TestClient(app)


def test_predict_success_round_trip():
    client = _build_client()
    response = client.post("/predict", json={"inputs": ["hello", "world"]})
    assert response.status_code == 200, "Response must not be empty"
    payload = response.json()
    assert payload["model_name"] == "toy-model", "Condition must be true"
    predictions = payload["predictions"]
    assert [p["prediction"] for p in predictions] == ["HELLO", "WORLD"]


def test_predict_failure_bubbles_error():
    client = _build_client()
    response = client.post("/predict", json={"inputs": ["raise-error"]})
    assert response.status_code == 500, "Response must not be empty"
    assert "Prediction failed" in response.json()["detail"], "Response must not be empty"


def test_embedding_success():
    client = _build_client()
    response = client.post("/embed", json={"texts": ["abc", "def"]})
    assert response.status_code == 200, "Response must not be empty"
    payload = response.json()
    assert payload["num_texts"] == 2, "Condition must be true"
    assert len(payload["embeddings"]) == 2, "Collection must not be empty"
