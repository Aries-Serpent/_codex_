# ruff: noqa: E402
"""
Ensure local tracking defaults are applied early while keeping import-order linters calm.
"""

import sys
from pathlib import Path
from types import ModuleType


class _StubObject:
    """Placeholder that fails lazily when used."""

    def __init__(self, target: str) -> None:
        self._target = target

    def __call__(self, *args, **kwargs):  # pragma: no cover - defensive
        raise ImportError(
            f"Optional dependency '{self._target}' is not installed; "
            "install it to enable this functionality."
        )

    def __getattr__(self, name: str):  # pragma: no cover - defensive
        raise ImportError(
            f"Optional dependency '{self._target}' is not installed; "
            "install it to enable this functionality."
        )


src_str = str(Path(__file__).parent / "src")
if src_str not in sys.path:
    sys.path.insert(0, src_str)


def _install_optional_stub(module_name: str, *, attrs: dict[str, object] | None = None) -> None:
    """Ensure ``module_name`` can be imported even when optional deps are missing.

    Some of the lightweight offline test suites gate execution behind
    ``pytest.importorskip`` checks for heavyweight ML dependencies.  When those
    dependencies are not installed (common in constrained CI sandboxes) we still
    want the tests to run against the fallback implementations that do not
    require the real packages.  Creating a tiny placeholder module allows the
    import check to succeed while still surfacing a clear error if any code
    actually tries to use the absent library.
    """

    if module_name in sys.modules:
        return

    try:
        __import__(module_name)
    except Exception:  # pragma: no cover - defensive guard
        stub = ModuleType(module_name)
        if attrs:
            for key, value in attrs.items():
                setattr(stub, key, value)

        def _missing_attr(name: str) -> None:
            raise ImportError(
                f"Optional dependency '{module_name}' is not installed; "
                "install it to enable this functionality."
            )

        stub.__getattr__ = _missing_attr  # type: ignore[attr-defined]
        stub.__all__ = []
        sys.modules[module_name] = stub


_install_optional_stub(
    "torch",
    attrs={
        "float32": _StubObject("torch.float32"),
        "float16": _StubObject("torch.float16"),
        "bfloat16": _StubObject("torch.bfloat16"),
    },
)
_install_optional_stub(
    "transformers",
    attrs={
        "AutoModelForCausalLM": _StubObject("transformers.AutoModelForCausalLM"),
        "AutoTokenizer": _StubObject("transformers.AutoTokenizer"),
    },
)
_install_optional_stub("sentencepiece")


from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking

ensure_local_tracking()
