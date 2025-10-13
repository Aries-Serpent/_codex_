"""Typed models for CSV-based mapping definitions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["RoutingPattern", "SlaParity"]


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
