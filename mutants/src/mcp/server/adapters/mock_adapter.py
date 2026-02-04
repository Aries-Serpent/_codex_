"""
Mock Adapter Module

This module provides functionality for mock adapter.

Usage:
    from adapters.mock_adapter import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from typing import Any, Iterable
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


class MockAdapter:
    """
    Minimal mock adapter for local dev and tests.
    """

    def xǁMockAdapterǁ__init____mutmut_orig(self):
        self.query_calls: list[dict[str, Any]] = []
        self.upsert_calls: list[dict[str, Any]] = []
        self.delete_calls: list[dict[str, Any]] = []

    def xǁMockAdapterǁ__init____mutmut_1(self):
        self.query_calls: list[dict[str, Any]] = None
        self.upsert_calls: list[dict[str, Any]] = []
        self.delete_calls: list[dict[str, Any]] = []

    def xǁMockAdapterǁ__init____mutmut_2(self):
        self.query_calls: list[dict[str, Any]] = []
        self.upsert_calls: list[dict[str, Any]] = None
        self.delete_calls: list[dict[str, Any]] = []

    def xǁMockAdapterǁ__init____mutmut_3(self):
        self.query_calls: list[dict[str, Any]] = []
        self.upsert_calls: list[dict[str, Any]] = []
        self.delete_calls: list[dict[str, Any]] = None
    
    xǁMockAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁ__init____mutmut_1': xǁMockAdapterǁ__init____mutmut_1, 
        'xǁMockAdapterǁ__init____mutmut_2': xǁMockAdapterǁ__init____mutmut_2, 
        'xǁMockAdapterǁ__init____mutmut_3': xǁMockAdapterǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMockAdapterǁ__init____mutmut_orig)
    xǁMockAdapterǁ__init____mutmut_orig.__name__ = 'xǁMockAdapterǁ__init__'

    def connect(self) -> None:
        return None

    def xǁMockAdapterǁquery_top_k__mutmut_orig(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_1(self, namespace: str, query_embedding: list[float], top_k: int = 6, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_2(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            None
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_3(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "XXnamespaceXX": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_4(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "NAMESPACE": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_5(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "XXquery_embeddingXX": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_6(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "QUERY_EMBEDDING": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_7(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "XXtop_kXX": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_8(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "TOP_K": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_9(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "XXfiltersXX": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_10(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "FILTERS": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_11(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"XXidXX": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_12(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"ID": "mock", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_13(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "XXmockXX", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_14(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "MOCK", "score": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_15(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "XXscoreXX": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_16(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "SCORE": 0.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_17(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 1.0, "content": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_18(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "XXcontentXX": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_19(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "CONTENT": "", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_20(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "XXXX", "metadata": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_21(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "XXmetadataXX": {}}]

    def xǁMockAdapterǁquery_top_k__mutmut_22(self, namespace: str, query_embedding: list[float], top_k: int = 5, filters=None):
        self.query_calls.append(
            {
                "namespace": namespace,
                "query_embedding": query_embedding,
                "top_k": top_k,
                "filters": filters,
            }
        )
        return [{"id": "mock", "score": 0.0, "content": "", "METADATA": {}}]
    
    xǁMockAdapterǁquery_top_k__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁquery_top_k__mutmut_1': xǁMockAdapterǁquery_top_k__mutmut_1, 
        'xǁMockAdapterǁquery_top_k__mutmut_2': xǁMockAdapterǁquery_top_k__mutmut_2, 
        'xǁMockAdapterǁquery_top_k__mutmut_3': xǁMockAdapterǁquery_top_k__mutmut_3, 
        'xǁMockAdapterǁquery_top_k__mutmut_4': xǁMockAdapterǁquery_top_k__mutmut_4, 
        'xǁMockAdapterǁquery_top_k__mutmut_5': xǁMockAdapterǁquery_top_k__mutmut_5, 
        'xǁMockAdapterǁquery_top_k__mutmut_6': xǁMockAdapterǁquery_top_k__mutmut_6, 
        'xǁMockAdapterǁquery_top_k__mutmut_7': xǁMockAdapterǁquery_top_k__mutmut_7, 
        'xǁMockAdapterǁquery_top_k__mutmut_8': xǁMockAdapterǁquery_top_k__mutmut_8, 
        'xǁMockAdapterǁquery_top_k__mutmut_9': xǁMockAdapterǁquery_top_k__mutmut_9, 
        'xǁMockAdapterǁquery_top_k__mutmut_10': xǁMockAdapterǁquery_top_k__mutmut_10, 
        'xǁMockAdapterǁquery_top_k__mutmut_11': xǁMockAdapterǁquery_top_k__mutmut_11, 
        'xǁMockAdapterǁquery_top_k__mutmut_12': xǁMockAdapterǁquery_top_k__mutmut_12, 
        'xǁMockAdapterǁquery_top_k__mutmut_13': xǁMockAdapterǁquery_top_k__mutmut_13, 
        'xǁMockAdapterǁquery_top_k__mutmut_14': xǁMockAdapterǁquery_top_k__mutmut_14, 
        'xǁMockAdapterǁquery_top_k__mutmut_15': xǁMockAdapterǁquery_top_k__mutmut_15, 
        'xǁMockAdapterǁquery_top_k__mutmut_16': xǁMockAdapterǁquery_top_k__mutmut_16, 
        'xǁMockAdapterǁquery_top_k__mutmut_17': xǁMockAdapterǁquery_top_k__mutmut_17, 
        'xǁMockAdapterǁquery_top_k__mutmut_18': xǁMockAdapterǁquery_top_k__mutmut_18, 
        'xǁMockAdapterǁquery_top_k__mutmut_19': xǁMockAdapterǁquery_top_k__mutmut_19, 
        'xǁMockAdapterǁquery_top_k__mutmut_20': xǁMockAdapterǁquery_top_k__mutmut_20, 
        'xǁMockAdapterǁquery_top_k__mutmut_21': xǁMockAdapterǁquery_top_k__mutmut_21, 
        'xǁMockAdapterǁquery_top_k__mutmut_22': xǁMockAdapterǁquery_top_k__mutmut_22
    }
    
    def query_top_k(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁquery_top_k__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁquery_top_k__mutmut_mutants"), args, kwargs, self)
        return result 
    
    query_top_k.__signature__ = _mutmut_signature(xǁMockAdapterǁquery_top_k__mutmut_orig)
    xǁMockAdapterǁquery_top_k__mutmut_orig.__name__ = 'xǁMockAdapterǁquery_top_k'

    def xǁMockAdapterǁupsert_batch__mutmut_orig(self, namespace: str, items: Iterable[dict[str, Any]]) -> None:
        self.upsert_calls.append({"namespace": namespace, "items": list(items)})

    def xǁMockAdapterǁupsert_batch__mutmut_1(self, namespace: str, items: Iterable[dict[str, Any]]) -> None:
        self.upsert_calls.append(None)

    def xǁMockAdapterǁupsert_batch__mutmut_2(self, namespace: str, items: Iterable[dict[str, Any]]) -> None:
        self.upsert_calls.append({"XXnamespaceXX": namespace, "items": list(items)})

    def xǁMockAdapterǁupsert_batch__mutmut_3(self, namespace: str, items: Iterable[dict[str, Any]]) -> None:
        self.upsert_calls.append({"NAMESPACE": namespace, "items": list(items)})

    def xǁMockAdapterǁupsert_batch__mutmut_4(self, namespace: str, items: Iterable[dict[str, Any]]) -> None:
        self.upsert_calls.append({"namespace": namespace, "XXitemsXX": list(items)})

    def xǁMockAdapterǁupsert_batch__mutmut_5(self, namespace: str, items: Iterable[dict[str, Any]]) -> None:
        self.upsert_calls.append({"namespace": namespace, "ITEMS": list(items)})

    def xǁMockAdapterǁupsert_batch__mutmut_6(self, namespace: str, items: Iterable[dict[str, Any]]) -> None:
        self.upsert_calls.append({"namespace": namespace, "items": list(None)})
    
    xǁMockAdapterǁupsert_batch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁupsert_batch__mutmut_1': xǁMockAdapterǁupsert_batch__mutmut_1, 
        'xǁMockAdapterǁupsert_batch__mutmut_2': xǁMockAdapterǁupsert_batch__mutmut_2, 
        'xǁMockAdapterǁupsert_batch__mutmut_3': xǁMockAdapterǁupsert_batch__mutmut_3, 
        'xǁMockAdapterǁupsert_batch__mutmut_4': xǁMockAdapterǁupsert_batch__mutmut_4, 
        'xǁMockAdapterǁupsert_batch__mutmut_5': xǁMockAdapterǁupsert_batch__mutmut_5, 
        'xǁMockAdapterǁupsert_batch__mutmut_6': xǁMockAdapterǁupsert_batch__mutmut_6
    }
    
    def upsert_batch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁupsert_batch__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁupsert_batch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    upsert_batch.__signature__ = _mutmut_signature(xǁMockAdapterǁupsert_batch__mutmut_orig)
    xǁMockAdapterǁupsert_batch__mutmut_orig.__name__ = 'xǁMockAdapterǁupsert_batch'

    def xǁMockAdapterǁdelete__mutmut_orig(self, namespace: str, id: str) -> bool:
        self.delete_calls.append({"namespace": namespace, "id": id})
        return True

    def xǁMockAdapterǁdelete__mutmut_1(self, namespace: str, id: str) -> bool:
        self.delete_calls.append(None)
        return True

    def xǁMockAdapterǁdelete__mutmut_2(self, namespace: str, id: str) -> bool:
        self.delete_calls.append({"XXnamespaceXX": namespace, "id": id})
        return True

    def xǁMockAdapterǁdelete__mutmut_3(self, namespace: str, id: str) -> bool:
        self.delete_calls.append({"NAMESPACE": namespace, "id": id})
        return True

    def xǁMockAdapterǁdelete__mutmut_4(self, namespace: str, id: str) -> bool:
        self.delete_calls.append({"namespace": namespace, "XXidXX": id})
        return True

    def xǁMockAdapterǁdelete__mutmut_5(self, namespace: str, id: str) -> bool:
        self.delete_calls.append({"namespace": namespace, "ID": id})
        return True

    def xǁMockAdapterǁdelete__mutmut_6(self, namespace: str, id: str) -> bool:
        self.delete_calls.append({"namespace": namespace, "id": id})
        return False
    
    xǁMockAdapterǁdelete__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁdelete__mutmut_1': xǁMockAdapterǁdelete__mutmut_1, 
        'xǁMockAdapterǁdelete__mutmut_2': xǁMockAdapterǁdelete__mutmut_2, 
        'xǁMockAdapterǁdelete__mutmut_3': xǁMockAdapterǁdelete__mutmut_3, 
        'xǁMockAdapterǁdelete__mutmut_4': xǁMockAdapterǁdelete__mutmut_4, 
        'xǁMockAdapterǁdelete__mutmut_5': xǁMockAdapterǁdelete__mutmut_5, 
        'xǁMockAdapterǁdelete__mutmut_6': xǁMockAdapterǁdelete__mutmut_6
    }
    
    def delete(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁdelete__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁdelete__mutmut_mutants"), args, kwargs, self)
        return result 
    
    delete.__signature__ = _mutmut_signature(xǁMockAdapterǁdelete__mutmut_orig)
    xǁMockAdapterǁdelete__mutmut_orig.__name__ = 'xǁMockAdapterǁdelete'

    def xǁMockAdapterǁhealth_check__mutmut_orig(self) -> dict[str, Any]:
        return {"status": "ok", "adapter": "mock"}

    def xǁMockAdapterǁhealth_check__mutmut_1(self) -> dict[str, Any]:
        return {"XXstatusXX": "ok", "adapter": "mock"}

    def xǁMockAdapterǁhealth_check__mutmut_2(self) -> dict[str, Any]:
        return {"STATUS": "ok", "adapter": "mock"}

    def xǁMockAdapterǁhealth_check__mutmut_3(self) -> dict[str, Any]:
        return {"status": "XXokXX", "adapter": "mock"}

    def xǁMockAdapterǁhealth_check__mutmut_4(self) -> dict[str, Any]:
        return {"status": "OK", "adapter": "mock"}

    def xǁMockAdapterǁhealth_check__mutmut_5(self) -> dict[str, Any]:
        return {"status": "ok", "XXadapterXX": "mock"}

    def xǁMockAdapterǁhealth_check__mutmut_6(self) -> dict[str, Any]:
        return {"status": "ok", "ADAPTER": "mock"}

    def xǁMockAdapterǁhealth_check__mutmut_7(self) -> dict[str, Any]:
        return {"status": "ok", "adapter": "XXmockXX"}

    def xǁMockAdapterǁhealth_check__mutmut_8(self) -> dict[str, Any]:
        return {"status": "ok", "adapter": "MOCK"}
    
    xǁMockAdapterǁhealth_check__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMockAdapterǁhealth_check__mutmut_1': xǁMockAdapterǁhealth_check__mutmut_1, 
        'xǁMockAdapterǁhealth_check__mutmut_2': xǁMockAdapterǁhealth_check__mutmut_2, 
        'xǁMockAdapterǁhealth_check__mutmut_3': xǁMockAdapterǁhealth_check__mutmut_3, 
        'xǁMockAdapterǁhealth_check__mutmut_4': xǁMockAdapterǁhealth_check__mutmut_4, 
        'xǁMockAdapterǁhealth_check__mutmut_5': xǁMockAdapterǁhealth_check__mutmut_5, 
        'xǁMockAdapterǁhealth_check__mutmut_6': xǁMockAdapterǁhealth_check__mutmut_6, 
        'xǁMockAdapterǁhealth_check__mutmut_7': xǁMockAdapterǁhealth_check__mutmut_7, 
        'xǁMockAdapterǁhealth_check__mutmut_8': xǁMockAdapterǁhealth_check__mutmut_8
    }
    
    def health_check(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMockAdapterǁhealth_check__mutmut_orig"), object.__getattribute__(self, "xǁMockAdapterǁhealth_check__mutmut_mutants"), args, kwargs, self)
        return result 
    
    health_check.__signature__ = _mutmut_signature(xǁMockAdapterǁhealth_check__mutmut_orig)
    xǁMockAdapterǁhealth_check__mutmut_orig.__name__ = 'xǁMockAdapterǁhealth_check'
