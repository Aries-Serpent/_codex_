import importlib.util
import os

import pytest

if os.environ.get("CODEX_CLI_LIGHTWEIGHT", "0") != "1":
    pytest.importorskip("yaml")
    pytest.importorskip("omegaconf")
    pytest.importorskip("hydra")

    spec = importlib.util.find_spec("torch")
    if spec is None:
        pytest.skip("torch not installed", allow_module_level=True)
