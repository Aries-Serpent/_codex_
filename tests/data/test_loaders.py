import asyncio
import json
from pathlib import Path

import pytest

from codex_ml.connectors.registry import register_connector
from codex_ml.connectors.remote import RemoteConnector
from codex_ml.data.loaders import stream_paths


def _make_files(tmp_path: Path, n: int) -> list[Path]:
    paths = []
    for i in range(n):
        p = tmp_path / f"{i}.jsonl"
        p.write_text('{"prompt": "p' + str(i) + '", "completion": "c"}\n', encoding="utf-8")
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


def test_stream_paths_connector_uri(tmp_path: Path, monkeypatch) -> None:
    cache_root = tmp_path / "cache"
    monkeypatch.setenv("CODEX_CONNECTOR_CACHE_ROOT", str(cache_root))

    class _TestRemote(RemoteConnector):
        def __init__(self, **kwargs):
            super().__init__(cache_root=tmp_path / "remote", **kwargs)

    register_connector("test-remote", _TestRemote)

    connector = _TestRemote()
    asyncio.run(
        connector.write_file(
            "datasets/sample.jsonl",
            b'{"prompt": "p0", "completion": "c"}\n',
        )
    )

    samples = list(stream_paths(["connector://test-remote/datasets/sample.jsonl"]))
    assert [sample.prompt for sample in samples] == ["p0"]
    cached = cache_root / "test-remote" / "datasets" / "sample.jsonl"
    assert cached.exists()


def test_stream_paths_connector_errors_propagate(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_CONNECTOR_CACHE_ROOT", str(tmp_path / "cache"))

    class _Empty(RemoteConnector):
        async def list_files(self, path: str):  # type: ignore[override]
            return []

    register_connector("empty-remote", _Empty)

    with pytest.raises(FileNotFoundError):
        list(stream_paths(["connector://empty-remote/datasets/sample.jsonl"]))


def test_stream_paths_mixed_sources_reuse_cache(tmp_path: Path, monkeypatch) -> None:
    cache_root = tmp_path / "cache"
    monkeypatch.setenv("CODEX_CONNECTOR_CACHE_ROOT", str(cache_root))

    local_root = tmp_path / "local"
    local_root.mkdir()
    local_paths = _make_files(local_root, 2)

    class _TestMixed(RemoteConnector):
        def __init__(self, **kwargs):
            super().__init__(cache_root=tmp_path / "remote", **kwargs)

    register_connector("mixed-remote", _TestMixed)

    connector = _TestMixed()
    payload = json.dumps({"prompt": "remote", "completion": "c"}).encode("utf-8")
    asyncio.run(connector.write_file("datasets/remote.jsonl", payload))

    sources = [
        str(local_paths[0]),
        "connector://mixed-remote/datasets/remote.jsonl",
        str(local_paths[1]),
    ]
    prompts = [sample.prompt for sample in stream_paths(sources, seed=123)]
    assert set(prompts) == {"p0", "p1", "remote"}

    cached_remote = cache_root / "mixed-remote" / "datasets" / "remote.jsonl"
    assert cached_remote.exists()
    cached_content = cached_remote.read_text(encoding="utf-8").strip()
    assert cached_content == json.dumps({"prompt": "remote", "completion": "c"})
