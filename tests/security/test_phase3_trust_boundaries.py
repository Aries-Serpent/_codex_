from __future__ import annotations

import gzip
import hashlib

import msgpack
import pytest

from aries_serpent_core.brain.session_serializer import SessionSerializer
from codex_ml.plugins.plugin_sandbox import Plugin, PluginSandbox
from codex_ml.utils import checkpoint_core


class _BoundaryPlugin(Plugin):
    def initialize(self) -> bool:
        return True

    def execute(self, *args: object, **kwargs: object) -> object:
        del args, kwargs
        raise LookupError("plugin-controlled failure")

    def cleanup(self) -> None:
        return None


class _UnprintablePluginError(Exception):
    def __str__(self) -> str:
        raise RuntimeError("exception text must not escape the plugin boundary")


class _UnprintableFailurePlugin(_BoundaryPlugin):
    def execute(self, *args: object, **kwargs: object) -> object:
        del args, kwargs
        raise _UnprintablePluginError()


def test_msgpack_decoder_rejects_oversized_and_non_mapping_payloads() -> None:
    serializer = SessionSerializer()

    with pytest.raises(ValueError, match="maximum encoded size"):
        serializer.deserialize_from_binary(msgpack.packb({"value": "x" * 32}), max_bytes=8)
    with pytest.raises(ValueError, match="must be a mapping"):
        serializer.deserialize_from_binary(msgpack.packb(["not", "state"]))


def test_gzip_decoder_stops_at_output_limit() -> None:
    serializer = SessionSerializer()
    compressed = gzip.compress(b"A" * 1024)

    with pytest.raises(ValueError, match="maximum output size"):
        serializer.decompress_payload(compressed, max_output_bytes=128)


def test_plugin_boundary_contains_unexpected_plugin_exceptions() -> None:
    plugin = _BoundaryPlugin()
    sandbox = PluginSandbox()

    assert sandbox.execute_sandboxed(plugin) is None
    assert sandbox.get_health_status(plugin.name).failure_count == 1


def test_plugin_boundary_rejects_arbitrary_method_dispatch() -> None:
    with pytest.raises(ValueError, match=r"limited to execute\(\)"):
        PluginSandbox().execute_sandboxed(_BoundaryPlugin(), "cleanup")


def test_plugin_boundary_does_not_format_plugin_controlled_exceptions() -> None:
    plugin = _UnprintableFailurePlugin()
    sandbox = PluginSandbox()

    assert sandbox.execute_sandboxed(plugin) is None
    assert sandbox.get_health_status(plugin.name).last_error == "_UnprintablePluginError"


def test_checkpoint_provenance_is_checked_before_deserialization(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"untrusted checkpoint")
    deserialized = False

    def fail_if_called(*args: object, **kwargs: object) -> object:
        nonlocal deserialized
        del args, kwargs
        deserialized = True
        raise AssertionError("deserialization must not run")

    monkeypatch.setattr(checkpoint_core, "_deserialize_payload", fail_if_called)

    with pytest.raises(checkpoint_core.CheckpointIntegrityError, match="Provenance"):
        checkpoint_core.load_checkpoint(checkpoint, expected_file_sha256="0" * 64)
    assert deserialized is False


def test_checkpoint_requires_embedded_integrity_provenance(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    checkpoint = tmp_path / "checkpoint.pt"
    raw = b"checkpoint"
    checkpoint.write_bytes(raw)
    monkeypatch.setattr(
        checkpoint_core,
        "_deserialize_payload",
        lambda *_args, **_kwargs: {
            "state": {},
            "meta": {"schema_version": checkpoint_core.SCHEMA_VERSION},
        },
    )
    monkeypatch.setattr(checkpoint_core, "_serialize_payload", lambda _payload: b"serialized")

    with pytest.raises(checkpoint_core.CheckpointIntegrityError, match="sha256"):
        checkpoint_core.load_checkpoint(
            checkpoint,
            expected_file_sha256=hashlib.sha256(raw).hexdigest(),
        )


@pytest.mark.parametrize("entry_path", ["../outside.pt", "/tmp/outside.pt"])
def test_checkpoint_index_cannot_escape_its_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path, entry_path: str
) -> None:
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    monkeypatch.setattr(
        checkpoint_core,
        "_load_index",
        lambda _root: {
            "entries": [{"path": entry_path, "metric": 0.1}],
            "mode": "min",
        },
    )

    with pytest.raises(checkpoint_core.CheckpointIntegrityError, match="escapes"):
        checkpoint_core.load_best(checkpoint_dir)
