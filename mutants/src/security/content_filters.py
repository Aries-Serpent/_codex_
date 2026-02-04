"""Content filtering helpers consolidating previously scattered logic."""

from __future__ import annotations

import re

from .core import SecurityError

_PROFANITY = {"foo", "barf", "bazinga", "dang"}
_PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\b\d{4} \d{4} \d{4} \d{4}\b"),  # Credit card (simplified)
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
]
_MALWARE_PATTERNS = [
    re.compile(r"(?:powershell.exe\s+-enc)", re.I),
    re.compile(r"curl\s+http[s]?://[\w./-]+\s*-o\s+/tmp/\w+", re.I),
    re.compile(r"rm\s+-rf\s+/", re.I),
]
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


def x_sanitize_text__mutmut_orig(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "[REDACTED]", sanitized, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_1(text: str) -> str:
    sanitized = None
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "[REDACTED]", sanitized, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_2(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = None
    return sanitized


def x_sanitize_text__mutmut_3(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(None, "[REDACTED]", sanitized, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_4(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), None, sanitized, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_5(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "[REDACTED]", None, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_6(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "[REDACTED]", sanitized, flags=None)
    return sanitized


def x_sanitize_text__mutmut_7(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub("[REDACTED]", sanitized, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_8(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), sanitized, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_9(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "[REDACTED]", flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_10(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "[REDACTED]", sanitized, )
    return sanitized


def x_sanitize_text__mutmut_11(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(None), "[REDACTED]", sanitized, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_12(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "XX[REDACTED]XX", sanitized, flags=re.I)
    return sanitized


def x_sanitize_text__mutmut_13(text: str) -> str:
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "[redacted]", sanitized, flags=re.I)
    return sanitized

x_sanitize_text__mutmut_mutants : ClassVar[MutantDict] = {
'x_sanitize_text__mutmut_1': x_sanitize_text__mutmut_1, 
    'x_sanitize_text__mutmut_2': x_sanitize_text__mutmut_2, 
    'x_sanitize_text__mutmut_3': x_sanitize_text__mutmut_3, 
    'x_sanitize_text__mutmut_4': x_sanitize_text__mutmut_4, 
    'x_sanitize_text__mutmut_5': x_sanitize_text__mutmut_5, 
    'x_sanitize_text__mutmut_6': x_sanitize_text__mutmut_6, 
    'x_sanitize_text__mutmut_7': x_sanitize_text__mutmut_7, 
    'x_sanitize_text__mutmut_8': x_sanitize_text__mutmut_8, 
    'x_sanitize_text__mutmut_9': x_sanitize_text__mutmut_9, 
    'x_sanitize_text__mutmut_10': x_sanitize_text__mutmut_10, 
    'x_sanitize_text__mutmut_11': x_sanitize_text__mutmut_11, 
    'x_sanitize_text__mutmut_12': x_sanitize_text__mutmut_12, 
    'x_sanitize_text__mutmut_13': x_sanitize_text__mutmut_13
}

def sanitize_text(*args, **kwargs):
    result = _mutmut_trampoline(x_sanitize_text__mutmut_orig, x_sanitize_text__mutmut_mutants, args, kwargs)
    return result 

sanitize_text.__signature__ = _mutmut_signature(x_sanitize_text__mutmut_orig)
x_sanitize_text__mutmut_orig.__name__ = 'x_sanitize_text'


def x_detect_profanity__mutmut_orig(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in _PROFANITY)


def x_detect_profanity__mutmut_1(text: str) -> bool:
    lowered = None
    return any(word in lowered for word in _PROFANITY)


def x_detect_profanity__mutmut_2(text: str) -> bool:
    lowered = text.upper()
    return any(word in lowered for word in _PROFANITY)


def x_detect_profanity__mutmut_3(text: str) -> bool:
    lowered = text.lower()
    return any(None)


def x_detect_profanity__mutmut_4(text: str) -> bool:
    lowered = text.lower()
    return any(word not in lowered for word in _PROFANITY)

x_detect_profanity__mutmut_mutants : ClassVar[MutantDict] = {
'x_detect_profanity__mutmut_1': x_detect_profanity__mutmut_1, 
    'x_detect_profanity__mutmut_2': x_detect_profanity__mutmut_2, 
    'x_detect_profanity__mutmut_3': x_detect_profanity__mutmut_3, 
    'x_detect_profanity__mutmut_4': x_detect_profanity__mutmut_4
}

def detect_profanity(*args, **kwargs):
    result = _mutmut_trampoline(x_detect_profanity__mutmut_orig, x_detect_profanity__mutmut_mutants, args, kwargs)
    return result 

detect_profanity.__signature__ = _mutmut_signature(x_detect_profanity__mutmut_orig)
x_detect_profanity__mutmut_orig.__name__ = 'x_detect_profanity'


def x_detect_personal_data__mutmut_orig(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"pii": []}
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(text)
        if matches_found:
            matches["pii"].extend(matches_found)
    return matches


def x_detect_personal_data__mutmut_1(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = None
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(text)
        if matches_found:
            matches["pii"].extend(matches_found)
    return matches


def x_detect_personal_data__mutmut_2(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"XXpiiXX": []}
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(text)
        if matches_found:
            matches["pii"].extend(matches_found)
    return matches


def x_detect_personal_data__mutmut_3(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"PII": []}
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(text)
        if matches_found:
            matches["pii"].extend(matches_found)
    return matches


def x_detect_personal_data__mutmut_4(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"pii": []}
    for pattern in _PII_PATTERNS:
        matches_found = None
        if matches_found:
            matches["pii"].extend(matches_found)
    return matches


def x_detect_personal_data__mutmut_5(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"pii": []}
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(None)
        if matches_found:
            matches["pii"].extend(matches_found)
    return matches


def x_detect_personal_data__mutmut_6(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"pii": []}
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(text)
        if matches_found:
            matches["pii"].extend(None)
    return matches


def x_detect_personal_data__mutmut_7(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"pii": []}
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(text)
        if matches_found:
            matches["XXpiiXX"].extend(matches_found)
    return matches


def x_detect_personal_data__mutmut_8(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"pii": []}
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(text)
        if matches_found:
            matches["PII"].extend(matches_found)
    return matches

x_detect_personal_data__mutmut_mutants : ClassVar[MutantDict] = {
'x_detect_personal_data__mutmut_1': x_detect_personal_data__mutmut_1, 
    'x_detect_personal_data__mutmut_2': x_detect_personal_data__mutmut_2, 
    'x_detect_personal_data__mutmut_3': x_detect_personal_data__mutmut_3, 
    'x_detect_personal_data__mutmut_4': x_detect_personal_data__mutmut_4, 
    'x_detect_personal_data__mutmut_5': x_detect_personal_data__mutmut_5, 
    'x_detect_personal_data__mutmut_6': x_detect_personal_data__mutmut_6, 
    'x_detect_personal_data__mutmut_7': x_detect_personal_data__mutmut_7, 
    'x_detect_personal_data__mutmut_8': x_detect_personal_data__mutmut_8
}

def detect_personal_data(*args, **kwargs):
    result = _mutmut_trampoline(x_detect_personal_data__mutmut_orig, x_detect_personal_data__mutmut_mutants, args, kwargs)
    return result 

detect_personal_data.__signature__ = _mutmut_signature(x_detect_personal_data__mutmut_orig)
x_detect_personal_data__mutmut_orig.__name__ = 'x_detect_personal_data'


def x_detect_malware_patterns__mutmut_orig(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in _MALWARE_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern)
    return hits


def x_detect_malware_patterns__mutmut_1(text: str) -> list[str]:
    hits: list[str] = None
    for pattern in _MALWARE_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern)
    return hits


def x_detect_malware_patterns__mutmut_2(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in _MALWARE_PATTERNS:
        if pattern.search(None):
            hits.append(pattern.pattern)
    return hits


def x_detect_malware_patterns__mutmut_3(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in _MALWARE_PATTERNS:
        if pattern.search(text):
            hits.append(None)
    return hits

x_detect_malware_patterns__mutmut_mutants : ClassVar[MutantDict] = {
'x_detect_malware_patterns__mutmut_1': x_detect_malware_patterns__mutmut_1, 
    'x_detect_malware_patterns__mutmut_2': x_detect_malware_patterns__mutmut_2, 
    'x_detect_malware_patterns__mutmut_3': x_detect_malware_patterns__mutmut_3
}

def detect_malware_patterns(*args, **kwargs):
    result = _mutmut_trampoline(x_detect_malware_patterns__mutmut_orig, x_detect_malware_patterns__mutmut_mutants, args, kwargs)
    return result 

detect_malware_patterns.__signature__ = _mutmut_signature(x_detect_malware_patterns__mutmut_orig)
x_detect_malware_patterns__mutmut_orig.__name__ = 'x_detect_malware_patterns'


def x_enforce_content_policies__mutmut_orig(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_1(text: str) -> None:
    if detect_profanity(None):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_2(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError(None)
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_3(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("XXProfanity detectedXX")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_4(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_5(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("PROFANITY DETECTED")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_6(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(None)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_7(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["XXpiiXX"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_8(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["PII"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_9(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError(None)
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_10(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("XXPII detectedXX")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_11(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("pii detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_12(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII DETECTED")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_13(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(None):
        raise SecurityError("Malware pattern detected")


def x_enforce_content_policies__mutmut_14(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError(None)


def x_enforce_content_policies__mutmut_15(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("XXMalware pattern detectedXX")


def x_enforce_content_policies__mutmut_16(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("malware pattern detected")


def x_enforce_content_policies__mutmut_17(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("MALWARE PATTERN DETECTED")

x_enforce_content_policies__mutmut_mutants : ClassVar[MutantDict] = {
'x_enforce_content_policies__mutmut_1': x_enforce_content_policies__mutmut_1, 
    'x_enforce_content_policies__mutmut_2': x_enforce_content_policies__mutmut_2, 
    'x_enforce_content_policies__mutmut_3': x_enforce_content_policies__mutmut_3, 
    'x_enforce_content_policies__mutmut_4': x_enforce_content_policies__mutmut_4, 
    'x_enforce_content_policies__mutmut_5': x_enforce_content_policies__mutmut_5, 
    'x_enforce_content_policies__mutmut_6': x_enforce_content_policies__mutmut_6, 
    'x_enforce_content_policies__mutmut_7': x_enforce_content_policies__mutmut_7, 
    'x_enforce_content_policies__mutmut_8': x_enforce_content_policies__mutmut_8, 
    'x_enforce_content_policies__mutmut_9': x_enforce_content_policies__mutmut_9, 
    'x_enforce_content_policies__mutmut_10': x_enforce_content_policies__mutmut_10, 
    'x_enforce_content_policies__mutmut_11': x_enforce_content_policies__mutmut_11, 
    'x_enforce_content_policies__mutmut_12': x_enforce_content_policies__mutmut_12, 
    'x_enforce_content_policies__mutmut_13': x_enforce_content_policies__mutmut_13, 
    'x_enforce_content_policies__mutmut_14': x_enforce_content_policies__mutmut_14, 
    'x_enforce_content_policies__mutmut_15': x_enforce_content_policies__mutmut_15, 
    'x_enforce_content_policies__mutmut_16': x_enforce_content_policies__mutmut_16, 
    'x_enforce_content_policies__mutmut_17': x_enforce_content_policies__mutmut_17
}

def enforce_content_policies(*args, **kwargs):
    result = _mutmut_trampoline(x_enforce_content_policies__mutmut_orig, x_enforce_content_policies__mutmut_mutants, args, kwargs)
    return result 

enforce_content_policies.__signature__ = _mutmut_signature(x_enforce_content_policies__mutmut_orig)
x_enforce_content_policies__mutmut_orig.__name__ = 'x_enforce_content_policies'
