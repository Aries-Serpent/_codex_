import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke


def _pip(*args: str) -> None:
    cmd = [sys.executable, "-m", "pip", *args]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL)


def test_entrypoint_discovery(tmp_path: Path):
    # Install the local sandbox plugin in editable mode (no network).
    pkg_root = Path(__file__).parent.parent / "plugins" / "_sandbox_pkg"
    assert (pkg_root / "pyproject.toml").exists()
    _pip("install", "-e", str(pkg_root))
    try:
        from codex_ml.plugins.registry import discover, get  # type: ignore

        eps = discover()
        assert "dummy" in eps, f"discovered={list(eps.keys())}"
        Dummy = eps["dummy"]
        inst = Dummy()
        assert hasattr(inst, "predict"), "Dummy plugin should define predict()"
        assert inst.predict("x") == "x"
        assert get("dummy") is Dummy
    finally:
        # Best-effort cleanup
        _pip("uninstall", "-y", "codex-dummy-plugin")
