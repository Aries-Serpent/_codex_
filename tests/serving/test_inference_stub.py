import pytest

from codex_ml.serving.inference_server import ModelConfig, create_app

pytest.importorskip("fastapi")
pytest.importorskip("starlette")


@pytest.fixture()
def client():
    config = ModelConfig(model_name="stub-model", model_type="stub")
    app = create_app(config=config)
    from fastapi.testclient import TestClient

    return TestClient(app)


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in {"ok", "healthy"}
    assert data["model_loaded"] is True


def test_predict_stub_roundtrip(client):
    payload = {"inputs": ["hello", "world"]}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_name"] == "stub-model"
    assert len(data["predictions"]) == 2
    assert all("label" in pred for pred in data["predictions"])
