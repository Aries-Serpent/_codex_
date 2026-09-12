from __future__ import annotations

import json

import pytest
from codex_contracts import (
    ArtifactReference,
    ContractValidationError,
    ErrorEnvelope,
    EventEnvelope,
)


def test_event_envelope_serializes_deterministically() -> None:
    event = EventEnvelope(
        kind="model.evaluated",
        source="codex-ml-eval",
        source_version="1.2.3",
        correlation_id="run-42",
        payload={"score": 0.9},
        event_id="event-1",
        emitted_at="2026-09-12T05:53:23Z",
    )

    assert json.loads(event.to_json()) == event.to_dict()
    assert event.to_json() == event.to_json()


def test_event_envelope_rejects_unsupported_schema() -> None:
    with pytest.raises(ContractValidationError, match="unsupported schema_version"):
        EventEnvelope(kind="x", source="test", schema_version="2.0")


def test_event_envelope_rejects_oversized_payload() -> None:
    event = EventEnvelope(kind="x", source="test", payload={"value": "large"})

    with pytest.raises(ContractValidationError, match="byte limit"):
        event.to_json(max_bytes=8)


def test_error_envelope_rejects_non_json_details() -> None:
    with pytest.raises(ContractValidationError, match="JSON-compatible"):
        ErrorEnvelope(category="invalid", message="bad value", details={"value": object()})


def test_artifact_reference_validates_digest() -> None:
    artifact = ArtifactReference(
        uri="s3://models/weights.safetensors",
        sha256="a" * 64,
        size_bytes=128,
        media_type="application/x-safetensors",
    )

    assert artifact.to_dict()["sha256"] == "a" * 64

    with pytest.raises(ValueError, match="sha256"):
        ArtifactReference(uri="file:///tmp/model", sha256="invalid", size_bytes=1)
