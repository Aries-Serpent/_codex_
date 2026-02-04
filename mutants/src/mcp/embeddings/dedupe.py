"""
Dedupe Module

This module provides functionality for dedupe.

Usage:
    from embeddings.dedupe import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from typing import Any
import hashlib
import json
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


def x_checksum_for_item__mutmut_orig(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_1(item: dict[str, Any]) -> str:
    s = None
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_2(item: dict[str, Any]) -> str:
    s = json.dumps(
        None,
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_3(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=None,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_4(item: dict[str, Any]) -> str:
    s = json.dumps(
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_5(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_6(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"XXidXX": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_7(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"ID": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_8(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get(None), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_9(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("XXidXX"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_10(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("ID"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_11(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "XXcontentXX": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_12(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "CONTENT": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_13(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get(None), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_14(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("XXcontentXX"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_15(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("CONTENT"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_16(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "XXmetadataXX": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_17(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "METADATA": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_18(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get(None, {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_19(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", None)},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_20(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get({})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_21(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", )},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_22(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("XXmetadataXX", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_23(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("METADATA", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_24(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=False,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_checksum_for_item__mutmut_25(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(None).hexdigest()


def x_checksum_for_item__mutmut_26(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode(None)).hexdigest()


def x_checksum_for_item__mutmut_27(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("XXutf-8XX")).hexdigest()


def x_checksum_for_item__mutmut_28(item: dict[str, Any]) -> str:
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("UTF-8")).hexdigest()

x_checksum_for_item__mutmut_mutants : ClassVar[MutantDict] = {
'x_checksum_for_item__mutmut_1': x_checksum_for_item__mutmut_1, 
    'x_checksum_for_item__mutmut_2': x_checksum_for_item__mutmut_2, 
    'x_checksum_for_item__mutmut_3': x_checksum_for_item__mutmut_3, 
    'x_checksum_for_item__mutmut_4': x_checksum_for_item__mutmut_4, 
    'x_checksum_for_item__mutmut_5': x_checksum_for_item__mutmut_5, 
    'x_checksum_for_item__mutmut_6': x_checksum_for_item__mutmut_6, 
    'x_checksum_for_item__mutmut_7': x_checksum_for_item__mutmut_7, 
    'x_checksum_for_item__mutmut_8': x_checksum_for_item__mutmut_8, 
    'x_checksum_for_item__mutmut_9': x_checksum_for_item__mutmut_9, 
    'x_checksum_for_item__mutmut_10': x_checksum_for_item__mutmut_10, 
    'x_checksum_for_item__mutmut_11': x_checksum_for_item__mutmut_11, 
    'x_checksum_for_item__mutmut_12': x_checksum_for_item__mutmut_12, 
    'x_checksum_for_item__mutmut_13': x_checksum_for_item__mutmut_13, 
    'x_checksum_for_item__mutmut_14': x_checksum_for_item__mutmut_14, 
    'x_checksum_for_item__mutmut_15': x_checksum_for_item__mutmut_15, 
    'x_checksum_for_item__mutmut_16': x_checksum_for_item__mutmut_16, 
    'x_checksum_for_item__mutmut_17': x_checksum_for_item__mutmut_17, 
    'x_checksum_for_item__mutmut_18': x_checksum_for_item__mutmut_18, 
    'x_checksum_for_item__mutmut_19': x_checksum_for_item__mutmut_19, 
    'x_checksum_for_item__mutmut_20': x_checksum_for_item__mutmut_20, 
    'x_checksum_for_item__mutmut_21': x_checksum_for_item__mutmut_21, 
    'x_checksum_for_item__mutmut_22': x_checksum_for_item__mutmut_22, 
    'x_checksum_for_item__mutmut_23': x_checksum_for_item__mutmut_23, 
    'x_checksum_for_item__mutmut_24': x_checksum_for_item__mutmut_24, 
    'x_checksum_for_item__mutmut_25': x_checksum_for_item__mutmut_25, 
    'x_checksum_for_item__mutmut_26': x_checksum_for_item__mutmut_26, 
    'x_checksum_for_item__mutmut_27': x_checksum_for_item__mutmut_27, 
    'x_checksum_for_item__mutmut_28': x_checksum_for_item__mutmut_28
}

def checksum_for_item(*args, **kwargs):
    result = _mutmut_trampoline(x_checksum_for_item__mutmut_orig, x_checksum_for_item__mutmut_mutants, args, kwargs)
    return result 

checksum_for_item.__signature__ = _mutmut_signature(x_checksum_for_item__mutmut_orig)
x_checksum_for_item__mutmut_orig.__name__ = 'x_checksum_for_item'


class InMemoryDeduper:
    def xǁInMemoryDeduperǁ__init____mutmut_orig(self):
        self._seen: set[str] = set()
    def xǁInMemoryDeduperǁ__init____mutmut_1(self):
        self._seen: set[str] = None
    
    xǁInMemoryDeduperǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInMemoryDeduperǁ__init____mutmut_1': xǁInMemoryDeduperǁ__init____mutmut_1
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInMemoryDeduperǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁInMemoryDeduperǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁInMemoryDeduperǁ__init____mutmut_orig)
    xǁInMemoryDeduperǁ__init____mutmut_orig.__name__ = 'xǁInMemoryDeduperǁ__init__'

    def xǁInMemoryDeduperǁis_duplicate__mutmut_orig(self, item: dict[str, Any]) -> bool:
        c = checksum_for_item(item)
        if c in self._seen:
            return True
        self._seen.add(c)
        return False

    def xǁInMemoryDeduperǁis_duplicate__mutmut_1(self, item: dict[str, Any]) -> bool:
        c = None
        if c in self._seen:
            return True
        self._seen.add(c)
        return False

    def xǁInMemoryDeduperǁis_duplicate__mutmut_2(self, item: dict[str, Any]) -> bool:
        c = checksum_for_item(None)
        if c in self._seen:
            return True
        self._seen.add(c)
        return False

    def xǁInMemoryDeduperǁis_duplicate__mutmut_3(self, item: dict[str, Any]) -> bool:
        c = checksum_for_item(item)
        if c not in self._seen:
            return True
        self._seen.add(c)
        return False

    def xǁInMemoryDeduperǁis_duplicate__mutmut_4(self, item: dict[str, Any]) -> bool:
        c = checksum_for_item(item)
        if c in self._seen:
            return False
        self._seen.add(c)
        return False

    def xǁInMemoryDeduperǁis_duplicate__mutmut_5(self, item: dict[str, Any]) -> bool:
        c = checksum_for_item(item)
        if c in self._seen:
            return True
        self._seen.add(None)
        return False

    def xǁInMemoryDeduperǁis_duplicate__mutmut_6(self, item: dict[str, Any]) -> bool:
        c = checksum_for_item(item)
        if c in self._seen:
            return True
        self._seen.add(c)
        return True
    
    xǁInMemoryDeduperǁis_duplicate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInMemoryDeduperǁis_duplicate__mutmut_1': xǁInMemoryDeduperǁis_duplicate__mutmut_1, 
        'xǁInMemoryDeduperǁis_duplicate__mutmut_2': xǁInMemoryDeduperǁis_duplicate__mutmut_2, 
        'xǁInMemoryDeduperǁis_duplicate__mutmut_3': xǁInMemoryDeduperǁis_duplicate__mutmut_3, 
        'xǁInMemoryDeduperǁis_duplicate__mutmut_4': xǁInMemoryDeduperǁis_duplicate__mutmut_4, 
        'xǁInMemoryDeduperǁis_duplicate__mutmut_5': xǁInMemoryDeduperǁis_duplicate__mutmut_5, 
        'xǁInMemoryDeduperǁis_duplicate__mutmut_6': xǁInMemoryDeduperǁis_duplicate__mutmut_6
    }
    
    def is_duplicate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInMemoryDeduperǁis_duplicate__mutmut_orig"), object.__getattribute__(self, "xǁInMemoryDeduperǁis_duplicate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    is_duplicate.__signature__ = _mutmut_signature(xǁInMemoryDeduperǁis_duplicate__mutmut_orig)
    xǁInMemoryDeduperǁis_duplicate__mutmut_orig.__name__ = 'xǁInMemoryDeduperǁis_duplicate'
