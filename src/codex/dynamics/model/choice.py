"""Models describing Dynamics 365 choice (picklist) metadata."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChoiceOption(BaseModel):
    """An option in a global choice set."""

    value: int
    label: str


class ChoiceSet(BaseModel):
    """Definition of a global choice set with multiple options."""

    name: str
    options: list[ChoiceOption] = Field(default_factory=list)

    def diff(self, other: ChoiceSet) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_options = {(opt.value, opt.label) for opt in self.options}
        other_options = {(opt.value, opt.label) for opt in other.options}
        if self_options != other_options:
            patches.append(
                {
                    "op": "replace",
                    "path": "/options",
                    "value": [opt.model_dump() for opt in self.options],
                }
            )
        return patches
