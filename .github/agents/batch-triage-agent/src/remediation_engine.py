"""
Remediation Engine - Auto-fix generation with risk classification

Generates automated remediation suggestions and applies low-risk fixes
with appropriate approval gates and safety checks.
"""

import json
import logging
import shlex
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for remediation actions."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RemediationType(Enum):
    """Types of remediation actions."""
    
    DEPENDENCY_UPDATE = "dependency_update"
    CONFIG_FIX = "config_fix"
    CODE_FIX = "code_fix"
    WORKFLOW_FIX = "workflow_fix"
    RERUN = "rerun"
    INVESTIGATE = "investigate"


@dataclass
class RemediationAction:
    """A remediation action with risk classification."""
    
    action_id: str
    remediation_type: RemediationType
    risk_level: RiskLevel
    confidence: float
    description: str
    automated_fix: Optional[str] = None
    manual_steps: Optional[List[str]] = None
    files_to_modify: Optional[List[str]] = None
    approval_required: bool = True
    estimated_resolution_time_minutes: int = 30
    
    def __post_init__(self):
        if self.manual_steps is None:
            self.manual_steps = []
        if self.files_to_modify is None:
            self.files_to_modify = []
        
        # Auto-determine approval requirement
        if self.risk_level == RiskLevel.LOW and self.confidence >= 0.9:
            self.approval_required = False
        else:
            self.approval_required = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "remediation_type": self.remediation_type.value,
            "risk_level": self.risk_level.value,
            "confidence": self.confidence,
            "description": self.description,
            "automated_fix": self.automated_fix,
            "manual_steps": self.manual_steps,
            "files_to_modify": self.files_to_modify,
            "approval_required": self.approval_required,
            "estimated_resolution_time_minutes": self.estimated_resolution_time_minutes,
        }


