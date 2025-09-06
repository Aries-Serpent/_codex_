import resource

from training.streaming import stream_texts


def test_streaming_memory(tmp_path):
    path = tmp_path / "big.txt"
    line = "a" * 1024 + "\n"
    with path.open("w") as f:
        for _ in range(5000):  # ~5 MB
            f.write(line)
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    total = 0
    for chunk in stream_texts(str(path), chunk_size=1024):
        total += len(chunk)
    after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    assert total >= 5_000_000
    # Ensure memory increase stays below 50 MB
    assert (after - before) < 50_000
