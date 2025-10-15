from __future__ import annotations

import json
import subprocess
import sys


def test_list_plugins_json_smoke() -> None:
    code = (
        "import sys, json; "
        "import codex_ml.cli.list_plugins as cli; "
        "sys.argv = ['list-plugins', '--format', 'json']; "
        "rc = cli.main(); "
        "sys.exit(rc)"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert "legacy" in payload and "programmatic" in payload


def test_list_plugins_names_only_contains_known_plugin() -> None:
    code = (
        "import sys; "
        "import codex_ml.cli.list_plugins as cli; "
        "sys.argv = ['list-plugins', '--names-only']; "
        "rc = cli.main(); "
        "sys.exit(rc)"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "whitespace" in proc.stdout


def test_list_plugins_no_discover_lists_tokenizers() -> None:
    code = (
        "import sys; "
        "import codex_ml.cli.list_plugins as cli; "
        "sys.argv = ['list-plugins', '--no-discover']; "
        "rc = cli.main(); "
        "sys.exit(rc)"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Tokenizers:" in proc.stdout
    assert "whitespace" in proc.stdout
