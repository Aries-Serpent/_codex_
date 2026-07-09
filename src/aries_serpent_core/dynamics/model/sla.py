"""Dynamics 365 SLA Policy models.

This module provides versioned Policy Objects for SLA and Entitlement
calculation logic, replacing hardcoded CSV configurations.

Logic Authority: src/codex/dynamics must own the SLA and Entitlement
calculation logic, allowing the agent to verify SLA logic against
the SaaS reality dynamically.

Migration from: configs/deployment/d365/slas.csv

D365 calendar integration: when ``D365_INSTANCE_URL`` and ``D365_TOKEN``
environment variables are both set, ``calculate_deadline()`` will attempt
to fetch the business-hours calendar from D365 and use it instead of the
built-in Mon–Fri 09:00–17:00 UTC default.  The integration is fully
optional and falls back gracefully when credentials are absent or the
remote call fails.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# Pre-compiled HH:MM time format regex used by D365CalendarClient
_TIME_HH_MM_RE = re.compile(r"^\d{2}:\d{2}$")


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
        if self.operator == "contains":
            return self.value in str(ticket_value)
        if self.operator == "not_equals":
            return ticket_value != self.value

        # Default: condition not met
        return False


class D365CalendarClient:
    """Microsoft Dynamics 365 calendar client for business-hours SLA.

    Fetches business-hour calendar data from D365 when credentials are available.
    Falls back gracefully when D365 is unreachable or credentials are absent.

    Required environment variables:
        D365_INSTANCE_URL: e.g. https://myorg.crm.dynamics.com
        D365_TOKEN: Bearer token for D365 API

    API reference:
        GET /api/data/v9.2/businessclosures  — company-wide closures/holidays
        GET /api/data/v9.2/calendars?$filter=type eq 1  — business calendars
    """

    def __init__(self) -> None:
        self._instance_url = os.environ.get("D365_INSTANCE_URL", "").rstrip("/")
        self._token = os.environ.get("D365_TOKEN", "")
        self._available = bool(self._instance_url and self._token)

    @property
    def is_available(self) -> bool:
        """True if D365 credentials are configured."""
        return self._available

    def fetch_business_hours_schedule(
        self, businesshoursid: str | None = None
    ) -> dict[str, Any] | None:
        """Fetch business hours schedule from D365.

        Returns a schedule dict compatible with SLAPolicy.calculate_deadline():
            {
                "timezone": "UTC",
                "hours": {
                    "monday": {"start": "09:00", "end": "17:00"},
                    ...
                },
                "holidays": ["2026-01-01", "2026-12-25"]  # ISO dates
            }

        Returns None if D365 is unavailable or the fetch fails.
        """
        if not self._available:
            return None
        try:
            import requests as _requests

            # Validate businesshoursid to prevent OData injection
            if businesshoursid is not None and not re.fullmatch(r"[\w\-]{1,128}", businesshoursid):
                logger.warning(
                    "D365CalendarClient: invalid businesshoursid %r; using default calendar filter.",  # noqa: E501
                    businesshoursid,
                )
                businesshoursid = None

            # Build OData query for calendar rules
            if businesshoursid:
                calendar_filter = f"?$filter=calendarid eq {businesshoursid}"
            else:
                calendar_filter = "?$filter=type eq 1"  # type 1 = work hours calendar

            resp = _requests.get(
                f"{self._instance_url}/api/data/v9.2/calendars{calendar_filter}",
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Accept": "application/json",
                    "OData-MaxVersion": "4.0",
                    "OData-Version": "4.0",
                },
                timeout=10,
            )
            if resp.status_code != 200:
                logger.warning(
                    "D365CalendarClient: calendar fetch returned HTTP %d; "
                    "falling back to local schedule",
                    resp.status_code,
                )
                return None

            data = resp.json()
            calendars = data.get("value", [])
            if not calendars:
                logger.warning("D365CalendarClient: no calendar rules returned; falling back.")
                return None

            # Parse D365 calendar rules into our schedule format.
            # D365 calendar rules have: starttime, endtime, weekday (0=Sun … 6=Sat)
            day_map = {
                0: "sunday",
                1: "monday",
                2: "tuesday",
                3: "wednesday",
                4: "thursday",
                5: "friday",
                6: "saturday",
            }
            hours: dict[str, Any] = {}
            tz_name = "UTC"

            for cal in calendars:
                for rule in cal.get("calendarrules", []):
                    weekday = rule.get("pattern", {}).get("weekday")
                    raw_start = rule.get("starttime", "09:00")[:5]
                    raw_end = rule.get("endtime", "17:00")[:5]
                    rule_tz = rule.get("timezonecode", "UTC")
                    if not _TIME_HH_MM_RE.match(raw_start) or not _TIME_HH_MM_RE.match(raw_end):
                        logger.warning(
                            "D365CalendarClient: skipping rule with malformed time start=%r end=%r",
                            raw_start,
                            raw_end,
                        )
                        continue
                    if rule_tz != tz_name and hours:
                        # Warn if rules carry conflicting timezone codes
                        logger.warning(
                            "D365CalendarClient: timezone mismatch in calendar rules "
                            "(%r vs %r); using first value.",
                            tz_name,
                            rule_tz,
                        )
                    elif not hours:
                        tz_name = rule_tz
                    if weekday is not None and weekday in day_map:
                        hours[day_map[weekday]] = {"start": raw_start, "end": raw_end}

            if not hours:
                return None

            return {"timezone": tz_name, "hours": hours}

        except ImportError:
            logger.warning(
                "D365CalendarClient: requests library unavailable; using local schedule."
            )
            return None
        except (ConnectionError, TimeoutError) as exc:
            logger.warning("D365CalendarClient: fetch failed (%s); using local schedule.", exc)
            return None


class SLAPolicy(BaseModel):
    """Versioned SLA Policy Object for Dynamics 365.

    This replaces the brittle CSV-based configuration with a typed,
    versioned policy that can be validated against the SaaS reality.
    When ``D365_INSTANCE_URL`` and ``D365_TOKEN`` env vars are set,
    ``calculate_deadline()`` will automatically fetch the live business-hours
    calendar from D365 instead of the built-in default schedule.

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
        if not self.business_hours_only:
            # Simple calculation: add target minutes to start time
            return start_time + timedelta(minutes=self.target_minutes)

        # Business-hours SLA calculation.
        # Attempt D365 calendar fetch when credentials are configured.
        _d365 = D365CalendarClient()
        if _d365.is_available and business_hours_schedule is None:
            d365_schedule = _d365.fetch_business_hours_schedule(
                getattr(self, "businesshoursid", None)
            )
            if d365_schedule is not None:
                business_hours_schedule = d365_schedule
                logger.info("calculate_deadline(): using D365 business-hours calendar.")

        if business_hours_schedule is None:
            # Default: Mon-Fri 09:00-17:00 UTC
            tz_name = "UTC"
            day_hours: dict[str, Any] = {
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "09:00", "end": "17:00"},
            }
        else:
            tz_name = business_hours_schedule.get("timezone", "UTC")
            day_hours = business_hours_schedule.get("hours", {})

        try:
            from zoneinfo import ZoneInfo

            tz = ZoneInfo(tz_name)
        except (ImportError, AttributeError):
            from datetime import timezone

            tz = timezone.utc  # type: ignore[assignment]

        # Ensure start_time is tz-aware in the target timezone
        if start_time.tzinfo is None:
            current = start_time.replace(tzinfo=tz)
        else:
            current = start_time.astimezone(tz)

        day_names = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        remaining = self.target_minutes

        # Validate that at least one business day is defined to prevent infinite loop
        if not any(day_hours.get(d) for d in day_names):
            raise ValueError(
                "business_hours_schedule contains no valid business days; "
                "at least one day with start/end hours is required."
            )

        _max_iterations = 3650  # safety cap: ~10 years of daily advances
        _iterations = 0
        while remaining > 0:
            if _iterations >= _max_iterations:
                raise RuntimeError(
                    f"SLA calculation exceeded {_max_iterations} day iterations; "
                    "check business_hours_schedule for a valid schedule."
                )
            _iterations += 1
            day_name = day_names[current.weekday()]
            schedule = day_hours.get(day_name)
            if schedule:
                start_h, start_m = map(int, schedule["start"].split(":"))
                end_h, end_m = map(int, schedule["end"].split(":"))
                day_start = current.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                day_end = current.replace(hour=end_h, minute=end_m, second=0, microsecond=0)

                # Clamp current to business window
                if current < day_start:
                    current = day_start
                if current < day_end:
                    available = int((day_end - current).total_seconds() // 60)
                    if remaining <= available:
                        current = current + timedelta(minutes=remaining)
                        break
                    remaining -= available
                    current = day_end

            # Advance to next day start
            next_day = (current + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            current = next_day

        return current

    def is_paused(self, ticket_state: dict[str, Any]) -> bool:
        """Check if SLA should be paused based on current ticket state.

        Args:
            ticket_state: Current ticket/case state dictionary

        Returns:
            True if any pause condition is met
        """
        return any(condition.evaluate(ticket_state) for condition in self.pause_conditions)

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
                if isinstance(self_value, list) and hasattr(
                    self_value[0] if self_value else None, "model_dump"
                ):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append(
                    {
                        "op": "replace",
                        "path": f"/{field_name}",
                        "value": value,
                    }
                )

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
            p for p in self.policies if not (p.name == policy.name and p.version == policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = datetime.now(UTC).isoformat()

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

        registry = cls(  # type: ignore[call-arg]
            policies=[],
            last_updated=datetime.now(UTC).isoformat(),
        )

        csv_file = Path(csv_path)
        if not csv_file.exists():
            return registry

        with csv_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse pause conditions from CSV format
                pause_conditions = []
                if row.get("pause_conditions"):
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

                policy = SLAPolicy(  # type: ignore[call-arg]
                    name=row.get("name", ""),
                    metric=SLAMetric(row.get("metric", "first_response")),
                    target_minutes=int(row.get("target_minutes", "60")),
                    pause_conditions=pause_conditions,
                    version="1.0.0",  # Initial version from CSV
                    effective_date=datetime.now(UTC).isoformat(),
                    description=f"Migrated from CSV: {csv_path}",
                )
                registry.add_policy(policy)

        return registry


__all__ = [
    "D365CalendarClient",
    "SLAMetric",
    "SLAPauseCondition",
    "SLAPolicy",
    "SLAPolicyRegistry",
]
