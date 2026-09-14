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


def test_event_envelope_parses_bounded_json() -> None:
    event = EventEnvelope(
        kind="model.evaluated",
        source="codex-ml-eval",
        payload={"scores": [0.8, 0.9]},
    )

    decoded = EventEnvelope.from_json(event.to_json())

    assert decoded.to_dict() == event.to_dict()
    with pytest.raises(TypeError):
        decoded.payload["scores"][0] = 0.0  # type: ignore[index]


@pytest.mark.parametrize(
    "data, message",
    [
        ('{"schema_version":"1.0","kind":"x","source":"y","payload":{"value":NaN}}', "valid JSON"),
        ('{"schema_version":"1.0","kind":"x","kind":"y","source":"z"}', "valid JSON"),
        ('{"schema_version":"1.0","kind":"x","source":"y","unexpected":true}', "unknown"),
    ],
)
def test_event_envelope_rejects_unsafe_json(data: str, message: str) -> None:
    with pytest.raises(ContractValidationError, match=message):
        EventEnvelope.from_json(data)


def test_event_envelope_rejects_oversized_and_incomplete_input() -> None:
    event = EventEnvelope(kind="x", source="test")

    with pytest.raises(ContractValidationError, match="byte limit"):
        EventEnvelope.from_json(event.to_json(), max_bytes=8)
    with pytest.raises(ContractValidationError, match="missing required"):
        EventEnvelope.from_json('{"schema_version":"1.0","kind":"x","source":"test"}')
    with pytest.raises(ContractValidationError, match="bytes or text"):
        EventEnvelope.from_json(42)  # type: ignore[arg-type]


def test_event_envelope_recursively_copies_and_freezes_payload() -> None:
    original = {"nested": {"values": [1, 2]}}
    event = EventEnvelope(kind="x", source="test", payload=original)
    original["nested"]["values"].append(3)

    assert event.to_dict()["payload"] == {"nested": {"values": [1, 2]}}
    with pytest.raises(TypeError):
        event.payload["nested"]["new"] = True  # type: ignore[index]


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"kind": "bad kind", "source": "test"}, "safe identifier"),
        ({"kind": "x", "source": "test", "event_id": ""}, "must not be empty"),
        ({"kind": "x", "source": "test", "emitted_at": "2026-09-12 05:53:23Z"}, "RFC 3339"),
        ({"kind": "x", "source": "test", "emitted_at": "2026-09-12T05:53:23"}, "RFC 3339"),
        ({"kind": "x", "source": "test", "emitted_at": "2026-02-30T05:53:23Z"}, "RFC 3339"),
    ],
)
def test_event_envelope_validates_identifiers_and_timestamp(
    kwargs: dict[str, object], message: str
) -> None:
    with pytest.raises(ContractValidationError, match=message):
        EventEnvelope(**kwargs)  # type: ignore[arg-type]


def test_event_envelope_bounds_nested_payloads() -> None:
    nested: dict[str, object] = {}
    cursor = nested
    for _ in range(18):
        child: dict[str, object] = {}
        cursor["child"] = child
        cursor = child

    with pytest.raises(ContractValidationError, match="nesting depth"):
        EventEnvelope(kind="x", source="test", payload=nested)


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

    with pytest.raises(ValueError, match="uri"):
        ArtifactReference(uri="file:///tmp/\nmodel", sha256="a" * 64, size_bytes=1)


@pytest.mark.parametrize(
    "uri",
    [
        "relative/path",
        "https://example.test:bad/model",
        "https://example.test/model#fragment",
        "https://example.test/%zz",
        "file://relative",
    ],
)
def test_artifact_reference_rejects_unsafe_uri(uri: str) -> None:
    with pytest.raises(ValueError, match="uri"):
        ArtifactReference(uri=uri, sha256="a" * 64, size_bytes=1)


def test_artifact_reference_validates_and_freezes_metadata() -> None:
    metadata = {"producer": "trainer"}
    artifact = ArtifactReference(
        uri="https://example.test/model",
        sha256="a" * 64,
        size_bytes=1,
        metadata=metadata,
    )
    metadata["producer"] = "changed"

    assert artifact.metadata["producer"] == "trainer"
    with pytest.raises(TypeError):
        artifact.metadata["new"] = "value"  # type: ignore[index]
    with pytest.raises(ValueError, match="metadata"):
        ArtifactReference(
            uri="s3://bucket/model",
            sha256="a" * 64,
            size_bytes=1,
            metadata={"bad key": "value"},
        )
