#!/usr/bin/env python3
"""
Example Cognitive Agent Implementation
Demonstrates complete PDA Loop pattern with cognitive brain integration.

This example shows:
1. How to extend CognitiveAgent
2. Implement all 4 PDA methods
3. Connect to cognitive brain
4. Use pattern recognizer
5. Execute with orchestrator

#AFTERMATH_PATTERN_IDENTIFIED: complete_agent_example
"""
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from github.agents.core import (
    CognitiveAgent,
    CognitiveBrain,
    PatternRecognizer,
    AgentOrchestrator
)


class ExampleAgent(CognitiveAgent):
    """
    Example agent that demonstrates the PDA Loop pattern.
    
    This agent analyzes Python files for code quality issues.
    """
    
    def __init__(self, workspace: Path):
        super().__init__(
            name="example-agent",
            version="1.0.0",
            workspace=workspace
        )
        self.pattern_recognizer = PatternRecognizer()
    
    def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        PERCEPTION: Analyze file and gather context.
        
        #AFTERMATH_METRIC: perception_time
        """
        print(f"🔍 PERCEIVE: Analyzing {task.get('file', 'unknown')}")
        
        file_path = Path(task.get("file", ""))
        
        # Use pattern recognizer to analyze file
        patterns = []
        if file_path.exists():
            patterns = self.pattern_recognizer.analyze_file(file_path)
        
        # Query cognitive brain for historical context
        history = []
        if self.cognitive_brain:
            history = self.cognitive_brain.get_recent_lessons(
                category="code_quality",
                limit=3
            )
        
        context = {
            "file": str(file_path),
            "patterns_detected": [
                {"name": p.name, "type": p.pattern_type, "confidence": p.confidence}
                for p in patterns
            ],
            "pattern_count": len(patterns),
            "historical_lessons": [l["lesson_text"] for l in history],
            "risks": self._assess_risks(patterns),
            "opportunities": self._identify_opportunities(patterns)
        }
        
        print(f"  - Detected {len(patterns)} patterns")
        print(f"  - {len(history)} historical lessons available")
        
        return context
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DECISION: Determine what actions to take.
        
        #AFTERMATH_DECISION_RATIONALE: prioritize_by_risk
        """
        print("🤔 DECIDE: Planning actions")
        
        # Prioritize based on risk and pattern count
        priority = min(10, context["pattern_count"])
        
        # Select strategy based on findings
        if context["pattern_count"] == 0:
            strategy = "no_action"
            steps = []
        elif context["pattern_count"] < 5:
            strategy = "minor_fixes"
            steps = ["fix_high_priority", "validate"]
        else:
            strategy = "major_refactor"
            steps = ["analyze_impact", "create_plan", "execute_fixes", "validate"]
        
        decision = {
            "strategy": strategy,
            "steps": steps,
            "priority": priority,
            "rationale": f"Found {context['pattern_count']} issues. "
                        f"Strategy: {strategy}",
            "estimated_time": len(steps) * 5  # 5 min per step
        }
        
        print(f"  - Strategy: {strategy}")
        print(f"  - Steps: {', '.join(steps)}")
        print(f"  - Priority: {priority}/10")
        
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACTION: Execute the planned actions.
        
        #AFTERMATH_METRIC: actions_executed, actions_successful
        """
        print("⚡ ACT: Executing actions")
        
        if decision["strategy"] == "no_action":
            print("  - No actions needed")
            return {
                "status": "success",
                "outputs": {"message": "No issues found"},
                "steps_completed": [],
                "logs": ["Analysis complete, no actions needed"]
            }
        
        # Simulate executing steps
        completed = []
        logs = []
        
        for step in decision["steps"]:
            print(f"  - Executing: {step}")
            completed.append(step)
            logs.append(f"Completed {step}")
        
        return {
            "status": "success",
            "outputs": {
                "fixes_applied": len(completed),
                "strategy": decision["strategy"]
            },
            "steps_completed": completed,
            "steps_failed": [],
            "logs": logs
        }
    
    def aftermath(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any],
        decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AFTERMATH: Learn from execution and persist insights.
        
        #AFTERMATH_LESSON_LEARNED: pattern_based_decisions_effective
        """
        print("📊 AFTERMATH: Learning and persisting insights")
        
        # Calculate metrics
        metrics = {
            "patterns_found": context.get("pattern_count", 0),
            "actions_taken": len(result.get("steps_completed", [])),
            "success": result["status"] == "success",
            "strategy_used": decision["strategy"]
        }
        
        # Identify patterns for future learning
        patterns = ["successful_analysis"]
        if metrics["patterns_found"] > 0:
            patterns.append("issues_detected")
        if metrics["success"]:
            patterns.append("successful_execution")
        
        # Extract lessons
        lessons = []
        if metrics["patterns_found"] == 0:
            lessons.append("Clean code detected - good practices maintained")
        elif metrics["success"]:
            lessons.append(f"Strategy '{decision['strategy']}' was effective")
        
        # Record in cognitive brain
        if self.cognitive_brain and self.session_id:
            for pattern_name in patterns:
                self.cognitive_brain.record_pattern(
                    session_id=self.session_id,
                    pattern_name=pattern_name,
                    pattern_type="execution",
                    description=f"Execution pattern: {pattern_name}"
                )
            
            for lesson in lessons:
                self.cognitive_brain.record_lesson(
                    session_id=self.session_id,
                    lesson_text=lesson,
                    category="code_quality",
                    confidence=0.9
                )
        
        print(f"  - Metrics: {metrics}")
        print(f"  - Patterns: {', '.join(patterns)}")
        print(f"  - Lessons: {len(lessons)} recorded")
        
        return {
            "metrics": metrics,
            "patterns": patterns,
            "lessons": lessons,
            "recommendations": ["Continue monitoring code quality"]
        }
    
    def _assess_risks(self, patterns) -> list:
        """Assess risks based on detected patterns."""
        risks = []
        for pattern in patterns:
            if "exception" in pattern.pattern_type:
                risks.append(f"Exception handling issue: {pattern.name}")
            elif pattern.name == "unused_import":
                risks.append("Code cleanliness: unused imports")
        return risks
    
    def _identify_opportunities(self, patterns) -> list:
        """Identify improvement opportunities."""
        opportunities = []
        if any(p.name == "missing_docstring" for p in patterns):
            opportunities.append("Add documentation to improve maintainability")
        if any(p.pattern_type == "test" for p in patterns):
            opportunities.append("Enhance test coverage")
        return opportunities


