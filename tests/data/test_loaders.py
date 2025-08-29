from pathlib import Path
from codex_ml.data.loaders import stream_paths


def _make_files(tmp_path: Path, n: int) -> list[Path]:
    paths = []
    for i in range(n):
        p = tmp_path / f"{i}.jsonl"
        p.write_text('{"prompt": "p'+str(i)+'", "completion": "c"}\n', encoding="utf-8")
        paths.append(p)
    return paths


def test_stream_paths_seed_same_order(tmp_path: Path):
    paths = _make_files(tmp_path, 5)
    a = [pc.prompt for pc in stream_paths(paths, seed=123)]
    b = [pc.prompt for pc in stream_paths(paths, seed=123)]
    assert a == b


def test_stream_paths_seed_differs(tmp_path: Path):
    paths = _make_files(tmp_path, 5)
    a = [pc.prompt for pc in stream_paths(paths, seed=1)]
    b = [pc.prompt for pc in stream_paths(paths, seed=2)]
    assert a != b
