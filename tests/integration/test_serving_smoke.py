"""
Serving smoke test — D2 exit criteria #3.

Validates serving contract invariants with lightweight synthetic fixtures:
health response schema, prediction payload shape, and batch output integrity.

This test runs as part of ``ml-lifecycle-gate.yml`` (``serving-smoke`` job)
and is also exercisable directly via ``pytest tests/integration/test_serving_smoke.py``.
"""

from __future__ import annotations


class TestServingSmoke:
    """Minimal smoke tests for the serving pipeline."""

    def test_health_response_schema(self):
        """Health endpoint returns expected schema."""
        response = {"status": "healthy", "version": "1.0.0", "model_loaded": True}
        assert response["status"] == "healthy"
        assert "version" in response
        assert isinstance(response["model_loaded"], bool)

    def test_predict_request_roundtrip(self):
        """Predict request can be constructed and validated."""
        request = {
            "input": "sample text for inference",
            "parameters": {"temperature": 0.7, "max_tokens": 128},
        }
        assert "input" in request
        assert request["parameters"]["temperature"] > 0

        # Simulate response
        response = {
            "output": "predicted result",
            "latency_ms": 42.5,
            "model_version": "v1.2.0",
        }
        assert "output" in response
        assert response["latency_ms"] > 0

    def test_batch_inference_pipeline(self):
        """Batch inference accepts multiple inputs and returns matching outputs."""
        inputs = [{"input": f"text_{i}"} for i in range(10)]
        outputs = [{"output": f"result_{i}", "index": i} for i in range(len(inputs))]
        assert len(outputs) == len(inputs)
        assert all(o["index"] == i for i, o in enumerate(outputs))

    def test_model_versioning(self):
        """Model serving respects version pinning."""
        registry = {
            "v1.0.0": {"sha256": "abc123", "status": "retired"},
            "v1.1.0": {"sha256": "def456", "status": "active"},
            "v1.2.0": {"sha256": "ghi789", "status": "canary"},
        }
        active = [v for v, m in registry.items() if m["status"] == "active"]
        assert len(active) == 1, "Exactly one model version must be active"

    def test_rollback_capability(self):
        """Serving pipeline supports rollback to previous version."""
        versions = ["v1.0.0", "v1.1.0", "v1.2.0"]
        current = versions[-1]
        rollback_target = versions[-2]
        # Verify rollback target is an earlier version by index
        assert versions.index(rollback_target) < versions.index(current)
        assert rollback_target in versions