def main():
    """Main example execution."""
    print("=" * 60)
    print("🧠 Cognitive Agent Example")
    print("=" * 60)
    print()
    
    # Setup
    workspace = Path.cwd()
    brain_path = workspace / ".codex" / "example_brain.db"
    
    # Create cognitive brain
    print("🔧 Initializing cognitive brain...")
    brain = CognitiveBrain(brain_path)
    print(f"   Database: {brain_path}")
    print()
    
    # Create agent
    print("🤖 Creating example agent...")
    agent = ExampleAgent(workspace)
    agent.set_cognitive_brain(brain)
    agent.set_session_id("example-session-001")
    print(f"   Agent: {agent.name} v{agent.version}")
    print()
    
    # Start session in brain
    brain.start_session(
        session_id="example-session-001",
        agent_name=agent.name,
        agent_version=agent.version,
        task_type="code_analysis"
    )
    
    # Example task: Analyze a file
    print("📋 Task: Analyze Python file")
    print("-" * 60)
    
    # Use this script as the example file to analyze
    task = {
        "task_type": "analyze_file",
        "file": __file__,
        "parameters": {
            "check_quality": True
        }
    }
    
    # Execute PDA loop
    print()
    result = agent.execute_pda_loop(task)
    print()
    
    # Show results
    print("=" * 60)
    print("📈 Results")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Execution Time: {result['metrics']['execution_time']:.2f}s")
    print()
    
    if result.get("lessons"):
        print("Lessons Learned:")
        for lesson in result["lessons"]:
            print(f"  • {lesson}")
        print()
    
    if result.get("patterns"):
        print("Patterns Identified:")
        for pattern in result["patterns"]:
            print(f"  • {pattern}")
        print()
    
    # End session
    brain.end_session("example-session-001", "success", result["metrics"])
    
    # Show brain statistics
    print("=" * 60)
    print("🧠 Cognitive Brain Statistics")
    print("=" * 60)
    stats = brain.get_stats()
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Total Patterns: {stats['total_patterns']}")
    print(f"Total Lessons: {stats['total_lessons']}")
    print()
    
    if stats.get("top_patterns"):
        print("Top Patterns:")
        for pattern in stats["top_patterns"][:5]:
            print(f"  • {pattern['pattern_name']}: {pattern['occurrences']} times")
    
    print()
    print("✅ Example complete!")
    print()
    print("💡 Try running this again to see the cognitive brain learn!")
    print(f"   Database location: {brain_path}")


if __name__ == "__main__":
    main()
