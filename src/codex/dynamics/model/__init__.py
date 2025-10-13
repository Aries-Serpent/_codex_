"""Data models for Dynamics 365 resources."""

from __future__ import annotations

from .choice import ChoiceSet
from .role import DynamicsPrivilege, DynamicsRole

__all__ = ["DynamicsPrivilege", "DynamicsRole", "ChoiceSet"]
