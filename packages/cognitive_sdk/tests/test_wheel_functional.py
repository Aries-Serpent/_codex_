"""Offline wheel functional gate for the ``codex-cognitive-sdk`` MVP distribution.

Implements the acceptance gate declared in ``RELEASE_CONTRACT.md``:

1. Build the wheel with ``python -m build --wheel`` (skipped when the
   ``build`` frontend is unavailable).
2. Install it into a clean target directory with
   ``pip install --no-deps --no-index --target`` (offline: only the locally
   built wheel is used).
3. Import ``codex_cognitive_sdk`` from that target in a clean subprocess
   interpreter (source tree not on ``sys.path``) and construct, validate,
   and round-trip a minimal :class:`ImprovementEvent`.

The test is deterministic and offline. It skips cleanly — with a recorded
reason — whenever ``pip``, ``build``, or the pinned build backend
(``hatchling``) cannot be provisioned without network access.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_TREE = (PACKAGE_ROOT / "src").resolve()

# Executed by the clean subprocess with the wheel-install target directory
# as ``sys.argv[1]``. It must not import anything outside the stdlib plus
# the installed wheel.
_SUBPROCESS_SCRIPT = r"""
import os
import sys
import sysconfig

target = os.path.realpath(sys.argv[1])
stdlib = os.path.realpath(sysconfig.get_path("stdlib"))
platstdlib = os.path.realpath(sysconfig.get_path("platstdlib"))
purelib = os.path.realpath(sysconfig.get_path("purelib"))
platlib = os.path.realpath(sysconfig.get_path("platlib"))
kept = []
for entry in sys.path:
    real = os.path.realpath(entry or os.getcwd())
    if real == target or real in {stdlib, platstdlib, purelib, platlib}:
        kept.append(entry)
        continue
    # Keep interpreter-internal entries (e.g. python312.zip, lib-dynload,
    # the encodings package) that live under the stdlib roots, and drop
    # everything else — notably any source-tree .pth entries from the
    # ambient environment.
    if real.startswith(stdlib + os.sep) or real.startswith(platstdlib + os.sep):
        kept.append(entry)
kept.insert(0, target)
sys.path = kept

import codex_cognitive_sdk as sdk
from codex_cognitive_sdk import (
    EVIDENCE_SCHEMA_VERSION,
    ImprovementEvent,
    SignalEvidence,
    SignalSource,
    event_from_dict,
    event_to_dict,
    make_event_id,
)

module_file = sdk.__file__.replace("\\", "/")
normalized_target = target.replace("\\", "/")
assert module_file.startswith(normalized_target), (
    f"codex_cognitive_sdk imported from {module_file!r}, expected under {normalized_target!r}"
)

signal = SignalEvidence(
    source=SignalSource.LOCAL_TEST_RUN,
    kind="wheel_functional_check",
    measured_at="2026-01-01T00:00:00+00:00",
    summary="offline wheel acceptance gate",
)
event = ImprovementEvent(
    schema_version=EVIDENCE_SCHEMA_VERSION,
    event_id=make_event_id("Aries-Serpent/_codex_", "0" * 40, signal, None, None),
    repo="Aries-Serpent/_codex_",
    ref="refs/heads/main",
    sha="0" * 40,
    signal=signal,
    recorded_at="2026-01-01T00:00:01+00:00",
)
event.validate()
restored = event_from_dict(event_to_dict(event))
assert restored == event, f"round trip mismatch: {restored!r} != {event!r}"
print(f"WHEEL_FUNCTIONAL_OK version={sdk.__version__} file={sdk.__file__}")
"""


def _build_wheel(destination: Path) -> Path:
    if importlib.util.find_spec("build") is None:
        pytest.skip("python -m build is not available in this environment")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--outdir",
            str(destination),
            str(PACKAGE_ROOT),
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).lower()
        offline_causes = (
            "connect",
            "network",
            "resolve",
            "download",
            "no matching distribution",
            "temporarily unavailable",
            "timed out",
            "certificate",
        )
        if any(marker in output for marker in offline_causes):
            pytest.skip(
                "offline environment cannot provision the pinned build backend "
                f"(hatchling): {result.stderr.strip()[-300:]}"
            )
        raise AssertionError(
            f"python -m build failed (rc={result.returncode})\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )
    wheels = sorted(destination.glob("codex_cognitive_sdk-*.whl"))
    assert wheels, f"no codex_cognitive_sdk wheel produced in {destination}"
    return wheels[-1]


def _install_wheel(wheel: Path, target: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--no-index",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "--target",
            str(target),
            str(wheel),
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).lower()
        if any(marker in output for marker in ("connect", "network", "no matching distribution")):
            pytest.skip(f"pip cannot install offline: {result.stderr.strip()[-300:]}")
        raise AssertionError(
            f"pip install of {wheel.name} failed (rc={result.returncode})\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )


def test_wheel_installs_and_imports_from_clean_target(tmp_path: Path) -> None:
    wheel = _build_wheel(tmp_path / "dist")
    target = tmp_path / "target"
    target.mkdir()
    _install_wheel(wheel, target)

    result = subprocess.run(
        [sys.executable, "-I", "-c", _SUBPROCESS_SCRIPT, str(target)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0, (
        f"clean-interpreter wheel functional check failed (rc={result.returncode})\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    assert "WHEEL_FUNCTIONAL_OK" in result.stdout
    resolved_target = str(target.resolve())
    module_file = result.stdout.split("file=", 1)[-1].strip()
    assert Path(module_file).resolve().is_relative_to(Path(resolved_target))
    assert not Path(module_file).resolve().is_relative_to(SRC_TREE)
