"""Legacy brain persistence stays atomic and never confirms failed learning."""

from __future__ import annotations

import copy
import json
import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

import aries_serpent_core.cognitive.brain_interface as brain_module
from aries_serpent_core.cognitive.brain_interface import (
    AgentBrainInterface,
    PatternPersistenceError,
)
from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore
from codex.cognitive_brain.outcome_tracking import OutcomeTracker, store_outcome_source


def _brain(repo_root: Path) -> AgentBrainInterface:
    directory = repo_root / ".codex" / "cognitive_brain"
    directory.mkdir(parents=True)
    data = {
        "metadata": {"version": "legacy", "custom": {"keep": [1, 2]}},
        "statistics": {"custom_counter": 11},
        "extension": {"preserved": True},
        "patterns": {
            "ci_timeout": {
                "id": "RP-019",
                "category": "ci_cd",
                "symptoms": ["ci job failure timeout"],
                "solutions": ["add timeout-minutes"],
                "success_rate": 0.9,
                "times_applied": 3,
            }
        },
    }
    (directory / "pattern_learning_store.json").write_text(
        json.dumps(data, indent=3) + "\n", encoding="utf-8"
    )
    return AgentBrainInterface("test-agent", repo_root=repo_root, auto_register=False)


@pytest.mark.parametrize(
    ("outcome", "expected_rate"),
    [("success", 0.93), ("failure", 0.63), ("partial", 0.78)],
)
def test_string_id_learning_survives_restart(
    tmp_path: Path, outcome: str, expected_rate: float
) -> None:
    brain = _brain(tmp_path)
    before = json.loads(brain.pattern_store_path.read_text(encoding="utf-8"))
    brain.pattern_store_path.chmod(0o640)

    assert brain.submit_learning("RP-019", outcome) is True

    restarted = AgentBrainInterface("test-agent", repo_root=tmp_path, auto_register=False)
    pattern = restarted.get_pattern("RP-019")
    assert pattern is not None
    assert pattern.pattern_id == "RP-019"
    assert pattern.times_applied == 4
    assert pattern.success_rate == pytest.approx(expected_rate)
    saved = json.loads(brain.pattern_store_path.read_text(encoding="utf-8"))
    assert saved["metadata"]["custom"] == before["metadata"]["custom"]
    assert saved["metadata"]["version"] == "legacy"
    assert saved["statistics"]["custom_counter"] == 11
    assert saved["statistics"]["total_applications"] == 4
    assert saved["extension"] == before["extension"]
    assert saved["patterns"]["ci_timeout"]["last_used"]
    assert stat.S_IMODE(brain.pattern_store_path.stat().st_mode) == 0o640
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


@pytest.mark.parametrize(
    "raw",
    [
        b'{"patterns": broken}\n',
        b"[]\n",
        b'{"patterns":[]}\n',
        b'{"patterns":{"broken":null}}\n',
        b'{"patterns":{},"metadata":[]}\n',
        b'{"patterns":{},"statistics":null}\n',
        b"\xffnot-utf8\n",
    ],
)
@pytest.mark.parametrize("operation", ["learning", "new_pattern", "existing_pattern"])
def test_malformed_existing_store_preserves_exact_bytes_and_memory(
    tmp_path: Path, raw: bytes, operation: str
) -> None:
    brain = _brain(tmp_path)
    previous_patterns = copy.deepcopy(brain._patterns)
    brain.pattern_store_path.write_bytes(raw)

    with pytest.raises((ValueError, UnicodeError)):
        if operation == "learning":
            brain.submit_learning("RP-019", "success")
        else:
            pattern_id = "RP-019" if operation == "existing_pattern" else "NEW-001"
            brain.submit_pattern(pattern_id, "testing", ["test"], ["fix"])

    assert brain.pattern_store_path.read_bytes() == raw
    assert brain._patterns == previous_patterns
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


