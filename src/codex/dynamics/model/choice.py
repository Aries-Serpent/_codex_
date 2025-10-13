from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChoiceOption(BaseModel):
    """An option in a global Choice Set (picklist)."""

    value: int
    label: str


class ChoiceSet(BaseModel):
    """Definition of a global Choice Set with multiple options."""

    name: str
    options: list[ChoiceOption] = Field(default_factory=list)

    def diff(self, other: ChoiceSet) -> list[dict[str, Any]]:
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
