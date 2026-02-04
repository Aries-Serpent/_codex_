"""
Choice Module

This module provides functionality for choice.

Usage:
    from model.choice import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
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


class ChoiceOption(BaseModel):
    """An option in a global Choice Set (picklist)."""

    value: int
    label: str


class ChoiceSet(BaseModel):
    """Definition of a global Choice Set with multiple options."""

    name: str
    options: list[ChoiceOption] = Field(default_factory=list)

    def xǁChoiceSetǁdiff__mutmut_orig(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_1(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = None
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_2(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = None
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_3(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = None
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_4(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts == other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_5(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                None
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_6(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "XXopXX": "replace",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_7(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "OP": "replace",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_8(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "XXreplaceXX",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_9(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "REPLACE",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_10(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "XXpathXX": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_11(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "PATH": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_12(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "XX/optionsXX",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_13(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "/OPTIONS",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_14(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "/options",
                    "XXvalueXX": [opt.model_dump() for opt in self.options],
                }
            )
        return patches

    def xǁChoiceSetǁdiff__mutmut_15(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_opts = {(opt.value, opt.label) for opt in self.options}
        other_opts = {(opt.value, opt.label) for opt in other.options}
        if self_opts != other_opts:
            patches.append(
                {
                    "op": "replace",
                    "path": "/options",
                    "VALUE": [opt.model_dump() for opt in self.options],
                }
            )
        return patches
    
    xǁChoiceSetǁdiff__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChoiceSetǁdiff__mutmut_1': xǁChoiceSetǁdiff__mutmut_1, 
        'xǁChoiceSetǁdiff__mutmut_2': xǁChoiceSetǁdiff__mutmut_2, 
        'xǁChoiceSetǁdiff__mutmut_3': xǁChoiceSetǁdiff__mutmut_3, 
        'xǁChoiceSetǁdiff__mutmut_4': xǁChoiceSetǁdiff__mutmut_4, 
        'xǁChoiceSetǁdiff__mutmut_5': xǁChoiceSetǁdiff__mutmut_5, 
        'xǁChoiceSetǁdiff__mutmut_6': xǁChoiceSetǁdiff__mutmut_6, 
        'xǁChoiceSetǁdiff__mutmut_7': xǁChoiceSetǁdiff__mutmut_7, 
        'xǁChoiceSetǁdiff__mutmut_8': xǁChoiceSetǁdiff__mutmut_8, 
        'xǁChoiceSetǁdiff__mutmut_9': xǁChoiceSetǁdiff__mutmut_9, 
        'xǁChoiceSetǁdiff__mutmut_10': xǁChoiceSetǁdiff__mutmut_10, 
        'xǁChoiceSetǁdiff__mutmut_11': xǁChoiceSetǁdiff__mutmut_11, 
        'xǁChoiceSetǁdiff__mutmut_12': xǁChoiceSetǁdiff__mutmut_12, 
        'xǁChoiceSetǁdiff__mutmut_13': xǁChoiceSetǁdiff__mutmut_13, 
        'xǁChoiceSetǁdiff__mutmut_14': xǁChoiceSetǁdiff__mutmut_14, 
        'xǁChoiceSetǁdiff__mutmut_15': xǁChoiceSetǁdiff__mutmut_15
    }
    
    def diff(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChoiceSetǁdiff__mutmut_orig"), object.__getattribute__(self, "xǁChoiceSetǁdiff__mutmut_mutants"), args, kwargs, self)
        return result 
    
    diff.__signature__ = _mutmut_signature(xǁChoiceSetǁdiff__mutmut_orig)
    xǁChoiceSetǁdiff__mutmut_orig.__name__ = 'xǁChoiceSetǁdiff'