@pytest.mark.parametrize("failure", ["create", "write", "file_sync", "replace"])
@pytest.mark.parametrize("operation", ["learning", "new_pattern", "existing_pattern"])
def test_failed_write_preserves_exact_bytes_and_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str, operation: str
) -> None:
    brain = _brain(tmp_path)
    raw = brain.pattern_store_path.read_bytes()
    previous_patterns = copy.deepcopy(brain._patterns)

    def fail(*args: object, **kwargs: object) -> None:
        raise OSError("injected persistence failure")

    if failure == "create":
        monkeypatch.setattr(brain_module.tempfile, "NamedTemporaryFile", fail)
    elif failure == "write":
        create_file = brain_module.tempfile.NamedTemporaryFile

        def create_failing_file(*args: object, **kwargs: object):
            handle = create_file(*args, **kwargs)
            write = handle.write

            def partial_write(payload: str) -> None:
                write(payload[:10])
                raise OSError("injected partial write")

            monkeypatch.setattr(handle, "write", partial_write)
            return handle

        monkeypatch.setattr(brain_module.tempfile, "NamedTemporaryFile", create_failing_file)
    elif failure == "file_sync":
        monkeypatch.setattr(brain_module.os, "fsync", fail)
    else:
        monkeypatch.setattr(brain_module.os, "replace", fail)

    with pytest.raises(PatternPersistenceError) as error:
        if operation == "learning":
            brain.submit_learning("RP-019", "success")
        else:
            pattern_id = "RP-019" if operation == "existing_pattern" else "NEW-001"
            brain.submit_pattern(pattern_id, "testing", ["test"], ["fix"])

    assert error.value.replaced is False
    assert isinstance(error.value.__cause__, OSError)
    assert brain.pattern_store_path.read_bytes() == raw
    assert brain._patterns == previous_patterns
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


def test_directory_sync_failure_is_not_confirmed_or_rolled_back_to_stale_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    brain = _brain(tmp_path)
    fsync = os.fsync

    def fail_directory_sync(fd: int) -> None:
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError("injected directory sync failure")
        fsync(fd)

    monkeypatch.setattr(brain_module.os, "fsync", fail_directory_sync)
    with pytest.raises(PatternPersistenceError) as error:
        brain.submit_learning("RP-019", "success")

    assert error.value.replaced is True
    saved = json.loads(brain.pattern_store_path.read_text(encoding="utf-8"))
    assert saved["patterns"] == brain._patterns
    assert brain._patterns["ci_timeout"]["times_applied"] == 4
    assert not any("Learning feedback submitted" in message for message in caplog.messages)
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


@pytest.mark.parametrize("failure", [None, "file_sync", "replace"])
def test_windows_platform_fixture_without_unix_primitives(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str | None
) -> None:
    brain = _brain(tmp_path)
    raw = brain.pattern_store_path.read_bytes()
    previous_patterns = copy.deepcopy(brain._patterns)
    calls = []
    handles = []
    create_file = brain_module.tempfile.NamedTemporaryFile

    def create_tracked_file(*args: object, **kwargs: object):
        handle = create_file(*args, **kwargs)
        handles.append(handle)
        return handle

    def sync_file(fd: int) -> None:
        assert stat.S_ISREG(os.fstat(fd).st_mode)
        calls.append("file_sync")
        if failure == "file_sync":
            raise OSError("injected file sync failure")
        os.fsync(fd)

    def replace_closed_file(source: str, destination: str) -> None:
        assert handles[0].closed
        assert calls == ["file_sync"]
        calls.append("replace")
        if failure == "replace":
            raise OSError("injected replacement failure")
        os.replace(source, destination)

    monkeypatch.setattr(brain_module.tempfile, "NamedTemporaryFile", create_tracked_file)
    monkeypatch.setattr(
        brain_module,
        "os",
        SimpleNamespace(name="nt", fsync=sync_file, replace=replace_closed_file),
    )
    if failure is None:
        assert brain.submit_learning("RP-019", "success") is True
        restarted = AgentBrainInterface("test-agent", repo_root=tmp_path, auto_register=False)
        pattern = restarted.get_pattern("RP-019")
        assert pattern is not None and pattern.times_applied == 4
        assert calls == ["file_sync", "replace"]
    else:
        with pytest.raises(PatternPersistenceError) as error:
            brain.submit_learning("RP-019", "success")
        assert error.value.replaced is False
        assert brain.pattern_store_path.read_bytes() == raw
        assert brain._patterns == previous_patterns
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


