"""Phase 4 tests for safety and lifecycle behavior at the Rust/Python boundary."""

from __future__ import annotations

import gc
import threading
import time

import pytest

codex_swarm = pytest.importorskip(
    "codex_swarm", reason="codex_swarm not built yet (run: maturin develop)"
)


def test_blocking_result_wait_releases_gil() -> None:
    """A Python thread must continue running while Rust waits for a result."""
    manager = codex_swarm.TaskManager()
    stop = threading.Event()
    ready = threading.Event()
    ticks = 0

    def ticker() -> None:
        nonlocal ticks
        ready.set()
        while not stop.is_set():
            ticks += 1

    thread = threading.Thread(target=ticker)
    thread.start()
    assert ready.wait(1.0)
    before = ticks
    try:
        assert manager.get_result(0.15) is None
    finally:
        stop.set()
        thread.join(1.0)

    assert not thread.is_alive()
    assert ticks - before > 100, "Rust held the GIL during a blocking wait"


def test_shutdown_cancels_in_flight_batch() -> None:
    """Shutdown must promptly cancel a batch that is running outside the GIL."""
    engine = codex_swarm.SwarmEngine(1)
    requested = 100_000_000
    started = threading.Event()
    processed: list[int] = []

    def run_batch() -> None:
        started.set()
        processed.append(engine.process_batch(requested))

    thread = threading.Thread(target=run_batch)
    thread.start()
    assert started.wait(1.0)
    time.sleep(0.02)
    assert thread.is_alive(), "test batch completed before cancellation was exercised"

    engine.shutdown()
    thread.join(2.0)

    assert not thread.is_alive(), "shutdown did not unblock the in-flight batch"
    assert processed and processed[0] < requested
    assert not engine.is_running()
    engine.shutdown()  # Idempotent at the Python boundary too.


def test_bounded_result_queue_applies_backpressure_and_shutdown_unblocks() -> None:
    """The fixed-capacity result queue must block rather than grow without bound."""
    manager = codex_swarm.TaskManager()
    capacity = 10_000
    for _ in range(capacity):
        manager.submit(b"queued")
    assert manager.result_count() == capacity

    started = threading.Event()
    finished = threading.Event()

    def submit_one_more() -> None:
        started.set()
        manager.submit(b"blocked")
        finished.set()

    thread = threading.Thread(target=submit_one_more)
    thread.start()
    assert started.wait(1.0)
    time.sleep(0.05)
    assert not finished.is_set(), "submission bypassed bounded backpressure"

    manager.shutdown()
    thread.join(1.0)

    assert finished.is_set(), "shutdown did not cancel the blocked submission"
    assert manager.result_count() == capacity
    assert not manager.is_running()


def test_decompression_limit_rejects_expansion() -> None:
    compressed = codex_swarm.Compression.compress(b"x" * 4096)

    with pytest.raises(ValueError, match=r"exceeds 128 byte limit"):
        codex_swarm.Compression.decompress_with_limit(compressed, 128)


def test_submitted_buffer_is_owned_after_python_source_is_mutated() -> None:
    """Rust must retain owned bytes, not a borrowed view into Python memory."""
    manager = codex_swarm.TaskManager()
    source = bytearray(b"phase-4-owned-buffer")
    expected = bytes(source)

    manager.submit(source)
    source[:] = b"!" * len(source)
    del source
    gc.collect()

    task_id, success, result = manager.get_result(1.0)
    assert task_id == 0
    assert success
    assert bytes(result) == expected


def test_process_tasks_remains_experimental_identity_transport() -> None:
    """Classify process_tasks explicitly: it is identity transport, not execution."""
    engine = codex_swarm.SwarmEngine(1)
    marker = object()
    mutable = {"state": "experimental"}

    returned = engine.process_tasks([marker, mutable])

    assert returned[0] is marker
    assert returned[1] is mutable
    engine.shutdown()
