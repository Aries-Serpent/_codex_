from __future__ import annotations

import json
import sys
import types

import codex_ml.cli.list_plugins as cli


def test_list_plugins_handles_missing_registry(monkeypatch, capsys) -> None:
    def _raise(*_args, **_kwargs):
        raise RuntimeError("registry unavailable")

    registry = types.ModuleType("codex_ml.registry")
    registry.list_models = _raise  # type: ignore[attr-defined]
    registry.list_tokenizers = _raise  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "codex_ml.registry", registry)

    data_registry = types.ModuleType("codex_ml.data.registry")
    data_registry.list_datasets = _raise  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "codex_ml.data.registry", data_registry)

    programmatic = types.ModuleType("codex_ml.plugins.programmatic")

    class _BrokenRegistry:
        def discover(self) -> dict[str, str]:  # pragma: no cover - executed in test
            raise RuntimeError("discover failed")

        def names(self) -> list[str]:  # pragma: no cover - executed in test
            raise RuntimeError("names failed")

    programmatic.registry = lambda: _BrokenRegistry()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "codex_ml.plugins.programmatic", programmatic)

    import codex_ml.plugins as plugins_pkg

    plugins_pkg.programmatic = programmatic

    rc = cli.main(["--format", "json"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Traceback" not in (captured.err or "")
    payload = json.loads(captured.out)
    assert payload["legacy"]["models"] == []
    assert payload["legacy"]["tokenizers"] == []
    assert payload["legacy"]["datasets"] == []
    assert payload["programmatic"]["names"] == []
    assert payload["programmatic"]["discovered"] == []
