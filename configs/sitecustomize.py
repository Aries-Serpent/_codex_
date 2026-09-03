# ruff: noqa: E402
"""
Ensure local tracking defaults are applied early while keeping import-order linters calm.
"""

import importlib.machinery
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
        raise AttributeError(
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
    except (ImportError, ModuleNotFoundError):  # only stub genuinely missing modules
        stub = ModuleType(module_name)
        stub.__spec__ = importlib.machinery.ModuleSpec(module_name, loader=None)
        stub.__loader__ = None
        stub.__package__ = module_name.rpartition(".")[0]
        stub.__codex_stub__ = True
        if attrs:
            for key, value in attrs.items():
                setattr(stub, key, value)

        def _missing_attr(name: str) -> None:
            # Dunder attributes (e.g. __file__, __spec__, __path__) must raise
            # AttributeError so that getattr(module, dunder, default) returns the
            # default instead of propagating an ImportError.  Hypothesis and other
            # introspection tools call getattr(module, "__file__", None) and rely on
            # this behaviour.
            if name.startswith("__") and name.endswith("__"):
                raise AttributeError(name)
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
_install_optional_stub("hydra")
_install_optional_stub("mlflow")
_install_optional_stub("apply_session_logging_workflow")
_install_optional_stub("chat")
_install_optional_stub("codex_end_to_end")
_install_optional_stub("codex_log_viewer")
_install_optional_stub("codex_logging_workflow")
_install_optional_stub("codex_patch_session_logging")
_install_optional_stub("codex_session_logging_workflow")
_install_optional_stub("codex_workflow")
_install_optional_stub("codex_workflow_session_query")
_install_optional_stub("conversation_logger")
_install_optional_stub("export")
_install_optional_stub("git_patch_parser_complete")
_install_optional_stub("query_logs")
_install_optional_stub("session_hooks")
_install_optional_stub("session_logger")
_install_optional_stub("session_query")
_install_optional_stub("test_chat_session")
_install_optional_stub("test_conversation_logger")
_install_optional_stub("test_export")
_install_optional_stub("test_logging_viewer_cli")
_install_optional_stub("test_session_hooks")
_install_optional_stub("test_session_logging")
_install_optional_stub("test_session_logging_mirror")
_install_optional_stub("test_session_query_smoke")
_install_optional_stub("viewer")


from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking

ensure_local_tracking()


# ============================================================================
# Offline-First Configuration for Experiment Tracking (Phase 3: Autonomy)
# ============================================================================
import os

# Default W&B to offline mode unless explicitly overridden
# This prevents accidental network calls during training
if "WANDB_MODE" not in os.environ:
    os.environ["WANDB_MODE"] = "offline"
    if not os.environ.get("CODEX_SILENT_SITECUSTOMIZE"):
        print(
            "ℹ️  W&B defaulted to offline mode (set WANDB_MODE=online to override)", file=sys.stderr
        )

# Set other offline-first defaults for HuggingFace
if "HF_HUB_OFFLINE" not in os.environ:
    os.environ["HF_HUB_OFFLINE"] = "1"

if "TRANSFORMERS_OFFLINE" not in os.environ:
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Disable telemetry by default
if "WANDB_DISABLE_CODE" not in os.environ:
    os.environ["WANDB_DISABLE_CODE"] = "true"

if "WANDB_SILENT" not in os.environ:
    os.environ["WANDB_SILENT"] = "true"
