"""Contract Gate System — 8-gate compliance validator for Phase 2 Foundation.

Implements 8-gate compliance validation for proposals:
- Gate 1: Contract Schema Validation
- Gate 2: Regression Test Validation
- Gate 3: Security Audit Pass
- Gate 4: Policy Tier Compliance
- Gate 5: Input-Lock Immutability
- Gate 6: Output-Contract Schema Match
- Gate 7: Decision-Trace Integrity
- Gate 8: Rollback Instruction Completeness
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema

logger = logging.getLogger(__name__)


class ContractGateError(Exception):
    """Raised when contract gate validation fails."""

    pass


@dataclass
class GateResult:
    """Result of a single gate validation."""

    gate_number: int
    gate_name: str
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "gate_number": self.gate_number,
            "gate_name": self.gate_name,
            "passed": self.passed,
            "details": self.details,
            "timestamp": self.timestamp,
            "error_message": self.error_message,
        }


@dataclass
class ComplianceResult:
    """Result of full 8-gate compliance check."""

    proposal_id: str
    all_passed: bool
    gate_results: List[GateResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "proposal_id": self.proposal_id,
            "all_passed": self.all_passed,
            "timestamp": self.timestamp,
            "gate_results": [
                {
                    "gate_number": r.gate_number,
                    "gate_name": r.gate_name,
                    "passed": r.passed,
                    "details": r.details,
                    "timestamp": r.timestamp,
                    "error_message": r.error_message,
                }
                for r in self.gate_results
            ],
            "summary": self.summary,
        }


class ContractGateSystem:
    """8-gate compliance validator for Phase 2 Foundation."""

    GATE_CONFIGS = {
        1: {
            "name": "Contract Schema Validation",
            "description": "Validate proposal structure against contract schema",
        },
        2: {
            "name": "Regression Test Validation",
            "description": "Verify regression tests pass for proposed changes",
        },
        3: {
            "name": "Security Audit Pass",
            "description": "Validate security audit completed and passed",
        },
        4: {
            "name": "Policy Tier Compliance",
            "description": "Verify action meets policy tier requirements",
        },
        5: {
            "name": "Input-Lock Immutability",
            "description": "Confirm input locks are immutable and signed",
        },
        6: {
            "name": "Output-Contract Schema Match",
            "description": "Validate output matches expected contract schema",
        },
        7: {
            "name": "Decision-Trace Integrity",
            "description": "Verify decision trace is complete and signed",
        },
        8: {
            "name": "Rollback Instruction Completeness",
            "description": "Confirm rollback instructions are present and valid",
        },
    }

    PROPOSAL_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Proposal",
        "type": "object",
        "required": ["lane_id", "action_type", "description"],
        "properties": {
            "lane_id": {"type": "string"},
            "action_type": {"type": "string"},
            "description": {"type": "string"},
            "affected_modules": {
                "type": "array",
                "items": {"type": "string"},
            },
            "metadata": {"type": "object"},
        },
    }

    def __init__(self, decision_trace_writer=None):
        """Initialize the contract gate system.

        Args:
            decision_trace_writer: Optional decision trace writer for logging
        """
        self.decision_trace_writer = decision_trace_writer

    def validate_gate_1_schema(self, proposal: Dict[str, Any]) -> GateResult:
        """Gate 1: Validate proposal structure against schema."""
        gate_num = 1
        gate_name = self.GATE_CONFIGS[gate_num]["name"]

        try:
            jsonschema.validate(proposal, self.PROPOSAL_SCHEMA)
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=True,
                details={"schema_version": "1.0", "validation_method": "jsonschema"},
            )
            logger.info(f"Gate {gate_num} ({gate_name}): PASS")
            return result
        except jsonschema.ValidationError as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=f"Schema validation failed: {e.message}",
            )
            logger.warning(f"Gate {gate_num} ({gate_name}): FAIL - {e.message}")
            return result
        except Exception as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=str(e),
            )
            logger.error(f"Gate {gate_num} ({gate_name}): ERROR - {e}")
            return result

    def validate_gate_2_regression_tests(
        self, proposal: Dict[str, Any]
    ) -> GateResult:
        """Gate 2: Verify regression tests pass."""
        gate_num = 2
        gate_name = self.GATE_CONFIGS[gate_num]["name"]

        try:
            test_results = proposal.get("regression_tests", {})
            passed = test_results.get("passed", False)
            test_count = test_results.get("test_count", 0)

            if not passed:
                result = GateResult(
                    gate_number=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    details={"test_count": test_count},
                    error_message="Regression tests did not pass",
                )
                logger.warning(f"Gate {gate_num} ({gate_name}): FAIL")
                return result

            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=True,
                details={"test_count": test_count, "all_passed": True},
            )
            logger.info(f"Gate {gate_num} ({gate_name}): PASS ({test_count} tests)")
            return result
        except Exception as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=str(e),
            )
            logger.error(f"Gate {gate_num} ({gate_name}): ERROR - {e}")
            return result

    def validate_gate_3_security_audit(self, proposal: Dict[str, Any]) -> GateResult:
        """Gate 3: Validate security audit pass."""
        gate_num = 3
        gate_name = self.GATE_CONFIGS[gate_num]["name"]

        try:
            security_audit = proposal.get("security_audit", {})
            passed = security_audit.get("passed", False)
            issues = security_audit.get("issues", [])

            if not passed:
                result = GateResult(
                    gate_number=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    details={"issue_count": len(issues)},
                    error_message="Security audit did not pass",
                )
                logger.warning(f"Gate {gate_num} ({gate_name}): FAIL ({len(issues)} issues)")
                return result

            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=True,
                details={"issue_count": len(issues), "audit_passed": True},
            )
            logger.info(f"Gate {gate_num} ({gate_name}): PASS")
            return result
        except Exception as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=str(e),
            )
            logger.error(f"Gate {gate_num} ({gate_name}): ERROR - {e}")
            return result

    def validate_gate_4_policy_tier(self, proposal: Dict[str, Any]) -> GateResult:
        """Gate 4: Verify policy tier compliance."""
        gate_num = 4
        gate_name = self.GATE_CONFIGS[gate_num]["name"]

        try:
            policy_tier = proposal.get("policy_tier", None)
            valid_tiers = ["T0", "T1", "T2", "T3"]

            if policy_tier not in valid_tiers:
                result = GateResult(
                    gate_number=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    details={"policy_tier": policy_tier, "valid_tiers": valid_tiers},
                    error_message=f"Invalid policy tier: {policy_tier}",
                )
                logger.warning(f"Gate {gate_num} ({gate_name}): FAIL")
                return result

            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=True,
                details={"policy_tier": policy_tier},
            )
            logger.info(f"Gate {gate_num} ({gate_name}): PASS (tier: {policy_tier})")
            return result
        except Exception as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=str(e),
            )
            logger.error(f"Gate {gate_num} ({gate_name}): ERROR - {e}")
            return result

    def validate_gate_5_input_lock(self, proposal: Dict[str, Any]) -> GateResult:
        """Gate 5: Confirm input-lock immutability."""
        gate_num = 5
        gate_name = self.GATE_CONFIGS[gate_num]["name"]

        try:
            input_lock = proposal.get("input_lock", {})
            lock_hash = input_lock.get("lock_hash", None)
            is_signed = input_lock.get("is_signed", False)

            if not lock_hash or not is_signed:
                result = GateResult(
                    gate_number=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    details={"has_lock_hash": bool(lock_hash), "is_signed": is_signed},
                    error_message="Input lock is not properly signed",
                )
                logger.warning(f"Gate {gate_num} ({gate_name}): FAIL")
                return result

            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=True,
                details={"has_lock_hash": True, "is_signed": True},
            )
            logger.info(f"Gate {gate_num} ({gate_name}): PASS")
            return result
        except Exception as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=str(e),
            )
            logger.error(f"Gate {gate_num} ({gate_name}): ERROR - {e}")
            return result

    def validate_gate_6_output_contract(self, proposal: Dict[str, Any]) -> GateResult:
        """Gate 6: Validate output matches contract schema."""
        gate_num = 6
        gate_name = self.GATE_CONFIGS[gate_num]["name"]

        try:
            output_contract = proposal.get("output_contract", {})
            schema = output_contract.get("schema", {})
            output = proposal.get("output", {})

            if not schema:
                result = GateResult(
                    gate_number=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    error_message="No output schema defined",
                )
                logger.warning(f"Gate {gate_num} ({gate_name}): FAIL")
                return result

            try:
                jsonschema.validate(output, schema)
            except jsonschema.ValidationError as e:
                result = GateResult(
                    gate_number=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    error_message=f"Output schema mismatch: {e.message}",
                )
                logger.warning(f"Gate {gate_num} ({gate_name}): FAIL")
                return result

            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=True,
                details={"schema_validated": True},
            )
            logger.info(f"Gate {gate_num} ({gate_name}): PASS")
            return result
        except Exception as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=str(e),
            )
            logger.error(f"Gate {gate_num} ({gate_name}): ERROR - {e}")
            return result

    def validate_gate_7_decision_trace(self, proposal: Dict[str, Any]) -> GateResult:
        """Gate 7: Verify decision-trace integrity."""
        gate_num = 7
        gate_name = self.GATE_CONFIGS[gate_num]["name"]

        try:
            decision_trace = proposal.get("decision_trace", {})
            trace_id = decision_trace.get("trace_id", None)
            is_signed = decision_trace.get("is_signed", False)
            entries = decision_trace.get("entries", [])

            if not trace_id or not is_signed or not entries:
                result = GateResult(
                    gate_number=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    details={
                        "has_trace_id": bool(trace_id),
                        "is_signed": is_signed,
                        "entry_count": len(entries),
                    },
                    error_message="Decision trace is incomplete or not signed",
                )
                logger.warning(f"Gate {gate_num} ({gate_name}): FAIL")
                return result

            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=True,
                details={
                    "has_trace_id": True,
                    "is_signed": True,
                    "entry_count": len(entries),
                },
            )
            logger.info(f"Gate {gate_num} ({gate_name}): PASS ({len(entries)} entries)")
            return result
        except Exception as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=str(e),
            )
            logger.error(f"Gate {gate_num} ({gate_name}): ERROR - {e}")
            return result

    def validate_gate_8_rollback(self, proposal: Dict[str, Any]) -> GateResult:
        """Gate 8: Confirm rollback instructions completeness."""
        gate_num = 8
        gate_name = self.GATE_CONFIGS[gate_num]["name"]

        try:
            rollback_instructions = proposal.get("rollback_instructions", {})
            steps = rollback_instructions.get("steps", [])
            is_validated = rollback_instructions.get("is_validated", False)

            if not steps or not is_validated:
                result = GateResult(
                    gate_number=gate_num,
                    gate_name=gate_name,
                    passed=False,
                    details={"step_count": len(steps), "is_validated": is_validated},
                    error_message="Rollback instructions incomplete or not validated",
                )
                logger.warning(f"Gate {gate_num} ({gate_name}): FAIL")
                return result

            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=True,
                details={"step_count": len(steps), "is_validated": True},
            )
            logger.info(f"Gate {gate_num} ({gate_name}): PASS ({len(steps)} steps)")
            return result
        except Exception as e:
            result = GateResult(
                gate_number=gate_num,
                gate_name=gate_name,
                passed=False,
                error_message=str(e),
            )
            logger.error(f"Gate {gate_num} ({gate_name}): ERROR - {e}")
            return result

    def validate_all_gates(self, proposal: Dict[str, Any]) -> ComplianceResult:
        """Run all 8 gates in sequence.

        Args:
            proposal: Proposal dictionary to validate

        Returns:
            ComplianceResult with all gate results

        Raises:
            ContractGateError: If validation setup fails
        """
        try:
            proposal_id = proposal.get("proposal_id", "unknown")
            gate_results = []

            # Run gates in order
            gate_results.append(self.validate_gate_1_schema(proposal))
            gate_results.append(self.validate_gate_2_regression_tests(proposal))
            gate_results.append(self.validate_gate_3_security_audit(proposal))
            gate_results.append(self.validate_gate_4_policy_tier(proposal))
            gate_results.append(self.validate_gate_5_input_lock(proposal))
            gate_results.append(self.validate_gate_6_output_contract(proposal))
            gate_results.append(self.validate_gate_7_decision_trace(proposal))
            gate_results.append(self.validate_gate_8_rollback(proposal))

            # Check if all passed
            all_passed = all(r.passed for r in gate_results)

            # Build summary
            summary = {
                "total_gates": 8,
                "passed_gates": sum(1 for r in gate_results if r.passed),
                "failed_gates": sum(1 for r in gate_results if not r.passed),
                "pass_rate": (sum(1 for r in gate_results if r.passed) / 8) * 100,
            }

            compliance_result = ComplianceResult(
                proposal_id=proposal_id,
                all_passed=all_passed,
                gate_results=gate_results,
                summary=summary,
            )

            # Log to decision trace if available
            if self.decision_trace_writer:
                self.decision_trace_writer.write(
                    {
                        "event": "compliance_check",
                        "proposal_id": proposal_id,
                        "all_passed": all_passed,
                        "summary": summary,
                    }
                )

            return compliance_result
        except Exception as e:
            raise ContractGateError(f"Failed to validate gates: {e}")
