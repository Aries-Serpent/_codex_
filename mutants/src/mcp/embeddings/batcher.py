"""
Batcher Module

This module provides functionality for batcher.

Usage:
    from embeddings.batcher import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from typing import Iterable, Any, Generator
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


def x_compute_checksum__mutmut_orig(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_1(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = None
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_2(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        None,
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_3(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=None,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_4(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_5(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_6(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"XXidXX": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_7(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"ID": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_8(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get(None), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_9(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("XXidXX"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_10(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("ID"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_11(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "XXcontentXX": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_12(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "CONTENT": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_13(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get(None), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_14(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("XXcontentXX"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_15(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("CONTENT"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_16(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "XXmetadataXX": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_17(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "METADATA": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_18(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get(None, {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_19(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", None)},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_20(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get({})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_21(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", )},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_22(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("XXmetadataXX", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_23(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("METADATA", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_24(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=False,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def x_compute_checksum__mutmut_25(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(None).hexdigest()


def x_compute_checksum__mutmut_26(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode(None)).hexdigest()


def x_compute_checksum__mutmut_27(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("XXutf-8XX")).hexdigest()


def x_compute_checksum__mutmut_28(item: dict) -> str:
    """
    Compute deterministic checksum for item content/metadata.
    """
    s = json.dumps(
        {"id": item.get("id"), "content": item.get("content"), "metadata": item.get("metadata", {})},
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("UTF-8")).hexdigest()

x_compute_checksum__mutmut_mutants : ClassVar[MutantDict] = {
'x_compute_checksum__mutmut_1': x_compute_checksum__mutmut_1, 
    'x_compute_checksum__mutmut_2': x_compute_checksum__mutmut_2, 
    'x_compute_checksum__mutmut_3': x_compute_checksum__mutmut_3, 
    'x_compute_checksum__mutmut_4': x_compute_checksum__mutmut_4, 
    'x_compute_checksum__mutmut_5': x_compute_checksum__mutmut_5, 
    'x_compute_checksum__mutmut_6': x_compute_checksum__mutmut_6, 
    'x_compute_checksum__mutmut_7': x_compute_checksum__mutmut_7, 
    'x_compute_checksum__mutmut_8': x_compute_checksum__mutmut_8, 
    'x_compute_checksum__mutmut_9': x_compute_checksum__mutmut_9, 
    'x_compute_checksum__mutmut_10': x_compute_checksum__mutmut_10, 
    'x_compute_checksum__mutmut_11': x_compute_checksum__mutmut_11, 
    'x_compute_checksum__mutmut_12': x_compute_checksum__mutmut_12, 
    'x_compute_checksum__mutmut_13': x_compute_checksum__mutmut_13, 
    'x_compute_checksum__mutmut_14': x_compute_checksum__mutmut_14, 
    'x_compute_checksum__mutmut_15': x_compute_checksum__mutmut_15, 
    'x_compute_checksum__mutmut_16': x_compute_checksum__mutmut_16, 
    'x_compute_checksum__mutmut_17': x_compute_checksum__mutmut_17, 
    'x_compute_checksum__mutmut_18': x_compute_checksum__mutmut_18, 
    'x_compute_checksum__mutmut_19': x_compute_checksum__mutmut_19, 
    'x_compute_checksum__mutmut_20': x_compute_checksum__mutmut_20, 
    'x_compute_checksum__mutmut_21': x_compute_checksum__mutmut_21, 
    'x_compute_checksum__mutmut_22': x_compute_checksum__mutmut_22, 
    'x_compute_checksum__mutmut_23': x_compute_checksum__mutmut_23, 
    'x_compute_checksum__mutmut_24': x_compute_checksum__mutmut_24, 
    'x_compute_checksum__mutmut_25': x_compute_checksum__mutmut_25, 
    'x_compute_checksum__mutmut_26': x_compute_checksum__mutmut_26, 
    'x_compute_checksum__mutmut_27': x_compute_checksum__mutmut_27, 
    'x_compute_checksum__mutmut_28': x_compute_checksum__mutmut_28
}

def compute_checksum(*args, **kwargs):
    result = _mutmut_trampoline(x_compute_checksum__mutmut_orig, x_compute_checksum__mutmut_mutants, args, kwargs)
    return result 

compute_checksum.__signature__ = _mutmut_signature(x_compute_checksum__mutmut_orig)
x_compute_checksum__mutmut_orig.__name__ = 'x_compute_checksum'


def x_batch_iterable__mutmut_orig(iterable: Iterable[Any], batch_size: int) -> Generator[list[Any], None, None]:
    batch = []
    for it in iterable:
        batch.append(it)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def x_batch_iterable__mutmut_1(iterable: Iterable[Any], batch_size: int) -> Generator[list[Any], None, None]:
    batch = None
    for it in iterable:
        batch.append(it)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def x_batch_iterable__mutmut_2(iterable: Iterable[Any], batch_size: int) -> Generator[list[Any], None, None]:
    batch = []
    for it in iterable:
        batch.append(None)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def x_batch_iterable__mutmut_3(iterable: Iterable[Any], batch_size: int) -> Generator[list[Any], None, None]:
    batch = []
    for it in iterable:
        batch.append(it)
        if len(batch) > batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def x_batch_iterable__mutmut_4(iterable: Iterable[Any], batch_size: int) -> Generator[list[Any], None, None]:
    batch = []
    for it in iterable:
        batch.append(it)
        if len(batch) >= batch_size:
            yield batch
            batch = None
    if batch:
        yield batch

x_batch_iterable__mutmut_mutants : ClassVar[MutantDict] = {
'x_batch_iterable__mutmut_1': x_batch_iterable__mutmut_1, 
    'x_batch_iterable__mutmut_2': x_batch_iterable__mutmut_2, 
    'x_batch_iterable__mutmut_3': x_batch_iterable__mutmut_3, 
    'x_batch_iterable__mutmut_4': x_batch_iterable__mutmut_4
}

def batch_iterable(*args, **kwargs):
    result = _mutmut_trampoline(x_batch_iterable__mutmut_orig, x_batch_iterable__mutmut_mutants, args, kwargs)
    return result 

batch_iterable.__signature__ = _mutmut_signature(x_batch_iterable__mutmut_orig)
x_batch_iterable__mutmut_orig.__name__ = 'x_batch_iterable'
