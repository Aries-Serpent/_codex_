"""Pydantic models describing Zendesk administrative resources."""

from .app import App
from .field import TicketField, TicketForm
from .group import Group, Membership
from .guide import GuideThemeRef, TemplatePatch
from .macro import Macro
from .routing import AgentSkills, Attribute, SkillValue, TicketSkillsPolicy
from .talk import Greeting, IVRMenu, IVRRoute, PhoneNumberBinding
from .trigger import Action, Condition, Trigger
from .view import View
from .webhook import Webhook
from .widget import WidgetConfig

__all__ = [
    "Action",
    "AgentSkills",
    "App",
    "Attribute",
    "Condition",
    "Greeting",
    "Group",
    "GuideThemeRef",
    "IVRMenu",
    "IVRRoute",
    "Macro",
    "Membership",
    "PhoneNumberBinding",
    "SkillValue",
    "TemplatePatch",
    "TicketField",
    "TicketForm",
    "TicketSkillsPolicy",
    "Trigger",
    "View",
    "Webhook",
    "WidgetConfig",
]

