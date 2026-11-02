"""Cancellation consumes execution identity without claiming full descendant containment."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.isolated_execution import (
    GateLog,
    IdempotencyLedger,
    IsolatedExecutor,
    scrub_environment,
)

PATCH = """diff --git a/src/value.py b/src/value.py
new file mode 100644
--- /dev/null
+++ b/src/value.py
@@ -0,0 +1 @@
+value = 2
"""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "config", "user.name", "fixture"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.test"], cwd=tmp_path, check=True
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src/old.py").write_text("value = 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_value.py").write_text(
        "import unittest,runpy\nclass Value(unittest.TestCase):\n"
        " def test_value(self): self.assertEqual(runpy.run_path('src/value.py')['value'],2)\n"
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_path, check=True)
    return tmp_path


def executor(repo: Path) -> IsolatedExecutor:
    (repo / "work").mkdir(exist_ok=True)
    return IsolatedExecutor(
        repo,
        authority=AuthorityEnvelope(require_human_approval=False),
        ledger=IdempotencyLedger(repo / "claims.jsonl"),
        work_root=repo / "work",
    )


def execute(subject: IsolatedExecutor, **kwargs):
    return subject.execute(
        event_id="cancel-fixture",
        patch_content=kwargs.pop("patch_content", PATCH),
        files=kwargs.pop("files", ("src/value.py",)),
        diff_lines=1,
        **kwargs,
    )


def running(pid: int) -> bool:
    """A killed orphan may remain a zombie until the host reaps it."""
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except FileNotFoundError:
        return False
    return state not in {"Z", "X"}


def test_cancel_before_launch_is_durable_and_never_applies(repo: Path, monkeypatch) -> None:
    subject = executor(repo)
    stop = threading.Event()
    stop.set()

    def forbidden(*args, **kwargs):
        pytest.fail("cancelled execution must not create a checkout or apply a patch")

    monkeypatch.setattr(subject, "_execute_in", forbidden)
    outcome = execute(subject, cancellation_event=stop)
    assert outcome.status == "cancelled"
    assert outcome.patch_hash == hashlib.sha256(PATCH.encode()).hexdigest()
    assert outcome.base_sha and len(outcome.base_sha) == 40
    assert outcome.attempt_id
    assert not list((repo / "work").iterdir())
    assert not (repo / "src/value.py").exists()
    records = [json.loads(line) for line in (repo / "claims.jsonl").read_text().splitlines()]
    assert [record["status"] for record in records] == ["claimed", "cancelled"]
    assert records[0]["attempt_id"] == records[1]["attempt_id"]
    restarted = executor(repo)
    monkeypatch.setattr(restarted, "_execute_in", forbidden)
    assert execute(restarted).status == "duplicate"
    assert restarted.ledger.claim("cancel-fixture", "a" * 64, "b" * 40) is None


@pytest.mark.parametrize("phase", ["baseline", "candidate"])
def test_cancel_kills_real_process_group_and_preserves_claim(
    repo: Path, monkeypatch, phase: str
) -> None:
    subject = executor(repo)
    stop = threading.Event()
    grandchild = (
        "import os,signal,time; from pathlib import Path; "
        "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
        "Path(os.environ['HOME'],'grandchild.pid').write_text(str(os.getpid())); time.sleep(60)"
    )
    child = (
        "import os,signal,subprocess,sys,time; from pathlib import Path; "
        "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
        "Path(os.environ['HOME'],'child.pid').write_text(str(os.getpid())); "
        f"subprocess.Popen([sys.executable,'-c',{grandchild!r}]); time.sleep(60)"
    )
    command = (
        "import os,signal,subprocess,sys,time; from pathlib import Path\n"
        + ("if not Path('src/value.py').exists(): sys.exit(1)\n" if phase == "candidate" else "")
        + "home=Path(os.environ['HOME'])\n"
        "signal.signal(signal.SIGTERM,lambda *_: (home/'term').write_text('received'))\n"
        "(home/'parent.pid').write_text(str(os.getpid()))\n"
        f"subprocess.Popen([sys.executable,'-c',{child!r}])\n"
        "time.sleep(60)\n"
    )
    subject.gates = (
        ("behavior", (sys.executable, "-c", command)),
        ("lint", (sys.executable, "-c", "raise AssertionError('must not launch')")),
    )
    pids: list[int] = []
    homes: list[Path] = []
    original_run = subprocess.run
    original_killpg = os.killpg
    applied: list[bool] = []
    signals: list[tuple[int, int]] = []
    grandchild_alive_at_kill: list[bool] = []

    def track_run(args, **kwargs):
        if args[:2] == ["git", "apply"] and len(args) == 3:
            applied.append(True)
        return original_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", track_run)

    def track_killpg(pid: int, sig: int) -> None:
        signals.append((pid, sig))
        if sig == signal.SIGKILL and pids and pid == pids[0]:
            grandchild_alive_at_kill.append(running(pids[-1]))
        original_killpg(pid, sig)

    monkeypatch.setattr(os, "killpg", track_killpg)

    def request_cancel() -> None:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            for path in (repo / "work").glob("*/home/grandchild.pid"):
                home = path.parent
                try:
                    found = [
                        int((home / name).read_text())
                        for name in ("parent.pid", "child.pid", "grandchild.pid")
                    ]
                except (FileNotFoundError, ValueError):
                    continue
                homes.append(home)
                pids.extend(found)
                stop.set()
                return
            time.sleep(0.01)
        stop.set()

    observer = threading.Thread(target=request_cancel)
    observer.start()
    started = time.monotonic()
    try:
        outcome = execute(subject, cancellation_event=stop)
        observer.join(timeout=12)
        assert not observer.is_alive()
        assert len(pids) == 3, outcome.reason
        deadline = time.monotonic() + 2
        while any(running(pid) for pid in pids) and time.monotonic() < deadline:
            time.sleep(0.01)
        assert not any(running(pid) for pid in pids)
        assert [sig for pid, sig in signals if pid == pids[0]] == [
            signal.SIGTERM,
            signal.SIGKILL,
        ]
        assert grandchild_alive_at_kill == [True]
        assert time.monotonic() - started < 12
        assert outcome.status == "cancelled", outcome.reason
        logs = outcome.baseline_gate_logs if phase == "baseline" else outcome.gate_logs
        assert len(logs) == 1
        assert (logs[0].status, logs[0].returncode) == ("cancelled", 130)
        assert Path(logs[0].output_path).is_file()
        assert bool(applied) == (phase == "candidate")
        assert not (repo / "src/value.py").exists()
        assert not homes[0].exists()
        assert execute(executor(repo)).status == "duplicate"
        assert IdempotencyLedger(repo / "claims.jsonl").seen("cancel-fixture")
    finally:
        stop.set()
        observer.join(timeout=12)
        for pid in pids:
            if running(pid):
                os.kill(pid, signal.SIGKILL)


def test_cancellation_after_baseline_prevents_candidate_effects(repo: Path, monkeypatch) -> None:
    subject = executor(repo)
    stop = threading.Event()
    called: list[str] = []

    def baseline(name, command, cwd, env, **kwargs):
        assert kwargs["cancellation_event"] is stop
        called.append(name)
        assert not (cwd / "src/value.py").exists()
        stop.set()
        return GateLog(name, command, 1, 0, hashlib.sha256(b"failure").hexdigest(), "failed")

    monkeypatch.setattr(subject, "_run_gate", baseline)
    outcome = execute(subject, cancellation_event=stop)
    assert outcome.status == "cancelled"
    assert called == ["behavior"]
    assert outcome.baseline_gate_logs[0].status == "failed"
    assert not outcome.gate_logs
    assert execute(executor(repo)).status == "duplicate"


def test_gate_prelaunch_cancellation_never_spawns(repo: Path, monkeypatch) -> None:
    stop = threading.Event()
    stop.set()

    def forbidden(*args, **kwargs):
        pytest.fail("pre-cancelled gate launched a process")

    subject = executor(repo)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    log = subject._run_gate(
        "behavior",
        (sys.executable, "-c", "pass"),
        repo,
        scrub_environment(),
        cancellation_event=stop,
    )
    assert (log.status, log.returncode) == ("cancelled", 130)


def test_cancel_after_passing_candidate_never_verifies(repo: Path, monkeypatch) -> None:
    subject = executor(repo)
    stop = threading.Event()
    original_gate = subject._run_gate

    def cancel_after_pass(*args, **kwargs):
        log = original_gate(*args, **kwargs)
        if log.status == "passed":
            stop.set()
        return log

    monkeypatch.setattr(subject, "_run_gate", cancel_after_pass)
    outcome = execute(subject, cancellation_event=stop)
    assert outcome.status == "cancelled"
    assert outcome.baseline_gate_logs[0].status == "failed"
    assert outcome.gate_logs[-1].status == "passed"
    assert not outcome.artifact_hash
    assert not outcome.candidate_tree_hash
    assert execute(executor(repo)).status == "duplicate"
    records = [json.loads(line) for line in (repo / "claims.jsonl").read_text().splitlines()]
    assert [record["status"] for record in records] == ["claimed", "cancelled"]
    assert records[0]["attempt_id"] == records[1]["attempt_id"]


@pytest.mark.parametrize(("exitcode", "status"), [(0, "passed"), (7, "failed")])
def test_observed_gate_exit_is_not_overwritten_by_concurrent_cancel(
    repo: Path, monkeypatch, exitcode: int, status: str
) -> None:
    subject = executor(repo)
    stop = threading.Event()
    original_gate = subject._run_gate
    signals: list[int] = []

    class CompletedGate:
        pid = 12345

        def wait(self, timeout):
            stop.set()
            return exitcode

    def synchronized_gate(*args, **kwargs):
        with monkeypatch.context() as patch:
            patch.setattr(subprocess, "Popen", lambda *args, **kwargs: CompletedGate())
            patch.setattr(os, "killpg", lambda pid, sig: signals.append(sig))
            return original_gate(*args, **kwargs)

    monkeypatch.setattr(subject, "_run_gate", synchronized_gate)
    outcome = execute(subject, cancellation_event=stop)
    assert outcome.status == "cancelled"
    assert len(outcome.baseline_gate_logs) == 1
    log = outcome.baseline_gate_logs[0]
    assert (log.returncode, log.status) == (exitcode, status)
    assert signals == [signal.SIGKILL]
    assert not outcome.gate_logs
    assert not outcome.artifact_hash
    assert execute(executor(repo)).status == "duplicate"
    records = [json.loads(line) for line in (repo / "claims.jsonl").read_text().splitlines()]
    assert [record["status"] for record in records] == ["claimed", "cancelled"]


def test_cancel_after_durable_completion_does_not_add_another_terminal(
    repo: Path, monkeypatch
) -> None:
    subject = executor(repo)
    stop = threading.Event()
    original_record = subject.ledger.record

    def cancel_after_record(outcome):
        original_record(outcome)
        if outcome.status == "verified":
            stop.set()

    monkeypatch.setattr(subject.ledger, "record", cancel_after_record)
    outcome = execute(subject, cancellation_event=stop)
    assert stop.is_set()
    assert outcome.status == "verified"
    assert execute(executor(repo), cancellation_event=stop).status == "duplicate"
    records = [json.loads(line) for line in (repo / "claims.jsonl").read_text().splitlines()]
    assert [record["status"] for record in records] == ["claimed", "verified"]
    assert records[0]["attempt_id"] == records[1]["attempt_id"]


def test_pending_claim_after_restart_never_reexecutes(repo: Path, monkeypatch) -> None:
    subject = executor(repo)
    assert subject.ledger.claim("cancel-fixture", "a" * 64, "b" * 40)
    original = (repo / "claims.jsonl").read_bytes()

    def forbidden(*args, **kwargs):
        pytest.fail("pending execution must require manual recovery, never retry")

    restarted = executor(repo)
    monkeypatch.setattr(restarted, "_execute_in", forbidden)
    assert execute(restarted).status == "duplicate"
    assert (repo / "claims.jsonl").read_bytes() == original
    assert not list((repo / "work").iterdir())


@pytest.mark.parametrize("malformed", ["unterminated", "missing_hash", "bad_attempt", "bad_status"])
def test_malformed_pending_claim_fails_closed_without_repair(
    repo: Path, monkeypatch, malformed: str
) -> None:
    record = {
        "schema_version": 2,
        "event_id": "cancel-fixture",
        "status": "claimed",
        "attempt_id": "a" * 32,
        "patch_hash": "b" * 64,
        "base_sha": "c" * 40,
    }
    if malformed == "missing_hash":
        del record["patch_hash"]
    elif malformed == "bad_attempt":
        record["attempt_id"] = "interrupted"
    elif malformed == "bad_status":
        record["status"] = "retryable"
    contents = json.dumps(record) + ("" if malformed == "unterminated" else "\n")
    (repo / "claims.jsonl").write_text(contents)

    def forbidden(*args, **kwargs):
        pytest.fail("malformed pending state must not launch execution")

    monkeypatch.setattr(IsolatedExecutor, "_execute_in", forbidden)
    with pytest.raises(ValueError, match="invalid execution ledger record"):
        execute(executor(repo))
    assert (repo / "claims.jsonl").read_text() == contents
    assert not list((repo / "work").iterdir())


@pytest.mark.parametrize(
    ("command", "deadline_offset", "expected"),
    [
        (("/nonexistent/cancellation-fixture",), 5, ("launch_error", 127)),
        ((sys.executable, "-c", "import time; time.sleep(60)"), 0.1, ("timeout", 124)),
    ],
)
def test_other_terminal_gate_statuses_are_not_cancellation(
    repo: Path, command: tuple[str, ...], deadline_offset: float, expected: tuple[str, int]
) -> None:
    home = repo / "gate-home"
    home.mkdir()
    log = executor(repo)._run_gate(
        "behavior",
        command,
        repo / "src",
        {**scrub_environment(), "HOME": str(home)},
        deadline=time.monotonic() + deadline_offset,
        cancellation_event=threading.Event(),
    )
    assert (log.status, log.returncode) == expected


def test_output_limit_retains_its_distinct_status(repo: Path, monkeypatch) -> None:
    original_file = tempfile.TemporaryFile

    def oversized_output(**kwargs):
        output = original_file(**kwargs)
        output.write(b"x" * (1024 * 1024 + 1))
        return output

    monkeypatch.setattr(tempfile, "TemporaryFile", oversized_output)
    home = repo / "gate-home"
    home.mkdir()
    log = executor(repo)._run_gate(
        "behavior",
        (sys.executable, "-c", "pass"),
        repo / "src",
        {**scrub_environment(), "HOME": str(home)},
        cancellation_event=threading.Event(),
    )
    assert (log.status, log.returncode) == ("output_limit", 125)


@pytest.mark.parametrize("mismatch", ["patch", "base", "scope"])
def test_identity_and_scope_rejection_remain_fail_closed(repo: Path, mismatch: str) -> None:
    kwargs = {
        "patch": {"patch_hash": "0" * 64},
        "base": {"base_sha": "HEAD"},
        "scope": {"files": ("src/old.py",)},
    }[mismatch]
    outcome = execute(executor(repo), cancellation_event=threading.Event(), **kwargs)
    assert outcome.status == "rejected"
    assert not outcome.gate_logs
    assert not (repo / "src/value.py").exists()


def test_uncancelled_execution_still_requires_fail_before_pass_after(repo: Path) -> None:
    outcome = execute(executor(repo), cancellation_event=threading.Event())
    assert outcome.status == "verified", outcome.reason
    assert any(log.status == "failed" for log in outcome.baseline_gate_logs)
    assert all(log.status == "passed" for log in outcome.gate_logs)
    assert outcome.patch_hash == hashlib.sha256(PATCH.encode()).hexdigest()
    assert outcome.candidate_tree_hash
    assert not (repo / "src/value.py").exists()


def test_passing_baseline_remains_rejected(repo: Path) -> None:
    subject = executor(repo)
    subject.gates = (("behavior", (sys.executable, "-c", "pass")),)
    outcome = execute(subject, cancellation_event=threading.Event())
    assert outcome.status == "rejected"
    assert outcome.reason == "no demonstrated failing baseline behavior"
