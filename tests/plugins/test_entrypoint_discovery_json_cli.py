from __future__ import annotations

import json
import subprocess
import sys


def test_list_plugins_json_includes_programmatic_names() -> None:
    code = (
        "import sys, json; "
        "from codex_ml.cli import list_plugins as lp; "
        "sys.argv=['codex-list-plugins','--format','json']; "
        "lp.main()"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0
    stdout = proc.stdout
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        marker = '"programmatic"'
        start = stdout.find(marker)
        if start == -1:
            raise AssertionError(f"JSON payload missing programmatic section: {stdout}") from None
        prefix = stdout[:start]
        brace = prefix.rfind("{")
        end = stdout.rfind("}")
        payload = json.loads(stdout[brace : end + 1])
    names = payload.get("programmatic", {}).get("names", [])
    # Should include at least the example plugins
    assert any(n in names for n in ("hello", "token-accuracy-plugin"))
