import json
import shutil
import subprocess
import types

import pytest

import scripts.check_licenses as check_licenses


@pytest.mark.skipif(shutil.which("pip-licenses") is None, reason="pip-licenses not installed")
def test_license_checker_pass(monkeypatch):
    dummy = types.SimpleNamespace(stdout=json.dumps([{"Name": "ok", "License": "MIT"}]))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: dummy)
    assert check_licenses.main() == 0


def test_license_checker_fail(monkeypatch):
    dummy = types.SimpleNamespace(stdout=json.dumps([{"Name": "bad", "License": "GPL"}]))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: dummy)
    assert check_licenses.main() == 1
