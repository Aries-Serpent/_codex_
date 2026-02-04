"""
Github App Auth Module

This module provides functionality for github app auth.

Usage:
    from integrations.github_app_auth import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import os
import time
from pathlib import Path
from typing import Mapping, MutableMapping
from urllib.parse import urlparse

import requests

try:  # pragma: no cover - optional dependency for JWT minting
    import jwt  # pyjwt
except Exception:  # pragma: no cover - defer error until minting
    jwt = None  # type: ignore


GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")
DEFAULT_API_BASE = GITHUB_API_BASE  # Backwards compatibility alias
API_VERSION = "2022-11-28"
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


class AuthError(RuntimeError):
    """Errors raised when GitHub authentication cannot be established."""


def x__read_private_key__mutmut_orig() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_1() -> str:
    pem = None
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_2() -> str:
    pem = os.getenv(None)
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_3() -> str:
    pem = os.getenv("XXGITHUB_APP_PRIVATE_KEY_PEMXX")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_4() -> str:
    pem = os.getenv("github_app_private_key_pem")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_5() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace(None, "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_6() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", None)
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_7() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_8() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", )
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_9() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("XX\\nXX", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_10() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "XX\nXX")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_11() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = None
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_12() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv(None)
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_13() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("XXGITHUB_APP_PRIVATE_KEY_PATHXX")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_14() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("github_app_private_key_path")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_15() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path or Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_16() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(None).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_17() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding=None)
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_18() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(None).read_text(encoding="utf-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_19() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="XXutf-8XX")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_20() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="UTF-8")
    raise AuthError(
        "Missing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH)."
    )


def x__read_private_key__mutmut_21() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        None
    )


def x__read_private_key__mutmut_22() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "XXMissing GitHub App private key (set GITHUB_APP_PRIVATE_KEY_PEM or GITHUB_APP_PRIVATE_KEY_PATH).XX"
    )


def x__read_private_key__mutmut_23() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "missing github app private key (set github_app_private_key_pem or github_app_private_key_path)."
    )


def x__read_private_key__mutmut_24() -> str:
    pem = os.getenv("GITHUB_APP_PRIVATE_KEY_PEM")
    if pem:
        return pem.replace("\\n", "\n")
    path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    raise AuthError(
        "MISSING GITHUB APP PRIVATE KEY (SET GITHUB_APP_PRIVATE_KEY_PEM OR GITHUB_APP_PRIVATE_KEY_PATH)."
    )

x__read_private_key__mutmut_mutants : ClassVar[MutantDict] = {
'x__read_private_key__mutmut_1': x__read_private_key__mutmut_1, 
    'x__read_private_key__mutmut_2': x__read_private_key__mutmut_2, 
    'x__read_private_key__mutmut_3': x__read_private_key__mutmut_3, 
    'x__read_private_key__mutmut_4': x__read_private_key__mutmut_4, 
    'x__read_private_key__mutmut_5': x__read_private_key__mutmut_5, 
    'x__read_private_key__mutmut_6': x__read_private_key__mutmut_6, 
    'x__read_private_key__mutmut_7': x__read_private_key__mutmut_7, 
    'x__read_private_key__mutmut_8': x__read_private_key__mutmut_8, 
    'x__read_private_key__mutmut_9': x__read_private_key__mutmut_9, 
    'x__read_private_key__mutmut_10': x__read_private_key__mutmut_10, 
    'x__read_private_key__mutmut_11': x__read_private_key__mutmut_11, 
    'x__read_private_key__mutmut_12': x__read_private_key__mutmut_12, 
    'x__read_private_key__mutmut_13': x__read_private_key__mutmut_13, 
    'x__read_private_key__mutmut_14': x__read_private_key__mutmut_14, 
    'x__read_private_key__mutmut_15': x__read_private_key__mutmut_15, 
    'x__read_private_key__mutmut_16': x__read_private_key__mutmut_16, 
    'x__read_private_key__mutmut_17': x__read_private_key__mutmut_17, 
    'x__read_private_key__mutmut_18': x__read_private_key__mutmut_18, 
    'x__read_private_key__mutmut_19': x__read_private_key__mutmut_19, 
    'x__read_private_key__mutmut_20': x__read_private_key__mutmut_20, 
    'x__read_private_key__mutmut_21': x__read_private_key__mutmut_21, 
    'x__read_private_key__mutmut_22': x__read_private_key__mutmut_22, 
    'x__read_private_key__mutmut_23': x__read_private_key__mutmut_23, 
    'x__read_private_key__mutmut_24': x__read_private_key__mutmut_24
}

def _read_private_key(*args, **kwargs):
    result = _mutmut_trampoline(x__read_private_key__mutmut_orig, x__read_private_key__mutmut_mutants, args, kwargs)
    return result 

_read_private_key.__signature__ = _mutmut_signature(x__read_private_key__mutmut_orig)
x__read_private_key__mutmut_orig.__name__ = 'x__read_private_key'


def x_mint_app_jwt__mutmut_orig(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_1(app_id: str | int, ttl: int = 541) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_2(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is not None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_3(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError(None)
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_4(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("XXpyjwt is required to mint an App JWT (pip install pyjwt).XX")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_5(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an app jwt (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_6(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("PYJWT IS REQUIRED TO MINT AN APP JWT (PIP INSTALL PYJWT).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_7(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = None
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_8(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(None)
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_9(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = None
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_10(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"XXiatXX": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_11(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"IAT": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_12(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now + 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_13(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 61, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_14(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "XXexpXX": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_15(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "EXP": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_16(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now - ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_17(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "XXissXX": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_18(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "ISS": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_19(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(None)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_20(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = None
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_21(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(None, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_22(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, None, algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_23(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm=None)
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_24(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(_read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_25(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, algorithm="RS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_26(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), )
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_27(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="XXRS256XX")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_28(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="rs256")
    return token if isinstance(token, str) else token.decode("utf-8")


def x_mint_app_jwt__mutmut_29(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode(None)


def x_mint_app_jwt__mutmut_30(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("XXutf-8XX")


def x_mint_app_jwt__mutmut_31(app_id: str | int, ttl: int = 540) -> str:
    """Mint a short-lived GitHub App JWT (Bearer) for authenticating as the App."""

    if jwt is None:
        raise AuthError("pyjwt is required to mint an App JWT (pip install pyjwt).")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + ttl, "iss": str(app_id)}
    token = jwt.encode(payload, _read_private_key(), algorithm="RS256")
    return token if isinstance(token, str) else token.decode("UTF-8")

x_mint_app_jwt__mutmut_mutants : ClassVar[MutantDict] = {
'x_mint_app_jwt__mutmut_1': x_mint_app_jwt__mutmut_1, 
    'x_mint_app_jwt__mutmut_2': x_mint_app_jwt__mutmut_2, 
    'x_mint_app_jwt__mutmut_3': x_mint_app_jwt__mutmut_3, 
    'x_mint_app_jwt__mutmut_4': x_mint_app_jwt__mutmut_4, 
    'x_mint_app_jwt__mutmut_5': x_mint_app_jwt__mutmut_5, 
    'x_mint_app_jwt__mutmut_6': x_mint_app_jwt__mutmut_6, 
    'x_mint_app_jwt__mutmut_7': x_mint_app_jwt__mutmut_7, 
    'x_mint_app_jwt__mutmut_8': x_mint_app_jwt__mutmut_8, 
    'x_mint_app_jwt__mutmut_9': x_mint_app_jwt__mutmut_9, 
    'x_mint_app_jwt__mutmut_10': x_mint_app_jwt__mutmut_10, 
    'x_mint_app_jwt__mutmut_11': x_mint_app_jwt__mutmut_11, 
    'x_mint_app_jwt__mutmut_12': x_mint_app_jwt__mutmut_12, 
    'x_mint_app_jwt__mutmut_13': x_mint_app_jwt__mutmut_13, 
    'x_mint_app_jwt__mutmut_14': x_mint_app_jwt__mutmut_14, 
    'x_mint_app_jwt__mutmut_15': x_mint_app_jwt__mutmut_15, 
    'x_mint_app_jwt__mutmut_16': x_mint_app_jwt__mutmut_16, 
    'x_mint_app_jwt__mutmut_17': x_mint_app_jwt__mutmut_17, 
    'x_mint_app_jwt__mutmut_18': x_mint_app_jwt__mutmut_18, 
    'x_mint_app_jwt__mutmut_19': x_mint_app_jwt__mutmut_19, 
    'x_mint_app_jwt__mutmut_20': x_mint_app_jwt__mutmut_20, 
    'x_mint_app_jwt__mutmut_21': x_mint_app_jwt__mutmut_21, 
    'x_mint_app_jwt__mutmut_22': x_mint_app_jwt__mutmut_22, 
    'x_mint_app_jwt__mutmut_23': x_mint_app_jwt__mutmut_23, 
    'x_mint_app_jwt__mutmut_24': x_mint_app_jwt__mutmut_24, 
    'x_mint_app_jwt__mutmut_25': x_mint_app_jwt__mutmut_25, 
    'x_mint_app_jwt__mutmut_26': x_mint_app_jwt__mutmut_26, 
    'x_mint_app_jwt__mutmut_27': x_mint_app_jwt__mutmut_27, 
    'x_mint_app_jwt__mutmut_28': x_mint_app_jwt__mutmut_28, 
    'x_mint_app_jwt__mutmut_29': x_mint_app_jwt__mutmut_29, 
    'x_mint_app_jwt__mutmut_30': x_mint_app_jwt__mutmut_30, 
    'x_mint_app_jwt__mutmut_31': x_mint_app_jwt__mutmut_31
}

def mint_app_jwt(*args, **kwargs):
    result = _mutmut_trampoline(x_mint_app_jwt__mutmut_orig, x_mint_app_jwt__mutmut_mutants, args, kwargs)
    return result 

mint_app_jwt.__signature__ = _mutmut_signature(x_mint_app_jwt__mutmut_orig)
x_mint_app_jwt__mutmut_orig.__name__ = 'x_mint_app_jwt'


def x_exchange_installation_token__mutmut_orig(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_1(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = None
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_2(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip(None)}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_3(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.lstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_4(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('XX/XX')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_5(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = None
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_6(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "XXAuthorizationXX": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_7(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_8(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "AUTHORIZATION": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_9(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "XXAcceptXX": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_10(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_11(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "ACCEPT": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_12(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "XXapplication/vnd.github+jsonXX",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_13(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "APPLICATION/VND.GITHUB+JSON",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_14(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "XXX-GitHub-Api-VersionXX": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_15(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "x-github-api-version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_16(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GITHUB-API-VERSION": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_17(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = None
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_18(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(None, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_19(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=None, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_20(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=None)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_21(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_22(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_23(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, )
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_24(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=16)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_25(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code == 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_26(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 202:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_27(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(None)
    data = resp.json()
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_28(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = None
    return data["token"], data.get("expires_at")


def x_exchange_installation_token__mutmut_29(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["XXtokenXX"], data.get("expires_at")


def x_exchange_installation_token__mutmut_30(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["TOKEN"], data.get("expires_at")


def x_exchange_installation_token__mutmut_31(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get(None)


def x_exchange_installation_token__mutmut_32(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("XXexpires_atXX")


def x_exchange_installation_token__mutmut_33(app_jwt: str, installation_id: str | int) -> tuple[str, str | None]:
    url = f"{GITHUB_API_BASE.rstrip('/')}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    resp = requests.post(url, headers=headers, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Installation token exchange failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data["token"], data.get("EXPIRES_AT")

x_exchange_installation_token__mutmut_mutants : ClassVar[MutantDict] = {
'x_exchange_installation_token__mutmut_1': x_exchange_installation_token__mutmut_1, 
    'x_exchange_installation_token__mutmut_2': x_exchange_installation_token__mutmut_2, 
    'x_exchange_installation_token__mutmut_3': x_exchange_installation_token__mutmut_3, 
    'x_exchange_installation_token__mutmut_4': x_exchange_installation_token__mutmut_4, 
    'x_exchange_installation_token__mutmut_5': x_exchange_installation_token__mutmut_5, 
    'x_exchange_installation_token__mutmut_6': x_exchange_installation_token__mutmut_6, 
    'x_exchange_installation_token__mutmut_7': x_exchange_installation_token__mutmut_7, 
    'x_exchange_installation_token__mutmut_8': x_exchange_installation_token__mutmut_8, 
    'x_exchange_installation_token__mutmut_9': x_exchange_installation_token__mutmut_9, 
    'x_exchange_installation_token__mutmut_10': x_exchange_installation_token__mutmut_10, 
    'x_exchange_installation_token__mutmut_11': x_exchange_installation_token__mutmut_11, 
    'x_exchange_installation_token__mutmut_12': x_exchange_installation_token__mutmut_12, 
    'x_exchange_installation_token__mutmut_13': x_exchange_installation_token__mutmut_13, 
    'x_exchange_installation_token__mutmut_14': x_exchange_installation_token__mutmut_14, 
    'x_exchange_installation_token__mutmut_15': x_exchange_installation_token__mutmut_15, 
    'x_exchange_installation_token__mutmut_16': x_exchange_installation_token__mutmut_16, 
    'x_exchange_installation_token__mutmut_17': x_exchange_installation_token__mutmut_17, 
    'x_exchange_installation_token__mutmut_18': x_exchange_installation_token__mutmut_18, 
    'x_exchange_installation_token__mutmut_19': x_exchange_installation_token__mutmut_19, 
    'x_exchange_installation_token__mutmut_20': x_exchange_installation_token__mutmut_20, 
    'x_exchange_installation_token__mutmut_21': x_exchange_installation_token__mutmut_21, 
    'x_exchange_installation_token__mutmut_22': x_exchange_installation_token__mutmut_22, 
    'x_exchange_installation_token__mutmut_23': x_exchange_installation_token__mutmut_23, 
    'x_exchange_installation_token__mutmut_24': x_exchange_installation_token__mutmut_24, 
    'x_exchange_installation_token__mutmut_25': x_exchange_installation_token__mutmut_25, 
    'x_exchange_installation_token__mutmut_26': x_exchange_installation_token__mutmut_26, 
    'x_exchange_installation_token__mutmut_27': x_exchange_installation_token__mutmut_27, 
    'x_exchange_installation_token__mutmut_28': x_exchange_installation_token__mutmut_28, 
    'x_exchange_installation_token__mutmut_29': x_exchange_installation_token__mutmut_29, 
    'x_exchange_installation_token__mutmut_30': x_exchange_installation_token__mutmut_30, 
    'x_exchange_installation_token__mutmut_31': x_exchange_installation_token__mutmut_31, 
    'x_exchange_installation_token__mutmut_32': x_exchange_installation_token__mutmut_32, 
    'x_exchange_installation_token__mutmut_33': x_exchange_installation_token__mutmut_33
}

def exchange_installation_token(*args, **kwargs):
    result = _mutmut_trampoline(x_exchange_installation_token__mutmut_orig, x_exchange_installation_token__mutmut_mutants, args, kwargs)
    return result 

exchange_installation_token.__signature__ = _mutmut_signature(x_exchange_installation_token__mutmut_orig)
x_exchange_installation_token__mutmut_orig.__name__ = 'x_exchange_installation_token'


def x_create_runner_registration_token__mutmut_orig(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_1(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo or not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_2(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_3(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_4(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError(None)
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_5(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("XXSpecify either repo=<name> or org=<name>.XX")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_6(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_7(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("SPECIFY EITHER REPO=<NAME> OR ORG=<NAME>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_8(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo or not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_9(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_10(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError(None)
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_11(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("XX--owner is required when specifying --repo.XX")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_12(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--OWNER IS REQUIRED WHEN SPECIFYING --REPO.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_13(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = None
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_14(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        None
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_15(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "XXAuthorizationXX": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_16(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_17(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "AUTHORIZATION": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_18(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "XXAcceptXX": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_19(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_20(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "ACCEPT": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_21(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "XXapplication/vnd.github+jsonXX",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_22(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "APPLICATION/VND.GITHUB+JSON",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_23(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "XXX-GitHub-Api-VersionXX": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_24(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "x-github-api-version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_25(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GITHUB-API-VERSION": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_26(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = None
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_27(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = None
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_28(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = None
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_29(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = None
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_30(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(None, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_31(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=None)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_32(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_33(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, )
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_34(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=16)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_35(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code == 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_36(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 202:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_37(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(None)
    return resp.json()["token"]


def x_create_runner_registration_token__mutmut_38(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["XXtokenXX"]


def x_create_runner_registration_token__mutmut_39(
    installation_token: str, *, owner: str, repo: str | None = None, org: str | None = None
) -> str:
    """Create a short-lived registration token for a self-hosted runner."""

    if not repo and not org:
        raise ValueError("Specify either repo=<name> or org=<name>.")
    if repo and not owner:
        raise ValueError("--owner is required when specifying --repo.")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"token {installation_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
    if repo:
        path = f"/repos/{owner}/{repo}/actions/runners/registration-token"
    else:
        path = f"/orgs/{org}/actions/runners/registration-token"
    url = f"{GITHUB_API_BASE}{path}"
    resp = session.post(url, timeout=15)
    if resp.status_code != 201:
        raise AuthError(f"Registration token creation failed: {resp.status_code} {resp.text}")
    return resp.json()["TOKEN"]

x_create_runner_registration_token__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_runner_registration_token__mutmut_1': x_create_runner_registration_token__mutmut_1, 
    'x_create_runner_registration_token__mutmut_2': x_create_runner_registration_token__mutmut_2, 
    'x_create_runner_registration_token__mutmut_3': x_create_runner_registration_token__mutmut_3, 
    'x_create_runner_registration_token__mutmut_4': x_create_runner_registration_token__mutmut_4, 
    'x_create_runner_registration_token__mutmut_5': x_create_runner_registration_token__mutmut_5, 
    'x_create_runner_registration_token__mutmut_6': x_create_runner_registration_token__mutmut_6, 
    'x_create_runner_registration_token__mutmut_7': x_create_runner_registration_token__mutmut_7, 
    'x_create_runner_registration_token__mutmut_8': x_create_runner_registration_token__mutmut_8, 
    'x_create_runner_registration_token__mutmut_9': x_create_runner_registration_token__mutmut_9, 
    'x_create_runner_registration_token__mutmut_10': x_create_runner_registration_token__mutmut_10, 
    'x_create_runner_registration_token__mutmut_11': x_create_runner_registration_token__mutmut_11, 
    'x_create_runner_registration_token__mutmut_12': x_create_runner_registration_token__mutmut_12, 
    'x_create_runner_registration_token__mutmut_13': x_create_runner_registration_token__mutmut_13, 
    'x_create_runner_registration_token__mutmut_14': x_create_runner_registration_token__mutmut_14, 
    'x_create_runner_registration_token__mutmut_15': x_create_runner_registration_token__mutmut_15, 
    'x_create_runner_registration_token__mutmut_16': x_create_runner_registration_token__mutmut_16, 
    'x_create_runner_registration_token__mutmut_17': x_create_runner_registration_token__mutmut_17, 
    'x_create_runner_registration_token__mutmut_18': x_create_runner_registration_token__mutmut_18, 
    'x_create_runner_registration_token__mutmut_19': x_create_runner_registration_token__mutmut_19, 
    'x_create_runner_registration_token__mutmut_20': x_create_runner_registration_token__mutmut_20, 
    'x_create_runner_registration_token__mutmut_21': x_create_runner_registration_token__mutmut_21, 
    'x_create_runner_registration_token__mutmut_22': x_create_runner_registration_token__mutmut_22, 
    'x_create_runner_registration_token__mutmut_23': x_create_runner_registration_token__mutmut_23, 
    'x_create_runner_registration_token__mutmut_24': x_create_runner_registration_token__mutmut_24, 
    'x_create_runner_registration_token__mutmut_25': x_create_runner_registration_token__mutmut_25, 
    'x_create_runner_registration_token__mutmut_26': x_create_runner_registration_token__mutmut_26, 
    'x_create_runner_registration_token__mutmut_27': x_create_runner_registration_token__mutmut_27, 
    'x_create_runner_registration_token__mutmut_28': x_create_runner_registration_token__mutmut_28, 
    'x_create_runner_registration_token__mutmut_29': x_create_runner_registration_token__mutmut_29, 
    'x_create_runner_registration_token__mutmut_30': x_create_runner_registration_token__mutmut_30, 
    'x_create_runner_registration_token__mutmut_31': x_create_runner_registration_token__mutmut_31, 
    'x_create_runner_registration_token__mutmut_32': x_create_runner_registration_token__mutmut_32, 
    'x_create_runner_registration_token__mutmut_33': x_create_runner_registration_token__mutmut_33, 
    'x_create_runner_registration_token__mutmut_34': x_create_runner_registration_token__mutmut_34, 
    'x_create_runner_registration_token__mutmut_35': x_create_runner_registration_token__mutmut_35, 
    'x_create_runner_registration_token__mutmut_36': x_create_runner_registration_token__mutmut_36, 
    'x_create_runner_registration_token__mutmut_37': x_create_runner_registration_token__mutmut_37, 
    'x_create_runner_registration_token__mutmut_38': x_create_runner_registration_token__mutmut_38, 
    'x_create_runner_registration_token__mutmut_39': x_create_runner_registration_token__mutmut_39
}

def create_runner_registration_token(*args, **kwargs):
    result = _mutmut_trampoline(x_create_runner_registration_token__mutmut_orig, x_create_runner_registration_token__mutmut_mutants, args, kwargs)
    return result 

create_runner_registration_token.__signature__ = _mutmut_signature(x_create_runner_registration_token__mutmut_orig)
x_create_runner_registration_token__mutmut_orig.__name__ = 'x_create_runner_registration_token'


def x__github_api_host__mutmut_orig(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_1(api_base: str) -> str:
    parsed = None
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_2(api_base: str) -> str:
    parsed = urlparse(None)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_3(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = None
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_4(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("XXhttps://XX", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_5(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("HTTPS://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_6(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "XXhttp://XX"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_7(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "HTTP://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_8(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(None):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_9(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = None
            break
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_10(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            return
    return stripped.split("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_11(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] and "api.github.com"


def x__github_api_host__mutmut_12(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split(None, 1)[0] or "api.github.com"


def x__github_api_host__mutmut_13(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", None)[0] or "api.github.com"


def x__github_api_host__mutmut_14(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split(1)[0] or "api.github.com"


def x__github_api_host__mutmut_15(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", )[0] or "api.github.com"


def x__github_api_host__mutmut_16(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.rsplit("/", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_17(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("XX/XX", 1)[0] or "api.github.com"


def x__github_api_host__mutmut_18(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 2)[0] or "api.github.com"


def x__github_api_host__mutmut_19(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[1] or "api.github.com"


def x__github_api_host__mutmut_20(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "XXapi.github.comXX"


def x__github_api_host__mutmut_21(api_base: str) -> str:
    parsed = urlparse(api_base)
    if parsed.hostname:
        return parsed.hostname
    stripped = api_base
    for prefix in ("https://", "http://"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped.split("/", 1)[0] or "API.GITHUB.COM"

x__github_api_host__mutmut_mutants : ClassVar[MutantDict] = {
'x__github_api_host__mutmut_1': x__github_api_host__mutmut_1, 
    'x__github_api_host__mutmut_2': x__github_api_host__mutmut_2, 
    'x__github_api_host__mutmut_3': x__github_api_host__mutmut_3, 
    'x__github_api_host__mutmut_4': x__github_api_host__mutmut_4, 
    'x__github_api_host__mutmut_5': x__github_api_host__mutmut_5, 
    'x__github_api_host__mutmut_6': x__github_api_host__mutmut_6, 
    'x__github_api_host__mutmut_7': x__github_api_host__mutmut_7, 
    'x__github_api_host__mutmut_8': x__github_api_host__mutmut_8, 
    'x__github_api_host__mutmut_9': x__github_api_host__mutmut_9, 
    'x__github_api_host__mutmut_10': x__github_api_host__mutmut_10, 
    'x__github_api_host__mutmut_11': x__github_api_host__mutmut_11, 
    'x__github_api_host__mutmut_12': x__github_api_host__mutmut_12, 
    'x__github_api_host__mutmut_13': x__github_api_host__mutmut_13, 
    'x__github_api_host__mutmut_14': x__github_api_host__mutmut_14, 
    'x__github_api_host__mutmut_15': x__github_api_host__mutmut_15, 
    'x__github_api_host__mutmut_16': x__github_api_host__mutmut_16, 
    'x__github_api_host__mutmut_17': x__github_api_host__mutmut_17, 
    'x__github_api_host__mutmut_18': x__github_api_host__mutmut_18, 
    'x__github_api_host__mutmut_19': x__github_api_host__mutmut_19, 
    'x__github_api_host__mutmut_20': x__github_api_host__mutmut_20, 
    'x__github_api_host__mutmut_21': x__github_api_host__mutmut_21
}

def _github_api_host(*args, **kwargs):
    result = _mutmut_trampoline(x__github_api_host__mutmut_orig, x__github_api_host__mutmut_mutants, args, kwargs)
    return result 

_github_api_host.__signature__ = _mutmut_signature(x__github_api_host__mutmut_orig)
x__github_api_host__mutmut_orig.__name__ = 'x__github_api_host'


def x__allowlisted_hosts__mutmut_orig(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_1(env: Mapping[str, str]) -> set[str]:
    raw = None
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_2(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("CODEX_NET_ALLOWLIST") and ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_3(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") and env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_4(env: Mapping[str, str]) -> set[str]:
    raw = env.get(None) or env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_5(env: Mapping[str, str]) -> set[str]:
    raw = env.get("XXCODEX_ALLOWLIST_HOSTSXX") or env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_6(env: Mapping[str, str]) -> set[str]:
    raw = env.get("codex_allowlist_hosts") or env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_7(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get(None) or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_8(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("XXCODEX_NET_ALLOWLISTXX") or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_9(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("codex_net_allowlist") or ""
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_10(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("CODEX_NET_ALLOWLIST") or "XXXX"
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_11(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().upper() for item in raw.split(",") if item.strip()}


def x__allowlisted_hosts__mutmut_12(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().lower() for item in raw.split(None) if item.strip()}


def x__allowlisted_hosts__mutmut_13(env: Mapping[str, str]) -> set[str]:
    raw = env.get("CODEX_ALLOWLIST_HOSTS") or env.get("CODEX_NET_ALLOWLIST") or ""
    return {item.strip().lower() for item in raw.split("XX,XX") if item.strip()}

x__allowlisted_hosts__mutmut_mutants : ClassVar[MutantDict] = {
'x__allowlisted_hosts__mutmut_1': x__allowlisted_hosts__mutmut_1, 
    'x__allowlisted_hosts__mutmut_2': x__allowlisted_hosts__mutmut_2, 
    'x__allowlisted_hosts__mutmut_3': x__allowlisted_hosts__mutmut_3, 
    'x__allowlisted_hosts__mutmut_4': x__allowlisted_hosts__mutmut_4, 
    'x__allowlisted_hosts__mutmut_5': x__allowlisted_hosts__mutmut_5, 
    'x__allowlisted_hosts__mutmut_6': x__allowlisted_hosts__mutmut_6, 
    'x__allowlisted_hosts__mutmut_7': x__allowlisted_hosts__mutmut_7, 
    'x__allowlisted_hosts__mutmut_8': x__allowlisted_hosts__mutmut_8, 
    'x__allowlisted_hosts__mutmut_9': x__allowlisted_hosts__mutmut_9, 
    'x__allowlisted_hosts__mutmut_10': x__allowlisted_hosts__mutmut_10, 
    'x__allowlisted_hosts__mutmut_11': x__allowlisted_hosts__mutmut_11, 
    'x__allowlisted_hosts__mutmut_12': x__allowlisted_hosts__mutmut_12, 
    'x__allowlisted_hosts__mutmut_13': x__allowlisted_hosts__mutmut_13
}

def _allowlisted_hosts(*args, **kwargs):
    result = _mutmut_trampoline(x__allowlisted_hosts__mutmut_orig, x__allowlisted_hosts__mutmut_mutants, args, kwargs)
    return result 

_allowlisted_hosts.__signature__ = _mutmut_signature(x__allowlisted_hosts__mutmut_orig)
x__allowlisted_hosts__mutmut_orig.__name__ = 'x__allowlisted_hosts'


def x_assert_online_allowlisted__mutmut_orig(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_1(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = None
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_2(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env and os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_3(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = None
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_4(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().upper()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_5(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get(None, "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_6(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", None).strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_7(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_8(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", ).strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_9(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("XXCODEX_NET_MODEXX", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_10(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("codex_net_mode", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_11(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "XXXX").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_12(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode == "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_13(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "XXonline_allowlistXX":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_14(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "ONLINE_ALLOWLIST":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_15(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit(None)

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_16(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("XXCODEX_NET_MODE=online_allowlist required for GitHub API accessXX")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_17(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("codex_net_mode=online_allowlist required for github api access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_18(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=ONLINE_ALLOWLIST REQUIRED FOR GITHUB API ACCESS")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_19(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = None
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_20(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(None)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_21(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_22(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            None
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_23(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "XXCODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub accessXX"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_24(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "codex_allowlist_hosts or codex_net_allowlist must include api.github.com for github access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_25(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS OR CODEX_NET_ALLOWLIST MUST INCLUDE API.GITHUB.COM FOR GITHUB ACCESS"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_26(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = None
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_27(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(None)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_28(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base and GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_29(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.upper() not in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_30(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() in hosts:
        raise SystemExit(
            f"{host} must be present in CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST for GitHub access"
        )


def x_assert_online_allowlisted__mutmut_31(
    *, env: Mapping[str, str] | None = None, api_base: str | None = None
) -> None:
    """Ensure GitHub API access is explicitly allowlisted before networking."""

    env_map: Mapping[str, str] = env or os.environ
    mode = env_map.get("CODEX_NET_MODE", "").strip().lower()
    if mode != "online_allowlist":
        raise SystemExit("CODEX_NET_MODE=online_allowlist required for GitHub API access")

    hosts = _allowlisted_hosts(env_map)
    if not hosts:
        raise SystemExit(
            "CODEX_ALLOWLIST_HOSTS or CODEX_NET_ALLOWLIST must include api.github.com for GitHub access"
        )

    host = _github_api_host(api_base or GITHUB_API_BASE)
    if host.lower() not in hosts:
        raise SystemExit(
            None
        )

x_assert_online_allowlisted__mutmut_mutants : ClassVar[MutantDict] = {
'x_assert_online_allowlisted__mutmut_1': x_assert_online_allowlisted__mutmut_1, 
    'x_assert_online_allowlisted__mutmut_2': x_assert_online_allowlisted__mutmut_2, 
    'x_assert_online_allowlisted__mutmut_3': x_assert_online_allowlisted__mutmut_3, 
    'x_assert_online_allowlisted__mutmut_4': x_assert_online_allowlisted__mutmut_4, 
    'x_assert_online_allowlisted__mutmut_5': x_assert_online_allowlisted__mutmut_5, 
    'x_assert_online_allowlisted__mutmut_6': x_assert_online_allowlisted__mutmut_6, 
    'x_assert_online_allowlisted__mutmut_7': x_assert_online_allowlisted__mutmut_7, 
    'x_assert_online_allowlisted__mutmut_8': x_assert_online_allowlisted__mutmut_8, 
    'x_assert_online_allowlisted__mutmut_9': x_assert_online_allowlisted__mutmut_9, 
    'x_assert_online_allowlisted__mutmut_10': x_assert_online_allowlisted__mutmut_10, 
    'x_assert_online_allowlisted__mutmut_11': x_assert_online_allowlisted__mutmut_11, 
    'x_assert_online_allowlisted__mutmut_12': x_assert_online_allowlisted__mutmut_12, 
    'x_assert_online_allowlisted__mutmut_13': x_assert_online_allowlisted__mutmut_13, 
    'x_assert_online_allowlisted__mutmut_14': x_assert_online_allowlisted__mutmut_14, 
    'x_assert_online_allowlisted__mutmut_15': x_assert_online_allowlisted__mutmut_15, 
    'x_assert_online_allowlisted__mutmut_16': x_assert_online_allowlisted__mutmut_16, 
    'x_assert_online_allowlisted__mutmut_17': x_assert_online_allowlisted__mutmut_17, 
    'x_assert_online_allowlisted__mutmut_18': x_assert_online_allowlisted__mutmut_18, 
    'x_assert_online_allowlisted__mutmut_19': x_assert_online_allowlisted__mutmut_19, 
    'x_assert_online_allowlisted__mutmut_20': x_assert_online_allowlisted__mutmut_20, 
    'x_assert_online_allowlisted__mutmut_21': x_assert_online_allowlisted__mutmut_21, 
    'x_assert_online_allowlisted__mutmut_22': x_assert_online_allowlisted__mutmut_22, 
    'x_assert_online_allowlisted__mutmut_23': x_assert_online_allowlisted__mutmut_23, 
    'x_assert_online_allowlisted__mutmut_24': x_assert_online_allowlisted__mutmut_24, 
    'x_assert_online_allowlisted__mutmut_25': x_assert_online_allowlisted__mutmut_25, 
    'x_assert_online_allowlisted__mutmut_26': x_assert_online_allowlisted__mutmut_26, 
    'x_assert_online_allowlisted__mutmut_27': x_assert_online_allowlisted__mutmut_27, 
    'x_assert_online_allowlisted__mutmut_28': x_assert_online_allowlisted__mutmut_28, 
    'x_assert_online_allowlisted__mutmut_29': x_assert_online_allowlisted__mutmut_29, 
    'x_assert_online_allowlisted__mutmut_30': x_assert_online_allowlisted__mutmut_30, 
    'x_assert_online_allowlisted__mutmut_31': x_assert_online_allowlisted__mutmut_31
}

def assert_online_allowlisted(*args, **kwargs):
    result = _mutmut_trampoline(x_assert_online_allowlisted__mutmut_orig, x_assert_online_allowlisted__mutmut_mutants, args, kwargs)
    return result 

assert_online_allowlisted.__signature__ = _mutmut_signature(x_assert_online_allowlisted__mutmut_orig)
x_assert_online_allowlisted__mutmut_orig.__name__ = 'x_assert_online_allowlisted'


def x_build_auth_header_from_env__mutmut_orig(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_1(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = None

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_2(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env and os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_3(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = None
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_4(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get(None, "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_5(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", None).strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_6(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_7(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", ).strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_8(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("XXGITHUB_TOKENXX", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_9(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("github_token", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_10(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "XXXX").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_11(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = None
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_12(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get(None, "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_13(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", None).strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_14(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_15(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", ).strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_16(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("XXGITHUB_APP_IDXX", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_17(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("github_app_id", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_18(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "XXXX").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_19(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = None
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_20(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get(None, "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_21(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", None).strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_22(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_23(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", ).strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_24(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("XXGITHUB_APP_INSTALLATION_IDXX", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_25(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("github_app_installation_id", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_26(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "XXXX").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_27(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id and not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_28(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_29(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_30(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            None
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_31(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "XXProvide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, XX"
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_32(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "provide github_token or github app credentials (github_app_id, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_33(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "PROVIDE GITHUB_TOKEN OR GITHUB APP CREDENTIALS (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_34(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "XXGITHUB_APP_INSTALLATION_ID, and private key).XX"
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_35(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "github_app_installation_id, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_36(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, AND PRIVATE KEY)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_37(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = None
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_38(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(None)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_39(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = None
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_40(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(None, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_41(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, None)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_42(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_43(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, )
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(exc)) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_44(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(None) from exc

    return f"token {installation_token}"


def x_build_auth_header_from_env__mutmut_45(
    *, env: MutableMapping[str, str] | Mapping[str, str] | None = None
) -> str:
    """Construct an Authorization header using env credentials."""

    env_map: Mapping[str, str] = env or os.environ

    token = env_map.get("GITHUB_TOKEN", "").strip()
    if token:
        return f"token {token}"

    app_id = env_map.get("GITHUB_APP_ID", "").strip()
    installation_id = env_map.get("GITHUB_APP_INSTALLATION_ID", "").strip()
    if not app_id or not installation_id:
        raise SystemExit(
            "Provide GITHUB_TOKEN or GitHub App credentials (GITHUB_APP_ID, "
            "GITHUB_APP_INSTALLATION_ID, and private key)."
        )

    try:
        app_jwt = mint_app_jwt(app_id)
        installation_token, _ = exchange_installation_token(app_jwt, installation_id)
    except AuthError as exc:  # pragma: no cover - network/env errors
        raise SystemExit(str(None)) from exc

    return f"token {installation_token}"

x_build_auth_header_from_env__mutmut_mutants : ClassVar[MutantDict] = {
'x_build_auth_header_from_env__mutmut_1': x_build_auth_header_from_env__mutmut_1, 
    'x_build_auth_header_from_env__mutmut_2': x_build_auth_header_from_env__mutmut_2, 
    'x_build_auth_header_from_env__mutmut_3': x_build_auth_header_from_env__mutmut_3, 
    'x_build_auth_header_from_env__mutmut_4': x_build_auth_header_from_env__mutmut_4, 
    'x_build_auth_header_from_env__mutmut_5': x_build_auth_header_from_env__mutmut_5, 
    'x_build_auth_header_from_env__mutmut_6': x_build_auth_header_from_env__mutmut_6, 
    'x_build_auth_header_from_env__mutmut_7': x_build_auth_header_from_env__mutmut_7, 
    'x_build_auth_header_from_env__mutmut_8': x_build_auth_header_from_env__mutmut_8, 
    'x_build_auth_header_from_env__mutmut_9': x_build_auth_header_from_env__mutmut_9, 
    'x_build_auth_header_from_env__mutmut_10': x_build_auth_header_from_env__mutmut_10, 
    'x_build_auth_header_from_env__mutmut_11': x_build_auth_header_from_env__mutmut_11, 
    'x_build_auth_header_from_env__mutmut_12': x_build_auth_header_from_env__mutmut_12, 
    'x_build_auth_header_from_env__mutmut_13': x_build_auth_header_from_env__mutmut_13, 
    'x_build_auth_header_from_env__mutmut_14': x_build_auth_header_from_env__mutmut_14, 
    'x_build_auth_header_from_env__mutmut_15': x_build_auth_header_from_env__mutmut_15, 
    'x_build_auth_header_from_env__mutmut_16': x_build_auth_header_from_env__mutmut_16, 
    'x_build_auth_header_from_env__mutmut_17': x_build_auth_header_from_env__mutmut_17, 
    'x_build_auth_header_from_env__mutmut_18': x_build_auth_header_from_env__mutmut_18, 
    'x_build_auth_header_from_env__mutmut_19': x_build_auth_header_from_env__mutmut_19, 
    'x_build_auth_header_from_env__mutmut_20': x_build_auth_header_from_env__mutmut_20, 
    'x_build_auth_header_from_env__mutmut_21': x_build_auth_header_from_env__mutmut_21, 
    'x_build_auth_header_from_env__mutmut_22': x_build_auth_header_from_env__mutmut_22, 
    'x_build_auth_header_from_env__mutmut_23': x_build_auth_header_from_env__mutmut_23, 
    'x_build_auth_header_from_env__mutmut_24': x_build_auth_header_from_env__mutmut_24, 
    'x_build_auth_header_from_env__mutmut_25': x_build_auth_header_from_env__mutmut_25, 
    'x_build_auth_header_from_env__mutmut_26': x_build_auth_header_from_env__mutmut_26, 
    'x_build_auth_header_from_env__mutmut_27': x_build_auth_header_from_env__mutmut_27, 
    'x_build_auth_header_from_env__mutmut_28': x_build_auth_header_from_env__mutmut_28, 
    'x_build_auth_header_from_env__mutmut_29': x_build_auth_header_from_env__mutmut_29, 
    'x_build_auth_header_from_env__mutmut_30': x_build_auth_header_from_env__mutmut_30, 
    'x_build_auth_header_from_env__mutmut_31': x_build_auth_header_from_env__mutmut_31, 
    'x_build_auth_header_from_env__mutmut_32': x_build_auth_header_from_env__mutmut_32, 
    'x_build_auth_header_from_env__mutmut_33': x_build_auth_header_from_env__mutmut_33, 
    'x_build_auth_header_from_env__mutmut_34': x_build_auth_header_from_env__mutmut_34, 
    'x_build_auth_header_from_env__mutmut_35': x_build_auth_header_from_env__mutmut_35, 
    'x_build_auth_header_from_env__mutmut_36': x_build_auth_header_from_env__mutmut_36, 
    'x_build_auth_header_from_env__mutmut_37': x_build_auth_header_from_env__mutmut_37, 
    'x_build_auth_header_from_env__mutmut_38': x_build_auth_header_from_env__mutmut_38, 
    'x_build_auth_header_from_env__mutmut_39': x_build_auth_header_from_env__mutmut_39, 
    'x_build_auth_header_from_env__mutmut_40': x_build_auth_header_from_env__mutmut_40, 
    'x_build_auth_header_from_env__mutmut_41': x_build_auth_header_from_env__mutmut_41, 
    'x_build_auth_header_from_env__mutmut_42': x_build_auth_header_from_env__mutmut_42, 
    'x_build_auth_header_from_env__mutmut_43': x_build_auth_header_from_env__mutmut_43, 
    'x_build_auth_header_from_env__mutmut_44': x_build_auth_header_from_env__mutmut_44, 
    'x_build_auth_header_from_env__mutmut_45': x_build_auth_header_from_env__mutmut_45
}

def build_auth_header_from_env(*args, **kwargs):
    result = _mutmut_trampoline(x_build_auth_header_from_env__mutmut_orig, x_build_auth_header_from_env__mutmut_mutants, args, kwargs)
    return result 

build_auth_header_from_env.__signature__ = _mutmut_signature(x_build_auth_header_from_env__mutmut_orig)
x_build_auth_header_from_env__mutmut_orig.__name__ = 'x_build_auth_header_from_env'
