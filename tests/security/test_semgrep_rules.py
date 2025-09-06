import shutil
import subprocess
from pathlib import Path

BAD_CODE = """
import subprocess, pickle, yaml, requests, ast
subprocess.run('ls', shell=True)
eval('1+1')
requests.get('http://example.com')
yaml.load('a: b')
pickle.load(open('a','rb'))
requests.get('http://example.com', verify=False)
"""


def test_semgrep_rules(tmp_path: Path) -> None:
    if shutil.which("semgrep") is None:
        import pytest

        pytest.skip("semgrep not installed")
    bad = tmp_path / "bad.py"
    bad.write_text(BAD_CODE)
    res = subprocess.run(
        ["semgrep", "--config", "semgrep_rules/", str(bad)],
        capture_output=True,
        text=True,
    )
    out = res.stdout
    assert "python.requests.no-timeout" in out
    assert "python.pickle.load" in out
