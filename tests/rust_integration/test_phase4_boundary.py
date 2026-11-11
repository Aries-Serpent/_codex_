"""Phase 4 tests for safety and lifecycle behavior at the Rust/Python boundary."""

from __future__ import annotations

import gc
import gzip
import threading
import time

import pytest

codex_swarm = pytest.importorskip(
    "codex_swarm", reason="codex_swarm not built yet (run: maturin develop)"
)


@pytest.mark.parametrize(
    "payload",
    [b"", b"\x00", bytes(range(256)) * 16, b"repetitive" * 8192],
    ids=["empty", "zero-byte", "binary", "repetitive"],
)
def test_gzip_python_rust_payload_compatibility(payload: bytes) -> None:
    python_stream = gzip.compress(payload, mtime=0)
    rust_stream = bytes(codex_swarm.Compression.compress(payload))

    assert bytes(codex_swarm.Compression.decompress(python_stream)) == payload
    assert gzip.decompress(rust_stream) == payload
    assert bytes(codex_swarm.Compression.decompress(rust_stream)) == payload


@pytest.mark.parametrize("limit", [0, 1, 128])
def test_gzip_exact_output_limits(limit: int) -> None:
    for length in sorted({max(0, limit - 1), limit, limit + 1}):
        payload = b"x" * length
        for stream in (
            gzip.compress(payload, mtime=0),
            bytes(codex_swarm.Compression.compress(payload)),
        ):
            if length > limit:
                with pytest.raises(ValueError, match=rf"exceeds {limit} byte limit"):
                    codex_swarm.Compression.decompress_with_limit(stream, limit)
            else:
                assert (
                    bytes(codex_swarm.Compression.decompress_with_limit(stream, limit)) == payload
                )


@pytest.mark.parametrize("damage", ["header", "checksum", "size", "truncated"])
def test_gzip_malformed_stream_errors(damage: str) -> None:
    stream = bytearray(gzip.compress(bytes(range(256)) * 4, mtime=0))
    if damage == "truncated":
        stream = stream[:-1]
    else:
        stream[{"header": 0, "checksum": -8, "size": -4}[damage]] ^= 0xFF
    for decompress in (
        codex_swarm.Compression.decompress,
        lambda data: codex_swarm.Compression.decompress_with_limit(data, 1024),
    ):
        with pytest.raises(OSError, match="Decompression failed"):
            decompress(bytes(stream))


def test_gzip_optional_headers_are_separate_from_compressed_payload() -> None:
    """Exercise the gzip header-progress changes in flate2 1.1.11."""
    payload = bytes(range(256)) * 32
    stream = gzip.compress(payload, mtime=0)
    header = bytearray(stream[:10])
    header[3] = 0x1C  # FEXTRA, FNAME and FCOMMENT
    optional = b"\x03\x00abc" + b"filename" * 1024 + b"\0comment\0"
    encoded = bytes(header) + optional + stream[10:]

    assert gzip.decompress(encoded) == payload
    assert bytes(codex_swarm.Compression.decompress_with_limit(encoded, len(payload))) == payload
    for boundary in (0, 1, 9, 10, 11, 14, 100, len(header) + len(optional) - 1):
        with pytest.raises(OSError, match="Decompression failed"):
            codex_swarm.Compression.decompress(encoded[:boundary])


def test_gzip_default_expansion_bound_is_preserved() -> None:
    limit = 64 * 1024 * 1024
    stream = gzip.compress(b"x" * (limit + 1), mtime=0)
    with pytest.raises(ValueError, match=rf"exceeds {limit} byte limit"):
        codex_swarm.Compression.decompress(stream)


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
    assert ready.wait(1.0), "Condition must be true"
    before = ticks
    try:
        assert manager.get_result(0.15) is None, "Result must not be empty"
    finally:
        stop.set()
        thread.join(1.0)

    assert not thread.is_alive(), "Condition must be true"
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
    assert started.wait(1.0), "Condition must be true"
    time.sleep(0.02)
    assert thread.is_alive(), "test batch completed before cancellation was exercised"

    engine.shutdown()
    thread.join(2.0)

    assert not thread.is_alive(), "shutdown did not unblock the in-flight batch"
    assert processed and processed[0] < requested, "processed is not valid"
    assert not engine.is_running(), "Condition must be true"
    engine.shutdown()  # Idempotent at the Python boundary too.


def test_bounded_result_queue_applies_backpressure_and_shutdown_unblocks() -> None:
    """The fixed-capacity result queue must block rather than grow without bound."""
    manager = codex_swarm.TaskManager()
    capacity = 10_000
    for _ in range(capacity):
        manager.submit(b"queued")
    assert manager.result_count() == capacity, "Result must not be empty"

    started = threading.Event()
    finished = threading.Event()

    def submit_one_more() -> None:
        started.set()
        manager.submit(b"blocked")
        finished.set()

    thread = threading.Thread(target=submit_one_more)
    thread.start()
    assert started.wait(1.0), "Condition must be true"
    time.sleep(0.05)
    assert not finished.is_set(), "submission bypassed bounded backpressure"

    manager.shutdown()
    thread.join(1.0)

    assert finished.is_set(), "shutdown did not cancel the blocked submission"
    assert manager.result_count() == capacity, "Result must not be empty"
    assert not manager.is_running(), "Condition must be true"


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
    assert task_id == 0, "task_id is not valid"
    assert success, "success is not valid"
    assert bytes(result) == expected, "Result must not be empty"


def test_process_tasks_remains_experimental_identity_transport() -> None:
    """Classify process_tasks explicitly: it is identity transport, not execution."""
    engine = codex_swarm.SwarmEngine(1)
    marker = object()
    mutable = {"state": "experimental"}

    returned = engine.process_tasks([marker, mutable])

    assert returned[0] is marker, "Condition must be true"
    assert returned[1] is mutable, "Condition must be true"
    engine.shutdown()
