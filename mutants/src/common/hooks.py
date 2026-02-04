"""
Hooks Module

This module provides functionality for hooks.

Usage:
    from common.hooks import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore
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


class BaseHook:
    def on_init(self, state: dict[str, Any]) -> None: ...

    def on_step_end(self, state: dict[str, Any]) -> None: ...

    def on_epoch_end(self, state: dict[str, Any]) -> None: ...

    def on_checkpoint(self, state: dict[str, Any]) -> None: ...

    def on_finish(self, state: dict[str, Any]) -> None: ...


class HookManager:
    def xǁHookManagerǁ__init____mutmut_orig(self, hooks: list[BaseHook] | None = None) -> None:
        self.hooks: list[BaseHook] = hooks or []
    def xǁHookManagerǁ__init____mutmut_1(self, hooks: list[BaseHook] | None = None) -> None:
        self.hooks: list[BaseHook] = None
    def xǁHookManagerǁ__init____mutmut_2(self, hooks: list[BaseHook] | None = None) -> None:
        self.hooks: list[BaseHook] = hooks and []
    
    xǁHookManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHookManagerǁ__init____mutmut_1': xǁHookManagerǁ__init____mutmut_1, 
        'xǁHookManagerǁ__init____mutmut_2': xǁHookManagerǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHookManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁHookManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁHookManagerǁ__init____mutmut_orig)
    xǁHookManagerǁ__init____mutmut_orig.__name__ = 'xǁHookManagerǁ__init__'

    def xǁHookManagerǁadd__mutmut_orig(self, hook: BaseHook) -> None:
        self.hooks.append(hook)

    def xǁHookManagerǁadd__mutmut_1(self, hook: BaseHook) -> None:
        self.hooks.append(None)
    
    xǁHookManagerǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHookManagerǁadd__mutmut_1': xǁHookManagerǁadd__mutmut_1
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHookManagerǁadd__mutmut_orig"), object.__getattribute__(self, "xǁHookManagerǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁHookManagerǁadd__mutmut_orig)
    xǁHookManagerǁadd__mutmut_orig.__name__ = 'xǁHookManagerǁadd'

    def xǁHookManagerǁdispatch__mutmut_orig(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_1(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(None)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_2(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(None, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_3(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, None)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_4(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_5(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, )(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_6(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(None, hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_7(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", None, name, exc)

    def xǁHookManagerǁdispatch__mutmut_8(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, None, exc)

    def xǁHookManagerǁdispatch__mutmut_9(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, None)

    def xǁHookManagerǁdispatch__mutmut_10(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_11(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", name, exc)

    def xǁHookManagerǁdispatch__mutmut_12(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, exc)

    def xǁHookManagerǁdispatch__mutmut_13(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, )

    def xǁHookManagerǁdispatch__mutmut_14(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("XXHook %s.%s error: %sXX", hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_15(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("hook %s.%s error: %s", hook.__class__.__name__, name, exc)

    def xǁHookManagerǁdispatch__mutmut_16(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("HOOK %S.%S ERROR: %S", hook.__class__.__name__, name, exc)
    
    xǁHookManagerǁdispatch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHookManagerǁdispatch__mutmut_1': xǁHookManagerǁdispatch__mutmut_1, 
        'xǁHookManagerǁdispatch__mutmut_2': xǁHookManagerǁdispatch__mutmut_2, 
        'xǁHookManagerǁdispatch__mutmut_3': xǁHookManagerǁdispatch__mutmut_3, 
        'xǁHookManagerǁdispatch__mutmut_4': xǁHookManagerǁdispatch__mutmut_4, 
        'xǁHookManagerǁdispatch__mutmut_5': xǁHookManagerǁdispatch__mutmut_5, 
        'xǁHookManagerǁdispatch__mutmut_6': xǁHookManagerǁdispatch__mutmut_6, 
        'xǁHookManagerǁdispatch__mutmut_7': xǁHookManagerǁdispatch__mutmut_7, 
        'xǁHookManagerǁdispatch__mutmut_8': xǁHookManagerǁdispatch__mutmut_8, 
        'xǁHookManagerǁdispatch__mutmut_9': xǁHookManagerǁdispatch__mutmut_9, 
        'xǁHookManagerǁdispatch__mutmut_10': xǁHookManagerǁdispatch__mutmut_10, 
        'xǁHookManagerǁdispatch__mutmut_11': xǁHookManagerǁdispatch__mutmut_11, 
        'xǁHookManagerǁdispatch__mutmut_12': xǁHookManagerǁdispatch__mutmut_12, 
        'xǁHookManagerǁdispatch__mutmut_13': xǁHookManagerǁdispatch__mutmut_13, 
        'xǁHookManagerǁdispatch__mutmut_14': xǁHookManagerǁdispatch__mutmut_14, 
        'xǁHookManagerǁdispatch__mutmut_15': xǁHookManagerǁdispatch__mutmut_15, 
        'xǁHookManagerǁdispatch__mutmut_16': xǁHookManagerǁdispatch__mutmut_16
    }
    
    def dispatch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHookManagerǁdispatch__mutmut_orig"), object.__getattribute__(self, "xǁHookManagerǁdispatch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    dispatch.__signature__ = _mutmut_signature(xǁHookManagerǁdispatch__mutmut_orig)
    xǁHookManagerǁdispatch__mutmut_orig.__name__ = 'xǁHookManagerǁdispatch'


class EMAHook(BaseHook):
    """Maintain an exponential moving average of model parameters."""

    def xǁEMAHookǁ__init____mutmut_orig(self, decay: float = 0.999) -> None:
        self.decay = decay
        self.shadow: dict[str, Any] = {}

    def xǁEMAHookǁ__init____mutmut_1(self, decay: float = 1.999) -> None:
        self.decay = decay
        self.shadow: dict[str, Any] = {}

    def xǁEMAHookǁ__init____mutmut_2(self, decay: float = 0.999) -> None:
        self.decay = None
        self.shadow: dict[str, Any] = {}

    def xǁEMAHookǁ__init____mutmut_3(self, decay: float = 0.999) -> None:
        self.decay = decay
        self.shadow: dict[str, Any] = None
    
    xǁEMAHookǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEMAHookǁ__init____mutmut_1': xǁEMAHookǁ__init____mutmut_1, 
        'xǁEMAHookǁ__init____mutmut_2': xǁEMAHookǁ__init____mutmut_2, 
        'xǁEMAHookǁ__init____mutmut_3': xǁEMAHookǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEMAHookǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁEMAHookǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁEMAHookǁ__init____mutmut_orig)
    xǁEMAHookǁ__init____mutmut_orig.__name__ = 'xǁEMAHookǁ__init__'

    def xǁEMAHookǁon_init__mutmut_orig(self, state: dict[str, Any]) -> None:
        if torch is None:
            return
        model = state.get("model")
        if model is None:
            return
        self.shadow = {name: param.detach().clone() for name, param in model.state_dict().items()}

    def xǁEMAHookǁon_init__mutmut_1(self, state: dict[str, Any]) -> None:
        if torch is not None:
            return
        model = state.get("model")
        if model is None:
            return
        self.shadow = {name: param.detach().clone() for name, param in model.state_dict().items()}

    def xǁEMAHookǁon_init__mutmut_2(self, state: dict[str, Any]) -> None:
        if torch is None:
            return
        model = None
        if model is None:
            return
        self.shadow = {name: param.detach().clone() for name, param in model.state_dict().items()}

    def xǁEMAHookǁon_init__mutmut_3(self, state: dict[str, Any]) -> None:
        if torch is None:
            return
        model = state.get(None)
        if model is None:
            return
        self.shadow = {name: param.detach().clone() for name, param in model.state_dict().items()}

    def xǁEMAHookǁon_init__mutmut_4(self, state: dict[str, Any]) -> None:
        if torch is None:
            return
        model = state.get("XXmodelXX")
        if model is None:
            return
        self.shadow = {name: param.detach().clone() for name, param in model.state_dict().items()}

    def xǁEMAHookǁon_init__mutmut_5(self, state: dict[str, Any]) -> None:
        if torch is None:
            return
        model = state.get("MODEL")
        if model is None:
            return
        self.shadow = {name: param.detach().clone() for name, param in model.state_dict().items()}

    def xǁEMAHookǁon_init__mutmut_6(self, state: dict[str, Any]) -> None:
        if torch is None:
            return
        model = state.get("model")
        if model is not None:
            return
        self.shadow = {name: param.detach().clone() for name, param in model.state_dict().items()}

    def xǁEMAHookǁon_init__mutmut_7(self, state: dict[str, Any]) -> None:
        if torch is None:
            return
        model = state.get("model")
        if model is None:
            return
        self.shadow = None
    
    xǁEMAHookǁon_init__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEMAHookǁon_init__mutmut_1': xǁEMAHookǁon_init__mutmut_1, 
        'xǁEMAHookǁon_init__mutmut_2': xǁEMAHookǁon_init__mutmut_2, 
        'xǁEMAHookǁon_init__mutmut_3': xǁEMAHookǁon_init__mutmut_3, 
        'xǁEMAHookǁon_init__mutmut_4': xǁEMAHookǁon_init__mutmut_4, 
        'xǁEMAHookǁon_init__mutmut_5': xǁEMAHookǁon_init__mutmut_5, 
        'xǁEMAHookǁon_init__mutmut_6': xǁEMAHookǁon_init__mutmut_6, 
        'xǁEMAHookǁon_init__mutmut_7': xǁEMAHookǁon_init__mutmut_7
    }
    
    def on_init(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEMAHookǁon_init__mutmut_orig"), object.__getattribute__(self, "xǁEMAHookǁon_init__mutmut_mutants"), args, kwargs, self)
        return result 
    
    on_init.__signature__ = _mutmut_signature(xǁEMAHookǁon_init__mutmut_orig)
    xǁEMAHookǁon_init__mutmut_orig.__name__ = 'xǁEMAHookǁon_init'

    def xǁEMAHookǁon_step_end__mutmut_orig(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_1(self, state: dict[str, Any]) -> None:
        if torch is None and not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_2(self, state: dict[str, Any]) -> None:
        if torch is not None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_3(self, state: dict[str, Any]) -> None:
        if torch is None or self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_4(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = None
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_5(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get(None)
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_6(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("XXmodelXX")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_7(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("MODEL")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_8(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is not None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_9(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name not in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_10(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(None, alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_11(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=None)

    def xǁEMAHookǁon_step_end__mutmut_12(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_13(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), )

    def xǁEMAHookǁon_step_end__mutmut_14(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(None).add_(param.detach(), alpha=1.0 - self.decay)

    def xǁEMAHookǁon_step_end__mutmut_15(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 + self.decay)

    def xǁEMAHookǁon_step_end__mutmut_16(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=2.0 - self.decay)
    
    xǁEMAHookǁon_step_end__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEMAHookǁon_step_end__mutmut_1': xǁEMAHookǁon_step_end__mutmut_1, 
        'xǁEMAHookǁon_step_end__mutmut_2': xǁEMAHookǁon_step_end__mutmut_2, 
        'xǁEMAHookǁon_step_end__mutmut_3': xǁEMAHookǁon_step_end__mutmut_3, 
        'xǁEMAHookǁon_step_end__mutmut_4': xǁEMAHookǁon_step_end__mutmut_4, 
        'xǁEMAHookǁon_step_end__mutmut_5': xǁEMAHookǁon_step_end__mutmut_5, 
        'xǁEMAHookǁon_step_end__mutmut_6': xǁEMAHookǁon_step_end__mutmut_6, 
        'xǁEMAHookǁon_step_end__mutmut_7': xǁEMAHookǁon_step_end__mutmut_7, 
        'xǁEMAHookǁon_step_end__mutmut_8': xǁEMAHookǁon_step_end__mutmut_8, 
        'xǁEMAHookǁon_step_end__mutmut_9': xǁEMAHookǁon_step_end__mutmut_9, 
        'xǁEMAHookǁon_step_end__mutmut_10': xǁEMAHookǁon_step_end__mutmut_10, 
        'xǁEMAHookǁon_step_end__mutmut_11': xǁEMAHookǁon_step_end__mutmut_11, 
        'xǁEMAHookǁon_step_end__mutmut_12': xǁEMAHookǁon_step_end__mutmut_12, 
        'xǁEMAHookǁon_step_end__mutmut_13': xǁEMAHookǁon_step_end__mutmut_13, 
        'xǁEMAHookǁon_step_end__mutmut_14': xǁEMAHookǁon_step_end__mutmut_14, 
        'xǁEMAHookǁon_step_end__mutmut_15': xǁEMAHookǁon_step_end__mutmut_15, 
        'xǁEMAHookǁon_step_end__mutmut_16': xǁEMAHookǁon_step_end__mutmut_16
    }
    
    def on_step_end(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEMAHookǁon_step_end__mutmut_orig"), object.__getattribute__(self, "xǁEMAHookǁon_step_end__mutmut_mutants"), args, kwargs, self)
        return result 
    
    on_step_end.__signature__ = _mutmut_signature(xǁEMAHookǁon_step_end__mutmut_orig)
    xǁEMAHookǁon_step_end__mutmut_orig.__name__ = 'xǁEMAHookǁon_step_end'

    def xǁEMAHookǁon_checkpoint__mutmut_orig(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_1(self, state: dict[str, Any]) -> None:
        if torch is None and not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_2(self, state: dict[str, Any]) -> None:
        if torch is not None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_3(self, state: dict[str, Any]) -> None:
        if torch is None or self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_4(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = None
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_5(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get(None)
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_6(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("XXcheckpoint_dirXX")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_7(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("CHECKPOINT_DIR")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_8(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is not None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_9(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(None, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_10(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, None)
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_11(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_12(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, )
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_13(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) * "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_14(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(None) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_15(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "XXema.ptXX")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_16(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "EMA.PT")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_17(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning(None, exc)

    def xǁEMAHookǁon_checkpoint__mutmut_18(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", None)

    def xǁEMAHookǁon_checkpoint__mutmut_19(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning(exc)

    def xǁEMAHookǁon_checkpoint__mutmut_20(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", )

    def xǁEMAHookǁon_checkpoint__mutmut_21(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("XXEMAHook save failed: %sXX", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_22(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("emahook save failed: %s", exc)

    def xǁEMAHookǁon_checkpoint__mutmut_23(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHOOK SAVE FAILED: %S", exc)
    
    xǁEMAHookǁon_checkpoint__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEMAHookǁon_checkpoint__mutmut_1': xǁEMAHookǁon_checkpoint__mutmut_1, 
        'xǁEMAHookǁon_checkpoint__mutmut_2': xǁEMAHookǁon_checkpoint__mutmut_2, 
        'xǁEMAHookǁon_checkpoint__mutmut_3': xǁEMAHookǁon_checkpoint__mutmut_3, 
        'xǁEMAHookǁon_checkpoint__mutmut_4': xǁEMAHookǁon_checkpoint__mutmut_4, 
        'xǁEMAHookǁon_checkpoint__mutmut_5': xǁEMAHookǁon_checkpoint__mutmut_5, 
        'xǁEMAHookǁon_checkpoint__mutmut_6': xǁEMAHookǁon_checkpoint__mutmut_6, 
        'xǁEMAHookǁon_checkpoint__mutmut_7': xǁEMAHookǁon_checkpoint__mutmut_7, 
        'xǁEMAHookǁon_checkpoint__mutmut_8': xǁEMAHookǁon_checkpoint__mutmut_8, 
        'xǁEMAHookǁon_checkpoint__mutmut_9': xǁEMAHookǁon_checkpoint__mutmut_9, 
        'xǁEMAHookǁon_checkpoint__mutmut_10': xǁEMAHookǁon_checkpoint__mutmut_10, 
        'xǁEMAHookǁon_checkpoint__mutmut_11': xǁEMAHookǁon_checkpoint__mutmut_11, 
        'xǁEMAHookǁon_checkpoint__mutmut_12': xǁEMAHookǁon_checkpoint__mutmut_12, 
        'xǁEMAHookǁon_checkpoint__mutmut_13': xǁEMAHookǁon_checkpoint__mutmut_13, 
        'xǁEMAHookǁon_checkpoint__mutmut_14': xǁEMAHookǁon_checkpoint__mutmut_14, 
        'xǁEMAHookǁon_checkpoint__mutmut_15': xǁEMAHookǁon_checkpoint__mutmut_15, 
        'xǁEMAHookǁon_checkpoint__mutmut_16': xǁEMAHookǁon_checkpoint__mutmut_16, 
        'xǁEMAHookǁon_checkpoint__mutmut_17': xǁEMAHookǁon_checkpoint__mutmut_17, 
        'xǁEMAHookǁon_checkpoint__mutmut_18': xǁEMAHookǁon_checkpoint__mutmut_18, 
        'xǁEMAHookǁon_checkpoint__mutmut_19': xǁEMAHookǁon_checkpoint__mutmut_19, 
        'xǁEMAHookǁon_checkpoint__mutmut_20': xǁEMAHookǁon_checkpoint__mutmut_20, 
        'xǁEMAHookǁon_checkpoint__mutmut_21': xǁEMAHookǁon_checkpoint__mutmut_21, 
        'xǁEMAHookǁon_checkpoint__mutmut_22': xǁEMAHookǁon_checkpoint__mutmut_22, 
        'xǁEMAHookǁon_checkpoint__mutmut_23': xǁEMAHookǁon_checkpoint__mutmut_23
    }
    
    def on_checkpoint(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEMAHookǁon_checkpoint__mutmut_orig"), object.__getattribute__(self, "xǁEMAHookǁon_checkpoint__mutmut_mutants"), args, kwargs, self)
        return result 
    
    on_checkpoint.__signature__ = _mutmut_signature(xǁEMAHookǁon_checkpoint__mutmut_orig)
    xǁEMAHookǁon_checkpoint__mutmut_orig.__name__ = 'xǁEMAHookǁon_checkpoint'


class CheckpointHook(BaseHook):
    def xǁCheckpointHookǁ__init____mutmut_orig(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_1(
        self, every_steps: int = 101, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_2(
        self, every_steps: int = 100, out_dir: str | Path = "XXdata/models/checkpointsXX"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_3(
        self, every_steps: int = 100, out_dir: str | Path = "DATA/MODELS/CHECKPOINTS"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_4(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = None
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_5(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(None, 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_6(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), None)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_7(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_8(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), )
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_9(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(None), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_10(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 2)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_11(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = None
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_12(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(None)
        self.out_dir.mkdir(parents=True, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_13(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=None, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_14(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=None)
    def xǁCheckpointHookǁ__init____mutmut_15(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_16(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, )
    def xǁCheckpointHookǁ__init____mutmut_17(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=False, exist_ok=True)
    def xǁCheckpointHookǁ__init____mutmut_18(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=False)
    
    xǁCheckpointHookǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCheckpointHookǁ__init____mutmut_1': xǁCheckpointHookǁ__init____mutmut_1, 
        'xǁCheckpointHookǁ__init____mutmut_2': xǁCheckpointHookǁ__init____mutmut_2, 
        'xǁCheckpointHookǁ__init____mutmut_3': xǁCheckpointHookǁ__init____mutmut_3, 
        'xǁCheckpointHookǁ__init____mutmut_4': xǁCheckpointHookǁ__init____mutmut_4, 
        'xǁCheckpointHookǁ__init____mutmut_5': xǁCheckpointHookǁ__init____mutmut_5, 
        'xǁCheckpointHookǁ__init____mutmut_6': xǁCheckpointHookǁ__init____mutmut_6, 
        'xǁCheckpointHookǁ__init____mutmut_7': xǁCheckpointHookǁ__init____mutmut_7, 
        'xǁCheckpointHookǁ__init____mutmut_8': xǁCheckpointHookǁ__init____mutmut_8, 
        'xǁCheckpointHookǁ__init____mutmut_9': xǁCheckpointHookǁ__init____mutmut_9, 
        'xǁCheckpointHookǁ__init____mutmut_10': xǁCheckpointHookǁ__init____mutmut_10, 
        'xǁCheckpointHookǁ__init____mutmut_11': xǁCheckpointHookǁ__init____mutmut_11, 
        'xǁCheckpointHookǁ__init____mutmut_12': xǁCheckpointHookǁ__init____mutmut_12, 
        'xǁCheckpointHookǁ__init____mutmut_13': xǁCheckpointHookǁ__init____mutmut_13, 
        'xǁCheckpointHookǁ__init____mutmut_14': xǁCheckpointHookǁ__init____mutmut_14, 
        'xǁCheckpointHookǁ__init____mutmut_15': xǁCheckpointHookǁ__init____mutmut_15, 
        'xǁCheckpointHookǁ__init____mutmut_16': xǁCheckpointHookǁ__init____mutmut_16, 
        'xǁCheckpointHookǁ__init____mutmut_17': xǁCheckpointHookǁ__init____mutmut_17, 
        'xǁCheckpointHookǁ__init____mutmut_18': xǁCheckpointHookǁ__init____mutmut_18
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCheckpointHookǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCheckpointHookǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCheckpointHookǁ__init____mutmut_orig)
    xǁCheckpointHookǁ__init____mutmut_orig.__name__ = 'xǁCheckpointHookǁ__init__'

    def xǁCheckpointHookǁon_step_end__mutmut_orig(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_1(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop(None, None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_2(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop(None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_3(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", )
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_4(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("XXcheckpoint_dirXX", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_5(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("CHECKPOINT_DIR", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_6(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is not None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_7(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = None
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_8(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(None)
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_9(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get(None, 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_10(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", None))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_11(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get(0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_12(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", ))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_13(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("XXglobal_stepXX", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_14(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("GLOBAL_STEP", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_15(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 1))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_16(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 and step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_17(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step < 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_18(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 1 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_19(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step / self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_20(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps == 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_21(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 1:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_22(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = None
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_23(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get(None)
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_24(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("XXmodelXX")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_25(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("MODEL")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_26(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None and not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_27(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is not None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_28(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_29(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(None, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_30(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, None):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_31(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr("state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_32(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, ):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_33(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "XXstate_dictXX"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_34(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "STATE_DICT"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_35(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = None
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_36(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir * f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_37(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(None, ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_38(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), None)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_39(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_40(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), )
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_41(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = None
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_42(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["XXcheckpoint_dirXX"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_43(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["CHECKPOINT_DIR"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_44(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(None)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_45(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning(None, exc)

    def xǁCheckpointHookǁon_step_end__mutmut_46(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", None)

    def xǁCheckpointHookǁon_step_end__mutmut_47(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning(exc)

    def xǁCheckpointHookǁon_step_end__mutmut_48(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", )

    def xǁCheckpointHookǁon_step_end__mutmut_49(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("XXCheckpoint save failed: %sXX", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_50(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("checkpoint save failed: %s", exc)

    def xǁCheckpointHookǁon_step_end__mutmut_51(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("CHECKPOINT SAVE FAILED: %S", exc)
    
    xǁCheckpointHookǁon_step_end__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCheckpointHookǁon_step_end__mutmut_1': xǁCheckpointHookǁon_step_end__mutmut_1, 
        'xǁCheckpointHookǁon_step_end__mutmut_2': xǁCheckpointHookǁon_step_end__mutmut_2, 
        'xǁCheckpointHookǁon_step_end__mutmut_3': xǁCheckpointHookǁon_step_end__mutmut_3, 
        'xǁCheckpointHookǁon_step_end__mutmut_4': xǁCheckpointHookǁon_step_end__mutmut_4, 
        'xǁCheckpointHookǁon_step_end__mutmut_5': xǁCheckpointHookǁon_step_end__mutmut_5, 
        'xǁCheckpointHookǁon_step_end__mutmut_6': xǁCheckpointHookǁon_step_end__mutmut_6, 
        'xǁCheckpointHookǁon_step_end__mutmut_7': xǁCheckpointHookǁon_step_end__mutmut_7, 
        'xǁCheckpointHookǁon_step_end__mutmut_8': xǁCheckpointHookǁon_step_end__mutmut_8, 
        'xǁCheckpointHookǁon_step_end__mutmut_9': xǁCheckpointHookǁon_step_end__mutmut_9, 
        'xǁCheckpointHookǁon_step_end__mutmut_10': xǁCheckpointHookǁon_step_end__mutmut_10, 
        'xǁCheckpointHookǁon_step_end__mutmut_11': xǁCheckpointHookǁon_step_end__mutmut_11, 
        'xǁCheckpointHookǁon_step_end__mutmut_12': xǁCheckpointHookǁon_step_end__mutmut_12, 
        'xǁCheckpointHookǁon_step_end__mutmut_13': xǁCheckpointHookǁon_step_end__mutmut_13, 
        'xǁCheckpointHookǁon_step_end__mutmut_14': xǁCheckpointHookǁon_step_end__mutmut_14, 
        'xǁCheckpointHookǁon_step_end__mutmut_15': xǁCheckpointHookǁon_step_end__mutmut_15, 
        'xǁCheckpointHookǁon_step_end__mutmut_16': xǁCheckpointHookǁon_step_end__mutmut_16, 
        'xǁCheckpointHookǁon_step_end__mutmut_17': xǁCheckpointHookǁon_step_end__mutmut_17, 
        'xǁCheckpointHookǁon_step_end__mutmut_18': xǁCheckpointHookǁon_step_end__mutmut_18, 
        'xǁCheckpointHookǁon_step_end__mutmut_19': xǁCheckpointHookǁon_step_end__mutmut_19, 
        'xǁCheckpointHookǁon_step_end__mutmut_20': xǁCheckpointHookǁon_step_end__mutmut_20, 
        'xǁCheckpointHookǁon_step_end__mutmut_21': xǁCheckpointHookǁon_step_end__mutmut_21, 
        'xǁCheckpointHookǁon_step_end__mutmut_22': xǁCheckpointHookǁon_step_end__mutmut_22, 
        'xǁCheckpointHookǁon_step_end__mutmut_23': xǁCheckpointHookǁon_step_end__mutmut_23, 
        'xǁCheckpointHookǁon_step_end__mutmut_24': xǁCheckpointHookǁon_step_end__mutmut_24, 
        'xǁCheckpointHookǁon_step_end__mutmut_25': xǁCheckpointHookǁon_step_end__mutmut_25, 
        'xǁCheckpointHookǁon_step_end__mutmut_26': xǁCheckpointHookǁon_step_end__mutmut_26, 
        'xǁCheckpointHookǁon_step_end__mutmut_27': xǁCheckpointHookǁon_step_end__mutmut_27, 
        'xǁCheckpointHookǁon_step_end__mutmut_28': xǁCheckpointHookǁon_step_end__mutmut_28, 
        'xǁCheckpointHookǁon_step_end__mutmut_29': xǁCheckpointHookǁon_step_end__mutmut_29, 
        'xǁCheckpointHookǁon_step_end__mutmut_30': xǁCheckpointHookǁon_step_end__mutmut_30, 
        'xǁCheckpointHookǁon_step_end__mutmut_31': xǁCheckpointHookǁon_step_end__mutmut_31, 
        'xǁCheckpointHookǁon_step_end__mutmut_32': xǁCheckpointHookǁon_step_end__mutmut_32, 
        'xǁCheckpointHookǁon_step_end__mutmut_33': xǁCheckpointHookǁon_step_end__mutmut_33, 
        'xǁCheckpointHookǁon_step_end__mutmut_34': xǁCheckpointHookǁon_step_end__mutmut_34, 
        'xǁCheckpointHookǁon_step_end__mutmut_35': xǁCheckpointHookǁon_step_end__mutmut_35, 
        'xǁCheckpointHookǁon_step_end__mutmut_36': xǁCheckpointHookǁon_step_end__mutmut_36, 
        'xǁCheckpointHookǁon_step_end__mutmut_37': xǁCheckpointHookǁon_step_end__mutmut_37, 
        'xǁCheckpointHookǁon_step_end__mutmut_38': xǁCheckpointHookǁon_step_end__mutmut_38, 
        'xǁCheckpointHookǁon_step_end__mutmut_39': xǁCheckpointHookǁon_step_end__mutmut_39, 
        'xǁCheckpointHookǁon_step_end__mutmut_40': xǁCheckpointHookǁon_step_end__mutmut_40, 
        'xǁCheckpointHookǁon_step_end__mutmut_41': xǁCheckpointHookǁon_step_end__mutmut_41, 
        'xǁCheckpointHookǁon_step_end__mutmut_42': xǁCheckpointHookǁon_step_end__mutmut_42, 
        'xǁCheckpointHookǁon_step_end__mutmut_43': xǁCheckpointHookǁon_step_end__mutmut_43, 
        'xǁCheckpointHookǁon_step_end__mutmut_44': xǁCheckpointHookǁon_step_end__mutmut_44, 
        'xǁCheckpointHookǁon_step_end__mutmut_45': xǁCheckpointHookǁon_step_end__mutmut_45, 
        'xǁCheckpointHookǁon_step_end__mutmut_46': xǁCheckpointHookǁon_step_end__mutmut_46, 
        'xǁCheckpointHookǁon_step_end__mutmut_47': xǁCheckpointHookǁon_step_end__mutmut_47, 
        'xǁCheckpointHookǁon_step_end__mutmut_48': xǁCheckpointHookǁon_step_end__mutmut_48, 
        'xǁCheckpointHookǁon_step_end__mutmut_49': xǁCheckpointHookǁon_step_end__mutmut_49, 
        'xǁCheckpointHookǁon_step_end__mutmut_50': xǁCheckpointHookǁon_step_end__mutmut_50, 
        'xǁCheckpointHookǁon_step_end__mutmut_51': xǁCheckpointHookǁon_step_end__mutmut_51
    }
    
    def on_step_end(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCheckpointHookǁon_step_end__mutmut_orig"), object.__getattribute__(self, "xǁCheckpointHookǁon_step_end__mutmut_mutants"), args, kwargs, self)
        return result 
    
    on_step_end.__signature__ = _mutmut_signature(xǁCheckpointHookǁon_step_end__mutmut_orig)
    xǁCheckpointHookǁon_step_end__mutmut_orig.__name__ = 'xǁCheckpointHookǁon_step_end'


class NDJSONLogHook(BaseHook):
    def xǁNDJSONLogHookǁ__init____mutmut_orig(self, file: str | Path) -> None:
        self.file = Path(file)
        self.file.parent.mkdir(parents=True, exist_ok=True)
    def xǁNDJSONLogHookǁ__init____mutmut_1(self, file: str | Path) -> None:
        self.file = None
        self.file.parent.mkdir(parents=True, exist_ok=True)
    def xǁNDJSONLogHookǁ__init____mutmut_2(self, file: str | Path) -> None:
        self.file = Path(None)
        self.file.parent.mkdir(parents=True, exist_ok=True)
    def xǁNDJSONLogHookǁ__init____mutmut_3(self, file: str | Path) -> None:
        self.file = Path(file)
        self.file.parent.mkdir(parents=None, exist_ok=True)
    def xǁNDJSONLogHookǁ__init____mutmut_4(self, file: str | Path) -> None:
        self.file = Path(file)
        self.file.parent.mkdir(parents=True, exist_ok=None)
    def xǁNDJSONLogHookǁ__init____mutmut_5(self, file: str | Path) -> None:
        self.file = Path(file)
        self.file.parent.mkdir(exist_ok=True)
    def xǁNDJSONLogHookǁ__init____mutmut_6(self, file: str | Path) -> None:
        self.file = Path(file)
        self.file.parent.mkdir(parents=True, )
    def xǁNDJSONLogHookǁ__init____mutmut_7(self, file: str | Path) -> None:
        self.file = Path(file)
        self.file.parent.mkdir(parents=False, exist_ok=True)
    def xǁNDJSONLogHookǁ__init____mutmut_8(self, file: str | Path) -> None:
        self.file = Path(file)
        self.file.parent.mkdir(parents=True, exist_ok=False)
    
    xǁNDJSONLogHookǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNDJSONLogHookǁ__init____mutmut_1': xǁNDJSONLogHookǁ__init____mutmut_1, 
        'xǁNDJSONLogHookǁ__init____mutmut_2': xǁNDJSONLogHookǁ__init____mutmut_2, 
        'xǁNDJSONLogHookǁ__init____mutmut_3': xǁNDJSONLogHookǁ__init____mutmut_3, 
        'xǁNDJSONLogHookǁ__init____mutmut_4': xǁNDJSONLogHookǁ__init____mutmut_4, 
        'xǁNDJSONLogHookǁ__init____mutmut_5': xǁNDJSONLogHookǁ__init____mutmut_5, 
        'xǁNDJSONLogHookǁ__init____mutmut_6': xǁNDJSONLogHookǁ__init____mutmut_6, 
        'xǁNDJSONLogHookǁ__init____mutmut_7': xǁNDJSONLogHookǁ__init____mutmut_7, 
        'xǁNDJSONLogHookǁ__init____mutmut_8': xǁNDJSONLogHookǁ__init____mutmut_8
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNDJSONLogHookǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁNDJSONLogHookǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁNDJSONLogHookǁ__init____mutmut_orig)
    xǁNDJSONLogHookǁ__init____mutmut_orig.__name__ = 'xǁNDJSONLogHookǁ__init__'

    def xǁNDJSONLogHookǁon_step_end__mutmut_orig(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_1(self, state: dict[str, Any]) -> None:
        record = None
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_2(self, state: dict[str, Any]) -> None:
        record = {
            "XXtsXX": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_3(self, state: dict[str, Any]) -> None:
        record = {
            "TS": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_4(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(None),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_5(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "XXstepXX": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_6(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "STEP": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_7(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(None),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_8(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get(None, 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_9(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", None)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_10(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get(0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_11(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", )),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_12(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("XXglobal_stepXX", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_13(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("GLOBAL_STEP", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_14(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 1)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_15(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "XXepochXX": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_16(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "EPOCH": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_17(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(None),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_18(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get(None, 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_19(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", None)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_20(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get(0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_21(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", )),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_22(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("XXepochXX", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_23(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("EPOCH", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_24(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 1)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_25(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "XXlossXX": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_26(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "LOSS": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_27(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(None) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_28(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get(None)) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_29(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("XXlast_lossXX")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_30(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("LAST_LOSS")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_31(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get(None) is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_32(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("XXlast_lossXX") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_33(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("LAST_LOSS") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_34(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_35(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open(None, encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_36(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding=None) as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_37(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open(encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_38(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", ) as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_39(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("XXaXX", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_40(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("A", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_41(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="XXutf-8XX") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_42(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="UTF-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_43(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(None)
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_44(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) - "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_45(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(None) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_46(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "XX\nXX")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_47(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug(None, exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_48(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", None)

    def xǁNDJSONLogHookǁon_step_end__mutmut_49(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug(exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_50(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", )

    def xǁNDJSONLogHookǁon_step_end__mutmut_51(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("XXNDJSONLogHook failed to append record: %sXX", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_52(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("ndjsonloghook failed to append record: %s", exc)

    def xǁNDJSONLogHookǁon_step_end__mutmut_53(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLOGHOOK FAILED TO APPEND RECORD: %S", exc)
    
    xǁNDJSONLogHookǁon_step_end__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁNDJSONLogHookǁon_step_end__mutmut_1': xǁNDJSONLogHookǁon_step_end__mutmut_1, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_2': xǁNDJSONLogHookǁon_step_end__mutmut_2, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_3': xǁNDJSONLogHookǁon_step_end__mutmut_3, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_4': xǁNDJSONLogHookǁon_step_end__mutmut_4, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_5': xǁNDJSONLogHookǁon_step_end__mutmut_5, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_6': xǁNDJSONLogHookǁon_step_end__mutmut_6, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_7': xǁNDJSONLogHookǁon_step_end__mutmut_7, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_8': xǁNDJSONLogHookǁon_step_end__mutmut_8, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_9': xǁNDJSONLogHookǁon_step_end__mutmut_9, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_10': xǁNDJSONLogHookǁon_step_end__mutmut_10, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_11': xǁNDJSONLogHookǁon_step_end__mutmut_11, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_12': xǁNDJSONLogHookǁon_step_end__mutmut_12, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_13': xǁNDJSONLogHookǁon_step_end__mutmut_13, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_14': xǁNDJSONLogHookǁon_step_end__mutmut_14, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_15': xǁNDJSONLogHookǁon_step_end__mutmut_15, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_16': xǁNDJSONLogHookǁon_step_end__mutmut_16, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_17': xǁNDJSONLogHookǁon_step_end__mutmut_17, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_18': xǁNDJSONLogHookǁon_step_end__mutmut_18, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_19': xǁNDJSONLogHookǁon_step_end__mutmut_19, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_20': xǁNDJSONLogHookǁon_step_end__mutmut_20, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_21': xǁNDJSONLogHookǁon_step_end__mutmut_21, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_22': xǁNDJSONLogHookǁon_step_end__mutmut_22, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_23': xǁNDJSONLogHookǁon_step_end__mutmut_23, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_24': xǁNDJSONLogHookǁon_step_end__mutmut_24, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_25': xǁNDJSONLogHookǁon_step_end__mutmut_25, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_26': xǁNDJSONLogHookǁon_step_end__mutmut_26, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_27': xǁNDJSONLogHookǁon_step_end__mutmut_27, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_28': xǁNDJSONLogHookǁon_step_end__mutmut_28, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_29': xǁNDJSONLogHookǁon_step_end__mutmut_29, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_30': xǁNDJSONLogHookǁon_step_end__mutmut_30, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_31': xǁNDJSONLogHookǁon_step_end__mutmut_31, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_32': xǁNDJSONLogHookǁon_step_end__mutmut_32, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_33': xǁNDJSONLogHookǁon_step_end__mutmut_33, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_34': xǁNDJSONLogHookǁon_step_end__mutmut_34, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_35': xǁNDJSONLogHookǁon_step_end__mutmut_35, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_36': xǁNDJSONLogHookǁon_step_end__mutmut_36, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_37': xǁNDJSONLogHookǁon_step_end__mutmut_37, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_38': xǁNDJSONLogHookǁon_step_end__mutmut_38, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_39': xǁNDJSONLogHookǁon_step_end__mutmut_39, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_40': xǁNDJSONLogHookǁon_step_end__mutmut_40, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_41': xǁNDJSONLogHookǁon_step_end__mutmut_41, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_42': xǁNDJSONLogHookǁon_step_end__mutmut_42, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_43': xǁNDJSONLogHookǁon_step_end__mutmut_43, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_44': xǁNDJSONLogHookǁon_step_end__mutmut_44, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_45': xǁNDJSONLogHookǁon_step_end__mutmut_45, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_46': xǁNDJSONLogHookǁon_step_end__mutmut_46, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_47': xǁNDJSONLogHookǁon_step_end__mutmut_47, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_48': xǁNDJSONLogHookǁon_step_end__mutmut_48, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_49': xǁNDJSONLogHookǁon_step_end__mutmut_49, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_50': xǁNDJSONLogHookǁon_step_end__mutmut_50, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_51': xǁNDJSONLogHookǁon_step_end__mutmut_51, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_52': xǁNDJSONLogHookǁon_step_end__mutmut_52, 
        'xǁNDJSONLogHookǁon_step_end__mutmut_53': xǁNDJSONLogHookǁon_step_end__mutmut_53
    }
    
    def on_step_end(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁNDJSONLogHookǁon_step_end__mutmut_orig"), object.__getattribute__(self, "xǁNDJSONLogHookǁon_step_end__mutmut_mutants"), args, kwargs, self)
        return result 
    
    on_step_end.__signature__ = _mutmut_signature(xǁNDJSONLogHookǁon_step_end__mutmut_orig)
    xǁNDJSONLogHookǁon_step_end__mutmut_orig.__name__ = 'xǁNDJSONLogHookǁon_step_end'
