"""
Seed Utils Module

This module provides functionality for seed utils.

Usage:
    from training.seed_utils import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Utilities for establishing deterministic seeds across common libraries."""


import os
import random
from typing import Any

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover - numpy is optional
    np = None  # type: ignore
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


def x__set_numpy_seed__mutmut_orig(seed: int) -> None:
    if np is None:
        return
    try:
        np.random.seed(seed)
    except (AttributeError, RuntimeError):
        # numpy can raise when compiled without RNG support
        pass


def x__set_numpy_seed__mutmut_1(seed: int) -> None:
    if np is not None:
        return
    try:
        np.random.seed(seed)
    except (AttributeError, RuntimeError):
        # numpy can raise when compiled without RNG support
        pass


def x__set_numpy_seed__mutmut_2(seed: int) -> None:
    if np is None:
        return
    try:
        np.random.seed(None)
    except (AttributeError, RuntimeError):
        # numpy can raise when compiled without RNG support
        pass

x__set_numpy_seed__mutmut_mutants : ClassVar[MutantDict] = {
'x__set_numpy_seed__mutmut_1': x__set_numpy_seed__mutmut_1, 
    'x__set_numpy_seed__mutmut_2': x__set_numpy_seed__mutmut_2
}

def _set_numpy_seed(*args, **kwargs):
    result = _mutmut_trampoline(x__set_numpy_seed__mutmut_orig, x__set_numpy_seed__mutmut_mutants, args, kwargs)
    return result 

_set_numpy_seed.__signature__ = _mutmut_signature(x__set_numpy_seed__mutmut_orig)
x__set_numpy_seed__mutmut_orig.__name__ = 'x__set_numpy_seed'


