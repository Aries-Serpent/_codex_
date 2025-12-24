#!/usr/bin/env python3
"""
AI-Driven Autonomous Codebase Management System

This module provides the foundation for achieving truly autonomous codebase
management where AI handles routine maintenance, optimization, and evolution
through self-directed actions, proactive monitoring, and intelligent decision-making.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import hashlib
import sys
import ast
import re


class ActionType(Enum):
    """Types of autonomous actions."""
    MAINTENANCE = "maintenance"
    OPTIMIZATION = "optimization"
    REFACTORING = "refactoring"
    SECURITY = "security"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEPENDENCY = "dependency"


class DecisionLevel(Enum):
    """Level of decision-making authority."""
    AUTONOMOUS = "autonomous"  # AI can execute immediately
    APPROVAL_REQUIRED = "approval_required"  # Needs human approval
    ESCALATE = "escalate"  # Must escalate to human


class HealthStatus(Enum):
    """Codebase health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DEGRADED = "degraded"


@dataclass
class HealthMetric:
    """Represents a single health metric."""
    name: str
    value: float
    threshold: float
    status: HealthStatus
    timestamp: str
    recommendation: Optional[str] = None


@dataclass
class ProposedAction:
    """Represents a proposed autonomous action."""
    id: str
    type: ActionType
    decision_level: DecisionLevel
    description: str
    rationale: str
    estimated_impact: str
    risk_level: str  # low, medium, high
    reversibility: bool
    estimated_duration: str
    proposed_at: str
    approved: bool = False
    executed: bool = False
    execution_result: Optional[str] = None


@dataclass
class CodebaseHealth:
    """Overall codebase health assessment."""
    timestamp: str
    overall_status: HealthStatus
    metrics: List[HealthMetric]
    proposed_actions: List[ProposedAction]
    alerts: List[str]


