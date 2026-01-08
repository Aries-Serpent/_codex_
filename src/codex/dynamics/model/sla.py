"""Dynamics 365 SLA Policy models.

This module provides versioned Policy Objects for SLA and Entitlement
calculation logic, replacing hardcoded CSV configurations.

Logic Authority: src/codex/dynamics must own the SLA and Entitlement
calculation logic, allowing the agent to verify SLA logic against
the SaaS reality dynamically.

Migration from: configs/deployment/d365/slas.csv
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SLAMetric(str, Enum):
    """SLA metric types supported by Dynamics 365."""

    FIRST_RESPONSE = "first_response"
    RESOLUTION = "resolution"
    ESCALATION = "escalation"


class SLAPauseCondition(BaseModel):
    """Condition that pauses SLA calculation."""

    field: str = Field(..., description="Field name to check")
    operator: str = Field(..., description="Comparison operator: equals, contains, etc.")
    value: Any = Field(..., description="Value to compare against")

    def evaluate(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(self.field)
        
        if self.operator == "equals":
            return ticket_value == self.value
        elif self.operator == "contains":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False


class SLAPolicy(BaseModel):
    """Versioned SLA Policy Object for Dynamics 365.
    
    This replaces the brittle CSV-based configuration with a typed,
    versioned policy that can be validated against the SaaS reality.
    
    Attributes:
        name: Policy identifier (e.g., "cdx_assignment_standard")
        metric: Type of SLA metric being measured
        target_minutes: Target time in minutes for this SLA
        pause_conditions: List of conditions that pause SLA calculation
        version: Policy version for change tracking
        effective_date: When this policy becomes effective (ISO 8601)
        description: Human-readable policy description
    """

    name: str = Field(..., description="Unique policy identifier")
    metric: SLAMetric = Field(..., description="SLA metric type")
    target_minutes: int = Field(..., gt=0, description="Target time in minutes")
    pause_conditions: list[SLAPauseCondition] = Field(
        default_factory=list,
        description="Conditions that pause SLA calculation",
    )
    version: str = Field(
        "1.0.0",
        description="Policy version (semantic versioning)",
    )
    effective_date: str = Field(
        ...,
        description="Effective date in ISO 8601 format",
    )
    description: str | None = Field(
        None,
        description="Human-readable description of policy",
    )
    applies_to: dict[str, Any] = Field(
        default_factory=dict,
        description="Criteria for when this policy applies (priority, type, etc.)",
    )
    business_hours_only: bool = Field(
        True,
        description="Whether to calculate SLA only during business hours",
    )

    @field_validator("effective_date")
    @classmethod
    def validate_effective_date(cls, v: str) -> str:
        """Validate that effective_date is a valid ISO 8601 timestamp."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValueError(f"Invalid ISO 8601 date: {v}") from e
        return v

    def calculate_deadline(
        self,
        start_time: datetime,
        *,
        business_hours_schedule: dict[str, Any] | None = None,
    ) -> datetime:
        """Calculate SLA deadline from start time.
        
        Args:
            start_time: When the SLA clock starts
            business_hours_schedule: Optional business hours configuration
            
        Returns:
            Deadline datetime when SLA will breach
        """
        if not self.business_hours_only or business_hours_schedule is None:
            # Simple calculation: add target minutes to start time
            return start_time + timedelta(minutes=self.target_minutes)
        
        # TODO: Implement business hours calculation
        # This would integrate with D365 business hours calendar
        return start_time + timedelta(minutes=self.target_minutes)

    def is_paused(self, ticket_state: dict[str, Any]) -> bool:
        """Check if SLA should be paused based on current ticket state.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if any pause condition is met
        """
        return any(
            condition.evaluate(ticket_state)
            for condition in self.pause_conditions
        )

    def diff(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "target_minutes",
            "pause_conditions",
            "description",
            "applies_to",
            "business_hours_only",
        ]

        for field_name in comparable_fields:
            self_value = getattr(self, field_name)
            other_value = getattr(other, field_name)

            if self_value != other_value:
                if isinstance(self_value, list) and hasattr(self_value[0] if self_value else None, "model_dump"):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def to_d365_format(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "slametric": self.metric.value,
            "applicablewhen": self.applies_to,
            "successconditions": {
                "target_minutes": self.target_minutes,
            },
            "pauseconfiguration": [
                {
                    "attribute": cond.field,
                    "operator": cond.operator,
                    "value": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }


class SLAPolicyRegistry(BaseModel):
    """Registry of SLA policies with versioning support."""

    policies: list[SLAPolicy] = Field(
        default_factory=list,
        description="List of SLA policies",
    )
    registry_version: str = Field(
        "1.0.0",
        description="Registry version",
    )
    last_updated: str = Field(
        ...,
        description="Last update timestamp (ISO 8601)",
    )

    def get_policy(self, name: str, version: str | None = None) -> SLAPolicy | None:
        """Retrieve a policy by name and optional version.
        
        Args:
            name: Policy name
            version: Specific version, or None for latest
            
        Returns:
            SLAPolicy if found, None otherwise
        """
        matching = [p for p in self.policies if p.name == name]
        
        if not matching:
            return None
        
        if version is None:
            # Return latest by effective_date
            return max(matching, key=lambda p: p.effective_date)
        
        # Return specific version
        for policy in matching:
            if policy.version == version:
                return policy
        
        return None

    def add_policy(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if not (p.name == policy.name and p.version == policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = datetime.now().isoformat()

    @classmethod
    def from_csv(cls, csv_path: str) -> SLAPolicyRegistry:
        """Migrate legacy CSV configuration to policy registry.
        
        Args:
            csv_path: Path to legacy slas.csv file
            
        Returns:
            SLAPolicyRegistry with migrated policies
        """
        import csv
        from pathlib import Path

        registry = cls(
            policies=[],
            last_updated=datetime.now().isoformat(),
        )

        csv_file = Path(csv_path)
        if not csv_file.exists():
            return registry

        with csv_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse pause conditions from CSV format
                pause_conditions = []
                if "pause_conditions" in row and row["pause_conditions"]:
                    # Expected format: "field:operator:value"
                    for condition_str in row["pause_conditions"].split(";"):
                        if ":" in condition_str:
                            field, operator, value = condition_str.split(":", 2)
                            pause_conditions.append(
                                SLAPauseCondition(
                                    field=field,
                                    operator=operator,
                                    value=value,
                                )
                            )

                policy = SLAPolicy(
                    name=row.get("name", ""),
                    metric=SLAMetric(row.get("metric", "first_response")),
                    target_minutes=int(row.get("target_minutes", "60")),
                    pause_conditions=pause_conditions,
                    version="1.0.0",  # Initial version from CSV
                    effective_date=datetime.now().isoformat(),
                    description=f"Migrated from CSV: {csv_path}",
                )
                registry.add_policy(policy)

        return registry


__all__ = [
    "SLAMetric",
    "SLAPauseCondition",
    "SLAPolicy",
    "SLAPolicyRegistry",
]