def test_posix_directory_open_failure_is_not_silently_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    brain = _brain(tmp_path)
    raw = brain.pattern_store_path.read_bytes()
    previous_patterns = copy.deepcopy(brain._patterns)

    def fail_open(*args: object, **kwargs: object) -> None:
        raise OSError("injected directory open failure")

    monkeypatch.setattr(
        brain_module,
        "os",
        SimpleNamespace(name="posix", O_RDONLY=os.O_RDONLY, open=fail_open),
    )
    with pytest.raises(PatternPersistenceError) as error:
        brain.submit_learning("RP-019", "success")
    assert error.value.replaced is False
    assert brain.pattern_store_path.read_bytes() == raw
    assert brain._patterns == previous_patterns
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


def test_serialization_failure_never_truncates_existing_store(tmp_path: Path) -> None:
    brain = _brain(tmp_path)
    raw = brain.pattern_store_path.read_bytes()
    brain._patterns["ci_timeout"]["unserializable"] = object()
    with pytest.raises(TypeError):
        brain._save_patterns()
    assert brain.pattern_store_path.read_bytes() == raw
    assert list(brain.cognitive_brain_dir.iterdir()) == [brain.pattern_store_path]


@pytest.mark.parametrize("raw", [b"{broken\n", b"[]", b'{"patterns":[]}'])
def test_restart_rejects_malformed_store_without_fake_empty_state(
    tmp_path: Path, raw: bytes
) -> None:
    brain = _brain(tmp_path)
    brain.pattern_store_path.write_bytes(raw)
    with pytest.raises(ValueError):
        AgentBrainInterface("test-agent", repo_root=tmp_path, auto_register=False)
    assert brain.pattern_store_path.read_bytes() == raw


def test_missing_pattern_does_not_report_completed_learning(tmp_path: Path) -> None:
    brain = _brain(tmp_path)
    raw = brain.pattern_store_path.read_bytes()
    assert brain.submit_learning("MISSING-001", "success") is False
    assert brain.pattern_store_path.read_bytes() == raw


def test_outcome_learning_failure_propagates_and_leaves_intent_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    brain = _brain(tmp_path)
    raw = brain.pattern_store_path.read_bytes()
    evidence_path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(evidence_path, allow_synthetic=True)
    store.record_outcome(
        event_id="e1",
        merged=True,
        outcome="success",
        pattern_id="RP-019",
        patch_hash="p",
        synthetic=True,
    )
    tracker = OutcomeTracker(
        brain, outcome_source=store_outcome_source(store), allow_synthetic=True
    )
    replace = os.replace

    def fail_brain_replace(source: str, destination: str) -> None:
        if Path(destination) == brain.pattern_store_path:
            raise OSError("injected brain persistence failure")
        replace(source, destination)

    monkeypatch.setattr(brain_module.os, "replace", fail_brain_replace)
    with pytest.raises(PatternPersistenceError):
        tracker.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")

    assert brain.pattern_store_path.read_bytes() == raw
    records = [json.loads(line) for line in evidence_path.read_text(encoding="utf-8").splitlines()]
    consumption = [
        record["payload"]["state"] for record in records if record["kind"] == "consumption"
    ]
    assert consumption == ["pending"]
    recovered = EvidenceStore(evidence_path, allow_synthetic=True)
    restarted = OutcomeTracker(
        brain, outcome_source=store_outcome_source(recovered), allow_synthetic=True
    )
    with pytest.raises(EvidenceIntegrityError, match="pending reconciliation"):
        restarted.process_outcome(event_id="e1", pattern_id="RP-019", patch_hash="p")
    assert brain.pattern_store_path.read_bytes() == raw
