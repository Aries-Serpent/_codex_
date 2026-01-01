"""
Dependency Tracker Module - AFTERMATH Phase

#AFTERMATH_PATTERN_IDENTIFIED: dependency_upgrade_tracking
Implements metrics tracking and lesson learning for dependency upgrades.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import sys

# Add core to path for CognitiveBrain access
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from cognitive_brain import CognitiveBrain


@dataclass
class UpgradeMetrics:
    """Metrics for dependency upgrades."""
    scan_date: str
    total_dependencies: int
    outdated_count: int
    upgraded_count: int
    success_rate: float
    average_upgrade_time: float
    security_updates: int
    breaking_changes_encountered: int
    rollbacks_performed: int
    auto_upgrade_rate: float
    manual_review_rate: float
    lessons_learned: List[str]


class DependencyTracker:
    """
    Dependency Tracker - AFTERMATH Phase
    
    #AFTERMATH_PATTERN_IDENTIFIED: upgrade_outcome_analysis
    
    Tracks upgrade outcomes and learns:
    - Success/failure rates
    - Common failure patterns
    - Package-specific insights
    - Upgrade timing patterns
    - Rollback frequency
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.brain = CognitiveBrain(Path(".codex/brain.db"))
        
    def aftermath(self, result: Dict[str, Any], context: Dict[str, Any], 
                  decision: Dict[str, Any]) -> None:
        """
        AFTERMATH: Track metrics and learn from upgrades.
        
        #AFTERMATH_PATTERN_IDENTIFIED: comprehensive_upgrade_tracking
        
        Args:
            result: Upgrade results from ACT phase
            context: Context from PERCEIVE phase
            decision: Decision from DECIDE phase
        """
        # Generate comprehensive metrics
        metrics = self._generate_metrics(result, context, decision)
        
        # Record metrics in cognitive brain
        self._record_metrics(metrics)
        
        # Store upgrade patterns
        self._store_patterns(result, decision)
        
        # Generate lessons learned
        lessons = self._generate_lessons(result, context, decision)
        
        # Store lessons in cognitive brain
        for lesson in lessons:
            self._store_lesson(lesson)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, lessons)
        
        # Save reports
        self._save_metrics_report(metrics, recommendations)
        self._save_markdown_report(metrics, lessons, recommendations)
        
        #AFTERMATH_METRIC: upgrade_session_complete = True
        #AFTERMATH_METRIC: total_upgrades = metrics.upgraded_count
        #AFTERMATH_METRIC: success_rate = metrics.success_rate
        #AFTERMATH_LESSON_LEARNED: dependency_upgrade_patterns_identified
        
        print(f"✅ Dependency upgrade tracking complete: {metrics.upgraded_count} upgrades processed")
        print(f"   Success rate: {metrics.success_rate:.1%}")
        print(f"   Security updates: {metrics.security_updates}")
    
    def _generate_metrics(self, result: Dict[str, Any], context: Dict[str, Any],
                         decision: Dict[str, Any]) -> UpgradeMetrics:
        """
        Generate comprehensive upgrade metrics.
        
        #AFTERMATH_PATTERN_IDENTIFIED: metric_generation
        """
        results = result.get("results", [])
        
        successful = sum(1 for r in results if r.success)
        success_rate = successful / len(results) if results else 0.0
        
        total_time = sum(r.duration_seconds for r in results)
        avg_time = total_time / len(results) if results else 0.0
        
        security_updates = sum(
            1 for r in results 
            if r.metadata.get("evaluation").priority.value == "p0"
        )
        
        breaking_changes = sum(
            1 for r in results
            if r.metadata.get("evaluation").breaking_change_risk.value in ["critical", "high"]
        )
        
        rollbacks = sum(1 for r in results if r.rollback_performed)
        
        auto_upgrades = sum(
            1 for r in results
            if r.metadata.get("evaluation").auto_upgradeable
        )
        auto_rate = auto_upgrades / len(results) if results else 0.0
        
        manual_rate = 1.0 - auto_rate
        
        lessons = self._generate_lessons(result, context, decision)
        
        return UpgradeMetrics(
            scan_date=datetime.now().isoformat(),
            total_dependencies=context.get("total_dependencies", 0),
            outdated_count=context.get("total_outdated", 0),
            upgraded_count=len(results),
            success_rate=success_rate,
            average_upgrade_time=avg_time,
            security_updates=security_updates,
            breaking_changes_encountered=breaking_changes,
            rollbacks_performed=rollbacks,
            auto_upgrade_rate=auto_rate,
            manual_review_rate=manual_rate,
            lessons_learned=lessons
        )
    
    def _record_metrics(self, metrics: UpgradeMetrics) -> None:
        """
        Record metrics in cognitive brain.
        
        #AFTERMATH_METRIC: dependency_upgrade_metrics
        """
        try:
            session_id = self.brain.start_session(
                agent_name="dep-upgrade-agent",
                task_description="Dependency upgrade session"
            )
            
            # Record all metrics
            metric_data = {
                "total_dependencies": metrics.total_dependencies,
                "outdated_count": metrics.outdated_count,
                "upgraded_count": metrics.upgraded_count,
                "success_rate": metrics.success_rate,
                "average_time": metrics.average_upgrade_time,
                "security_updates": metrics.security_updates,
                "breaking_changes": metrics.breaking_changes_encountered,
                "rollbacks": metrics.rollbacks_performed,
                "auto_upgrade_rate": metrics.auto_upgrade_rate
            }
            
            for key, value in metric_data.items():
                self.brain.record_metric(
                    session_id=session_id,
                    metric_name=key,
                    metric_value=value
                )
            
            self.brain.end_session(session_id, success=True)
        except Exception as e:
            print(f"Warning: Failed to record metrics: {e}")
    
    def _store_patterns(self, result: Dict[str, Any], decision: Dict[str, Any]) -> None:
        """
        Store upgrade patterns in cognitive brain.
        
        #AFTERMATH_PATTERN_IDENTIFIED: pattern_storage
        """
        try:
            results = result.get("results", [])
            
            for upgrade_result in results[:10]:  # Top 10
                evaluation = upgrade_result.metadata.get("evaluation")
                
                pattern_data = {
                    "package": upgrade_result.package_name,
                    "from_version": upgrade_result.from_version,
                    "to_version": upgrade_result.to_version,
                    "success": upgrade_result.success,
                    "breaking_change_risk": evaluation.breaking_change_risk.value,
                    "auto_upgradeable": evaluation.auto_upgradeable,
                    "rollback_needed": upgrade_result.rollback_performed
                }
                
                self.brain.store_pattern(
                    pattern_type="dependency_update",
                    pattern_data=pattern_data,
                    confidence=0.85 if upgrade_result.success else 0.6,
                    source="dep-upgrade-agent"
                )
        except Exception as e:
            print(f"Warning: Failed to store patterns: {e}")
    
    def _generate_lessons(self, result: Dict[str, Any], context: Dict[str, Any],
                         decision: Dict[str, Any]) -> List[str]:
        """
        Generate lessons learned from upgrades.
        
        #AFTERMATH_LESSON_LEARNED: upgrade_insights
        """
        lessons = []
        results = result.get("results", [])
        
        # Lesson 1: Success rate
        if results:
            success_rate = sum(1 for r in results if r.success) / len(results)
            lessons.append(f"Upgrade success rate: {success_rate:.1%} ({sum(1 for r in results if r.success)}/{len(results)})")
        
        # Lesson 2: Rollback frequency
        rollbacks = sum(1 for r in results if r.rollback_performed)
        if rollbacks > 0:
            lessons.append(f"Rollbacks performed: {rollbacks} - Review test coverage and upgrade strategy")
        
        # Lesson 3: Auto-upgrade effectiveness
        auto_upgrades = sum(1 for r in results if r.metadata.get("evaluation").auto_upgradeable)
        if auto_upgrades > 0:
            auto_success = sum(1 for r in results if r.metadata.get("evaluation").auto_upgradeable and r.success)
            lessons.append(f"Auto-upgrade success: {auto_success}/{auto_upgrades} - Consider expanding auto-upgrade criteria")
        
        # Lesson 4: Security updates
        security = sum(1 for r in results if r.metadata.get("evaluation").priority.value == "p0")
        if security > 0:
            lessons.append(f"Security updates applied: {security} - Continue prioritizing security patches")
        
        # Lesson 5: Common failure patterns
        failed = [r for r in results if not r.success]
        if len(failed) > 2:
            lessons.append(f"Common failure pattern detected in {len(failed)} upgrades - Review test suite stability")
        
        return lessons
    
    def _store_lesson(self, lesson: str) -> None:
        """Store individual lesson in cognitive brain."""
        try:
            self.brain.store_lesson(
                category="dependency_upgrades",
                content=lesson,
                confidence=0.85,
                source="dep-upgrade-agent"
            )
        except Exception as e:
            print(f"Warning: Failed to store lesson: {e}")
    
    def _generate_recommendations(self, metrics: UpgradeMetrics, 
                                 lessons: List[str]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Low success rate
        if metrics.success_rate < 0.7:
            recommendations.append(
                f"⚠️ Success rate is low ({metrics.success_rate:.1%}) - Review test coverage and upgrade process"
            )
        
        # High rollback rate
        if metrics.rollbacks_performed > metrics.upgraded_count * 0.3:
            recommendations.append(
                f"⚠️ High rollback rate ({metrics.rollbacks_performed}/{metrics.upgraded_count}) - Consider staged rollouts"
            )
        
        # Security updates pending
        if metrics.security_updates > 0:
            recommendations.append(
                f"🔴 {metrics.security_updates} security updates applied - Monitor for issues"
            )
        
        # Breaking changes
        if metrics.breaking_changes_encountered > 0:
            recommendations.append(
                f"⚠️ {metrics.breaking_changes_encountered} breaking changes encountered - Review migration guides"
            )
        
        # Outdated dependencies
        if metrics.outdated_count > metrics.upgraded_count:
            remaining = metrics.outdated_count - metrics.upgraded_count
            recommendations.append(
                f"📋 {remaining} dependencies still outdated - Schedule next upgrade session"
            )
        
        # Auto-upgrade opportunities
        if metrics.auto_upgrade_rate < 0.5:
            recommendations.append(
                f"💡 Only {metrics.auto_upgrade_rate:.1%} auto-upgraded - Consider expanding criteria"
            )
        
        return recommendations
    
    def _save_metrics_report(self, metrics: UpgradeMetrics, 
                            recommendations: List[str]) -> None:
        """Save metrics as JSON report."""
        report_path = self.repo_path / ".codex" / "dependency_metrics.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "scan_date": metrics.scan_date,
            "summary": {
                "total_dependencies": metrics.total_dependencies,
                "outdated": metrics.outdated_count,
                "upgraded": metrics.upgraded_count,
                "success_rate": metrics.success_rate,
                "security_updates": metrics.security_updates
            },
            "metrics": {
                "average_upgrade_time": metrics.average_upgrade_time,
                "breaking_changes": metrics.breaking_changes_encountered,
                "rollbacks": metrics.rollbacks_performed,
                "auto_upgrade_rate": metrics.auto_upgrade_rate,
                "manual_review_rate": metrics.manual_review_rate
            },
            "lessons_learned": metrics.lessons_learned,
            "recommendations": recommendations
        }
        
        report_path.write_text(json.dumps(report, indent=2))
    
    def _save_markdown_report(self, metrics: UpgradeMetrics, lessons: List[str],
                             recommendations: List[str]) -> None:
        """Save report as Markdown."""
        report_path = self.repo_path / ".codex" / "DEPENDENCY_UPGRADE_REPORT.md"
        
        content = f"""# Dependency Upgrade Report

**Date**: {metrics.scan_date}

## Executive Summary

- **Total Dependencies**: {metrics.total_dependencies}
- **Outdated**: {metrics.outdated_count}
- **Upgraded**: {metrics.upgraded_count}
- **Success Rate**: {metrics.success_rate:.1%}
- **Security Updates**: {metrics.security_updates}

## Upgrade Metrics

- **Average Upgrade Time**: {metrics.average_upgrade_time:.1f} seconds
- **Breaking Changes Encountered**: {metrics.breaking_changes_encountered}
- **Rollbacks Performed**: {metrics.rollbacks_performed}
- **Auto-Upgrade Rate**: {metrics.auto_upgrade_rate:.1%}
- **Manual Review Rate**: {metrics.manual_review_rate:.1%}

## Lessons Learned

"""
        for lesson in lessons:
            content += f"- {lesson}\n"
        
        content += """
## Recommendations

"""
        for rec in recommendations:
            content += f"- {rec}\n"
        
        content += """
## Next Steps

1. Review failed upgrades and address issues
2. Monitor deployed updates for stability
3. Schedule next upgrade session for remaining outdated dependencies
4. Update upgrade criteria based on lessons learned

"""
        
        report_path.write_text(content)
