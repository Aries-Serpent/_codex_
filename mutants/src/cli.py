"""Minimal command-line interface for running Codex training loops."""

from __future__ import annotations

import argparse
import importlib
import importlib.machinery
import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from data.registry import build as build_registered_dataset
from logging_utils import LoggingConfig
from metrics import accuracy as metrics_accuracy
from omegaconf import OmegaConf
from src.training.trainer import CheckpointConfig, Trainer, TrainerConfig

logger = logging.getLogger(__name__)

try:
    from hydra import compose, initialize_config_dir
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    from config_legacy import compose, initialize_config_dir

CLI_PACKAGE_PATH = Path(__file__).resolve().parent.parent / "cli"
PROJECT_ROOT = CLI_PACKAGE_PATH.parent
sys.path.insert(0, str(PROJECT_ROOT))

TOKENIZATION_DIR = PROJECT_ROOT / "tokenization"
tokenization_pkg = sys.modules.get("tokenization")
if tokenization_pkg is None:
    tokenization_pkg = importlib.util.module_from_spec(
        importlib.machinery.ModuleSpec("tokenization", loader=None, is_package=True)
    )
    tokenization_pkg.__path__ = [str(TOKENIZATION_DIR)]
    sys.modules["tokenization"] = tokenization_pkg

tokenization_spec = importlib.util.spec_from_file_location(
    "tokenization.loader",
    TOKENIZATION_DIR / "loader.py",
    submodule_search_locations=[str(TOKENIZATION_DIR)],
)
if tokenization_spec is None or tokenization_spec.loader is None:
    raise ImportError(f"Unable to load tokenization.loader from {TOKENIZATION_DIR}")
tokenization_loader = importlib.util.module_from_spec(tokenization_spec)
sys.modules["tokenization.loader"] = tokenization_loader
tokenization_spec.loader.exec_module(tokenization_loader)
TRAIN_CODEX_PATH = CLI_PACKAGE_PATH / "train_codex.py"
if not TRAIN_CODEX_PATH.exists():
    raise ImportError(f"train_codex module not found at {TRAIN_CODEX_PATH}")

