"""
Codex CLI Module — Unified Command-Line Interface

AI_AGENT_HINTS:
- Canonical import (Click legacy/test): `from codex.cli import cli`
- Canonical import (Typer modern): `from codex.cli import app`
- Entry point: `from codex.cli import main`
- Implementation locations:
  - Click:  src/codex/cli.py  (exports click.Group named `cli`)
  - Typer:  src/codex/cli/main.py (exports Typer `app` and `main`)
- Design: Facade export surface to keep imports deterministic (no shadowing surprises).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from .main import app, main

# Deterministically load Click CLI group from src/codex/cli.py without shadowing/circular imports.
_codex_root = Path(__file__).resolve().parent.parent  # src/codex
_click_cli_path = _codex_root / "cli.py"
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


def x__load_click_cli__mutmut_orig() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_1() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "XXcodex._cli_clickXX" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_2() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "CODEX._CLI_CLICK" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_3() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" not in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_4() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = None
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_5() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["XXcodex._cli_clickXX"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_6() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["CODEX._CLI_CLICK"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_7() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(None, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_8() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, None, None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_9() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr("cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_10() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_11() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", )

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_12() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "XXcliXX", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_13() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "CLI", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_14() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() and not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_15() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_16() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_17() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = None
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_18() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location(None, _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_19() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", None)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_20() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location(_click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_21() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", )
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_22() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("XXcodex._cli_clickXX", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_23() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("CODEX._CLI_CLICK", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_24() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None and spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_25() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is not None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_26() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is not None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_27() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = None
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_28() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(None)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_29() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_30() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["XXcodex._cli_clickXX"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_31() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["CODEX._CLI_CLICK"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_32() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(None)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


def x__load_click_cli__mutmut_33() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(None, "cli", None)


def x__load_click_cli__mutmut_34() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, None, None)


def x__load_click_cli__mutmut_35() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr("cli", None)


def x__load_click_cli__mutmut_36() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, None)


def x__load_click_cli__mutmut_37() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", )


def x__load_click_cli__mutmut_38() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "XXcliXX", None)


def x__load_click_cli__mutmut_39() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None

    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "CLI", None)

x__load_click_cli__mutmut_mutants : ClassVar[MutantDict] = {
'x__load_click_cli__mutmut_1': x__load_click_cli__mutmut_1, 
    'x__load_click_cli__mutmut_2': x__load_click_cli__mutmut_2, 
    'x__load_click_cli__mutmut_3': x__load_click_cli__mutmut_3, 
    'x__load_click_cli__mutmut_4': x__load_click_cli__mutmut_4, 
    'x__load_click_cli__mutmut_5': x__load_click_cli__mutmut_5, 
    'x__load_click_cli__mutmut_6': x__load_click_cli__mutmut_6, 
    'x__load_click_cli__mutmut_7': x__load_click_cli__mutmut_7, 
    'x__load_click_cli__mutmut_8': x__load_click_cli__mutmut_8, 
    'x__load_click_cli__mutmut_9': x__load_click_cli__mutmut_9, 
    'x__load_click_cli__mutmut_10': x__load_click_cli__mutmut_10, 
    'x__load_click_cli__mutmut_11': x__load_click_cli__mutmut_11, 
    'x__load_click_cli__mutmut_12': x__load_click_cli__mutmut_12, 
    'x__load_click_cli__mutmut_13': x__load_click_cli__mutmut_13, 
    'x__load_click_cli__mutmut_14': x__load_click_cli__mutmut_14, 
    'x__load_click_cli__mutmut_15': x__load_click_cli__mutmut_15, 
    'x__load_click_cli__mutmut_16': x__load_click_cli__mutmut_16, 
    'x__load_click_cli__mutmut_17': x__load_click_cli__mutmut_17, 
    'x__load_click_cli__mutmut_18': x__load_click_cli__mutmut_18, 
    'x__load_click_cli__mutmut_19': x__load_click_cli__mutmut_19, 
    'x__load_click_cli__mutmut_20': x__load_click_cli__mutmut_20, 
    'x__load_click_cli__mutmut_21': x__load_click_cli__mutmut_21, 
    'x__load_click_cli__mutmut_22': x__load_click_cli__mutmut_22, 
    'x__load_click_cli__mutmut_23': x__load_click_cli__mutmut_23, 
    'x__load_click_cli__mutmut_24': x__load_click_cli__mutmut_24, 
    'x__load_click_cli__mutmut_25': x__load_click_cli__mutmut_25, 
    'x__load_click_cli__mutmut_26': x__load_click_cli__mutmut_26, 
    'x__load_click_cli__mutmut_27': x__load_click_cli__mutmut_27, 
    'x__load_click_cli__mutmut_28': x__load_click_cli__mutmut_28, 
    'x__load_click_cli__mutmut_29': x__load_click_cli__mutmut_29, 
    'x__load_click_cli__mutmut_30': x__load_click_cli__mutmut_30, 
    'x__load_click_cli__mutmut_31': x__load_click_cli__mutmut_31, 
    'x__load_click_cli__mutmut_32': x__load_click_cli__mutmut_32, 
    'x__load_click_cli__mutmut_33': x__load_click_cli__mutmut_33, 
    'x__load_click_cli__mutmut_34': x__load_click_cli__mutmut_34, 
    'x__load_click_cli__mutmut_35': x__load_click_cli__mutmut_35, 
    'x__load_click_cli__mutmut_36': x__load_click_cli__mutmut_36, 
    'x__load_click_cli__mutmut_37': x__load_click_cli__mutmut_37, 
    'x__load_click_cli__mutmut_38': x__load_click_cli__mutmut_38, 
    'x__load_click_cli__mutmut_39': x__load_click_cli__mutmut_39
}

def _load_click_cli(*args, **kwargs):
    result = _mutmut_trampoline(x__load_click_cli__mutmut_orig, x__load_click_cli__mutmut_mutants, args, kwargs)
    return result 

_load_click_cli.__signature__ = _mutmut_signature(x__load_click_cli__mutmut_orig)
x__load_click_cli__mutmut_orig.__name__ = 'x__load_click_cli'


cli = _load_click_cli()

# Also expose CLI groups and helpers for testing
logs = None
tokenizer_group = None
repro_group = None
_fix_pool = None

if cli is not None:
    # Import the groups from the loaded module
    _cli_module = sys.modules.get("codex._cli_click")
    if _cli_module:
        logs = getattr(_cli_module, "logs", None)
        tokenizer_group = getattr(_cli_module, "tokenizer_group", None)
        repro_group = getattr(_cli_module, "repro_group", None)
        _fix_pool = getattr(_cli_module, "_fix_pool", None)

__all__ = ["app", "main", "cli", "logs", "tokenizer_group", "repro_group", "_fix_pool"]

if cli is None:
    # Non-fatal import warning, but tests will fail if Click CLI is required.
    import warnings

    warnings.warn(
        f"Click CLI group 'cli' could not be loaded from {_click_cli_path}. "
        "IMPACT: All CLI commands (e.g., 'codex run', 'codex analyze') will be unavailable. "
        "RESOLUTION: Ensure src/codex/cli.py exists and exports a Click 'cli' group. "
        "Check for import errors with: python -c 'from src.codex.cli import cli; print(cli)'",
        ImportWarning,
        stacklevel=2,
    )