class CodeHealthSensor:
    """Monitors codebase health through various checks."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()
    
    def analyze_complexity(self) -> List[HealthMetric]:
        """Analyze code complexity across the codebase."""
        metrics = []
        high_complexity_files = []
        
        for py_file in self.repo_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in ['.venv', '__pycache__', 'build']):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Simple cyclomatic complexity approximation
                        complexity = self._calculate_complexity(node)
                        if complexity > 15:
                            high_complexity_files.append((str(py_file), node.name, complexity))
            
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                continue
        
        if high_complexity_files:
            avg_complexity = sum(c for _, _, c in high_complexity_files) / len(high_complexity_files)
            status = HealthStatus.WARNING if avg_complexity > 20 else HealthStatus.HEALTHY
            
            metrics.append(HealthMetric(
                name="code_complexity",
                value=avg_complexity,
                threshold=15.0,
                status=status,
                timestamp=datetime.now().isoformat(),
                recommendation=f"Found {len(high_complexity_files)} high-complexity functions"
            ))
        
        return metrics
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate approximate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def detect_duplicate_code(self) -> List[HealthMetric]:
        """Detect duplicate code blocks."""
        metrics = []
        
        # Simple hash-based duplicate detection
        code_hashes: Dict[str, List[str]] = {}
        
        for py_file in self.repo_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in ['.venv', '__pycache__']):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                # Hash chunks of code
                lines = content.split('\n')
                for i in range(0, len(lines) - 10, 5):
                    chunk = '\n'.join(lines[i:i+10])
                    chunk_hash = hashlib.md5(chunk.encode(), usedforsecurity=False).hexdigest()
                    if chunk_hash not in code_hashes:
                        code_hashes[chunk_hash] = []
                    code_hashes[chunk_hash].append(str(py_file))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                continue
        
        duplicates = {h: files for h, files in code_hashes.items() if len(set(files)) > 1}
        duplicate_ratio = len(duplicates) / max(len(code_hashes), 1)
        
        status = HealthStatus.WARNING if duplicate_ratio > 0.1 else HealthStatus.HEALTHY
        
        metrics.append(HealthMetric(
            name="code_duplication",
            value=duplicate_ratio,
            threshold=0.1,
            status=status,
            timestamp=datetime.now().isoformat(),
            recommendation=f"Found {len(duplicates)} duplicate code blocks" if duplicates else None
        ))
        
        return metrics
    
    def check_test_coverage(self) -> List[HealthMetric]:
        """Estimate test coverage by checking test file presence."""
        metrics = []
        
        source_files = list(self.repo_path.rglob("src/**/*.py"))
        test_files = list(self.repo_path.rglob("tests/**/test_*.py"))
        
        if source_files:
            coverage_ratio = len(test_files) / len(source_files)
            status = HealthStatus.HEALTHY if coverage_ratio > 0.8 else HealthStatus.WARNING
            
            metrics.append(HealthMetric(
                name="test_coverage",
                value=coverage_ratio,
                threshold=0.8,
                status=status,
                timestamp=datetime.now().isoformat(),
                recommendation=f"Test files: {len(test_files)}, Source files: {len(source_files)}"
            ))
        
        return metrics
    
    def scan_security_issues(self) -> List[HealthMetric]:
        """Scan for common security issues."""
        metrics = []
        security_issues = []
        
        for py_file in self.repo_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in ['.venv', '__pycache__']):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check for common security anti-patterns
                if re.search(r'eval\s*\(', content):
                    security_issues.append((str(py_file), "eval() usage"))
                if re.search(r'exec\s*\(', content):
                    security_issues.append((str(py_file), "exec() usage"))
                if re.search(r'pickle\.loads?\(', content):
                    security_issues.append((str(py_file), "pickle usage"))
                
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                continue
        
        status = HealthStatus.WARNING if security_issues else HealthStatus.HEALTHY
        
        metrics.append(HealthMetric(
            name="security_scan",
            value=len(security_issues),
            threshold=0.0,
            status=status,
            timestamp=datetime.now().isoformat(),
            recommendation=f"Found {len(security_issues)} potential security issues" if security_issues else "No obvious security issues"
        ))
        
        return metrics


class ActionProposer:
    """Proposes autonomous actions based on health metrics."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()
    
    def propose_actions(self, health: CodebaseHealth) -> List[ProposedAction]:
        """Propose actions based on health metrics."""
        actions = []
        
        for metric in health.metrics:
            if metric.status in (HealthStatus.WARNING, HealthStatus.CRITICAL):
                action = self._create_action_for_metric(metric)
                if action:
                    actions.append(action)
        
        return actions
    
    def _create_action_for_metric(self, metric: HealthMetric) -> Optional[ProposedAction]:
        """Create an appropriate action for a metric."""
        if metric.name == "code_complexity":
            return ProposedAction(
                id=self._generate_id("complexity"),
                type=ActionType.REFACTORING,
                decision_level=DecisionLevel.APPROVAL_REQUIRED,
                description="Refactor high-complexity functions",
                rationale=f"Average complexity {metric.value:.1f} exceeds threshold {metric.threshold}",
                estimated_impact="Improved maintainability and readability",
                risk_level="medium",
                reversibility=True,
                estimated_duration="2-4 hours",
                proposed_at=datetime.now().isoformat()
            )
        
        elif metric.name == "code_duplication":
            return ProposedAction(
                id=self._generate_id("duplication"),
                type=ActionType.REFACTORING,
                decision_level=DecisionLevel.APPROVAL_REQUIRED,
                description="Extract duplicate code into shared utilities",
                rationale=f"Duplication ratio {metric.value:.1%} exceeds threshold",
                estimated_impact="Reduced code size and maintenance burden",
                risk_level="low",
                reversibility=True,
                estimated_duration="1-2 hours",
                proposed_at=datetime.now().isoformat()
            )
        
        elif metric.name == "test_coverage":
            return ProposedAction(
                id=self._generate_id("tests"),
                type=ActionType.TESTING,
                decision_level=DecisionLevel.AUTONOMOUS,
                description="Generate missing test files",
                rationale=f"Test coverage {metric.value:.1%} below threshold",
                estimated_impact="Improved code quality and confidence",
                risk_level="low",
                reversibility=True,
                estimated_duration="30 minutes",
                proposed_at=datetime.now().isoformat()
            )
        
        elif metric.name == "security_scan":
            if metric.value > 0:
                return ProposedAction(
                    id=self._generate_id("security"),
                    type=ActionType.SECURITY,
                    decision_level=DecisionLevel.ESCALATE,
                    description="Address potential security vulnerabilities",
                    rationale=f"Found {int(metric.value)} potential security issues",
                    estimated_impact="Enhanced security posture",
                    risk_level="high",
                    reversibility=False,
                    estimated_duration="Variable",
                    proposed_at=datetime.now().isoformat()
                )
        
        return None
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique action ID."""
        timestamp = datetime.now().isoformat()
        content = f"{prefix}:{timestamp}"
        return hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:12]


class AutonomousAgent:
    """Main autonomous codebase management agent."""
    
    def __init__(self, repo_path: Path, config_path: Optional[Path] = None):
        self.repo_path = repo_path.resolve()
        self.config_path = config_path or (repo_path / ".codex" / "autonomous_agent.json")
        self.config = self._load_config()
        
        self.sensor = CodeHealthSensor(repo_path)
        self.proposer = ActionProposer(repo_path)
        
        self.state_path = repo_path / ".codex" / "agent_state"
        self.state_path.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        
        # Default configuration
        return {
            "autonomous_actions_enabled": True,
            "approval_threshold": "medium",
            "monitoring_interval_minutes": 30,
            "max_autonomous_actions_per_cycle": 3,
            "learning_enabled": True,
            "rollback_enabled": True
        }
    
    def assess_health(self) -> CodebaseHealth:
        """Assess current codebase health."""
        print("Assessing codebase health...")
        
        all_metrics = []
        
        # Run all sensors
        all_metrics.extend(self.sensor.analyze_complexity())
        all_metrics.extend(self.sensor.detect_duplicate_code())
        all_metrics.extend(self.sensor.check_test_coverage())
        all_metrics.extend(self.sensor.scan_security_issues())
        
        # Determine overall status
        statuses = [m.status for m in all_metrics]
        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Generate alerts
        alerts = []
        for metric in all_metrics:
            if metric.status in (HealthStatus.WARNING, HealthStatus.CRITICAL):
                alerts.append(f"{metric.name}: {metric.recommendation}")
        
        return CodebaseHealth(
            timestamp=datetime.now().isoformat(),
            overall_status=overall_status,
            metrics=all_metrics,
            proposed_actions=[],
            alerts=alerts
        )
    
    def propose_improvements(self, health: CodebaseHealth) -> List[ProposedAction]:
        """Propose improvement actions based on health assessment."""
        print("Proposing improvement actions...")
        
        actions = self.proposer.propose_actions(health)
        
        # Filter based on configuration
        max_actions = self.config.get("max_autonomous_actions_per_cycle", 3)
        
        # Prioritize by decision level and risk
        actions.sort(key=lambda a: (
            a.decision_level.value,
            {"low": 0, "medium": 1, "high": 2}[a.risk_level]
        ))
        
        return actions[:max_actions]
    
    def execute_autonomous_actions(self, actions: List[ProposedAction]) -> List[ProposedAction]:
        """Execute actions that don't require approval."""
        if not self.config.get("autonomous_actions_enabled", True):
            print("Autonomous actions are disabled")
            return []
        
        executed = []
        
        for action in actions:
            if action.decision_level == DecisionLevel.AUTONOMOUS:
                print(f"Executing autonomous action: {action.description}")
                
                # Execute the action
                result = self._execute_action(action)
                action.executed = True
                action.execution_result = result
                
                executed.append(action)
                
                # Learn from execution
                if self.config.get("learning_enabled", True):
                    self._record_execution(action)
        
        return executed
    
    def _execute_action(self, action: ProposedAction) -> str:
        """Execute a specific action."""
        # Placeholder for actual execution logic
        # In a real implementation, this would call appropriate tools
        
        if action.type == ActionType.TESTING:
            return "Test generation would be triggered here"
        elif action.type == ActionType.MAINTENANCE:
            return "Maintenance tasks would be executed here"
        else:
            return f"Action of type {action.type.value} would be executed here"
    
    def _record_execution(self, action: ProposedAction):
        """Record action execution for learning."""
        execution_log = self.state_path / "execution_log.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_id": action.id,
            "action_type": action.type.value,
            "result": action.execution_result,
            "success": action.execution_result is not None
        }
        
        with open(execution_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def save_state(self, health: CodebaseHealth, actions: List[ProposedAction]):
        """Save current agent state."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "health": asdict(health),
            "actions": [asdict(a) for a in actions]
        }
        
        state_file = self.state_path / f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"State saved: {state_file}")
    
    def run_cycle(self) -> Tuple[CodebaseHealth, List[ProposedAction]]:
        """Run a complete monitoring and action cycle."""
        print("="*70)
        print("Starting Autonomous Agent Cycle")
        print("="*70)
        
        # Assess health
        health = self.assess_health()
        
        # Propose actions
        actions = self.propose_improvements(health)
        health.proposed_actions = actions
        
        # Execute autonomous actions
        executed = self.execute_autonomous_actions(actions)
        
        # Save state
        self.save_state(health, actions)
        
        # Print summary
        self.print_summary(health, actions, executed)
        
        return health, actions
    
    def print_summary(self, health: CodebaseHealth, actions: List[ProposedAction], executed: List[ProposedAction]):
        """Print cycle summary."""
        print("\n" + "="*70)
        print("Autonomous Agent Cycle Summary")
        print("="*70)
        print(f"Overall Health: {health.overall_status.value}")
        print(f"Metrics Checked: {len(health.metrics)}")
        print(f"Alerts: {len(health.alerts)}")
        print(f"Proposed Actions: {len(actions)}")
        print(f"Executed Actions: {len(executed)}")
        
        if health.alerts:
            print("\n⚠ Alerts:")
            for alert in health.alerts[:5]:
                print(f"  - {alert}")
        
        if actions:
            print(f"\n📋 Proposed Actions:")
            for action in actions:
                status = "✓ Executed" if action.executed else "⏸ Pending Approval"
                print(f"  [{status}] {action.description}")
                print(f"      Risk: {action.risk_level}, Level: {action.decision_level.value}")
        
        print("="*70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Driven Autonomous Codebase Management")
    parser.add_argument("--repo", type=Path, default=Path.cwd(),
                       help="Repository path")
    parser.add_argument("--config", type=Path,
                       help="Agent configuration file")
    parser.add_argument("--continuous", action="store_true",
                       help="Run in continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=30,
                       help="Monitoring interval in minutes (continuous mode)")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = AutonomousAgent(args.repo, args.config)
    
    if args.continuous:
        print(f"Starting continuous monitoring (interval: {args.interval} minutes)")
        print("Press Ctrl+C to stop")
        
        import time
        try:
            while True:
                agent.run_cycle()
                print(f"\nSleeping for {args.interval} minutes...")
                time.sleep(args.interval * 60)
        except KeyboardInterrupt:
            print("\nStopping autonomous agent...")
    else:
        # Single cycle
        agent.run_cycle()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
