"""
Zendesk model namespace.

This package contains Pydantic models representing Zendesk administrative
resources such as triggers, ticket fields, forms, groups, and more.  The
models support diffing via a `diff` method that compares two instances and
returns a list of patch operations.
"""

from .field import TicketField, TicketForm
from .group import Group, Membership
from .trigger import Action, Condition, Trigger

__all__ = [
    "Trigger",
    "Condition",
    "Action",
    "TicketField",
    "TicketForm",
    "Group",
    "Membership",
]