spec = importlib.util.spec_from_file_location("cli.train_codex", TRAIN_CODEX_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load train_codex module from {TRAIN_CODEX_PATH}")
train_codex = importlib.util.module_from_spec(spec)
sys.modules["cli.train_codex"] = train_codex
spec.loader.exec_module(train_codex)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x__ensure_real_torch__mutmut_orig() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_1() -> None:
    module = None
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_2() -> None:
    module = sys.modules.get(None)
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_3() -> None:
    module = sys.modules.get("XXtorchXX")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_4() -> None:
    module = sys.modules.get("TORCH")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_5() -> None:
    module = sys.modules.get("torch")
    if module is not None or not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_6() -> None:
    module = sys.modules.get("torch")
    if module is None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_7() -> None:
    module = sys.modules.get("torch")
    if module is not None and getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_8() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith(None):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_9() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(None, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_10() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, None, "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_11() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", None).endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_12() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr("__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_13() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_14() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", ).endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_15() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "XX__version__XX", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_16() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__VERSION__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_17() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "XXXX").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_18() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("XXstubXX"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_19() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("STUB"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_20() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = None
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_21() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent * f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_22() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(None).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_23() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() or str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_24() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(None) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_25() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_26() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(None, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_27() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, None)
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_28() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_29() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, )
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_30() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(1, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_31() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(None))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_32() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "XXtorchXX" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_33() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "TORCH" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_34() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" not in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_35() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["XXtorchXX"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_36() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["TORCH"]
    importlib.import_module("torch")


def x__ensure_real_torch__mutmut_37() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module(None)


def x__ensure_real_torch__mutmut_38() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("XXtorchXX")


def x__ensure_real_torch__mutmut_39() -> None:
    module = sys.modules.get("torch")
    if module is not None and not getattr(module, "__version__", "").endswith("stub"):
        return
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    importlib.import_module("TORCH")

x__ensure_real_torch__mutmut_mutants : ClassVar[MutantDict] = {
'x__ensure_real_torch__mutmut_1': x__ensure_real_torch__mutmut_1, 
    'x__ensure_real_torch__mutmut_2': x__ensure_real_torch__mutmut_2, 
    'x__ensure_real_torch__mutmut_3': x__ensure_real_torch__mutmut_3, 
    'x__ensure_real_torch__mutmut_4': x__ensure_real_torch__mutmut_4, 
    'x__ensure_real_torch__mutmut_5': x__ensure_real_torch__mutmut_5, 
    'x__ensure_real_torch__mutmut_6': x__ensure_real_torch__mutmut_6, 
    'x__ensure_real_torch__mutmut_7': x__ensure_real_torch__mutmut_7, 
    'x__ensure_real_torch__mutmut_8': x__ensure_real_torch__mutmut_8, 
    'x__ensure_real_torch__mutmut_9': x__ensure_real_torch__mutmut_9, 
    'x__ensure_real_torch__mutmut_10': x__ensure_real_torch__mutmut_10, 
    'x__ensure_real_torch__mutmut_11': x__ensure_real_torch__mutmut_11, 
    'x__ensure_real_torch__mutmut_12': x__ensure_real_torch__mutmut_12, 
    'x__ensure_real_torch__mutmut_13': x__ensure_real_torch__mutmut_13, 
    'x__ensure_real_torch__mutmut_14': x__ensure_real_torch__mutmut_14, 
    'x__ensure_real_torch__mutmut_15': x__ensure_real_torch__mutmut_15, 
    'x__ensure_real_torch__mutmut_16': x__ensure_real_torch__mutmut_16, 
    'x__ensure_real_torch__mutmut_17': x__ensure_real_torch__mutmut_17, 
    'x__ensure_real_torch__mutmut_18': x__ensure_real_torch__mutmut_18, 
    'x__ensure_real_torch__mutmut_19': x__ensure_real_torch__mutmut_19, 
    'x__ensure_real_torch__mutmut_20': x__ensure_real_torch__mutmut_20, 
    'x__ensure_real_torch__mutmut_21': x__ensure_real_torch__mutmut_21, 
    'x__ensure_real_torch__mutmut_22': x__ensure_real_torch__mutmut_22, 
    'x__ensure_real_torch__mutmut_23': x__ensure_real_torch__mutmut_23, 
    'x__ensure_real_torch__mutmut_24': x__ensure_real_torch__mutmut_24, 
    'x__ensure_real_torch__mutmut_25': x__ensure_real_torch__mutmut_25, 
    'x__ensure_real_torch__mutmut_26': x__ensure_real_torch__mutmut_26, 
    'x__ensure_real_torch__mutmut_27': x__ensure_real_torch__mutmut_27, 
    'x__ensure_real_torch__mutmut_28': x__ensure_real_torch__mutmut_28, 
    'x__ensure_real_torch__mutmut_29': x__ensure_real_torch__mutmut_29, 
    'x__ensure_real_torch__mutmut_30': x__ensure_real_torch__mutmut_30, 
    'x__ensure_real_torch__mutmut_31': x__ensure_real_torch__mutmut_31, 
    'x__ensure_real_torch__mutmut_32': x__ensure_real_torch__mutmut_32, 
    'x__ensure_real_torch__mutmut_33': x__ensure_real_torch__mutmut_33, 
    'x__ensure_real_torch__mutmut_34': x__ensure_real_torch__mutmut_34, 
    'x__ensure_real_torch__mutmut_35': x__ensure_real_torch__mutmut_35, 
    'x__ensure_real_torch__mutmut_36': x__ensure_real_torch__mutmut_36, 
    'x__ensure_real_torch__mutmut_37': x__ensure_real_torch__mutmut_37, 
    'x__ensure_real_torch__mutmut_38': x__ensure_real_torch__mutmut_38, 
    'x__ensure_real_torch__mutmut_39': x__ensure_real_torch__mutmut_39
}

def _ensure_real_torch(*args, **kwargs):
    result = _mutmut_trampoline(x__ensure_real_torch__mutmut_orig, x__ensure_real_torch__mutmut_mutants, args, kwargs)
    return result 

_ensure_real_torch.__signature__ = _mutmut_signature(x__ensure_real_torch__mutmut_orig)
x__ensure_real_torch__mutmut_orig.__name__ = 'x__ensure_real_torch'


def x__resolve_callable__mutmut_orig(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_1(target: str) -> Any:
    module_name, _, attr = None
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_2(target: str) -> Any:
    module_name, _, attr = target.rpartition(None)
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_3(target: str) -> Any:
    module_name, _, attr = target.partition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_4(target: str) -> Any:
    module_name, _, attr = target.rpartition("XX.XX")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_5(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_6(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(None)
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_7(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith(None):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_8(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("XXtorchXX"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_9(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("TORCH"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_10(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = None
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_11(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(None)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_12(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(None, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_13(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, None)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_14(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_15(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, )
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"Module '{module_name}' has no attribute '{attr}'") from exc


def x__resolve_callable__mutmut_16(target: str) -> Any:
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"Target '{target}' must include a module path")
    if module_name.startswith("torch"):
        _ensure_real_torch()
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise AttributeError(None) from exc

x__resolve_callable__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_callable__mutmut_1': x__resolve_callable__mutmut_1, 
    'x__resolve_callable__mutmut_2': x__resolve_callable__mutmut_2, 
    'x__resolve_callable__mutmut_3': x__resolve_callable__mutmut_3, 
    'x__resolve_callable__mutmut_4': x__resolve_callable__mutmut_4, 
    'x__resolve_callable__mutmut_5': x__resolve_callable__mutmut_5, 
    'x__resolve_callable__mutmut_6': x__resolve_callable__mutmut_6, 
    'x__resolve_callable__mutmut_7': x__resolve_callable__mutmut_7, 
    'x__resolve_callable__mutmut_8': x__resolve_callable__mutmut_8, 
    'x__resolve_callable__mutmut_9': x__resolve_callable__mutmut_9, 
    'x__resolve_callable__mutmut_10': x__resolve_callable__mutmut_10, 
    'x__resolve_callable__mutmut_11': x__resolve_callable__mutmut_11, 
    'x__resolve_callable__mutmut_12': x__resolve_callable__mutmut_12, 
    'x__resolve_callable__mutmut_13': x__resolve_callable__mutmut_13, 
    'x__resolve_callable__mutmut_14': x__resolve_callable__mutmut_14, 
    'x__resolve_callable__mutmut_15': x__resolve_callable__mutmut_15, 
    'x__resolve_callable__mutmut_16': x__resolve_callable__mutmut_16
}

def _resolve_callable(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_callable__mutmut_orig, x__resolve_callable__mutmut_mutants, args, kwargs)
    return result 

_resolve_callable.__signature__ = _mutmut_signature(x__resolve_callable__mutmut_orig)
x__resolve_callable__mutmut_orig.__name__ = 'x__resolve_callable'


def x__section_to_dict__mutmut_orig(section: Any) -> dict[str, Any]:
    if isinstance(section, Mapping):
        return dict(section)
    return {}


def x__section_to_dict__mutmut_1(section: Any) -> dict[str, Any]:
    if isinstance(section, Mapping):
        return dict(None)
    return {}

x__section_to_dict__mutmut_mutants : ClassVar[MutantDict] = {
'x__section_to_dict__mutmut_1': x__section_to_dict__mutmut_1
}

def _section_to_dict(*args, **kwargs):
    result = _mutmut_trampoline(x__section_to_dict__mutmut_orig, x__section_to_dict__mutmut_mutants, args, kwargs)
    return result 

_section_to_dict.__signature__ = _mutmut_signature(x__section_to_dict__mutmut_orig)
x__section_to_dict__mutmut_orig.__name__ = 'x__section_to_dict'


def x_simple_synthetic_data__mutmut_orig(**params: Any) -> tuple[Any, Any | None]:
    """Expose the built-in synthetic dataset via a convenience wrapper."""

    return build_registered_dataset("synthetic_classification", **params)


def x_simple_synthetic_data__mutmut_1(**params: Any) -> tuple[Any, Any | None]:
    """Expose the built-in synthetic dataset via a convenience wrapper."""

    return build_registered_dataset(None, **params)


def x_simple_synthetic_data__mutmut_2(**params: Any) -> tuple[Any, Any | None]:
    """Expose the built-in synthetic dataset via a convenience wrapper."""

    return build_registered_dataset(**params)


def x_simple_synthetic_data__mutmut_3(**params: Any) -> tuple[Any, Any | None]:
    """Expose the built-in synthetic dataset via a convenience wrapper."""

    return build_registered_dataset("synthetic_classification", )


def x_simple_synthetic_data__mutmut_4(**params: Any) -> tuple[Any, Any | None]:
    """Expose the built-in synthetic dataset via a convenience wrapper."""

    return build_registered_dataset("XXsynthetic_classificationXX", **params)


def x_simple_synthetic_data__mutmut_5(**params: Any) -> tuple[Any, Any | None]:
    """Expose the built-in synthetic dataset via a convenience wrapper."""

    return build_registered_dataset("SYNTHETIC_CLASSIFICATION", **params)

x_simple_synthetic_data__mutmut_mutants : ClassVar[MutantDict] = {
'x_simple_synthetic_data__mutmut_1': x_simple_synthetic_data__mutmut_1, 
    'x_simple_synthetic_data__mutmut_2': x_simple_synthetic_data__mutmut_2, 
    'x_simple_synthetic_data__mutmut_3': x_simple_synthetic_data__mutmut_3, 
    'x_simple_synthetic_data__mutmut_4': x_simple_synthetic_data__mutmut_4, 
    'x_simple_synthetic_data__mutmut_5': x_simple_synthetic_data__mutmut_5
}

def simple_synthetic_data(*args, **kwargs):
    result = _mutmut_trampoline(x_simple_synthetic_data__mutmut_orig, x_simple_synthetic_data__mutmut_mutants, args, kwargs)
    return result 

simple_synthetic_data.__signature__ = _mutmut_signature(x_simple_synthetic_data__mutmut_orig)
x_simple_synthetic_data__mutmut_orig.__name__ = 'x_simple_synthetic_data'


def x_classification_accuracy__mutmut_orig(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_1(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(None, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_2(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, None):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_3(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr("logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_4(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, ):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_5(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "XXlogitsXX"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_6(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "LOGITS"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_7(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = None
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_8(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(None, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_9(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, None):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_10(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr("detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_11(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, ):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_12(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "XXdetachXX"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_13(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "DETACH"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_14(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = None
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_15(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(None, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_16(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, None):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_17(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr("cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_18(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, ):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_19(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "XXcpuXX"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_20(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "CPU"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_21(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = None
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_22(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(None, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_23(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, None):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_24(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr("numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_25(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, ):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_26(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "XXnumpyXX"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_27(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "NUMPY"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_28(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = None
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_29(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(None)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_30(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = None
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_31(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(None, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_32(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, None):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_33(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr("detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_34(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, ):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_35(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "XXdetachXX"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_36(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "DETACH"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_37(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = None
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_38(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(None, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_39(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, None):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_40(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr("cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_41(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, ):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_42(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "XXcpuXX"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_43(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "CPU"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_44(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = None
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_45(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(None, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_46(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, None):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_47(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr("numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_48(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, ):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_49(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "XXnumpyXX"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_50(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "NUMPY"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_51(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = None
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_52(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(None)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_53(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = None
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_54(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = None
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_55(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=None)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_56(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=+1)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_57(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-2)
    return float(metrics_accuracy(predictions, labels_array))


def x_classification_accuracy__mutmut_58(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(None)


def x_classification_accuracy__mutmut_59(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(None, labels_array))


def x_classification_accuracy__mutmut_60(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, None))


def x_classification_accuracy__mutmut_61(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(labels_array))


def x_classification_accuracy__mutmut_62(outputs: Any, labels: Any) -> float:
    """Compute classification accuracy given logits and integer labels."""

    if hasattr(outputs, "logits"):
        outputs = outputs.logits
    if hasattr(outputs, "detach"):
        outputs = outputs.detach()
    if hasattr(outputs, "cpu"):
        outputs = outputs.cpu()
    if hasattr(outputs, "numpy"):
        import numpy as np

        logits = np.asarray(outputs)
    else:
        logits = outputs
    if hasattr(labels, "detach"):
        labels = labels.detach()
    if hasattr(labels, "cpu"):
        labels = labels.cpu()
    if hasattr(labels, "numpy"):
        import numpy as np

        labels_array = np.asarray(labels)
    else:
        labels_array = labels
    predictions = logits.argmax(axis=-1)
    return float(metrics_accuracy(predictions, ))

x_classification_accuracy__mutmut_mutants : ClassVar[MutantDict] = {
'x_classification_accuracy__mutmut_1': x_classification_accuracy__mutmut_1, 
    'x_classification_accuracy__mutmut_2': x_classification_accuracy__mutmut_2, 
    'x_classification_accuracy__mutmut_3': x_classification_accuracy__mutmut_3, 
    'x_classification_accuracy__mutmut_4': x_classification_accuracy__mutmut_4, 
    'x_classification_accuracy__mutmut_5': x_classification_accuracy__mutmut_5, 
    'x_classification_accuracy__mutmut_6': x_classification_accuracy__mutmut_6, 
    'x_classification_accuracy__mutmut_7': x_classification_accuracy__mutmut_7, 
    'x_classification_accuracy__mutmut_8': x_classification_accuracy__mutmut_8, 
    'x_classification_accuracy__mutmut_9': x_classification_accuracy__mutmut_9, 
    'x_classification_accuracy__mutmut_10': x_classification_accuracy__mutmut_10, 
    'x_classification_accuracy__mutmut_11': x_classification_accuracy__mutmut_11, 
    'x_classification_accuracy__mutmut_12': x_classification_accuracy__mutmut_12, 
    'x_classification_accuracy__mutmut_13': x_classification_accuracy__mutmut_13, 
    'x_classification_accuracy__mutmut_14': x_classification_accuracy__mutmut_14, 
    'x_classification_accuracy__mutmut_15': x_classification_accuracy__mutmut_15, 
    'x_classification_accuracy__mutmut_16': x_classification_accuracy__mutmut_16, 
    'x_classification_accuracy__mutmut_17': x_classification_accuracy__mutmut_17, 
    'x_classification_accuracy__mutmut_18': x_classification_accuracy__mutmut_18, 
    'x_classification_accuracy__mutmut_19': x_classification_accuracy__mutmut_19, 
    'x_classification_accuracy__mutmut_20': x_classification_accuracy__mutmut_20, 
    'x_classification_accuracy__mutmut_21': x_classification_accuracy__mutmut_21, 
    'x_classification_accuracy__mutmut_22': x_classification_accuracy__mutmut_22, 
    'x_classification_accuracy__mutmut_23': x_classification_accuracy__mutmut_23, 
    'x_classification_accuracy__mutmut_24': x_classification_accuracy__mutmut_24, 
    'x_classification_accuracy__mutmut_25': x_classification_accuracy__mutmut_25, 
    'x_classification_accuracy__mutmut_26': x_classification_accuracy__mutmut_26, 
    'x_classification_accuracy__mutmut_27': x_classification_accuracy__mutmut_27, 
    'x_classification_accuracy__mutmut_28': x_classification_accuracy__mutmut_28, 
    'x_classification_accuracy__mutmut_29': x_classification_accuracy__mutmut_29, 
    'x_classification_accuracy__mutmut_30': x_classification_accuracy__mutmut_30, 
    'x_classification_accuracy__mutmut_31': x_classification_accuracy__mutmut_31, 
    'x_classification_accuracy__mutmut_32': x_classification_accuracy__mutmut_32, 
    'x_classification_accuracy__mutmut_33': x_classification_accuracy__mutmut_33, 
    'x_classification_accuracy__mutmut_34': x_classification_accuracy__mutmut_34, 
    'x_classification_accuracy__mutmut_35': x_classification_accuracy__mutmut_35, 
    'x_classification_accuracy__mutmut_36': x_classification_accuracy__mutmut_36, 
    'x_classification_accuracy__mutmut_37': x_classification_accuracy__mutmut_37, 
    'x_classification_accuracy__mutmut_38': x_classification_accuracy__mutmut_38, 
    'x_classification_accuracy__mutmut_39': x_classification_accuracy__mutmut_39, 
    'x_classification_accuracy__mutmut_40': x_classification_accuracy__mutmut_40, 
    'x_classification_accuracy__mutmut_41': x_classification_accuracy__mutmut_41, 
    'x_classification_accuracy__mutmut_42': x_classification_accuracy__mutmut_42, 
    'x_classification_accuracy__mutmut_43': x_classification_accuracy__mutmut_43, 
    'x_classification_accuracy__mutmut_44': x_classification_accuracy__mutmut_44, 
    'x_classification_accuracy__mutmut_45': x_classification_accuracy__mutmut_45, 
    'x_classification_accuracy__mutmut_46': x_classification_accuracy__mutmut_46, 
    'x_classification_accuracy__mutmut_47': x_classification_accuracy__mutmut_47, 
    'x_classification_accuracy__mutmut_48': x_classification_accuracy__mutmut_48, 
    'x_classification_accuracy__mutmut_49': x_classification_accuracy__mutmut_49, 
    'x_classification_accuracy__mutmut_50': x_classification_accuracy__mutmut_50, 
    'x_classification_accuracy__mutmut_51': x_classification_accuracy__mutmut_51, 
    'x_classification_accuracy__mutmut_52': x_classification_accuracy__mutmut_52, 
    'x_classification_accuracy__mutmut_53': x_classification_accuracy__mutmut_53, 
    'x_classification_accuracy__mutmut_54': x_classification_accuracy__mutmut_54, 
    'x_classification_accuracy__mutmut_55': x_classification_accuracy__mutmut_55, 
    'x_classification_accuracy__mutmut_56': x_classification_accuracy__mutmut_56, 
    'x_classification_accuracy__mutmut_57': x_classification_accuracy__mutmut_57, 
    'x_classification_accuracy__mutmut_58': x_classification_accuracy__mutmut_58, 
    'x_classification_accuracy__mutmut_59': x_classification_accuracy__mutmut_59, 
    'x_classification_accuracy__mutmut_60': x_classification_accuracy__mutmut_60, 
    'x_classification_accuracy__mutmut_61': x_classification_accuracy__mutmut_61, 
    'x_classification_accuracy__mutmut_62': x_classification_accuracy__mutmut_62
}

def classification_accuracy(*args, **kwargs):
    result = _mutmut_trampoline(x_classification_accuracy__mutmut_orig, x_classification_accuracy__mutmut_mutants, args, kwargs)
    return result 

classification_accuracy.__signature__ = _mutmut_signature(x_classification_accuracy__mutmut_orig)
x_classification_accuracy__mutmut_orig.__name__ = 'x_classification_accuracy'


def x__instantiate_model__mutmut_orig(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_1(model_cfg: Mapping[str, Any]) -> Any:
    target = None
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_2(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get(None)
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_3(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("XXtargetXX")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_4(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("TARGET")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_5(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_6(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError(None)
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_7(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("XXmodel.target is requiredXX")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_8(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("MODEL.TARGET IS REQUIRED")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_9(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = None
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_10(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(None)
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_11(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get(None))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_12(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("XXparamsXX"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_13(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("PARAMS"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_model__mutmut_14(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = None
    return factory(**params)


def x__instantiate_model__mutmut_15(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(None)
    return factory(**params)


def x__instantiate_model__mutmut_16(model_cfg: Mapping[str, Any]) -> Any:
    target = model_cfg.get("target")
    if not target:
        raise ValueError("model.target is required")
    params = _section_to_dict(model_cfg.get("params"))
    factory = _resolve_callable(str(None))
    return factory(**params)

x__instantiate_model__mutmut_mutants : ClassVar[MutantDict] = {
'x__instantiate_model__mutmut_1': x__instantiate_model__mutmut_1, 
    'x__instantiate_model__mutmut_2': x__instantiate_model__mutmut_2, 
    'x__instantiate_model__mutmut_3': x__instantiate_model__mutmut_3, 
    'x__instantiate_model__mutmut_4': x__instantiate_model__mutmut_4, 
    'x__instantiate_model__mutmut_5': x__instantiate_model__mutmut_5, 
    'x__instantiate_model__mutmut_6': x__instantiate_model__mutmut_6, 
    'x__instantiate_model__mutmut_7': x__instantiate_model__mutmut_7, 
    'x__instantiate_model__mutmut_8': x__instantiate_model__mutmut_8, 
    'x__instantiate_model__mutmut_9': x__instantiate_model__mutmut_9, 
    'x__instantiate_model__mutmut_10': x__instantiate_model__mutmut_10, 
    'x__instantiate_model__mutmut_11': x__instantiate_model__mutmut_11, 
    'x__instantiate_model__mutmut_12': x__instantiate_model__mutmut_12, 
    'x__instantiate_model__mutmut_13': x__instantiate_model__mutmut_13, 
    'x__instantiate_model__mutmut_14': x__instantiate_model__mutmut_14, 
    'x__instantiate_model__mutmut_15': x__instantiate_model__mutmut_15, 
    'x__instantiate_model__mutmut_16': x__instantiate_model__mutmut_16
}

def _instantiate_model(*args, **kwargs):
    result = _mutmut_trampoline(x__instantiate_model__mutmut_orig, x__instantiate_model__mutmut_mutants, args, kwargs)
    return result 

_instantiate_model.__signature__ = _mutmut_signature(x__instantiate_model__mutmut_orig)
x__instantiate_model__mutmut_orig.__name__ = 'x__instantiate_model'


def x__instantiate_optimizer__mutmut_orig(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_1(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = None
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_2(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get(None)
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_3(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("XXtargetXX")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_4(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("TARGET")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_5(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_6(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError(None)
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_7(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("XXoptimizer.target is requiredXX")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_8(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("OPTIMIZER.TARGET IS REQUIRED")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_9(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = None
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_10(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(None)
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_11(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get(None))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_12(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("XXparamsXX"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_13(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("PARAMS"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_14(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = None
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_15(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(None)
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_16(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(None))
    return factory(model.parameters(), **params)


def x__instantiate_optimizer__mutmut_17(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(None, **params)


def x__instantiate_optimizer__mutmut_18(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(**params)


def x__instantiate_optimizer__mutmut_19(optimizer_cfg: Mapping[str, Any], model: Any) -> Any:
    target = optimizer_cfg.get("target")
    if not target:
        raise ValueError("optimizer.target is required")
    params = _section_to_dict(optimizer_cfg.get("params"))
    factory = _resolve_callable(str(target))
    return factory(model.parameters(), )

x__instantiate_optimizer__mutmut_mutants : ClassVar[MutantDict] = {
'x__instantiate_optimizer__mutmut_1': x__instantiate_optimizer__mutmut_1, 
    'x__instantiate_optimizer__mutmut_2': x__instantiate_optimizer__mutmut_2, 
    'x__instantiate_optimizer__mutmut_3': x__instantiate_optimizer__mutmut_3, 
    'x__instantiate_optimizer__mutmut_4': x__instantiate_optimizer__mutmut_4, 
    'x__instantiate_optimizer__mutmut_5': x__instantiate_optimizer__mutmut_5, 
    'x__instantiate_optimizer__mutmut_6': x__instantiate_optimizer__mutmut_6, 
    'x__instantiate_optimizer__mutmut_7': x__instantiate_optimizer__mutmut_7, 
    'x__instantiate_optimizer__mutmut_8': x__instantiate_optimizer__mutmut_8, 
    'x__instantiate_optimizer__mutmut_9': x__instantiate_optimizer__mutmut_9, 
    'x__instantiate_optimizer__mutmut_10': x__instantiate_optimizer__mutmut_10, 
    'x__instantiate_optimizer__mutmut_11': x__instantiate_optimizer__mutmut_11, 
    'x__instantiate_optimizer__mutmut_12': x__instantiate_optimizer__mutmut_12, 
    'x__instantiate_optimizer__mutmut_13': x__instantiate_optimizer__mutmut_13, 
    'x__instantiate_optimizer__mutmut_14': x__instantiate_optimizer__mutmut_14, 
    'x__instantiate_optimizer__mutmut_15': x__instantiate_optimizer__mutmut_15, 
    'x__instantiate_optimizer__mutmut_16': x__instantiate_optimizer__mutmut_16, 
    'x__instantiate_optimizer__mutmut_17': x__instantiate_optimizer__mutmut_17, 
    'x__instantiate_optimizer__mutmut_18': x__instantiate_optimizer__mutmut_18, 
    'x__instantiate_optimizer__mutmut_19': x__instantiate_optimizer__mutmut_19
}

def _instantiate_optimizer(*args, **kwargs):
    result = _mutmut_trampoline(x__instantiate_optimizer__mutmut_orig, x__instantiate_optimizer__mutmut_mutants, args, kwargs)
    return result 

_instantiate_optimizer.__signature__ = _mutmut_signature(x__instantiate_optimizer__mutmut_orig)
x__instantiate_optimizer__mutmut_orig.__name__ = 'x__instantiate_optimizer'


def x__resolve_loss__mutmut_orig(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_1(loss_cfg: Mapping[str, Any] | None) -> Any:
    if loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_2(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = None
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_3(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get(None)
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_4(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("XXtargetXX")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_5(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("TARGET")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_6(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = None
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_7(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(None)
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_8(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get(None))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_9(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("XXparamsXX"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_10(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("PARAMS"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_11(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = None
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_12(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(None)
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_13(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(None))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_14(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: None
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_15(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(None, labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_16(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, None, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_17(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(labels, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_18(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, **params)
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_19(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, )
        return fn
    raise ValueError("loss configuration must provide a target")


def x__resolve_loss__mutmut_20(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError(None)


def x__resolve_loss__mutmut_21(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("XXloss configuration must provide a targetXX")


def x__resolve_loss__mutmut_22(loss_cfg: Mapping[str, Any] | None) -> Any:
    if not loss_cfg:
        import torch.nn.functional as F

        return F.cross_entropy
    target = loss_cfg.get("target")
    params = _section_to_dict(loss_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    raise ValueError("LOSS CONFIGURATION MUST PROVIDE A TARGET")

x__resolve_loss__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_loss__mutmut_1': x__resolve_loss__mutmut_1, 
    'x__resolve_loss__mutmut_2': x__resolve_loss__mutmut_2, 
    'x__resolve_loss__mutmut_3': x__resolve_loss__mutmut_3, 
    'x__resolve_loss__mutmut_4': x__resolve_loss__mutmut_4, 
    'x__resolve_loss__mutmut_5': x__resolve_loss__mutmut_5, 
    'x__resolve_loss__mutmut_6': x__resolve_loss__mutmut_6, 
    'x__resolve_loss__mutmut_7': x__resolve_loss__mutmut_7, 
    'x__resolve_loss__mutmut_8': x__resolve_loss__mutmut_8, 
    'x__resolve_loss__mutmut_9': x__resolve_loss__mutmut_9, 
    'x__resolve_loss__mutmut_10': x__resolve_loss__mutmut_10, 
    'x__resolve_loss__mutmut_11': x__resolve_loss__mutmut_11, 
    'x__resolve_loss__mutmut_12': x__resolve_loss__mutmut_12, 
    'x__resolve_loss__mutmut_13': x__resolve_loss__mutmut_13, 
    'x__resolve_loss__mutmut_14': x__resolve_loss__mutmut_14, 
    'x__resolve_loss__mutmut_15': x__resolve_loss__mutmut_15, 
    'x__resolve_loss__mutmut_16': x__resolve_loss__mutmut_16, 
    'x__resolve_loss__mutmut_17': x__resolve_loss__mutmut_17, 
    'x__resolve_loss__mutmut_18': x__resolve_loss__mutmut_18, 
    'x__resolve_loss__mutmut_19': x__resolve_loss__mutmut_19, 
    'x__resolve_loss__mutmut_20': x__resolve_loss__mutmut_20, 
    'x__resolve_loss__mutmut_21': x__resolve_loss__mutmut_21, 
    'x__resolve_loss__mutmut_22': x__resolve_loss__mutmut_22
}

def _resolve_loss(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_loss__mutmut_orig, x__resolve_loss__mutmut_mutants, args, kwargs)
    return result 

_resolve_loss.__signature__ = _mutmut_signature(x__resolve_loss__mutmut_orig)
x__resolve_loss__mutmut_orig.__name__ = 'x__resolve_loss'


def x__resolve_metric__mutmut_orig(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_1(metric_cfg: Mapping[str, Any] | None) -> Any:
    if metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_2(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = None
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_3(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get(None)
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_4(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("XXtargetXX")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_5(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("TARGET")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_6(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = None
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_7(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(None)
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_8(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get(None))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_9(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("XXparamsXX"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_10(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("PARAMS"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_11(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = None
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_12(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(None)
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_13(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(None))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_14(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: None
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_15(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(None, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_16(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, None, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_17(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_18(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_19(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, )
        return fn
    name = metric_cfg.get("name")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_20(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = None
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_21(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get(None)
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_22(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("XXnameXX")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_23(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("NAME")
    if name == "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_24(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name != "accuracy":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_25(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "XXaccuracyXX":
        return classification_accuracy
    return None


def x__resolve_metric__mutmut_26(metric_cfg: Mapping[str, Any] | None) -> Any:
    if not metric_cfg:
        return None
    target = metric_cfg.get("target")
    params = _section_to_dict(metric_cfg.get("params"))
    if target:
        fn = _resolve_callable(str(target))
        if params:
            return lambda outputs, labels: fn(outputs, labels, **params)
        return fn
    name = metric_cfg.get("name")
    if name == "ACCURACY":
        return classification_accuracy
    return None

x__resolve_metric__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_metric__mutmut_1': x__resolve_metric__mutmut_1, 
    'x__resolve_metric__mutmut_2': x__resolve_metric__mutmut_2, 
    'x__resolve_metric__mutmut_3': x__resolve_metric__mutmut_3, 
    'x__resolve_metric__mutmut_4': x__resolve_metric__mutmut_4, 
    'x__resolve_metric__mutmut_5': x__resolve_metric__mutmut_5, 
    'x__resolve_metric__mutmut_6': x__resolve_metric__mutmut_6, 
    'x__resolve_metric__mutmut_7': x__resolve_metric__mutmut_7, 
    'x__resolve_metric__mutmut_8': x__resolve_metric__mutmut_8, 
    'x__resolve_metric__mutmut_9': x__resolve_metric__mutmut_9, 
    'x__resolve_metric__mutmut_10': x__resolve_metric__mutmut_10, 
    'x__resolve_metric__mutmut_11': x__resolve_metric__mutmut_11, 
    'x__resolve_metric__mutmut_12': x__resolve_metric__mutmut_12, 
    'x__resolve_metric__mutmut_13': x__resolve_metric__mutmut_13, 
    'x__resolve_metric__mutmut_14': x__resolve_metric__mutmut_14, 
    'x__resolve_metric__mutmut_15': x__resolve_metric__mutmut_15, 
    'x__resolve_metric__mutmut_16': x__resolve_metric__mutmut_16, 
    'x__resolve_metric__mutmut_17': x__resolve_metric__mutmut_17, 
    'x__resolve_metric__mutmut_18': x__resolve_metric__mutmut_18, 
    'x__resolve_metric__mutmut_19': x__resolve_metric__mutmut_19, 
    'x__resolve_metric__mutmut_20': x__resolve_metric__mutmut_20, 
    'x__resolve_metric__mutmut_21': x__resolve_metric__mutmut_21, 
    'x__resolve_metric__mutmut_22': x__resolve_metric__mutmut_22, 
    'x__resolve_metric__mutmut_23': x__resolve_metric__mutmut_23, 
    'x__resolve_metric__mutmut_24': x__resolve_metric__mutmut_24, 
    'x__resolve_metric__mutmut_25': x__resolve_metric__mutmut_25, 
    'x__resolve_metric__mutmut_26': x__resolve_metric__mutmut_26
}

def _resolve_metric(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_metric__mutmut_orig, x__resolve_metric__mutmut_mutants, args, kwargs)
    return result 

_resolve_metric.__signature__ = _mutmut_signature(x__resolve_metric__mutmut_orig)
x__resolve_metric__mutmut_orig.__name__ = 'x__resolve_metric'


def x__resolve_dataloaders__mutmut_orig(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_1(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_2(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError(None)
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_3(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("XXdata configuration is requiredXX")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_4(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("DATA CONFIGURATION IS REQUIRED")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_5(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = None
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_6(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(None)
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_7(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get(None))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_8(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("XXparamsXX"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_9(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("PARAMS"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_10(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = None
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_11(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get(None)
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_12(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("XXtargetXX")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_13(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("TARGET")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_14(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = None
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_15(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(None)
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_16(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(None))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_17(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = None
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_18(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = None
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_19(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get(None)
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_20(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("XXnameXX")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_21(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("NAME")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_22(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_23(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError(None)
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_24(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("XXdata configuration must provide 'target' or 'name'XX")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_25(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("DATA CONFIGURATION MUST PROVIDE 'TARGET' OR 'NAME'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_26(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = None
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_27(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(None, **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_28(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(**params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_29(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), )
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_30(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(None), **params)
    if isinstance(loaders, tuple) and len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_31(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) or len(loaders) == 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_32(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) != 2:
        return loaders  # type: ignore[return-value]
    return loaders, None


def x__resolve_dataloaders__mutmut_33(data_cfg: Mapping[str, Any]) -> tuple[Any, Any | None]:
    if not data_cfg:
        raise ValueError("data configuration is required")
    params = _section_to_dict(data_cfg.get("params"))
    target = data_cfg.get("target")
    if target:
        builder = _resolve_callable(str(target))
        loaders = builder(**params)
    else:
        name = data_cfg.get("name")
        if not name:
            raise ValueError("data configuration must provide 'target' or 'name'")
        loaders = build_registered_dataset(str(name), **params)
    if isinstance(loaders, tuple) and len(loaders) == 3:
        return loaders  # type: ignore[return-value]
    return loaders, None

x__resolve_dataloaders__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_dataloaders__mutmut_1': x__resolve_dataloaders__mutmut_1, 
    'x__resolve_dataloaders__mutmut_2': x__resolve_dataloaders__mutmut_2, 
    'x__resolve_dataloaders__mutmut_3': x__resolve_dataloaders__mutmut_3, 
    'x__resolve_dataloaders__mutmut_4': x__resolve_dataloaders__mutmut_4, 
    'x__resolve_dataloaders__mutmut_5': x__resolve_dataloaders__mutmut_5, 
    'x__resolve_dataloaders__mutmut_6': x__resolve_dataloaders__mutmut_6, 
    'x__resolve_dataloaders__mutmut_7': x__resolve_dataloaders__mutmut_7, 
    'x__resolve_dataloaders__mutmut_8': x__resolve_dataloaders__mutmut_8, 
    'x__resolve_dataloaders__mutmut_9': x__resolve_dataloaders__mutmut_9, 
    'x__resolve_dataloaders__mutmut_10': x__resolve_dataloaders__mutmut_10, 
    'x__resolve_dataloaders__mutmut_11': x__resolve_dataloaders__mutmut_11, 
    'x__resolve_dataloaders__mutmut_12': x__resolve_dataloaders__mutmut_12, 
    'x__resolve_dataloaders__mutmut_13': x__resolve_dataloaders__mutmut_13, 
    'x__resolve_dataloaders__mutmut_14': x__resolve_dataloaders__mutmut_14, 
    'x__resolve_dataloaders__mutmut_15': x__resolve_dataloaders__mutmut_15, 
    'x__resolve_dataloaders__mutmut_16': x__resolve_dataloaders__mutmut_16, 
    'x__resolve_dataloaders__mutmut_17': x__resolve_dataloaders__mutmut_17, 
    'x__resolve_dataloaders__mutmut_18': x__resolve_dataloaders__mutmut_18, 
    'x__resolve_dataloaders__mutmut_19': x__resolve_dataloaders__mutmut_19, 
    'x__resolve_dataloaders__mutmut_20': x__resolve_dataloaders__mutmut_20, 
    'x__resolve_dataloaders__mutmut_21': x__resolve_dataloaders__mutmut_21, 
    'x__resolve_dataloaders__mutmut_22': x__resolve_dataloaders__mutmut_22, 
    'x__resolve_dataloaders__mutmut_23': x__resolve_dataloaders__mutmut_23, 
    'x__resolve_dataloaders__mutmut_24': x__resolve_dataloaders__mutmut_24, 
    'x__resolve_dataloaders__mutmut_25': x__resolve_dataloaders__mutmut_25, 
    'x__resolve_dataloaders__mutmut_26': x__resolve_dataloaders__mutmut_26, 
    'x__resolve_dataloaders__mutmut_27': x__resolve_dataloaders__mutmut_27, 
    'x__resolve_dataloaders__mutmut_28': x__resolve_dataloaders__mutmut_28, 
    'x__resolve_dataloaders__mutmut_29': x__resolve_dataloaders__mutmut_29, 
    'x__resolve_dataloaders__mutmut_30': x__resolve_dataloaders__mutmut_30, 
    'x__resolve_dataloaders__mutmut_31': x__resolve_dataloaders__mutmut_31, 
    'x__resolve_dataloaders__mutmut_32': x__resolve_dataloaders__mutmut_32, 
    'x__resolve_dataloaders__mutmut_33': x__resolve_dataloaders__mutmut_33
}

def _resolve_dataloaders(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_dataloaders__mutmut_orig, x__resolve_dataloaders__mutmut_mutants, args, kwargs)
    return result 

_resolve_dataloaders.__signature__ = _mutmut_signature(x__resolve_dataloaders__mutmut_orig)
x__resolve_dataloaders__mutmut_orig.__name__ = 'x__resolve_dataloaders'


def x_main__mutmut_orig(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_1(argv: Sequence[str] | None = None) -> int:
    parser = None
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_2(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_3(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="XXRun Codex training via Hydra configXX")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_4(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="run codex training via hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_5(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RUN CODEX TRAINING VIA HYDRA CONFIG")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_6(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument(None, required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_7(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=None, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_8(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help=None)
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_9(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument(required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_10(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_11(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, )
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_12(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("XX--config-pathXX", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_13(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--CONFIG-PATH", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_14(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=False, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_15(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="XXDirectory containing Hydra configsXX")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_16(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="directory containing hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_17(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="DIRECTORY CONTAINING HYDRA CONFIGS")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_18(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        None, default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_19(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default=None, help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_20(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help=None
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_21(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_22(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_23(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_24(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "XX--config-nameXX", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_25(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--CONFIG-NAME", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_26(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="XXtrainXX", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_27(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="TRAIN", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_28(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="XXConfig file name inside the directoryXX"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_29(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_30(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="CONFIG FILE NAME INSIDE THE DIRECTORY"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_31(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        None,
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_32(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs=None,
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_33(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help=None,
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_34(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_35(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_36(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_37(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "XXoverridesXX",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_38(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "OVERRIDES",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_39(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="XX*XX",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_40(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="XXOptional Hydra-style overrides (e.g. trainer.epochs=2)XX",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_41(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="optional hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_42(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="OPTIONAL HYDRA-STYLE OVERRIDES (E.G. TRAINER.EPOCHS=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_43(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = None

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_44(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(None)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_45(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = None

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_46(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(None)

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_47(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides and [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_48(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=None):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_49(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_50(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, ):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_51(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = None

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_52(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=None, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_53(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=None)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_54(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_55(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, )

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_56(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = None
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_57(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(None, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_58(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=None)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_59(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_60(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, )
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_61(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=False)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_62(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_63(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError(None)

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_64(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("XXHydra configuration must resolve to a mappingXX")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_65(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_66(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("HYDRA CONFIGURATION MUST RESOLVE TO A MAPPING")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_67(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = None
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_68(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(None)
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_69(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(None))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_70(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get(None)))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_71(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("XXmodelXX")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_72(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("MODEL")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_73(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = None
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_74(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(None, model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_75(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), None)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_76(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_77(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), )
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_78(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(None), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_79(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get(None)), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_80(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("XXoptimizerXX")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_81(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("OPTIMIZER")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_82(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = None
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_83(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(None)
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_84(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(None))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_85(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get(None)))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_86(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("XXdataXX")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_87(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("DATA")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_88(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = None
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_89(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(None)
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_90(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(None))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_91(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get(None)))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_92(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("XXlossXX")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_93(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("LOSS")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_94(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = None

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_95(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(None)

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_96(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(None))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_97(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get(None)))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_98(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("XXmetricXX")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_99(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("METRIC")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_100(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = None
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_101(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(None)
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_102(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get(None))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_103(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("XXtrainerXX"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_104(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("TRAINER"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_105(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = None
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_106(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(None)
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_107(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get(None))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_108(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("XXloggingXX"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_109(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("LOGGING"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_110(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = None
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_111(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop(None, None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_112(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop(None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_113(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", )
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_114(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("XXloggingXX", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_115(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("LOGGING", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_116(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = None
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_117(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop(None, None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_118(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop(None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_119(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", )
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_120(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("XXcheckpointXX", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_121(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("CHECKPOINT", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_122(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = ""
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_123(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_124(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = None
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_125(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = None
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_126(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                None
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_127(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "XXtrainer.checkpoint configuration must be a mapping or CheckpointConfigXX"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_128(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or checkpointconfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_129(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "TRAINER.CHECKPOINT CONFIGURATION MUST BE A MAPPING OR CHECKPOINTCONFIG"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_130(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = None
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_131(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = None
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_132(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_133(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = None

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_134(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = None
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_135(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get(None)
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_136(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("XXdeviceXX")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_137(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("DEVICE")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_138(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = None

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_139(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=None,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_140(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=None,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_141(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=None,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_142(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=None,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_143(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=None,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_144(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=None,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_145(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=None,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_146(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_147(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_148(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_149(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_150(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_151(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_152(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_153(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_154(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_155(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(None) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_156(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_157(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "XXXX") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 0


def x_main__mutmut_158(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex training via Hydra config")
    parser.add_argument("--config-path", required=True, help="Directory containing Hydra configs")
    parser.add_argument(
        "--config-name", default="train", help="Config file name inside the directory"
    )
    parser.add_argument(
        "overrides",
        nargs="*",
        help="Optional Hydra-style overrides (e.g. trainer.epochs=2)",
    )
    args = parser.parse_args(argv)

    overrides = list(args.overrides or [])

    with initialize_config_dir(version_base=None, config_dir=args.config_path):
        cfg = compose(config_name=args.config_name, overrides=overrides)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(cfg_dict, Mapping):
        raise TypeError("Hydra configuration must resolve to a mapping")

    model = _instantiate_model(_section_to_dict(cfg_dict.get("model")))
    optimizer = _instantiate_optimizer(_section_to_dict(cfg_dict.get("optimizer")), model)
    train_loader, val_loader = _resolve_dataloaders(_section_to_dict(cfg_dict.get("data")))
    loss_fn = _resolve_loss(_section_to_dict(cfg_dict.get("loss")))
    metric_fn = _resolve_metric(_section_to_dict(cfg_dict.get("metric")))

    trainer_section = _section_to_dict(cfg_dict.get("trainer"))
    logging_section = _section_to_dict(cfg_dict.get("logging"))
    logging_cfg = LoggingConfig(**logging_section) if logging_section else LoggingConfig()
    trainer_section.pop("logging", None)
    checkpoint_section = trainer_section.pop("checkpoint", None)
    checkpoint_cfg: CheckpointConfig | None = None
    if checkpoint_section is not None:
        if isinstance(checkpoint_section, CheckpointConfig):
            checkpoint_cfg = checkpoint_section
        elif isinstance(checkpoint_section, Mapping):
            checkpoint_cfg = CheckpointConfig(**checkpoint_section)
        else:
            raise TypeError(
                "trainer.checkpoint configuration must be a mapping or CheckpointConfig"
            )

    trainer_cfg = TrainerConfig(**trainer_section)
    trainer_cfg.logging = logging_cfg
    if checkpoint_cfg is not None:
        trainer_cfg.checkpoint = checkpoint_cfg

    device = cfg_dict.get("device")
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        metric_fn=metric_fn,
        config=trainer_cfg,
        device=str(device) if device not in (None, "") else None,
    )

    try:
        trainer.train()
    finally:
        trainer.close()
    return 1

x_main__mutmut_mutants : ClassVar[MutantDict] = {
'x_main__mutmut_1': x_main__mutmut_1, 
    'x_main__mutmut_2': x_main__mutmut_2, 
    'x_main__mutmut_3': x_main__mutmut_3, 
    'x_main__mutmut_4': x_main__mutmut_4, 
    'x_main__mutmut_5': x_main__mutmut_5, 
    'x_main__mutmut_6': x_main__mutmut_6, 
    'x_main__mutmut_7': x_main__mutmut_7, 
    'x_main__mutmut_8': x_main__mutmut_8, 
    'x_main__mutmut_9': x_main__mutmut_9, 
    'x_main__mutmut_10': x_main__mutmut_10, 
    'x_main__mutmut_11': x_main__mutmut_11, 
    'x_main__mutmut_12': x_main__mutmut_12, 
    'x_main__mutmut_13': x_main__mutmut_13, 
    'x_main__mutmut_14': x_main__mutmut_14, 
    'x_main__mutmut_15': x_main__mutmut_15, 
    'x_main__mutmut_16': x_main__mutmut_16, 
    'x_main__mutmut_17': x_main__mutmut_17, 
    'x_main__mutmut_18': x_main__mutmut_18, 
    'x_main__mutmut_19': x_main__mutmut_19, 
    'x_main__mutmut_20': x_main__mutmut_20, 
    'x_main__mutmut_21': x_main__mutmut_21, 
    'x_main__mutmut_22': x_main__mutmut_22, 
    'x_main__mutmut_23': x_main__mutmut_23, 
    'x_main__mutmut_24': x_main__mutmut_24, 
    'x_main__mutmut_25': x_main__mutmut_25, 
    'x_main__mutmut_26': x_main__mutmut_26, 
    'x_main__mutmut_27': x_main__mutmut_27, 
    'x_main__mutmut_28': x_main__mutmut_28, 
    'x_main__mutmut_29': x_main__mutmut_29, 
    'x_main__mutmut_30': x_main__mutmut_30, 
    'x_main__mutmut_31': x_main__mutmut_31, 
    'x_main__mutmut_32': x_main__mutmut_32, 
    'x_main__mutmut_33': x_main__mutmut_33, 
    'x_main__mutmut_34': x_main__mutmut_34, 
    'x_main__mutmut_35': x_main__mutmut_35, 
    'x_main__mutmut_36': x_main__mutmut_36, 
    'x_main__mutmut_37': x_main__mutmut_37, 
    'x_main__mutmut_38': x_main__mutmut_38, 
    'x_main__mutmut_39': x_main__mutmut_39, 
    'x_main__mutmut_40': x_main__mutmut_40, 
    'x_main__mutmut_41': x_main__mutmut_41, 
    'x_main__mutmut_42': x_main__mutmut_42, 
    'x_main__mutmut_43': x_main__mutmut_43, 
    'x_main__mutmut_44': x_main__mutmut_44, 
    'x_main__mutmut_45': x_main__mutmut_45, 
    'x_main__mutmut_46': x_main__mutmut_46, 
    'x_main__mutmut_47': x_main__mutmut_47, 
    'x_main__mutmut_48': x_main__mutmut_48, 
    'x_main__mutmut_49': x_main__mutmut_49, 
    'x_main__mutmut_50': x_main__mutmut_50, 
    'x_main__mutmut_51': x_main__mutmut_51, 
    'x_main__mutmut_52': x_main__mutmut_52, 
    'x_main__mutmut_53': x_main__mutmut_53, 
    'x_main__mutmut_54': x_main__mutmut_54, 
    'x_main__mutmut_55': x_main__mutmut_55, 
    'x_main__mutmut_56': x_main__mutmut_56, 
    'x_main__mutmut_57': x_main__mutmut_57, 
    'x_main__mutmut_58': x_main__mutmut_58, 
    'x_main__mutmut_59': x_main__mutmut_59, 
    'x_main__mutmut_60': x_main__mutmut_60, 
    'x_main__mutmut_61': x_main__mutmut_61, 
    'x_main__mutmut_62': x_main__mutmut_62, 
    'x_main__mutmut_63': x_main__mutmut_63, 
    'x_main__mutmut_64': x_main__mutmut_64, 
    'x_main__mutmut_65': x_main__mutmut_65, 
    'x_main__mutmut_66': x_main__mutmut_66, 
    'x_main__mutmut_67': x_main__mutmut_67, 
    'x_main__mutmut_68': x_main__mutmut_68, 
    'x_main__mutmut_69': x_main__mutmut_69, 
    'x_main__mutmut_70': x_main__mutmut_70, 
    'x_main__mutmut_71': x_main__mutmut_71, 
    'x_main__mutmut_72': x_main__mutmut_72, 
    'x_main__mutmut_73': x_main__mutmut_73, 
    'x_main__mutmut_74': x_main__mutmut_74, 
    'x_main__mutmut_75': x_main__mutmut_75, 
    'x_main__mutmut_76': x_main__mutmut_76, 
    'x_main__mutmut_77': x_main__mutmut_77, 
    'x_main__mutmut_78': x_main__mutmut_78, 
    'x_main__mutmut_79': x_main__mutmut_79, 
    'x_main__mutmut_80': x_main__mutmut_80, 
    'x_main__mutmut_81': x_main__mutmut_81, 
    'x_main__mutmut_82': x_main__mutmut_82, 
    'x_main__mutmut_83': x_main__mutmut_83, 
    'x_main__mutmut_84': x_main__mutmut_84, 
    'x_main__mutmut_85': x_main__mutmut_85, 
    'x_main__mutmut_86': x_main__mutmut_86, 
    'x_main__mutmut_87': x_main__mutmut_87, 
    'x_main__mutmut_88': x_main__mutmut_88, 
    'x_main__mutmut_89': x_main__mutmut_89, 
    'x_main__mutmut_90': x_main__mutmut_90, 
    'x_main__mutmut_91': x_main__mutmut_91, 
    'x_main__mutmut_92': x_main__mutmut_92, 
    'x_main__mutmut_93': x_main__mutmut_93, 
    'x_main__mutmut_94': x_main__mutmut_94, 
    'x_main__mutmut_95': x_main__mutmut_95, 
    'x_main__mutmut_96': x_main__mutmut_96, 
    'x_main__mutmut_97': x_main__mutmut_97, 
    'x_main__mutmut_98': x_main__mutmut_98, 
    'x_main__mutmut_99': x_main__mutmut_99, 
    'x_main__mutmut_100': x_main__mutmut_100, 
    'x_main__mutmut_101': x_main__mutmut_101, 
    'x_main__mutmut_102': x_main__mutmut_102, 
    'x_main__mutmut_103': x_main__mutmut_103, 
    'x_main__mutmut_104': x_main__mutmut_104, 
    'x_main__mutmut_105': x_main__mutmut_105, 
    'x_main__mutmut_106': x_main__mutmut_106, 
    'x_main__mutmut_107': x_main__mutmut_107, 
    'x_main__mutmut_108': x_main__mutmut_108, 
    'x_main__mutmut_109': x_main__mutmut_109, 
    'x_main__mutmut_110': x_main__mutmut_110, 
    'x_main__mutmut_111': x_main__mutmut_111, 
    'x_main__mutmut_112': x_main__mutmut_112, 
    'x_main__mutmut_113': x_main__mutmut_113, 
    'x_main__mutmut_114': x_main__mutmut_114, 
    'x_main__mutmut_115': x_main__mutmut_115, 
    'x_main__mutmut_116': x_main__mutmut_116, 
    'x_main__mutmut_117': x_main__mutmut_117, 
    'x_main__mutmut_118': x_main__mutmut_118, 
    'x_main__mutmut_119': x_main__mutmut_119, 
    'x_main__mutmut_120': x_main__mutmut_120, 
    'x_main__mutmut_121': x_main__mutmut_121, 
    'x_main__mutmut_122': x_main__mutmut_122, 
    'x_main__mutmut_123': x_main__mutmut_123, 
    'x_main__mutmut_124': x_main__mutmut_124, 
    'x_main__mutmut_125': x_main__mutmut_125, 
    'x_main__mutmut_126': x_main__mutmut_126, 
    'x_main__mutmut_127': x_main__mutmut_127, 
    'x_main__mutmut_128': x_main__mutmut_128, 
    'x_main__mutmut_129': x_main__mutmut_129, 
    'x_main__mutmut_130': x_main__mutmut_130, 
    'x_main__mutmut_131': x_main__mutmut_131, 
    'x_main__mutmut_132': x_main__mutmut_132, 
    'x_main__mutmut_133': x_main__mutmut_133, 
    'x_main__mutmut_134': x_main__mutmut_134, 
    'x_main__mutmut_135': x_main__mutmut_135, 
    'x_main__mutmut_136': x_main__mutmut_136, 
    'x_main__mutmut_137': x_main__mutmut_137, 
    'x_main__mutmut_138': x_main__mutmut_138, 
    'x_main__mutmut_139': x_main__mutmut_139, 
    'x_main__mutmut_140': x_main__mutmut_140, 
    'x_main__mutmut_141': x_main__mutmut_141, 
    'x_main__mutmut_142': x_main__mutmut_142, 
    'x_main__mutmut_143': x_main__mutmut_143, 
    'x_main__mutmut_144': x_main__mutmut_144, 
    'x_main__mutmut_145': x_main__mutmut_145, 
    'x_main__mutmut_146': x_main__mutmut_146, 
    'x_main__mutmut_147': x_main__mutmut_147, 
    'x_main__mutmut_148': x_main__mutmut_148, 
    'x_main__mutmut_149': x_main__mutmut_149, 
    'x_main__mutmut_150': x_main__mutmut_150, 
    'x_main__mutmut_151': x_main__mutmut_151, 
    'x_main__mutmut_152': x_main__mutmut_152, 
    'x_main__mutmut_153': x_main__mutmut_153, 
    'x_main__mutmut_154': x_main__mutmut_154, 
    'x_main__mutmut_155': x_main__mutmut_155, 
    'x_main__mutmut_156': x_main__mutmut_156, 
    'x_main__mutmut_157': x_main__mutmut_157, 
    'x_main__mutmut_158': x_main__mutmut_158
}

def main(*args, **kwargs):
    result = _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs)
    return result 

main.__signature__ = _mutmut_signature(x_main__mutmut_orig)
x_main__mutmut_orig.__name__ = 'x_main'


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
