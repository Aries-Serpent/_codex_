"""
Randomness Module

This module provides functionality for randomness.

Usage:
    from common.randomness import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
import os
import random

logger = logging.getLogger(__name__)


try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

try:
    import torch
except Exception:  # pragma: no cover
    torch = None
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


def x_set_seed__mutmut_orig(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_1(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is not None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_2(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = None

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_3(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(None)

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_4(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get(None, "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_5(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", None))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_6(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_7(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", ))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_8(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("XXSEEDXX", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_9(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("seed", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_10(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "XX1337XX"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_11(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(None)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_12(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_13(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(None)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_14(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_15(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = None
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_16(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(None, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_17(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, None, None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_18(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr("manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_19(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_20(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", )
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_21(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "XXmanual_seedXX", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_22(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "MANUAL_SEED", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_23(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = ""

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_24(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_25(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(None)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_26(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug(None, exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_27(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", None)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_28(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug(exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_29(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", )
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_30(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("XXUnable to invoke torch.manual_seed: %sXX", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_31(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_32(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("UNABLE TO INVOKE TORCH.MANUAL_SEED: %S", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_33(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = None
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_34(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(None, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_35(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, None, None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_36(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr("cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_37(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_38(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", )
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_39(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "XXcudaXX", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_40(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "CUDA", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_41(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = ""

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_42(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_43(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(None, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_44(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, None, lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_45(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", None)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_46(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr("is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_47(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_48(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", )():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_49(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "XXis_availableXX", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_50(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "IS_AVAILABLE", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_51(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: None)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_52(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: True)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_53(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = None
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_54(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(None, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_55(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, None, None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_56(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr("manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_57(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_58(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", )
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_59(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "XXmanual_seed_allXX", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_60(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "MANUAL_SEED_ALL", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_61(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(None):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_62(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(None)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_63(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug(None, exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_64(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", None)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_65(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug(exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_66(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", )

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_67(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("XXUnable to configure torch.cuda seeds: %sXX", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_68(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_69(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("UNABLE TO CONFIGURE TORCH.CUDA SEEDS: %S", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_70(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = None
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_71(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(None, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_72(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, None, None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_73(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr("backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_74(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_75(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", )
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_76(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "XXbackendsXX", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_77(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "BACKENDS", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_78(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = ""

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_79(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_80(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = None  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_81(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = False  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_82(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = None  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_83(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = True  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_84(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(None)
                        logger.debug("Unable to set CuDNN deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_85(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug(None, exc)

    return seed


def x_set_seed__mutmut_86(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", None)

    return seed


def x_set_seed__mutmut_87(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug(exc)

    return seed


def x_set_seed__mutmut_88(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("Unable to set CuDNN deterministic flags: %s", )

    return seed


def x_set_seed__mutmut_89(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("XXUnable to set CuDNN deterministic flags: %sXX", exc)

    return seed


def x_set_seed__mutmut_90(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("unable to set cudnn deterministic flags: %s", exc)

    return seed


def x_set_seed__mutmut_91(seed: int | None) -> int:
    """
    Set process-wide random seeds for Python, NumPy, and PyTorch (if available).
    Returns the effective seed used.
    """

    if seed is None:
        seed = int(os.environ.get("SEED", "1337"))

    random.seed(seed)

    if np is not None:
        np.random.seed(seed)

    if torch is not None:
        try:
            manual_seed = getattr(torch, "manual_seed", None)
        except (ImportError, AttributeError):
            manual_seed = None

        if manual_seed is not None:
            try:
                manual_seed(seed)
            except Exception as exc:  # pragma: no cover - fallback logging only
                logger.debug("Unable to invoke torch.manual_seed: %s", exc)
            else:
                try:
                    cuda_module = getattr(torch, "cuda", None)
                except (ImportError, AttributeError):
                    cuda_module = None

                if cuda_module is not None:
                    try:
                        if getattr(cuda_module, "is_available", lambda: False)():
                            manual_seed_all = getattr(cuda_module, "manual_seed_all", None)
                            if callable(manual_seed_all):
                                manual_seed_all(seed)
                    except Exception as exc:  # pragma: no cover - fallback logging only
                        logger.debug("Unable to configure torch.cuda seeds: %s", exc)

                try:
                    backends = getattr(torch, "backends", None)
                except (ImportError, AttributeError):
                    backends = None

                if backends is not None:
                    try:
                        backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                        backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                    except Exception as exc:
                        logger.debug(f"Exception: {exc}")
                        logger.debug("UNABLE TO SET CUDNN DETERMINISTIC FLAGS: %S", exc)

    return seed

x_set_seed__mutmut_mutants : ClassVar[MutantDict] = {
'x_set_seed__mutmut_1': x_set_seed__mutmut_1, 
    'x_set_seed__mutmut_2': x_set_seed__mutmut_2, 
    'x_set_seed__mutmut_3': x_set_seed__mutmut_3, 
    'x_set_seed__mutmut_4': x_set_seed__mutmut_4, 
    'x_set_seed__mutmut_5': x_set_seed__mutmut_5, 
    'x_set_seed__mutmut_6': x_set_seed__mutmut_6, 
    'x_set_seed__mutmut_7': x_set_seed__mutmut_7, 
    'x_set_seed__mutmut_8': x_set_seed__mutmut_8, 
    'x_set_seed__mutmut_9': x_set_seed__mutmut_9, 
    'x_set_seed__mutmut_10': x_set_seed__mutmut_10, 
    'x_set_seed__mutmut_11': x_set_seed__mutmut_11, 
    'x_set_seed__mutmut_12': x_set_seed__mutmut_12, 
    'x_set_seed__mutmut_13': x_set_seed__mutmut_13, 
    'x_set_seed__mutmut_14': x_set_seed__mutmut_14, 
    'x_set_seed__mutmut_15': x_set_seed__mutmut_15, 
    'x_set_seed__mutmut_16': x_set_seed__mutmut_16, 
    'x_set_seed__mutmut_17': x_set_seed__mutmut_17, 
    'x_set_seed__mutmut_18': x_set_seed__mutmut_18, 
    'x_set_seed__mutmut_19': x_set_seed__mutmut_19, 
    'x_set_seed__mutmut_20': x_set_seed__mutmut_20, 
    'x_set_seed__mutmut_21': x_set_seed__mutmut_21, 
    'x_set_seed__mutmut_22': x_set_seed__mutmut_22, 
    'x_set_seed__mutmut_23': x_set_seed__mutmut_23, 
    'x_set_seed__mutmut_24': x_set_seed__mutmut_24, 
    'x_set_seed__mutmut_25': x_set_seed__mutmut_25, 
    'x_set_seed__mutmut_26': x_set_seed__mutmut_26, 
    'x_set_seed__mutmut_27': x_set_seed__mutmut_27, 
    'x_set_seed__mutmut_28': x_set_seed__mutmut_28, 
    'x_set_seed__mutmut_29': x_set_seed__mutmut_29, 
    'x_set_seed__mutmut_30': x_set_seed__mutmut_30, 
    'x_set_seed__mutmut_31': x_set_seed__mutmut_31, 
    'x_set_seed__mutmut_32': x_set_seed__mutmut_32, 
    'x_set_seed__mutmut_33': x_set_seed__mutmut_33, 
    'x_set_seed__mutmut_34': x_set_seed__mutmut_34, 
    'x_set_seed__mutmut_35': x_set_seed__mutmut_35, 
    'x_set_seed__mutmut_36': x_set_seed__mutmut_36, 
    'x_set_seed__mutmut_37': x_set_seed__mutmut_37, 
    'x_set_seed__mutmut_38': x_set_seed__mutmut_38, 
    'x_set_seed__mutmut_39': x_set_seed__mutmut_39, 
    'x_set_seed__mutmut_40': x_set_seed__mutmut_40, 
    'x_set_seed__mutmut_41': x_set_seed__mutmut_41, 
    'x_set_seed__mutmut_42': x_set_seed__mutmut_42, 
    'x_set_seed__mutmut_43': x_set_seed__mutmut_43, 
    'x_set_seed__mutmut_44': x_set_seed__mutmut_44, 
    'x_set_seed__mutmut_45': x_set_seed__mutmut_45, 
    'x_set_seed__mutmut_46': x_set_seed__mutmut_46, 
    'x_set_seed__mutmut_47': x_set_seed__mutmut_47, 
    'x_set_seed__mutmut_48': x_set_seed__mutmut_48, 
    'x_set_seed__mutmut_49': x_set_seed__mutmut_49, 
    'x_set_seed__mutmut_50': x_set_seed__mutmut_50, 
    'x_set_seed__mutmut_51': x_set_seed__mutmut_51, 
    'x_set_seed__mutmut_52': x_set_seed__mutmut_52, 
    'x_set_seed__mutmut_53': x_set_seed__mutmut_53, 
    'x_set_seed__mutmut_54': x_set_seed__mutmut_54, 
    'x_set_seed__mutmut_55': x_set_seed__mutmut_55, 
    'x_set_seed__mutmut_56': x_set_seed__mutmut_56, 
    'x_set_seed__mutmut_57': x_set_seed__mutmut_57, 
    'x_set_seed__mutmut_58': x_set_seed__mutmut_58, 
    'x_set_seed__mutmut_59': x_set_seed__mutmut_59, 
    'x_set_seed__mutmut_60': x_set_seed__mutmut_60, 
    'x_set_seed__mutmut_61': x_set_seed__mutmut_61, 
    'x_set_seed__mutmut_62': x_set_seed__mutmut_62, 
    'x_set_seed__mutmut_63': x_set_seed__mutmut_63, 
    'x_set_seed__mutmut_64': x_set_seed__mutmut_64, 
    'x_set_seed__mutmut_65': x_set_seed__mutmut_65, 
    'x_set_seed__mutmut_66': x_set_seed__mutmut_66, 
    'x_set_seed__mutmut_67': x_set_seed__mutmut_67, 
    'x_set_seed__mutmut_68': x_set_seed__mutmut_68, 
    'x_set_seed__mutmut_69': x_set_seed__mutmut_69, 
    'x_set_seed__mutmut_70': x_set_seed__mutmut_70, 
    'x_set_seed__mutmut_71': x_set_seed__mutmut_71, 
    'x_set_seed__mutmut_72': x_set_seed__mutmut_72, 
    'x_set_seed__mutmut_73': x_set_seed__mutmut_73, 
    'x_set_seed__mutmut_74': x_set_seed__mutmut_74, 
    'x_set_seed__mutmut_75': x_set_seed__mutmut_75, 
    'x_set_seed__mutmut_76': x_set_seed__mutmut_76, 
    'x_set_seed__mutmut_77': x_set_seed__mutmut_77, 
    'x_set_seed__mutmut_78': x_set_seed__mutmut_78, 
    'x_set_seed__mutmut_79': x_set_seed__mutmut_79, 
    'x_set_seed__mutmut_80': x_set_seed__mutmut_80, 
    'x_set_seed__mutmut_81': x_set_seed__mutmut_81, 
    'x_set_seed__mutmut_82': x_set_seed__mutmut_82, 
    'x_set_seed__mutmut_83': x_set_seed__mutmut_83, 
    'x_set_seed__mutmut_84': x_set_seed__mutmut_84, 
    'x_set_seed__mutmut_85': x_set_seed__mutmut_85, 
    'x_set_seed__mutmut_86': x_set_seed__mutmut_86, 
    'x_set_seed__mutmut_87': x_set_seed__mutmut_87, 
    'x_set_seed__mutmut_88': x_set_seed__mutmut_88, 
    'x_set_seed__mutmut_89': x_set_seed__mutmut_89, 
    'x_set_seed__mutmut_90': x_set_seed__mutmut_90, 
    'x_set_seed__mutmut_91': x_set_seed__mutmut_91
}

def set_seed(*args, **kwargs):
    result = _mutmut_trampoline(x_set_seed__mutmut_orig, x_set_seed__mutmut_mutants, args, kwargs)
    return result 

set_seed.__signature__ = _mutmut_signature(x_set_seed__mutmut_orig)
x_set_seed__mutmut_orig.__name__ = 'x_set_seed'
