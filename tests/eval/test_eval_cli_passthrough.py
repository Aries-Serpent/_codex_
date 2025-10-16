from __future__ import annotations

import sys
import types

from codex_ml.cli.entrypoints import eval_main


def test_eval_cli_env_override_and_passthrough(monkeypatch) -> None:
    dummy = types.ModuleType("dummy_eval")

    def _main() -> int:
        print("PASSTHROUGH")
        return 123

    dummy.main = _main  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "dummy_eval", dummy)
    monkeypatch.setenv("CODEX_EVAL_ENTRY", "dummy_eval:main")
    monkeypatch.setattr(sys, "argv", ["codex-eval"])

    rc = eval_main()

    assert rc == 123
