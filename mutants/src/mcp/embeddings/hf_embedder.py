"""
Hf Embedder Module

This module provides functionality for hf embedder.

Usage:
    from embeddings.hf_embedder import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import importlib
import importlib.util
import logging
from typing import Any

from .interface import EmbedderInterface

logger = logging.getLogger(__name__)
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


class HFEmbedder(EmbedderInterface):
    """
    Hugging Face embedder skeleton (sentence-transformers / transformers).
    Lazy-loads required model to avoid heavy imports in tests.
    """

    def xǁHFEmbedderǁ__init____mutmut_orig(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def xǁHFEmbedderǁ__init____mutmut_1(self, model_name: str = "XXsentence-transformers/all-MiniLM-L6-v2XX"):
        self.model_name = model_name
        self._model = None

    def xǁHFEmbedderǁ__init____mutmut_2(self, model_name: str = "sentence-transformers/all-minilm-l6-v2"):
        self.model_name = model_name
        self._model = None

    def xǁHFEmbedderǁ__init____mutmut_3(self, model_name: str = "SENTENCE-TRANSFORMERS/ALL-MINILM-L6-V2"):
        self.model_name = model_name
        self._model = None

    def xǁHFEmbedderǁ__init____mutmut_4(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = None
        self._model = None

    def xǁHFEmbedderǁ__init____mutmut_5(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = ""
    
    xǁHFEmbedderǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHFEmbedderǁ__init____mutmut_1': xǁHFEmbedderǁ__init____mutmut_1, 
        'xǁHFEmbedderǁ__init____mutmut_2': xǁHFEmbedderǁ__init____mutmut_2, 
        'xǁHFEmbedderǁ__init____mutmut_3': xǁHFEmbedderǁ__init____mutmut_3, 
        'xǁHFEmbedderǁ__init____mutmut_4': xǁHFEmbedderǁ__init____mutmut_4, 
        'xǁHFEmbedderǁ__init____mutmut_5': xǁHFEmbedderǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHFEmbedderǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁHFEmbedderǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁHFEmbedderǁ__init____mutmut_orig)
    xǁHFEmbedderǁ__init____mutmut_orig.__name__ = 'xǁHFEmbedderǁ__init__'

    def xǁHFEmbedderǁ_ensure_model__mutmut_orig(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_1(self):
        if self._model:
            return
        if importlib.util.find_spec(None) is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_2(self):
        if self._model:
            return
        if importlib.util.find_spec("XXsentence_transformersXX") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_3(self):
        if self._model:
            return
        if importlib.util.find_spec("SENTENCE_TRANSFORMERS") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_4(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is not None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_5(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning(None)
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_6(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("XXsentence_transformers not availableXX")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_7(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("SENTENCE_TRANSFORMERS NOT AVAILABLE")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_8(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = None
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_9(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module(None)
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_10(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("XXsentence_transformersXX")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_11(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("SENTENCE_TRANSFORMERS")
        self._model = sentence_transformers.SentenceTransformer(self.model_name)

    def xǁHFEmbedderǁ_ensure_model__mutmut_12(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = None

    def xǁHFEmbedderǁ_ensure_model__mutmut_13(self):
        if self._model:
            return
        if importlib.util.find_spec("sentence_transformers") is None:
            logger.warning("sentence_transformers not available")
            return
        sentence_transformers = importlib.import_module("sentence_transformers")
        self._model = sentence_transformers.SentenceTransformer(None)
    
    xǁHFEmbedderǁ_ensure_model__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHFEmbedderǁ_ensure_model__mutmut_1': xǁHFEmbedderǁ_ensure_model__mutmut_1, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_2': xǁHFEmbedderǁ_ensure_model__mutmut_2, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_3': xǁHFEmbedderǁ_ensure_model__mutmut_3, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_4': xǁHFEmbedderǁ_ensure_model__mutmut_4, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_5': xǁHFEmbedderǁ_ensure_model__mutmut_5, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_6': xǁHFEmbedderǁ_ensure_model__mutmut_6, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_7': xǁHFEmbedderǁ_ensure_model__mutmut_7, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_8': xǁHFEmbedderǁ_ensure_model__mutmut_8, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_9': xǁHFEmbedderǁ_ensure_model__mutmut_9, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_10': xǁHFEmbedderǁ_ensure_model__mutmut_10, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_11': xǁHFEmbedderǁ_ensure_model__mutmut_11, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_12': xǁHFEmbedderǁ_ensure_model__mutmut_12, 
        'xǁHFEmbedderǁ_ensure_model__mutmut_13': xǁHFEmbedderǁ_ensure_model__mutmut_13
    }
    
    def _ensure_model(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHFEmbedderǁ_ensure_model__mutmut_orig"), object.__getattribute__(self, "xǁHFEmbedderǁ_ensure_model__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _ensure_model.__signature__ = _mutmut_signature(xǁHFEmbedderǁ_ensure_model__mutmut_orig)
    xǁHFEmbedderǁ_ensure_model__mutmut_orig.__name__ = 'xǁHFEmbedderǁ_ensure_model'

    def xǁHFEmbedderǁembed__mutmut_orig(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if not self._model:
            # safe fallback
            return [[0.0] * 1 for _ in texts]
        return self._model.encode(texts).tolist()

    def xǁHFEmbedderǁembed__mutmut_1(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if self._model:
            # safe fallback
            return [[0.0] * 1 for _ in texts]
        return self._model.encode(texts).tolist()

    def xǁHFEmbedderǁembed__mutmut_2(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if not self._model:
            # safe fallback
            return [[0.0] / 1 for _ in texts]
        return self._model.encode(texts).tolist()

    def xǁHFEmbedderǁembed__mutmut_3(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if not self._model:
            # safe fallback
            return [[1.0] * 1 for _ in texts]
        return self._model.encode(texts).tolist()

    def xǁHFEmbedderǁembed__mutmut_4(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if not self._model:
            # safe fallback
            return [[0.0] * 2 for _ in texts]
        return self._model.encode(texts).tolist()

    def xǁHFEmbedderǁembed__mutmut_5(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if not self._model:
            # safe fallback
            return [[0.0] * 1 for _ in texts]
        return self._model.encode(None).tolist()
    
    xǁHFEmbedderǁembed__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHFEmbedderǁembed__mutmut_1': xǁHFEmbedderǁembed__mutmut_1, 
        'xǁHFEmbedderǁembed__mutmut_2': xǁHFEmbedderǁembed__mutmut_2, 
        'xǁHFEmbedderǁembed__mutmut_3': xǁHFEmbedderǁembed__mutmut_3, 
        'xǁHFEmbedderǁembed__mutmut_4': xǁHFEmbedderǁembed__mutmut_4, 
        'xǁHFEmbedderǁembed__mutmut_5': xǁHFEmbedderǁembed__mutmut_5
    }
    
    def embed(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHFEmbedderǁembed__mutmut_orig"), object.__getattribute__(self, "xǁHFEmbedderǁembed__mutmut_mutants"), args, kwargs, self)
        return result 
    
    embed.__signature__ = _mutmut_signature(xǁHFEmbedderǁembed__mutmut_orig)
    xǁHFEmbedderǁembed__mutmut_orig.__name__ = 'xǁHFEmbedderǁembed'

    def xǁHFEmbedderǁhealth_check__mutmut_orig(self) -> dict[str, Any]:
        return {"status": "ok" if self._model is not None else "disconnected", "adapter": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_1(self) -> dict[str, Any]:
        return {"XXstatusXX": "ok" if self._model is not None else "disconnected", "adapter": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_2(self) -> dict[str, Any]:
        return {"STATUS": "ok" if self._model is not None else "disconnected", "adapter": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_3(self) -> dict[str, Any]:
        return {"status": "XXokXX" if self._model is not None else "disconnected", "adapter": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_4(self) -> dict[str, Any]:
        return {"status": "OK" if self._model is not None else "disconnected", "adapter": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_5(self) -> dict[str, Any]:
        return {"status": "ok" if self._model is None else "disconnected", "adapter": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_6(self) -> dict[str, Any]:
        return {"status": "ok" if self._model is not None else "XXdisconnectedXX", "adapter": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_7(self) -> dict[str, Any]:
        return {"status": "ok" if self._model is not None else "DISCONNECTED", "adapter": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_8(self) -> dict[str, Any]:
        return {"status": "ok" if self._model is not None else "disconnected", "XXadapterXX": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_9(self) -> dict[str, Any]:
        return {"status": "ok" if self._model is not None else "disconnected", "ADAPTER": "hf"}

    def xǁHFEmbedderǁhealth_check__mutmut_10(self) -> dict[str, Any]:
        return {"status": "ok" if self._model is not None else "disconnected", "adapter": "XXhfXX"}

    def xǁHFEmbedderǁhealth_check__mutmut_11(self) -> dict[str, Any]:
        return {"status": "ok" if self._model is not None else "disconnected", "adapter": "HF"}
    
    xǁHFEmbedderǁhealth_check__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHFEmbedderǁhealth_check__mutmut_1': xǁHFEmbedderǁhealth_check__mutmut_1, 
        'xǁHFEmbedderǁhealth_check__mutmut_2': xǁHFEmbedderǁhealth_check__mutmut_2, 
        'xǁHFEmbedderǁhealth_check__mutmut_3': xǁHFEmbedderǁhealth_check__mutmut_3, 
        'xǁHFEmbedderǁhealth_check__mutmut_4': xǁHFEmbedderǁhealth_check__mutmut_4, 
        'xǁHFEmbedderǁhealth_check__mutmut_5': xǁHFEmbedderǁhealth_check__mutmut_5, 
        'xǁHFEmbedderǁhealth_check__mutmut_6': xǁHFEmbedderǁhealth_check__mutmut_6, 
        'xǁHFEmbedderǁhealth_check__mutmut_7': xǁHFEmbedderǁhealth_check__mutmut_7, 
        'xǁHFEmbedderǁhealth_check__mutmut_8': xǁHFEmbedderǁhealth_check__mutmut_8, 
        'xǁHFEmbedderǁhealth_check__mutmut_9': xǁHFEmbedderǁhealth_check__mutmut_9, 
        'xǁHFEmbedderǁhealth_check__mutmut_10': xǁHFEmbedderǁhealth_check__mutmut_10, 
        'xǁHFEmbedderǁhealth_check__mutmut_11': xǁHFEmbedderǁhealth_check__mutmut_11
    }
    
    def health_check(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHFEmbedderǁhealth_check__mutmut_orig"), object.__getattribute__(self, "xǁHFEmbedderǁhealth_check__mutmut_mutants"), args, kwargs, self)
        return result 
    
    health_check.__signature__ = _mutmut_signature(xǁHFEmbedderǁhealth_check__mutmut_orig)
    xǁHFEmbedderǁhealth_check__mutmut_orig.__name__ = 'xǁHFEmbedderǁhealth_check'
