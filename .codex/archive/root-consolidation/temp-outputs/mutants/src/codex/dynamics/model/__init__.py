"""Data models for Dynamics 365 resources."""

from __future__ import annotations

from .choice import ChoiceOption, ChoiceSet
from .role import DynamicsPrivilege, DynamicsRole
from .sla import SLAMetric, SLAPauseCondition, SLAPolicy, SLAPolicyRegistry

__all__ = [
    "ChoiceOption",
    "ChoiceSet",
    "DynamicsPrivilege",
    "DynamicsRole",
    "SLAMetric",
    "SLAPauseCondition",
    "SLAPolicy",
    "SLAPolicyRegistry",
]
