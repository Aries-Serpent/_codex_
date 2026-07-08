"""
Test Toml Compat

Test module for toml compat.
"""

import io

from src.codex_ml.utils.toml_compat import load, loads


def test_loads_parses_minimal_table():
    data = loads("[a]\nb=1\n")
    assert data["a"]["b"] == 1, "Data must not be empty"


def test_load_from_bytes_buffer():
    buf = io.BytesIO(b"[x]\ny=2\n")
    data = load(buf)
    assert data["x"]["y"] == 2, "Data must not be empty"
