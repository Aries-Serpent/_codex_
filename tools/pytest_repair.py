#!/usr/bin/env python3
import pathlib, re, subprocess, sys

def has_pytest_cov() -> bool:
    try:
        out = subprocess.run([sys.executable,"-m","pip","show","pytest-cov"],
                             capture_output=True, text=True)
        return out.returncode == 0
    except Exception:
        return False

root = pathlib.Path('.')
pytest_ini = root/"pytest.ini"
pyproject = root/"pyproject.toml"
noxfile   = root/"noxfile.py"

cov_ok = has_pytest_cov()
changed = False

def scrub_cov(text: str) -> str:
    text = re.sub(r"--cov[=\s][^\s]+", "", text)
    text = re.sub(r"--cov-report[=\s][^\s]+", "", text)
    text = re.sub(r"--cov-branch\b", "", text)
    text = re.sub(r"--cov-fail-under[=\s]\d+", "", text)
    return re.sub(r"\s{2,}", " ", text).strip()

if pytest_ini.exists():
    t = pytest_ini.read_text(encoding="utf-8")
    if not cov_ok and "--cov" in t:
        t2 = re.sub(r"(?m)^addopts\s*=\s*(.*)$",
                    lambda m: f"addopts = {scrub_cov(m.group(1))}", t)
        if t2 != t:
            pytest_ini.write_text(t2, encoding="utf-8"); changed = True

if noxfile.exists():
    t = noxfile.read_text(encoding="utf-8")
    if not cov_ok and "--cov" in t:
        t2 = scrub_cov(t)
        if t2 != t:
            noxfile.write_text(t2, encoding="utf-8"); changed = True

print({"cov_plugin_present": cov_ok, "configs_changed": changed})
