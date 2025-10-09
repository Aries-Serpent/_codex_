from __future__ import annotations

import sys
import types

import pytest

from codex_ml.cli.metrics_cli import _csv_to_duckdb


class DummyConnection:
    def __init__(self, executed: list[tuple[str, tuple[str, ...]]]):
        self._executed = executed

    def execute(self, sql: str, params: list[str] | None = None):
        self._executed.append((sql, tuple(params or ())))
        return self

    def close(self) -> None:
        return None


@pytest.mark.parametrize("mode", ["replace", "append", "fail"])
def test_csv_to_duckdb_uses_parameterized_paths(monkeypatch, tmp_path, mode):
    csv_path = tmp_path / "foo'bar" / "metrics.csv"
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text("run_id,epoch,key,value\n", encoding="utf-8")

    duck_db = tmp_path / "out.duckdb"

    executed: list[tuple[str, tuple[str, ...]]] = []

    def fake_connect(path: str):
        assert path == duck_db.as_posix()
        return DummyConnection(executed)

    fake_duckdb = types.SimpleNamespace(connect=fake_connect)
    monkeypatch.setitem(sys.modules, "duckdb", fake_duckdb)

    result = _csv_to_duckdb(csv_path, duck_db, "metrics", mode=mode)
    assert result is True

    assert executed, "expected SQL commands to be executed"
    for _, params in executed:
        assert params and params[0] == csv_path.as_posix()
