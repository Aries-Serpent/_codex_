"""Dynamics 365 SLA Policy models.

This module provides versioned Policy Objects for SLA and Entitlement
calculation logic, replacing hardcoded CSV configurations.

Logic Authority: src/codex/dynamics must own the SLA and Entitlement
calculation logic, allowing the agent to verify SLA logic against
the SaaS reality dynamically.

Migration from: configs/deployment/d365/slas.csv
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator
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

    def xǁSLAPauseConditionǁevaluate__mutmut_orig(self, ticket_state: dict[str, Any]) -> bool:
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

    def xǁSLAPauseConditionǁevaluate__mutmut_1(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = None
        
        if self.operator == "equals":
            return ticket_value == self.value
        elif self.operator == "contains":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_2(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(None)
        
        if self.operator == "equals":
            return ticket_value == self.value
        elif self.operator == "contains":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_3(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(self.field)
        
        if self.operator != "equals":
            return ticket_value == self.value
        elif self.operator == "contains":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_4(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(self.field)
        
        if self.operator == "XXequalsXX":
            return ticket_value == self.value
        elif self.operator == "contains":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_5(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(self.field)
        
        if self.operator == "EQUALS":
            return ticket_value == self.value
        elif self.operator == "contains":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_6(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(self.field)
        
        if self.operator == "equals":
            return ticket_value != self.value
        elif self.operator == "contains":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_7(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(self.field)
        
        if self.operator == "equals":
            return ticket_value == self.value
        elif self.operator != "contains":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_8(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(self.field)
        
        if self.operator == "equals":
            return ticket_value == self.value
        elif self.operator == "XXcontainsXX":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_9(self, ticket_state: dict[str, Any]) -> bool:
        """Evaluate if this pause condition is met.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if condition is met and SLA should be paused
        """
        ticket_value = ticket_state.get(self.field)
        
        if self.operator == "equals":
            return ticket_value == self.value
        elif self.operator == "CONTAINS":
            return self.value in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_10(self, ticket_state: dict[str, Any]) -> bool:
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
            return self.value not in str(ticket_value)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_11(self, ticket_state: dict[str, Any]) -> bool:
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
            return self.value in str(None)
        elif self.operator == "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_12(self, ticket_state: dict[str, Any]) -> bool:
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
        elif self.operator != "not_equals":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_13(self, ticket_state: dict[str, Any]) -> bool:
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
        elif self.operator == "XXnot_equalsXX":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_14(self, ticket_state: dict[str, Any]) -> bool:
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
        elif self.operator == "NOT_EQUALS":
            return ticket_value != self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_15(self, ticket_state: dict[str, Any]) -> bool:
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
            return ticket_value == self.value
        
        # Default: condition not met
        return False

    def xǁSLAPauseConditionǁevaluate__mutmut_16(self, ticket_state: dict[str, Any]) -> bool:
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
        return True
    
    xǁSLAPauseConditionǁevaluate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSLAPauseConditionǁevaluate__mutmut_1': xǁSLAPauseConditionǁevaluate__mutmut_1, 
        'xǁSLAPauseConditionǁevaluate__mutmut_2': xǁSLAPauseConditionǁevaluate__mutmut_2, 
        'xǁSLAPauseConditionǁevaluate__mutmut_3': xǁSLAPauseConditionǁevaluate__mutmut_3, 
        'xǁSLAPauseConditionǁevaluate__mutmut_4': xǁSLAPauseConditionǁevaluate__mutmut_4, 
        'xǁSLAPauseConditionǁevaluate__mutmut_5': xǁSLAPauseConditionǁevaluate__mutmut_5, 
        'xǁSLAPauseConditionǁevaluate__mutmut_6': xǁSLAPauseConditionǁevaluate__mutmut_6, 
        'xǁSLAPauseConditionǁevaluate__mutmut_7': xǁSLAPauseConditionǁevaluate__mutmut_7, 
        'xǁSLAPauseConditionǁevaluate__mutmut_8': xǁSLAPauseConditionǁevaluate__mutmut_8, 
        'xǁSLAPauseConditionǁevaluate__mutmut_9': xǁSLAPauseConditionǁevaluate__mutmut_9, 
        'xǁSLAPauseConditionǁevaluate__mutmut_10': xǁSLAPauseConditionǁevaluate__mutmut_10, 
        'xǁSLAPauseConditionǁevaluate__mutmut_11': xǁSLAPauseConditionǁevaluate__mutmut_11, 
        'xǁSLAPauseConditionǁevaluate__mutmut_12': xǁSLAPauseConditionǁevaluate__mutmut_12, 
        'xǁSLAPauseConditionǁevaluate__mutmut_13': xǁSLAPauseConditionǁevaluate__mutmut_13, 
        'xǁSLAPauseConditionǁevaluate__mutmut_14': xǁSLAPauseConditionǁevaluate__mutmut_14, 
        'xǁSLAPauseConditionǁevaluate__mutmut_15': xǁSLAPauseConditionǁevaluate__mutmut_15, 
        'xǁSLAPauseConditionǁevaluate__mutmut_16': xǁSLAPauseConditionǁevaluate__mutmut_16
    }
    
    def evaluate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSLAPauseConditionǁevaluate__mutmut_orig"), object.__getattribute__(self, "xǁSLAPauseConditionǁevaluate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    evaluate.__signature__ = _mutmut_signature(xǁSLAPauseConditionǁevaluate__mutmut_orig)
    xǁSLAPauseConditionǁevaluate__mutmut_orig.__name__ = 'xǁSLAPauseConditionǁevaluate'


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

    def xǁSLAPolicyǁcalculate_deadline__mutmut_orig(
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

    def xǁSLAPolicyǁcalculate_deadline__mutmut_1(
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
        if not self.business_hours_only and business_hours_schedule is None:
            # Simple calculation: add target minutes to start time
            return start_time + timedelta(minutes=self.target_minutes)
        
        # TODO: Implement business hours calculation
        # This would integrate with D365 business hours calendar
        return start_time + timedelta(minutes=self.target_minutes)

    def xǁSLAPolicyǁcalculate_deadline__mutmut_2(
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
        if self.business_hours_only or business_hours_schedule is None:
            # Simple calculation: add target minutes to start time
            return start_time + timedelta(minutes=self.target_minutes)
        
        # TODO: Implement business hours calculation
        # This would integrate with D365 business hours calendar
        return start_time + timedelta(minutes=self.target_minutes)

    def xǁSLAPolicyǁcalculate_deadline__mutmut_3(
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
        if not self.business_hours_only or business_hours_schedule is not None:
            # Simple calculation: add target minutes to start time
            return start_time + timedelta(minutes=self.target_minutes)
        
        # TODO: Implement business hours calculation
        # This would integrate with D365 business hours calendar
        return start_time + timedelta(minutes=self.target_minutes)

    def xǁSLAPolicyǁcalculate_deadline__mutmut_4(
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
            return start_time - timedelta(minutes=self.target_minutes)
        
        # TODO: Implement business hours calculation
        # This would integrate with D365 business hours calendar
        return start_time + timedelta(minutes=self.target_minutes)

    def xǁSLAPolicyǁcalculate_deadline__mutmut_5(
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
            return start_time + timedelta(minutes=None)
        
        # TODO: Implement business hours calculation
        # This would integrate with D365 business hours calendar
        return start_time + timedelta(minutes=self.target_minutes)

    def xǁSLAPolicyǁcalculate_deadline__mutmut_6(
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
        return start_time - timedelta(minutes=self.target_minutes)

    def xǁSLAPolicyǁcalculate_deadline__mutmut_7(
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
        return start_time + timedelta(minutes=None)
    
    xǁSLAPolicyǁcalculate_deadline__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSLAPolicyǁcalculate_deadline__mutmut_1': xǁSLAPolicyǁcalculate_deadline__mutmut_1, 
        'xǁSLAPolicyǁcalculate_deadline__mutmut_2': xǁSLAPolicyǁcalculate_deadline__mutmut_2, 
        'xǁSLAPolicyǁcalculate_deadline__mutmut_3': xǁSLAPolicyǁcalculate_deadline__mutmut_3, 
        'xǁSLAPolicyǁcalculate_deadline__mutmut_4': xǁSLAPolicyǁcalculate_deadline__mutmut_4, 
        'xǁSLAPolicyǁcalculate_deadline__mutmut_5': xǁSLAPolicyǁcalculate_deadline__mutmut_5, 
        'xǁSLAPolicyǁcalculate_deadline__mutmut_6': xǁSLAPolicyǁcalculate_deadline__mutmut_6, 
        'xǁSLAPolicyǁcalculate_deadline__mutmut_7': xǁSLAPolicyǁcalculate_deadline__mutmut_7
    }
    
    def calculate_deadline(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSLAPolicyǁcalculate_deadline__mutmut_orig"), object.__getattribute__(self, "xǁSLAPolicyǁcalculate_deadline__mutmut_mutants"), args, kwargs, self)
        return result 
    
    calculate_deadline.__signature__ = _mutmut_signature(xǁSLAPolicyǁcalculate_deadline__mutmut_orig)
    xǁSLAPolicyǁcalculate_deadline__mutmut_orig.__name__ = 'xǁSLAPolicyǁcalculate_deadline'

    def xǁSLAPolicyǁis_paused__mutmut_orig(self, ticket_state: dict[str, Any]) -> bool:
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

    def xǁSLAPolicyǁis_paused__mutmut_1(self, ticket_state: dict[str, Any]) -> bool:
        """Check if SLA should be paused based on current ticket state.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if any pause condition is met
        """
        return any(
            None
        )

    def xǁSLAPolicyǁis_paused__mutmut_2(self, ticket_state: dict[str, Any]) -> bool:
        """Check if SLA should be paused based on current ticket state.
        
        Args:
            ticket_state: Current ticket/case state dictionary
            
        Returns:
            True if any pause condition is met
        """
        return any(
            condition.evaluate(None)
            for condition in self.pause_conditions
        )
    
    xǁSLAPolicyǁis_paused__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSLAPolicyǁis_paused__mutmut_1': xǁSLAPolicyǁis_paused__mutmut_1, 
        'xǁSLAPolicyǁis_paused__mutmut_2': xǁSLAPolicyǁis_paused__mutmut_2
    }
    
    def is_paused(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSLAPolicyǁis_paused__mutmut_orig"), object.__getattribute__(self, "xǁSLAPolicyǁis_paused__mutmut_mutants"), args, kwargs, self)
        return result 
    
    is_paused.__signature__ = _mutmut_signature(xǁSLAPolicyǁis_paused__mutmut_orig)
    xǁSLAPolicyǁis_paused__mutmut_orig.__name__ = 'xǁSLAPolicyǁis_paused'

    def xǁSLAPolicyǁdiff__mutmut_orig(self, other: SLAPolicy) -> list[dict[str, Any]]:
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

    def xǁSLAPolicyǁdiff__mutmut_1(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = None

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

    def xǁSLAPolicyǁdiff__mutmut_2(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = None

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

    def xǁSLAPolicyǁdiff__mutmut_3(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "XXmetricXX",
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

    def xǁSLAPolicyǁdiff__mutmut_4(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "METRIC",
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

    def xǁSLAPolicyǁdiff__mutmut_5(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "XXtarget_minutesXX",
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

    def xǁSLAPolicyǁdiff__mutmut_6(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "TARGET_MINUTES",
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

    def xǁSLAPolicyǁdiff__mutmut_7(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "target_minutes",
            "XXpause_conditionsXX",
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

    def xǁSLAPolicyǁdiff__mutmut_8(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "target_minutes",
            "PAUSE_CONDITIONS",
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

    def xǁSLAPolicyǁdiff__mutmut_9(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "target_minutes",
            "pause_conditions",
            "XXdescriptionXX",
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

    def xǁSLAPolicyǁdiff__mutmut_10(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "target_minutes",
            "pause_conditions",
            "DESCRIPTION",
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

    def xǁSLAPolicyǁdiff__mutmut_11(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "target_minutes",
            "pause_conditions",
            "description",
            "XXapplies_toXX",
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

    def xǁSLAPolicyǁdiff__mutmut_12(self, other: SLAPolicy) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.
        
        This enables drift detection between policy versions.
        """
        patches: list[dict[str, Any]] = []

        comparable_fields = [
            "metric",
            "target_minutes",
            "pause_conditions",
            "description",
            "APPLIES_TO",
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

    def xǁSLAPolicyǁdiff__mutmut_13(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            "XXbusiness_hours_onlyXX",
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

    def xǁSLAPolicyǁdiff__mutmut_14(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            "BUSINESS_HOURS_ONLY",
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

    def xǁSLAPolicyǁdiff__mutmut_15(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            self_value = None
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

    def xǁSLAPolicyǁdiff__mutmut_16(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            self_value = getattr(None, field_name)
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

    def xǁSLAPolicyǁdiff__mutmut_17(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            self_value = getattr(self, None)
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

    def xǁSLAPolicyǁdiff__mutmut_18(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            self_value = getattr(field_name)
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

    def xǁSLAPolicyǁdiff__mutmut_19(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            self_value = getattr(self, )
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

    def xǁSLAPolicyǁdiff__mutmut_20(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            other_value = None

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

    def xǁSLAPolicyǁdiff__mutmut_21(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            other_value = getattr(None, field_name)

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

    def xǁSLAPolicyǁdiff__mutmut_22(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            other_value = getattr(other, None)

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

    def xǁSLAPolicyǁdiff__mutmut_23(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            other_value = getattr(field_name)

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

    def xǁSLAPolicyǁdiff__mutmut_24(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
            other_value = getattr(other, )

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

    def xǁSLAPolicyǁdiff__mutmut_25(self, other: SLAPolicy) -> list[dict[str, Any]]:
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

            if self_value == other_value:
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

    def xǁSLAPolicyǁdiff__mutmut_26(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                if isinstance(self_value, list) or hasattr(self_value[0] if self_value else None, "model_dump"):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_27(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                if isinstance(self_value, list) and hasattr(None, "model_dump"):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_28(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                if isinstance(self_value, list) and hasattr(self_value[0] if self_value else None, None):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_29(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                if isinstance(self_value, list) and hasattr("model_dump"):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_30(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                if isinstance(self_value, list) and hasattr(self_value[0] if self_value else None, ):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_31(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                if isinstance(self_value, list) and hasattr(self_value[1] if self_value else None, "model_dump"):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_32(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                if isinstance(self_value, list) and hasattr(self_value[0] if self_value else None, "XXmodel_dumpXX"):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_33(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                if isinstance(self_value, list) and hasattr(self_value[0] if self_value else None, "MODEL_DUMP"):
                    value = [item.model_dump() for item in self_value]
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_34(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    value = None
                else:
                    value = self_value

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_35(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    value = None

                patches.append({
                    "op": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_36(self, other: SLAPolicy) -> list[dict[str, Any]]:
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

                patches.append(None)

        return patches

    def xǁSLAPolicyǁdiff__mutmut_37(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    "XXopXX": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_38(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    "OP": "replace",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_39(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    "op": "XXreplaceXX",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_40(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    "op": "REPLACE",
                    "path": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_41(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    "XXpathXX": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_42(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    "PATH": f"/{field_name}",
                    "value": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_43(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    "XXvalueXX": value,
                })

        return patches

    def xǁSLAPolicyǁdiff__mutmut_44(self, other: SLAPolicy) -> list[dict[str, Any]]:
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
                    "VALUE": value,
                })

        return patches
    
    xǁSLAPolicyǁdiff__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSLAPolicyǁdiff__mutmut_1': xǁSLAPolicyǁdiff__mutmut_1, 
        'xǁSLAPolicyǁdiff__mutmut_2': xǁSLAPolicyǁdiff__mutmut_2, 
        'xǁSLAPolicyǁdiff__mutmut_3': xǁSLAPolicyǁdiff__mutmut_3, 
        'xǁSLAPolicyǁdiff__mutmut_4': xǁSLAPolicyǁdiff__mutmut_4, 
        'xǁSLAPolicyǁdiff__mutmut_5': xǁSLAPolicyǁdiff__mutmut_5, 
        'xǁSLAPolicyǁdiff__mutmut_6': xǁSLAPolicyǁdiff__mutmut_6, 
        'xǁSLAPolicyǁdiff__mutmut_7': xǁSLAPolicyǁdiff__mutmut_7, 
        'xǁSLAPolicyǁdiff__mutmut_8': xǁSLAPolicyǁdiff__mutmut_8, 
        'xǁSLAPolicyǁdiff__mutmut_9': xǁSLAPolicyǁdiff__mutmut_9, 
        'xǁSLAPolicyǁdiff__mutmut_10': xǁSLAPolicyǁdiff__mutmut_10, 
        'xǁSLAPolicyǁdiff__mutmut_11': xǁSLAPolicyǁdiff__mutmut_11, 
        'xǁSLAPolicyǁdiff__mutmut_12': xǁSLAPolicyǁdiff__mutmut_12, 
        'xǁSLAPolicyǁdiff__mutmut_13': xǁSLAPolicyǁdiff__mutmut_13, 
        'xǁSLAPolicyǁdiff__mutmut_14': xǁSLAPolicyǁdiff__mutmut_14, 
        'xǁSLAPolicyǁdiff__mutmut_15': xǁSLAPolicyǁdiff__mutmut_15, 
        'xǁSLAPolicyǁdiff__mutmut_16': xǁSLAPolicyǁdiff__mutmut_16, 
        'xǁSLAPolicyǁdiff__mutmut_17': xǁSLAPolicyǁdiff__mutmut_17, 
        'xǁSLAPolicyǁdiff__mutmut_18': xǁSLAPolicyǁdiff__mutmut_18, 
        'xǁSLAPolicyǁdiff__mutmut_19': xǁSLAPolicyǁdiff__mutmut_19, 
        'xǁSLAPolicyǁdiff__mutmut_20': xǁSLAPolicyǁdiff__mutmut_20, 
        'xǁSLAPolicyǁdiff__mutmut_21': xǁSLAPolicyǁdiff__mutmut_21, 
        'xǁSLAPolicyǁdiff__mutmut_22': xǁSLAPolicyǁdiff__mutmut_22, 
        'xǁSLAPolicyǁdiff__mutmut_23': xǁSLAPolicyǁdiff__mutmut_23, 
        'xǁSLAPolicyǁdiff__mutmut_24': xǁSLAPolicyǁdiff__mutmut_24, 
        'xǁSLAPolicyǁdiff__mutmut_25': xǁSLAPolicyǁdiff__mutmut_25, 
        'xǁSLAPolicyǁdiff__mutmut_26': xǁSLAPolicyǁdiff__mutmut_26, 
        'xǁSLAPolicyǁdiff__mutmut_27': xǁSLAPolicyǁdiff__mutmut_27, 
        'xǁSLAPolicyǁdiff__mutmut_28': xǁSLAPolicyǁdiff__mutmut_28, 
        'xǁSLAPolicyǁdiff__mutmut_29': xǁSLAPolicyǁdiff__mutmut_29, 
        'xǁSLAPolicyǁdiff__mutmut_30': xǁSLAPolicyǁdiff__mutmut_30, 
        'xǁSLAPolicyǁdiff__mutmut_31': xǁSLAPolicyǁdiff__mutmut_31, 
        'xǁSLAPolicyǁdiff__mutmut_32': xǁSLAPolicyǁdiff__mutmut_32, 
        'xǁSLAPolicyǁdiff__mutmut_33': xǁSLAPolicyǁdiff__mutmut_33, 
        'xǁSLAPolicyǁdiff__mutmut_34': xǁSLAPolicyǁdiff__mutmut_34, 
        'xǁSLAPolicyǁdiff__mutmut_35': xǁSLAPolicyǁdiff__mutmut_35, 
        'xǁSLAPolicyǁdiff__mutmut_36': xǁSLAPolicyǁdiff__mutmut_36, 
        'xǁSLAPolicyǁdiff__mutmut_37': xǁSLAPolicyǁdiff__mutmut_37, 
        'xǁSLAPolicyǁdiff__mutmut_38': xǁSLAPolicyǁdiff__mutmut_38, 
        'xǁSLAPolicyǁdiff__mutmut_39': xǁSLAPolicyǁdiff__mutmut_39, 
        'xǁSLAPolicyǁdiff__mutmut_40': xǁSLAPolicyǁdiff__mutmut_40, 
        'xǁSLAPolicyǁdiff__mutmut_41': xǁSLAPolicyǁdiff__mutmut_41, 
        'xǁSLAPolicyǁdiff__mutmut_42': xǁSLAPolicyǁdiff__mutmut_42, 
        'xǁSLAPolicyǁdiff__mutmut_43': xǁSLAPolicyǁdiff__mutmut_43, 
        'xǁSLAPolicyǁdiff__mutmut_44': xǁSLAPolicyǁdiff__mutmut_44
    }
    
    def diff(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSLAPolicyǁdiff__mutmut_orig"), object.__getattribute__(self, "xǁSLAPolicyǁdiff__mutmut_mutants"), args, kwargs, self)
        return result 
    
    diff.__signature__ = _mutmut_signature(xǁSLAPolicyǁdiff__mutmut_orig)
    xǁSLAPolicyǁdiff__mutmut_orig.__name__ = 'xǁSLAPolicyǁdiff'

    def xǁSLAPolicyǁto_d365_format__mutmut_orig(self) -> dict[str, Any]:
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

    def xǁSLAPolicyǁto_d365_format__mutmut_1(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "XXnameXX": self.name,
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

    def xǁSLAPolicyǁto_d365_format__mutmut_2(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "NAME": self.name,
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

    def xǁSLAPolicyǁto_d365_format__mutmut_3(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "XXslametricXX": self.metric.value,
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

    def xǁSLAPolicyǁto_d365_format__mutmut_4(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "SLAMETRIC": self.metric.value,
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

    def xǁSLAPolicyǁto_d365_format__mutmut_5(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "slametric": self.metric.value,
            "XXapplicablewhenXX": self.applies_to,
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

    def xǁSLAPolicyǁto_d365_format__mutmut_6(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "slametric": self.metric.value,
            "APPLICABLEWHEN": self.applies_to,
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

    def xǁSLAPolicyǁto_d365_format__mutmut_7(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "slametric": self.metric.value,
            "applicablewhen": self.applies_to,
            "XXsuccessconditionsXX": {
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

    def xǁSLAPolicyǁto_d365_format__mutmut_8(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "slametric": self.metric.value,
            "applicablewhen": self.applies_to,
            "SUCCESSCONDITIONS": {
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

    def xǁSLAPolicyǁto_d365_format__mutmut_9(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "slametric": self.metric.value,
            "applicablewhen": self.applies_to,
            "successconditions": {
                "XXtarget_minutesXX": self.target_minutes,
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

    def xǁSLAPolicyǁto_d365_format__mutmut_10(self) -> dict[str, Any]:
        """Convert to Dynamics 365 SLA configuration format.
        
        Returns:
            Dictionary suitable for D365 SLA API
        """
        return {
            "name": self.name,
            "slametric": self.metric.value,
            "applicablewhen": self.applies_to,
            "successconditions": {
                "TARGET_MINUTES": self.target_minutes,
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

    def xǁSLAPolicyǁto_d365_format__mutmut_11(self) -> dict[str, Any]:
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
            "XXpauseconfigurationXX": [
                {
                    "attribute": cond.field,
                    "operator": cond.operator,
                    "value": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_12(self) -> dict[str, Any]:
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
            "PAUSECONFIGURATION": [
                {
                    "attribute": cond.field,
                    "operator": cond.operator,
                    "value": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_13(self) -> dict[str, Any]:
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
                    "XXattributeXX": cond.field,
                    "operator": cond.operator,
                    "value": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_14(self) -> dict[str, Any]:
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
                    "ATTRIBUTE": cond.field,
                    "operator": cond.operator,
                    "value": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_15(self) -> dict[str, Any]:
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
                    "XXoperatorXX": cond.operator,
                    "value": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_16(self) -> dict[str, Any]:
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
                    "OPERATOR": cond.operator,
                    "value": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_17(self) -> dict[str, Any]:
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
                    "XXvalueXX": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_18(self) -> dict[str, Any]:
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
                    "VALUE": cond.value,
                }
                for cond in self.pause_conditions
            ],
            "businesshoursid": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_19(self) -> dict[str, Any]:
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
            "XXbusinesshoursidXX": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_20(self) -> dict[str, Any]:
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
            "BUSINESSHOURSID": None if not self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_21(self) -> dict[str, Any]:
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
            "businesshoursid": None if self.business_hours_only else "default",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_22(self) -> dict[str, Any]:
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
            "businesshoursid": None if not self.business_hours_only else "XXdefaultXX",
        }

    def xǁSLAPolicyǁto_d365_format__mutmut_23(self) -> dict[str, Any]:
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
            "businesshoursid": None if not self.business_hours_only else "DEFAULT",
        }
    
    xǁSLAPolicyǁto_d365_format__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSLAPolicyǁto_d365_format__mutmut_1': xǁSLAPolicyǁto_d365_format__mutmut_1, 
        'xǁSLAPolicyǁto_d365_format__mutmut_2': xǁSLAPolicyǁto_d365_format__mutmut_2, 
        'xǁSLAPolicyǁto_d365_format__mutmut_3': xǁSLAPolicyǁto_d365_format__mutmut_3, 
        'xǁSLAPolicyǁto_d365_format__mutmut_4': xǁSLAPolicyǁto_d365_format__mutmut_4, 
        'xǁSLAPolicyǁto_d365_format__mutmut_5': xǁSLAPolicyǁto_d365_format__mutmut_5, 
        'xǁSLAPolicyǁto_d365_format__mutmut_6': xǁSLAPolicyǁto_d365_format__mutmut_6, 
        'xǁSLAPolicyǁto_d365_format__mutmut_7': xǁSLAPolicyǁto_d365_format__mutmut_7, 
        'xǁSLAPolicyǁto_d365_format__mutmut_8': xǁSLAPolicyǁto_d365_format__mutmut_8, 
        'xǁSLAPolicyǁto_d365_format__mutmut_9': xǁSLAPolicyǁto_d365_format__mutmut_9, 
        'xǁSLAPolicyǁto_d365_format__mutmut_10': xǁSLAPolicyǁto_d365_format__mutmut_10, 
        'xǁSLAPolicyǁto_d365_format__mutmut_11': xǁSLAPolicyǁto_d365_format__mutmut_11, 
        'xǁSLAPolicyǁto_d365_format__mutmut_12': xǁSLAPolicyǁto_d365_format__mutmut_12, 
        'xǁSLAPolicyǁto_d365_format__mutmut_13': xǁSLAPolicyǁto_d365_format__mutmut_13, 
        'xǁSLAPolicyǁto_d365_format__mutmut_14': xǁSLAPolicyǁto_d365_format__mutmut_14, 
        'xǁSLAPolicyǁto_d365_format__mutmut_15': xǁSLAPolicyǁto_d365_format__mutmut_15, 
        'xǁSLAPolicyǁto_d365_format__mutmut_16': xǁSLAPolicyǁto_d365_format__mutmut_16, 
        'xǁSLAPolicyǁto_d365_format__mutmut_17': xǁSLAPolicyǁto_d365_format__mutmut_17, 
        'xǁSLAPolicyǁto_d365_format__mutmut_18': xǁSLAPolicyǁto_d365_format__mutmut_18, 
        'xǁSLAPolicyǁto_d365_format__mutmut_19': xǁSLAPolicyǁto_d365_format__mutmut_19, 
        'xǁSLAPolicyǁto_d365_format__mutmut_20': xǁSLAPolicyǁto_d365_format__mutmut_20, 
        'xǁSLAPolicyǁto_d365_format__mutmut_21': xǁSLAPolicyǁto_d365_format__mutmut_21, 
        'xǁSLAPolicyǁto_d365_format__mutmut_22': xǁSLAPolicyǁto_d365_format__mutmut_22, 
        'xǁSLAPolicyǁto_d365_format__mutmut_23': xǁSLAPolicyǁto_d365_format__mutmut_23
    }
    
    def to_d365_format(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSLAPolicyǁto_d365_format__mutmut_orig"), object.__getattribute__(self, "xǁSLAPolicyǁto_d365_format__mutmut_mutants"), args, kwargs, self)
        return result 
    
    to_d365_format.__signature__ = _mutmut_signature(xǁSLAPolicyǁto_d365_format__mutmut_orig)
    xǁSLAPolicyǁto_d365_format__mutmut_orig.__name__ = 'xǁSLAPolicyǁto_d365_format'


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

    def xǁSLAPolicyRegistryǁget_policy__mutmut_orig(self, name: str, version: str | None = None) -> SLAPolicy | None:
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

    def xǁSLAPolicyRegistryǁget_policy__mutmut_1(self, name: str, version: str | None = None) -> SLAPolicy | None:
        """Retrieve a policy by name and optional version.
        
        Args:
            name: Policy name
            version: Specific version, or None for latest
            
        Returns:
            SLAPolicy if found, None otherwise
        """
        matching = None
        
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

    def xǁSLAPolicyRegistryǁget_policy__mutmut_2(self, name: str, version: str | None = None) -> SLAPolicy | None:
        """Retrieve a policy by name and optional version.
        
        Args:
            name: Policy name
            version: Specific version, or None for latest
            
        Returns:
            SLAPolicy if found, None otherwise
        """
        matching = [p for p in self.policies if p.name != name]
        
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

    def xǁSLAPolicyRegistryǁget_policy__mutmut_3(self, name: str, version: str | None = None) -> SLAPolicy | None:
        """Retrieve a policy by name and optional version.
        
        Args:
            name: Policy name
            version: Specific version, or None for latest
            
        Returns:
            SLAPolicy if found, None otherwise
        """
        matching = [p for p in self.policies if p.name == name]
        
        if matching:
            return None
        
        if version is None:
            # Return latest by effective_date
            return max(matching, key=lambda p: p.effective_date)
        
        # Return specific version
        for policy in matching:
            if policy.version == version:
                return policy
        
        return None

    def xǁSLAPolicyRegistryǁget_policy__mutmut_4(self, name: str, version: str | None = None) -> SLAPolicy | None:
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
        
        if version is not None:
            # Return latest by effective_date
            return max(matching, key=lambda p: p.effective_date)
        
        # Return specific version
        for policy in matching:
            if policy.version == version:
                return policy
        
        return None

    def xǁSLAPolicyRegistryǁget_policy__mutmut_5(self, name: str, version: str | None = None) -> SLAPolicy | None:
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
            return max(None, key=lambda p: p.effective_date)
        
        # Return specific version
        for policy in matching:
            if policy.version == version:
                return policy
        
        return None

    def xǁSLAPolicyRegistryǁget_policy__mutmut_6(self, name: str, version: str | None = None) -> SLAPolicy | None:
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
            return max(matching, key=None)
        
        # Return specific version
        for policy in matching:
            if policy.version == version:
                return policy
        
        return None

    def xǁSLAPolicyRegistryǁget_policy__mutmut_7(self, name: str, version: str | None = None) -> SLAPolicy | None:
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
            return max(key=lambda p: p.effective_date)
        
        # Return specific version
        for policy in matching:
            if policy.version == version:
                return policy
        
        return None

    def xǁSLAPolicyRegistryǁget_policy__mutmut_8(self, name: str, version: str | None = None) -> SLAPolicy | None:
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
            return max(matching, )
        
        # Return specific version
        for policy in matching:
            if policy.version == version:
                return policy
        
        return None

    def xǁSLAPolicyRegistryǁget_policy__mutmut_9(self, name: str, version: str | None = None) -> SLAPolicy | None:
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
            return max(matching, key=lambda p: None)
        
        # Return specific version
        for policy in matching:
            if policy.version == version:
                return policy
        
        return None

    def xǁSLAPolicyRegistryǁget_policy__mutmut_10(self, name: str, version: str | None = None) -> SLAPolicy | None:
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
            if policy.version != version:
                return policy
        
        return None
    
    xǁSLAPolicyRegistryǁget_policy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSLAPolicyRegistryǁget_policy__mutmut_1': xǁSLAPolicyRegistryǁget_policy__mutmut_1, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_2': xǁSLAPolicyRegistryǁget_policy__mutmut_2, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_3': xǁSLAPolicyRegistryǁget_policy__mutmut_3, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_4': xǁSLAPolicyRegistryǁget_policy__mutmut_4, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_5': xǁSLAPolicyRegistryǁget_policy__mutmut_5, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_6': xǁSLAPolicyRegistryǁget_policy__mutmut_6, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_7': xǁSLAPolicyRegistryǁget_policy__mutmut_7, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_8': xǁSLAPolicyRegistryǁget_policy__mutmut_8, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_9': xǁSLAPolicyRegistryǁget_policy__mutmut_9, 
        'xǁSLAPolicyRegistryǁget_policy__mutmut_10': xǁSLAPolicyRegistryǁget_policy__mutmut_10
    }
    
    def get_policy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSLAPolicyRegistryǁget_policy__mutmut_orig"), object.__getattribute__(self, "xǁSLAPolicyRegistryǁget_policy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_policy.__signature__ = _mutmut_signature(xǁSLAPolicyRegistryǁget_policy__mutmut_orig)
    xǁSLAPolicyRegistryǁget_policy__mutmut_orig.__name__ = 'xǁSLAPolicyRegistryǁget_policy'

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_orig(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if not (p.name == policy.name and p.version == policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = datetime.now(UTC).isoformat()

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_1(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = None
        self.policies.append(policy)
        self.last_updated = datetime.now(UTC).isoformat()

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_2(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if (p.name == policy.name and p.version == policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = datetime.now(UTC).isoformat()

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_3(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if not (p.name == policy.name or p.version == policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = datetime.now(UTC).isoformat()

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_4(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if not (p.name != policy.name and p.version == policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = datetime.now(UTC).isoformat()

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_5(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if not (p.name == policy.name and p.version != policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = datetime.now(UTC).isoformat()

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_6(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if not (p.name == policy.name and p.version == policy.version)
        ]
        self.policies.append(None)
        self.last_updated = datetime.now(UTC).isoformat()

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_7(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if not (p.name == policy.name and p.version == policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = None

    def xǁSLAPolicyRegistryǁadd_policy__mutmut_8(self, policy: SLAPolicy) -> None:
        """Add or update a policy in the registry."""
        # Remove existing policy with same name and version
        self.policies = [
            p for p in self.policies
            if not (p.name == policy.name and p.version == policy.version)
        ]
        self.policies.append(policy)
        self.last_updated = datetime.now(None).isoformat()
    
    xǁSLAPolicyRegistryǁadd_policy__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSLAPolicyRegistryǁadd_policy__mutmut_1': xǁSLAPolicyRegistryǁadd_policy__mutmut_1, 
        'xǁSLAPolicyRegistryǁadd_policy__mutmut_2': xǁSLAPolicyRegistryǁadd_policy__mutmut_2, 
        'xǁSLAPolicyRegistryǁadd_policy__mutmut_3': xǁSLAPolicyRegistryǁadd_policy__mutmut_3, 
        'xǁSLAPolicyRegistryǁadd_policy__mutmut_4': xǁSLAPolicyRegistryǁadd_policy__mutmut_4, 
        'xǁSLAPolicyRegistryǁadd_policy__mutmut_5': xǁSLAPolicyRegistryǁadd_policy__mutmut_5, 
        'xǁSLAPolicyRegistryǁadd_policy__mutmut_6': xǁSLAPolicyRegistryǁadd_policy__mutmut_6, 
        'xǁSLAPolicyRegistryǁadd_policy__mutmut_7': xǁSLAPolicyRegistryǁadd_policy__mutmut_7, 
        'xǁSLAPolicyRegistryǁadd_policy__mutmut_8': xǁSLAPolicyRegistryǁadd_policy__mutmut_8
    }
    
    def add_policy(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSLAPolicyRegistryǁadd_policy__mutmut_orig"), object.__getattribute__(self, "xǁSLAPolicyRegistryǁadd_policy__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_policy.__signature__ = _mutmut_signature(xǁSLAPolicyRegistryǁadd_policy__mutmut_orig)
    xǁSLAPolicyRegistryǁadd_policy__mutmut_orig.__name__ = 'xǁSLAPolicyRegistryǁadd_policy'

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
