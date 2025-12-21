"""
Workflow Orchestration Components

This module contains workflow orchestration and planning logic.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    Orchestrates review workflow and next steps.
    
    Generates prioritized action plans with:
    - Step-by-step remediation
    - Time estimates
    - Dependency ordering
    - Resource requirements
    """
    
    async def create_plan(self, context, result) -> Dict[str, Any]:
        """
        Create orchestration plan based on review results.
        
        Args:
            context: ReviewContext with PR information
            result: ReviewResult with analysis findings
            
        Returns:
            Orchestration plan with prioritized steps
        """
        plan = {
            "priority": self._determine_priority(result),
            "steps": [],
            "estimated_time": 0,
            "dependencies": []
        }
        
        # Add steps based on findings
        steps = []
        
        # Security issues first (highest priority)
        security_suggestions = [s for s in result.suggestions if s.get("category") == "security"]
        if security_suggestions:
            critical_count = sum(1 for s in security_suggestions if s.get("severity") == "critical")
            high_count = sum(1 for s in security_suggestions if s.get("severity") == "high")
            
            if critical_count > 0:
                steps.append({
                    "order": len(steps) + 1,
                    "description": f"Address {critical_count} critical security vulnerability(ies)",
                    "command": "# Review and fix each critical security issue",
                    "estimated_minutes": critical_count * 15,
                    "priority": "critical"
                })
            
            if high_count > 0:
                steps.append({
                    "order": len(steps) + 1,
                    "description": f"Fix {high_count} high-severity security issue(s)",
                    "command": "# Review and fix each high-severity security issue",
                    "estimated_minutes": high_count * 10,
                    "priority": "high"
                })
        
        # Code quality fixes
        quality_suggestions = [s for s in result.suggestions if s.get("category") == "code_quality"]
        if quality_suggestions:
            steps.append({
                "order": len(steps) + 1,
                "description": f"Apply code quality fixes ({len(quality_suggestions)} issues)",
                "command": "black . && ruff check --fix",
                "estimated_minutes": 5,
                "priority": "medium"
            })
        
        # Documentation updates
        doc_suggestions = [s for s in result.suggestions if s.get("category") == "documentation"]
        if doc_suggestions:
            steps.append({
                "order": len(steps) + 1,
                "description": f"Update documentation ({len(doc_suggestions)} items)",
                "command": "# Review and update documentation",
                "estimated_minutes": len(doc_suggestions) * 5,
                "priority": "medium"
            })
        
        # Performance improvements (optional)
        perf_suggestions = [s for s in result.suggestions if s.get("category") == "performance"]
        if perf_suggestions:
            steps.append({
                "order": len(steps) + 1,
                "description": f"Consider performance optimizations ({len(perf_suggestions)} opportunities)",
                "command": "# Review and apply performance improvements",
                "estimated_minutes": len(perf_suggestions) * 10,
                "priority": "low"
            })
        
        # Knowledge gap research
        if result.knowledge_gaps:
            steps.append({
                "order": len(steps) + 1,
                "description": "Research knowledge gaps for better context",
                "command": "# Manual research required",
                "estimated_minutes": len(result.knowledge_gaps) * 10,
                "priority": "low"
            })
        
        # Testing
        steps.append({
            "order": len(steps) + 1,
            "description": "Run full test suite",
            "command": "pytest tests/ -v",
            "estimated_minutes": 5,
            "priority": "high"
        })
        
        plan["steps"] = steps
        plan["estimated_time"] = sum(s.get("estimated_minutes", 0) for s in steps)
        
        logger.info(f"Created orchestration plan with {len(steps)} steps, estimated time: {plan['estimated_time']} minutes")
        
        return plan
    
    def _determine_priority(self, result) -> str:
        """
        Determine priority level based on review results.
        
        Returns:
            Priority string: critical, high, medium, or low
        """
        # Critical if any critical severity issues
        if any(s.get("severity") == "critical" for s in result.suggestions):
            return "critical"
        
        # High if security issues or many suggestions
        if any(s.get("category") == "security" for s in result.suggestions):
            return "high"
        
        if len(result.suggestions) > 10:
            return "high"
        
        # Medium if some suggestions
        if len(result.suggestions) > 0:
            return "medium"
        
        return "low"
