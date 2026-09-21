#!/usr/bin/env python3
import pathlib
import re
import subprocess
import sys


def has_pytest_cov() -> bool:
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pytest-cov"], capture_output=True, text=True
        )
        return out.returncode == 0
    except Exception:
        return False


def _strip_coverage_flags(raw: str) -> str:
    pattern = re.compile(
        r'(?<![\w-])--cov(?:-(?:report|branch|fail-under))?(?:[=\s]+[^\s,\)"]+)?'
    )
    return pattern.sub("", raw).strip()


root = pathlib.Path(".")
pytest_ini_candidates = [root / "configs" / "development" / "pytest.ini", root / "pytest.ini"]
pytest_ini = next(
    (path for path in pytest_ini_candidates if path.exists()), pytest_ini_candidates[0]
)
noxfile = root / "configs" / "development" / "noxfile.py"

cov_ok = has_pytest_cov()
changed = False


def scrub_cov(text: str) -> str:
    """Remove coverage flags without rewriting unrelated Python formatting."""
    regex = re.compile(
        r'(?<![\w-])--cov(?:-(?:report|branch|fail-under))?(?:[=\s]+[^\s,\)"]+)?'
    )
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if "--cov" not in line:
            lines.append(line)
            continue
        lines.append(regex.sub("", line))
    return "".join(lines)


if pytest_ini.exists():
    t = pytest_ini.read_text(encoding="utf-8")
    if not cov_ok and "--cov" in t:
        t2 = re.sub(
            r"(?m)^(addopts\s*=\s*)(.*)$",
            lambda m: f"{m.group(1)}{_strip_coverage_flags(m.group(2))}",
            t,
        )
        if t2 != t:
            pytest_ini.write_text(t2, encoding="utf-8")
            changed = True

if noxfile.exists():
    t = noxfile.read_text(encoding="utf-8")
    if not cov_ok and "--cov" in t:
        t2 = scrub_cov(t)
        if t2 != t:
            noxfile.write_text(t2, encoding="utf-8")
            changed = True

sys.stdout.write(str({"cov_plugin_present": cov_ok, "configs_changed": changed}) + "\n")
