
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/healthz")
    assert r.status_code == 200

def test_kb():
    r = client.post("/kb/search", json={"query": "flags", "top_k": 2})
    assert r.status_code == 200
    assert "results" in r.json()