def x__set_torch_seed__mutmut_orig(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_1(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = None
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_2(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"XXavailableXX": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_3(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"AVAILABLE": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_4(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": True}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_5(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(None)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_6(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(None)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_7(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = None
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_8(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["XXavailableXX"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_9(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["AVAILABLE"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_10(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = False
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_11(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = None

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_12(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["XXdeterministicXX"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_13(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["DETERMINISTIC"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_14(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(None)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_15(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = None
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_16(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = False
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_17(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(None, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_18(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=None)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_19(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_20(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, )  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_21(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(False, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_22(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=True)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_23(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(None)
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_24(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(None, exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_25(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=None)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_26(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_27(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", )
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_28(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=False)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_29(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(None)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_30(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(False)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_31(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(None)
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_32(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(None, exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_33(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=None)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_34(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_35(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", )
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_36(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=False)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_37(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = None

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_38(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "XXunsupportedXX"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_39(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "UNSUPPORTED"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_40(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_41(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not False:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_42(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = None

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_43(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["XXdeterministicXX"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_44(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["DETERMINISTIC"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_45(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = None
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_46(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = True
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_47(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = None
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_48(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = False
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_49(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = None
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_50(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["XXcudnnXX"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_51(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["CUDNN"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_52(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"XXbenchmarkXX": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_53(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"BENCHMARK": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_54(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": True, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_55(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "XXdeterministicXX": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_56(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "DETERMINISTIC": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_57(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": False}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_58(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = None
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_59(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["XXcudnnXX"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_60(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["CUDNN"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_61(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "XXunavailableXX"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_62(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "UNAVAILABLE"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_63(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(None)
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_64(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(None, exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_65(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=None)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_66(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(exc_info=True)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_67(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", )
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_68(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=False)
        torch_info = {"available": False}

    return torch_info


def x__set_torch_seed__mutmut_69(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = None

    return torch_info


def x__set_torch_seed__mutmut_70(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"XXavailableXX": False}

    return torch_info


def x__set_torch_seed__mutmut_71(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"AVAILABLE": False}

    return torch_info


def x__set_torch_seed__mutmut_72(seed: int, deterministic: bool) -> dict[str, Any]:
    torch_info: dict[str, Any] = {"available": False}
    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        try:
            torch.cuda.manual_seed_all(seed)
        except (RuntimeError, AttributeError):
            # CUDA might be unavailable; ignore in that case
            pass

        torch_info["available"] = True
        torch_info["deterministic"] = bool(deterministic)

        if deterministic:
            deterministic_state: Any = True
            try:
                torch.use_deterministic_algorithms(True, warn_only=False)  # type: ignore[attr-defined]
            except TypeError as e:
                logger.debug(f"TypeError: {e}")
                logger.warning(f"TypeError: {e}", exc_info=True)
                # Older torch versions accept a single positional argument
                torch.use_deterministic_algorithms(True)  # type: ignore[arg-type]
            except AttributeError as e:
                logger.debug(f"AttributeError: {e}")
                logger.warning(f"AttributeError: {e}", exc_info=True)
                deterministic_state = "unsupported"

            if deterministic_state is not True:
                torch_info["deterministic"] = deterministic_state

            try:
                import torch.backends.cudnn as cudnn  # type: ignore

                cudnn.benchmark = False
                cudnn.deterministic = True
                torch_info["cudnn"] = {"benchmark": False, "deterministic": True}
            except (ImportError, AttributeError):
                torch_info["cudnn"] = "unavailable"
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        torch_info = {"available": True}

    return torch_info

x__set_torch_seed__mutmut_mutants : ClassVar[MutantDict] = {
'x__set_torch_seed__mutmut_1': x__set_torch_seed__mutmut_1, 
    'x__set_torch_seed__mutmut_2': x__set_torch_seed__mutmut_2, 
    'x__set_torch_seed__mutmut_3': x__set_torch_seed__mutmut_3, 
    'x__set_torch_seed__mutmut_4': x__set_torch_seed__mutmut_4, 
    'x__set_torch_seed__mutmut_5': x__set_torch_seed__mutmut_5, 
    'x__set_torch_seed__mutmut_6': x__set_torch_seed__mutmut_6, 
    'x__set_torch_seed__mutmut_7': x__set_torch_seed__mutmut_7, 
    'x__set_torch_seed__mutmut_8': x__set_torch_seed__mutmut_8, 
    'x__set_torch_seed__mutmut_9': x__set_torch_seed__mutmut_9, 
    'x__set_torch_seed__mutmut_10': x__set_torch_seed__mutmut_10, 
    'x__set_torch_seed__mutmut_11': x__set_torch_seed__mutmut_11, 
    'x__set_torch_seed__mutmut_12': x__set_torch_seed__mutmut_12, 
    'x__set_torch_seed__mutmut_13': x__set_torch_seed__mutmut_13, 
    'x__set_torch_seed__mutmut_14': x__set_torch_seed__mutmut_14, 
    'x__set_torch_seed__mutmut_15': x__set_torch_seed__mutmut_15, 
    'x__set_torch_seed__mutmut_16': x__set_torch_seed__mutmut_16, 
    'x__set_torch_seed__mutmut_17': x__set_torch_seed__mutmut_17, 
    'x__set_torch_seed__mutmut_18': x__set_torch_seed__mutmut_18, 
    'x__set_torch_seed__mutmut_19': x__set_torch_seed__mutmut_19, 
    'x__set_torch_seed__mutmut_20': x__set_torch_seed__mutmut_20, 
    'x__set_torch_seed__mutmut_21': x__set_torch_seed__mutmut_21, 
    'x__set_torch_seed__mutmut_22': x__set_torch_seed__mutmut_22, 
    'x__set_torch_seed__mutmut_23': x__set_torch_seed__mutmut_23, 
    'x__set_torch_seed__mutmut_24': x__set_torch_seed__mutmut_24, 
    'x__set_torch_seed__mutmut_25': x__set_torch_seed__mutmut_25, 
    'x__set_torch_seed__mutmut_26': x__set_torch_seed__mutmut_26, 
    'x__set_torch_seed__mutmut_27': x__set_torch_seed__mutmut_27, 
    'x__set_torch_seed__mutmut_28': x__set_torch_seed__mutmut_28, 
    'x__set_torch_seed__mutmut_29': x__set_torch_seed__mutmut_29, 
    'x__set_torch_seed__mutmut_30': x__set_torch_seed__mutmut_30, 
    'x__set_torch_seed__mutmut_31': x__set_torch_seed__mutmut_31, 
    'x__set_torch_seed__mutmut_32': x__set_torch_seed__mutmut_32, 
    'x__set_torch_seed__mutmut_33': x__set_torch_seed__mutmut_33, 
    'x__set_torch_seed__mutmut_34': x__set_torch_seed__mutmut_34, 
    'x__set_torch_seed__mutmut_35': x__set_torch_seed__mutmut_35, 
    'x__set_torch_seed__mutmut_36': x__set_torch_seed__mutmut_36, 
    'x__set_torch_seed__mutmut_37': x__set_torch_seed__mutmut_37, 
    'x__set_torch_seed__mutmut_38': x__set_torch_seed__mutmut_38, 
    'x__set_torch_seed__mutmut_39': x__set_torch_seed__mutmut_39, 
    'x__set_torch_seed__mutmut_40': x__set_torch_seed__mutmut_40, 
    'x__set_torch_seed__mutmut_41': x__set_torch_seed__mutmut_41, 
    'x__set_torch_seed__mutmut_42': x__set_torch_seed__mutmut_42, 
    'x__set_torch_seed__mutmut_43': x__set_torch_seed__mutmut_43, 
    'x__set_torch_seed__mutmut_44': x__set_torch_seed__mutmut_44, 
    'x__set_torch_seed__mutmut_45': x__set_torch_seed__mutmut_45, 
    'x__set_torch_seed__mutmut_46': x__set_torch_seed__mutmut_46, 
    'x__set_torch_seed__mutmut_47': x__set_torch_seed__mutmut_47, 
    'x__set_torch_seed__mutmut_48': x__set_torch_seed__mutmut_48, 
    'x__set_torch_seed__mutmut_49': x__set_torch_seed__mutmut_49, 
    'x__set_torch_seed__mutmut_50': x__set_torch_seed__mutmut_50, 
    'x__set_torch_seed__mutmut_51': x__set_torch_seed__mutmut_51, 
    'x__set_torch_seed__mutmut_52': x__set_torch_seed__mutmut_52, 
    'x__set_torch_seed__mutmut_53': x__set_torch_seed__mutmut_53, 
    'x__set_torch_seed__mutmut_54': x__set_torch_seed__mutmut_54, 
    'x__set_torch_seed__mutmut_55': x__set_torch_seed__mutmut_55, 
    'x__set_torch_seed__mutmut_56': x__set_torch_seed__mutmut_56, 
    'x__set_torch_seed__mutmut_57': x__set_torch_seed__mutmut_57, 
    'x__set_torch_seed__mutmut_58': x__set_torch_seed__mutmut_58, 
    'x__set_torch_seed__mutmut_59': x__set_torch_seed__mutmut_59, 
    'x__set_torch_seed__mutmut_60': x__set_torch_seed__mutmut_60, 
    'x__set_torch_seed__mutmut_61': x__set_torch_seed__mutmut_61, 
    'x__set_torch_seed__mutmut_62': x__set_torch_seed__mutmut_62, 
    'x__set_torch_seed__mutmut_63': x__set_torch_seed__mutmut_63, 
    'x__set_torch_seed__mutmut_64': x__set_torch_seed__mutmut_64, 
    'x__set_torch_seed__mutmut_65': x__set_torch_seed__mutmut_65, 
    'x__set_torch_seed__mutmut_66': x__set_torch_seed__mutmut_66, 
    'x__set_torch_seed__mutmut_67': x__set_torch_seed__mutmut_67, 
    'x__set_torch_seed__mutmut_68': x__set_torch_seed__mutmut_68, 
    'x__set_torch_seed__mutmut_69': x__set_torch_seed__mutmut_69, 
    'x__set_torch_seed__mutmut_70': x__set_torch_seed__mutmut_70, 
    'x__set_torch_seed__mutmut_71': x__set_torch_seed__mutmut_71, 
    'x__set_torch_seed__mutmut_72': x__set_torch_seed__mutmut_72
}

def _set_torch_seed(*args, **kwargs):
    result = _mutmut_trampoline(x__set_torch_seed__mutmut_orig, x__set_torch_seed__mutmut_mutants, args, kwargs)
    return result 

_set_torch_seed.__signature__ = _mutmut_signature(x__set_torch_seed__mutmut_orig)
x__set_torch_seed__mutmut_orig.__name__ = 'x__set_torch_seed'


def x_set_all_seeds__mutmut_orig(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_1(seed: int = 1338, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_2(seed: int = 1337, deterministic: bool = False) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_3(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault(None, str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_4(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", None)
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_5(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault(str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_6(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", )
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_7(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("XXPYTHONHASHSEEDXX", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_8(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("pythonhashseed", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_9(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(None))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_10(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(None)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_11(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(None)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_12(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = None

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_13(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(None, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_14(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, None)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_15(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_16(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, )

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_17(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "XXseedXX": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_18(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "SEED": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_19(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "XXPYTHONHASHSEEDXX": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_20(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_21(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get(None),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_22(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("XXPYTHONHASHSEEDXX"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_23(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("pythonhashseed"),
        "numpy": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_24(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "XXnumpyXX": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_25(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "NUMPY": bool(np is not None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_26(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_27(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is None),
        "torch": torch_info,
    }


def x_set_all_seeds__mutmut_28(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "XXtorchXX": torch_info,
    }


def x_set_all_seeds__mutmut_29(seed: int = 1337, deterministic: bool = True) -> dict[str, Any]:
    """Seed Python, numpy, and torch RNGs consistently.

    Parameters
    ----------
    seed:
        The integer seed value applied to all supported RNGs.
    deterministic:
        When ``True`` attempt to enforce deterministic kernels for torch.

    Returns
    -------
    dict[str, Any]
        A summary describing which backends were affected. This is useful for
        structured logging during smoke tests.
    """

    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    _set_numpy_seed(seed)
    torch_info = _set_torch_seed(seed, deterministic)

    return {
        "seed": seed,
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "numpy": bool(np is not None),
        "TORCH": torch_info,
    }

x_set_all_seeds__mutmut_mutants : ClassVar[MutantDict] = {
'x_set_all_seeds__mutmut_1': x_set_all_seeds__mutmut_1, 
    'x_set_all_seeds__mutmut_2': x_set_all_seeds__mutmut_2, 
    'x_set_all_seeds__mutmut_3': x_set_all_seeds__mutmut_3, 
    'x_set_all_seeds__mutmut_4': x_set_all_seeds__mutmut_4, 
    'x_set_all_seeds__mutmut_5': x_set_all_seeds__mutmut_5, 
    'x_set_all_seeds__mutmut_6': x_set_all_seeds__mutmut_6, 
    'x_set_all_seeds__mutmut_7': x_set_all_seeds__mutmut_7, 
    'x_set_all_seeds__mutmut_8': x_set_all_seeds__mutmut_8, 
    'x_set_all_seeds__mutmut_9': x_set_all_seeds__mutmut_9, 
    'x_set_all_seeds__mutmut_10': x_set_all_seeds__mutmut_10, 
    'x_set_all_seeds__mutmut_11': x_set_all_seeds__mutmut_11, 
    'x_set_all_seeds__mutmut_12': x_set_all_seeds__mutmut_12, 
    'x_set_all_seeds__mutmut_13': x_set_all_seeds__mutmut_13, 
    'x_set_all_seeds__mutmut_14': x_set_all_seeds__mutmut_14, 
    'x_set_all_seeds__mutmut_15': x_set_all_seeds__mutmut_15, 
    'x_set_all_seeds__mutmut_16': x_set_all_seeds__mutmut_16, 
    'x_set_all_seeds__mutmut_17': x_set_all_seeds__mutmut_17, 
    'x_set_all_seeds__mutmut_18': x_set_all_seeds__mutmut_18, 
    'x_set_all_seeds__mutmut_19': x_set_all_seeds__mutmut_19, 
    'x_set_all_seeds__mutmut_20': x_set_all_seeds__mutmut_20, 
    'x_set_all_seeds__mutmut_21': x_set_all_seeds__mutmut_21, 
    'x_set_all_seeds__mutmut_22': x_set_all_seeds__mutmut_22, 
    'x_set_all_seeds__mutmut_23': x_set_all_seeds__mutmut_23, 
    'x_set_all_seeds__mutmut_24': x_set_all_seeds__mutmut_24, 
    'x_set_all_seeds__mutmut_25': x_set_all_seeds__mutmut_25, 
    'x_set_all_seeds__mutmut_26': x_set_all_seeds__mutmut_26, 
    'x_set_all_seeds__mutmut_27': x_set_all_seeds__mutmut_27, 
    'x_set_all_seeds__mutmut_28': x_set_all_seeds__mutmut_28, 
    'x_set_all_seeds__mutmut_29': x_set_all_seeds__mutmut_29
}

def set_all_seeds(*args, **kwargs):
    result = _mutmut_trampoline(x_set_all_seeds__mutmut_orig, x_set_all_seeds__mutmut_mutants, args, kwargs)
    return result 

set_all_seeds.__signature__ = _mutmut_signature(x_set_all_seeds__mutmut_orig)
x_set_all_seeds__mutmut_orig.__name__ = 'x_set_all_seeds'


__all__ = ["set_all_seeds"]
