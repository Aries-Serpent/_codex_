"""Typed models for CSV-based mapping definitions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["RoutingPattern", "SlaParity"]
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


class RoutingPattern(BaseModel):
    """Routing parity definition between Dataverse and Zendesk."""

    pattern_name: str
    cdm_condition: str
    zd_destination_group: str
    d365_queue: str

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SlaParity(BaseModel):
    """SLA parity definition between Dataverse and Zendesk."""

    cdm_metric: str
    zd_target_minutes: int = Field(ge=0)
    d365_target_minutes: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
