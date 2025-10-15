from __future__ import annotations

import json
import subprocess
import sys


def test_list_plugins_json_smoke():
    code = (
        "import sys, json; "
        "import codex_ml.cli.list_plugins as L; "
        "sys.argv=['list-plugins','--format','json']; "
        "rc=L.main(); "
        "sys.exit(rc)"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert "programmatic" in data and "legacy" in data
    assert isinstance(data["programmatic"].get("names", []), list)


def test_list_plugins_names_only_smoke():
    code = (
        "import sys; "
        "import codex_ml.cli.list_plugins as L; "
        "sys.argv=['list-plugins','--names-only']; "
        "sys.exit(L.main())"
    )
    proc = subprocess.run([sys.executable, "-c", code])
    assert proc.returncode == 0


def test_list_plugins_no_discover_smoke():
    code = (
        "import sys; "
        "import codex_ml.cli.list_plugins as L; "
        "sys.argv=['list-plugins','--no-discover','--format','json']; "
        "sys.exit(L.main())"
    )
    proc = subprocess.run([sys.executable, "-c", code])
    assert proc.returncode == 0
