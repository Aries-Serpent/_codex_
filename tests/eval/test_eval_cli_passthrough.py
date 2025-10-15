from __future__ import annotations

import subprocess
import sys
import types


def test_eval_cli_env_override_and_passthrough(monkeypatch):
    dummy = types.ModuleType("dummy_eval")

    def _main():
        assert "--foo" in sys.argv and "bar" in sys.argv
        return 0

    dummy.main = _main  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "dummy_eval", dummy)

    code = (
        "import os, sys; "
        "os.environ['CODEX_EVAL_ENTRY']='dummy_eval:main'; "
        "import codex_ml.cli.entrypoints as E; "
        "sys.argv=['codex-eval','--','--foo','bar']; "
        "sys.exit(E.eval_main())"
    )
    proc = subprocess.run([sys.executable, "-c", code])
    assert proc.returncode == 0