class RemediationEngine:
    """
    Generates and applies remediation actions with risk-based approval gates.
    
    Capabilities:
    - Auto-fix generation
    - Risk classification
    - Approval gate management
    - Safe fix application
    """
    
    def __init__(
        self,
        repo_root: Path = Path("."),
        dry_run: bool = False,
    ):
        """
        Initialize remediation engine.
        
        Args:
            repo_root: Repository root path
            dry_run: If True, simulate fixes without applying
        """
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.actions: List[RemediationAction] = []
    
    def generate_remediation(
        self,
        failure_type: str,
        root_cause: str,
        detected_issues: List[Dict[str, Any]],
        suggested_actions: List[Dict[str, Any]],
        confidence: float = 0.5,
    ) -> List[RemediationAction]:
        """
        Generate remediation actions for a failure.
        
        Args:
            failure_type: Type of failure
            root_cause: Root cause description
            detected_issues: List of detected issues
            suggested_actions: List of suggested actions
            confidence: Confidence score
            
        Returns:
            List of remediation actions
        """
        actions = []
        
        # Generate actions based on failure type
        if failure_type == "test_failure":
            actions.extend(self._generate_test_failure_remediations(
                root_cause, detected_issues, confidence
            ))
        elif failure_type == "import_error":
            actions.extend(self._generate_import_error_remediations(
                root_cause, detected_issues, confidence
            ))
        elif failure_type == "build_failure":
            actions.extend(self._generate_build_failure_remediations(
                root_cause, detected_issues, confidence
            ))
        elif failure_type == "lint_error":
            actions.extend(self._generate_lint_error_remediations(
                root_cause, detected_issues, confidence
            ))
        else:
            # Generic remediation
            actions.append(self._generate_generic_remediation(
                failure_type, root_cause, confidence
            ))
        
        # Add suggested actions from self-healing engine
        for suggested in suggested_actions:
            action = self._convert_suggested_action(suggested, confidence)
            if action:
                actions.append(action)
        
        self.actions.extend(actions)
        return actions
    
    def _generate_test_failure_remediations(
        self,
        root_cause: str,
        detected_issues: List[Dict[str, Any]],
        confidence: float,
    ) -> List[RemediationAction]:
        """Generate remediations for test failures."""
        actions = []
        
        # Check if it's an assertion error
        if "assertion" in root_cause.lower():
            actions.append(RemediationAction(
                action_id=f"test_fix_{id(root_cause)}",
                remediation_type=RemediationType.CODE_FIX,
                risk_level=RiskLevel.MEDIUM,
                confidence=confidence,
                description=f"Update test assertions for: {root_cause[:100]}",
                manual_steps=[
                    "Review test failure logs",
                    "Update expected values in assertions",
                    "Run tests locally to verify",
                ],
                estimated_resolution_time_minutes=20,
            ))
        else:
            # Generic test rerun
            actions.append(RemediationAction(
                action_id=f"test_rerun_{id(root_cause)}",
                remediation_type=RemediationType.RERUN,
                risk_level=RiskLevel.LOW,
                confidence=0.6,
                description="Rerun failed tests (may be flaky)",
                automated_fix="gh workflow run test.yml",
                estimated_resolution_time_minutes=5,
            ))
        
        return actions
    
    def _generate_import_error_remediations(
        self,
        root_cause: str,
        detected_issues: List[Dict[str, Any]],
        confidence: float,
    ) -> List[RemediationAction]:
        """Generate remediations for import errors."""
        actions = []
        
        # Extract module name
        import re
        match = re.search(r"module['\"]?\s*['\"]?(\S+)['\"]?", root_cause, re.IGNORECASE)
        module_name = match.group(1) if match else "unknown"
        
        actions.append(RemediationAction(
            action_id=f"dep_install_{id(root_cause)}",
            remediation_type=RemediationType.DEPENDENCY_UPDATE,
            risk_level=RiskLevel.LOW,
            confidence=min(confidence + 0.2, 1.0),
            description=f"Install missing dependency: {module_name}",
            automated_fix=f"pip install {module_name}",
            manual_steps=[
                f"Add {module_name} to requirements.txt",
                "Run pip install -e .",
                "Verify import works",
            ],
            estimated_resolution_time_minutes=10,
        ))
        
        return actions
    
    def _generate_build_failure_remediations(
        self,
        root_cause: str,
        detected_issues: List[Dict[str, Any]],
        confidence: float,
    ) -> List[RemediationAction]:
        """Generate remediations for build failures."""
        actions = []
        
        actions.append(RemediationAction(
            action_id=f"build_investigate_{id(root_cause)}",
            remediation_type=RemediationType.INVESTIGATE,
            risk_level=RiskLevel.HIGH,
            confidence=confidence,
            description=f"Investigate build failure: {root_cause[:100]}",
            manual_steps=[
                "Review build logs",
                "Check for configuration issues",
                "Verify dependencies are installed",
                "Test build locally",
            ],
            estimated_resolution_time_minutes=60,
        ))
        
        return actions
    
    def _generate_lint_error_remediations(
        self,
        root_cause: str,
        detected_issues: List[Dict[str, Any]],
        confidence: float,
    ) -> List[RemediationAction]:
        """Generate remediations for lint errors."""
        actions = []
        
        actions.append(RemediationAction(
            action_id=f"lint_fix_{id(root_cause)}",
            remediation_type=RemediationType.CODE_FIX,
            risk_level=RiskLevel.LOW,
            confidence=0.85,
            description="Auto-fix lint errors",
            automated_fix="ruff check --fix .",
            manual_steps=[
                "Run ruff check --fix .",
                "Run black .",
                "Review changes",
                "Commit fixes",
            ],
            estimated_resolution_time_minutes=10,
        ))
        
        return actions
    
    def _generate_generic_remediation(
        self,
        failure_type: str,
        root_cause: str,
        confidence: float,
    ) -> RemediationAction:
        """Generate generic remediation."""
        return RemediationAction(
            action_id=f"generic_{id(root_cause)}",
            remediation_type=RemediationType.INVESTIGATE,
            risk_level=RiskLevel.HIGH,
            confidence=confidence,
            description=f"Investigate {failure_type}: {root_cause[:100]}",
            manual_steps=[
                "Review failure logs",
                "Identify root cause",
                "Develop fix",
                "Test locally",
                "Apply fix",
            ],
            estimated_resolution_time_minutes=45,
        )
    
    def _convert_suggested_action(
        self,
        suggested: Dict[str, Any],
        confidence: float,
    ) -> Optional[RemediationAction]:
        """Convert suggested action to RemediationAction."""
        action_type = suggested.get("action_type", "unknown")
        description = suggested.get("description", "No description")
        
        # Map action types to remediation types
        type_mapping = {
            "dependency_update": RemediationType.DEPENDENCY_UPDATE,
            "config_fix": RemediationType.CONFIG_FIX,
            "code_fix": RemediationType.CODE_FIX,
            "rerun": RemediationType.RERUN,
        }
        
        remediation_type = type_mapping.get(action_type, RemediationType.INVESTIGATE)
        
        # Determine risk level
        risk_level = RiskLevel.MEDIUM
        if remediation_type == RemediationType.RERUN:
            risk_level = RiskLevel.LOW
        elif remediation_type == RemediationType.CODE_FIX:
            risk_level = RiskLevel.HIGH
        
        return RemediationAction(
            action_id=f"action_{id(suggested)}",
            remediation_type=remediation_type,
            risk_level=risk_level,
            confidence=confidence,
            description=description,
            estimated_resolution_time_minutes=30,
        )
    
    def classify_risk(self, action: RemediationAction) -> RiskLevel:
        """
        Classify risk level for a remediation action.
        
        Args:
            action: Remediation action
            
        Returns:
            Risk level
        """
        # Already classified, but allow re-evaluation
        
        # Low risk: high confidence, no code changes, reversible
        if (action.confidence >= 0.9 and 
            action.remediation_type in [RemediationType.RERUN, RemediationType.DEPENDENCY_UPDATE]):
            return RiskLevel.LOW
        
        # High risk: code changes, low confidence, affects multiple files
        if (action.remediation_type == RemediationType.CODE_FIX or
            action.confidence < 0.5 or
            (action.files_to_modify and len(action.files_to_modify) > 5)):
            return RiskLevel.HIGH
        
        # Medium risk: everything else
        return RiskLevel.MEDIUM
    
    def filter_by_risk(self, risk_level: RiskLevel) -> List[RemediationAction]:
        """
        Filter actions by risk level.
        
        Args:
            risk_level: Risk level to filter by
            
        Returns:
            List of matching actions
        """
        return [a for a in self.actions if a.risk_level == risk_level]
    
    def apply_action(self, action: RemediationAction) -> Dict[str, Any]:
        """
        Apply a remediation action.
        
        Args:
            action: Action to apply
            
        Returns:
            Result dictionary
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would apply action: {action.action_id}")
            return {"success": True, "dry_run": True, "action_id": action.action_id}
        
        if action.approval_required:
            logger.warning(f"Action {action.action_id} requires approval - skipping auto-apply")
            return {"success": False, "error": "Approval required", "action_id": action.action_id}
        
        if not action.automated_fix:
            logger.warning(f"Action {action.action_id} has no automated fix")
            return {"success": False, "error": "No automated fix", "action_id": action.action_id}
        
        # Apply automated fix
        try:
            import subprocess
            # Use shlex.split to safely parse the command string
            # This prevents shell injection vulnerabilities
            cmd_args = shlex.split(action.automated_fix)
            result = subprocess.run(
                cmd_args,
                shell=False,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.repo_root,
            )
            
            success = result.returncode == 0
            return {
                "success": success,
                "action_id": action.action_id,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as e:
            logger.error(f"Failed to apply action {action.action_id}: {e}")
            return {"success": False, "error": str(e), "action_id": action.action_id}
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate remediation report.
        
        Returns:
            Report dictionary
        """
        by_risk = {
            "low": self.filter_by_risk(RiskLevel.LOW),
            "medium": self.filter_by_risk(RiskLevel.MEDIUM),
            "high": self.filter_by_risk(RiskLevel.HIGH),
        }
        
        return {
            "total_actions": len(self.actions),
            "by_risk_level": {
                "low": len(by_risk["low"]),
                "medium": len(by_risk["medium"]),
                "high": len(by_risk["high"]),
            },
            "auto_appliable": sum(1 for a in self.actions if not a.approval_required),
            "requires_approval": sum(1 for a in self.actions if a.approval_required),
            "actions": [a.to_dict() for a in self.actions],
        }
