"""Dynamics 365 role and privilege models."""

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


class DynamicsPrivilege(BaseModel):
    """A privilege entry in a Dynamics 365 role (entity-level permission)."""

    entity: str
    privilege: str
    level: str


class DynamicsRole(BaseModel):
    """Dynamics 365 security role with a set of privileges."""

    name: str
    privileges: list[DynamicsPrivilege] = Field(default_factory=list)

    def xǁDynamicsRoleǁdiff__mutmut_orig(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_1(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = None
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_2(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = None
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_3(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = None
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_4(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set == other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_5(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                None
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_6(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "XXopXX": "replace",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_7(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "OP": "replace",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_8(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "XXreplaceXX",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_9(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "REPLACE",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_10(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "XXpathXX": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_11(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "PATH": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_12(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "XX/privilegesXX",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_13(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/PRIVILEGES",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_14(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/privileges",
                    "XXvalueXX": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

    def xǁDynamicsRoleǁdiff__mutmut_15(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/privileges",
                    "VALUE": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches
    
    xǁDynamicsRoleǁdiff__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDynamicsRoleǁdiff__mutmut_1': xǁDynamicsRoleǁdiff__mutmut_1, 
        'xǁDynamicsRoleǁdiff__mutmut_2': xǁDynamicsRoleǁdiff__mutmut_2, 
        'xǁDynamicsRoleǁdiff__mutmut_3': xǁDynamicsRoleǁdiff__mutmut_3, 
        'xǁDynamicsRoleǁdiff__mutmut_4': xǁDynamicsRoleǁdiff__mutmut_4, 
        'xǁDynamicsRoleǁdiff__mutmut_5': xǁDynamicsRoleǁdiff__mutmut_5, 
        'xǁDynamicsRoleǁdiff__mutmut_6': xǁDynamicsRoleǁdiff__mutmut_6, 
        'xǁDynamicsRoleǁdiff__mutmut_7': xǁDynamicsRoleǁdiff__mutmut_7, 
        'xǁDynamicsRoleǁdiff__mutmut_8': xǁDynamicsRoleǁdiff__mutmut_8, 
        'xǁDynamicsRoleǁdiff__mutmut_9': xǁDynamicsRoleǁdiff__mutmut_9, 
        'xǁDynamicsRoleǁdiff__mutmut_10': xǁDynamicsRoleǁdiff__mutmut_10, 
        'xǁDynamicsRoleǁdiff__mutmut_11': xǁDynamicsRoleǁdiff__mutmut_11, 
        'xǁDynamicsRoleǁdiff__mutmut_12': xǁDynamicsRoleǁdiff__mutmut_12, 
        'xǁDynamicsRoleǁdiff__mutmut_13': xǁDynamicsRoleǁdiff__mutmut_13, 
        'xǁDynamicsRoleǁdiff__mutmut_14': xǁDynamicsRoleǁdiff__mutmut_14, 
        'xǁDynamicsRoleǁdiff__mutmut_15': xǁDynamicsRoleǁdiff__mutmut_15
    }
    
    def diff(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDynamicsRoleǁdiff__mutmut_orig"), object.__getattribute__(self, "xǁDynamicsRoleǁdiff__mutmut_mutants"), args, kwargs, self)
        return result 
    
    diff.__signature__ = _mutmut_signature(xǁDynamicsRoleǁdiff__mutmut_orig)
    xǁDynamicsRoleǁdiff__mutmut_orig.__name__ = 'xǁDynamicsRoleǁdiff'
