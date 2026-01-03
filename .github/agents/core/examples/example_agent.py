#!/usr/bin/env python3
"""
Example Cognitive Agent - Demonstrates Full PDA Loop Implementation.

This example shows how to:
1. Create a concrete agent extending CognitiveAgent
2. Implement all 4 PDA methods (perceive, decide, act, aftermath)
3. Connect to the cognitive brain for learning
4. Use the pattern recognizer
5. Execute with the orchestrator

Usage:
    python example_agent.py
    python example_agent.py --workspace /path/to/repo
    python example_agent.py --db /path/to/brain.db
"""
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import uuid

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_agent import CognitiveAgent
from cognitive_brain import CognitiveBrain
from pattern_recognizer import PatternRecognizer
from orchestrator import AgentOrchestrator


class CodeAnalysisAgent(CognitiveAgent):
    """
    Example agent that analyzes code files for patterns and issues.
    
    Demonstrates a complete PDA Loop implementation with cognitive brain
    integration for cross-session learning.
    """
    
    def __init__(self, workspace: Path):
        """
        Initialize the code analysis agent.
        
        Args:
            workspace: Path to repository/codebase to analyze
        """
        super().__init__(
            name="code-analysis-agent",
            version="1.0.0",
            workspace=workspace
        )
        self.pattern_recognizer = PatternRecognizer()
        self.analysis_results: List[Dict[str, Any]] = []
    
    def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        PERCEPTION: Gather context and analyze the task environment.
        
        This method:
        - Parses task parameters
        - Scans the workspace for relevant files
        - Identifies existing patterns
        - Queries cognitive brain for historical context
        
        Args:
            task: Task specification with type and parameters
        
        Returns:
            Context dictionary for decision making
        """
        task_type = task.get("task_type", "analyze")
        params = task.get("parameters", {})
        
        # Get target files or directory
        target = params.get("target", self.workspace)
        if isinstance(target, str):
            target = Path(target)
        
        # Find Python files to analyze
        python_files = []
        if target.is_file():
            python_files = [target]
        elif target.is_dir():
            python_files = list(target.glob("**/*.py"))[:10]  # Limit for demo
        
        # Detect patterns in files
        detected_patterns = []
        for file_path in python_files:
            try:
                patterns = self.pattern_recognizer.analyze_file(file_path)
                detected_patterns.extend(patterns)
            except Exception as e:
                print(f"  Warning: Could not analyze {file_path}: {e}")
        
        # Query cognitive brain for history if available
        history = []
        if self.cognitive_brain:
            history = self.cognitive_brain.get_session_history(
                agent_name=self.name,
                limit=5
            )
        
        # Build context
        context = {
            "parsed_inputs": {
                "task_type": task_type,
                "target": str(target),
                "file_count": len(python_files)
            },
            "files": [str(f) for f in python_files],
            "patterns": [
                {
                    "name": p.name,
                    "type": p.pattern_type,
                    "locations": p.locations,
                    "confidence": p.confidence
                }
                for p in detected_patterns
            ],
            "history": history,
            "risks": [],
            "opportunities": []
        }
        
        # Identify risks based on patterns
        anti_patterns = [p for p in detected_patterns if "bare" in p.name or "broad" in p.name]
        if anti_patterns:
            context["risks"].append({
                "type": "anti_patterns_detected",
                "count": len(anti_patterns),
                "severity": "medium"
            })
        
        # Identify opportunities
        if len(python_files) > 0:
            context["opportunities"].append({
                "type": "code_improvement",
                "description": f"Found {len(detected_patterns)} patterns in {len(python_files)} files"
            })
        
        return context
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DECISION: Determine the optimal course of action.
        
        This method:
        - Analyzes the context from perception
        - Selects the best strategy
        - Plans execution steps
        - Provides rationale for the decision
        
        Args:
            context: Context dictionary from perceive()
        
        Returns:
            Decision dictionary with strategy and steps
        """
        task_type = context["parsed_inputs"]["task_type"]
        pattern_count = len(context.get("patterns", []))
        file_count = context["parsed_inputs"]["file_count"]
        risks = context.get("risks", [])
        
        # Determine strategy based on context
        if task_type == "analyze":
            if pattern_count > 10:
                strategy = "deep_analysis"
                steps = ["categorize_patterns", "prioritize_issues", "generate_report"]
            else:
                strategy = "quick_scan"
                steps = ["list_patterns", "summarize"]
        elif task_type == "fix":
            strategy = "auto_fix"
            steps = ["identify_fixable", "apply_fixes", "verify"]
        else:
            strategy = "default"
            steps = ["process"]
        
        # Adjust priority based on risks
        priority = 5
        if any(r["severity"] == "high" for r in risks):
            priority = 9
        elif any(r["severity"] == "medium" for r in risks):
            priority = 7
        
        return {
            "strategy": strategy,
            "steps": steps,
            "priority": priority,
            "rationale": f"Selected '{strategy}' strategy for {file_count} files with {pattern_count} patterns",
            "estimated_time": len(steps) * 10  # 10 seconds per step
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACTION: Execute the decided plan with guardrails.
        
        This method:
        - Executes each step in the plan
        - Tracks progress and handles errors
        - Produces outputs and logs
        
        Args:
            decision: Decision dictionary from decide()
        
        Returns:
            Result dictionary with status and outputs
        """
        strategy = decision["strategy"]
        steps = decision["steps"]
        
        outputs = {
            "strategy_used": strategy,
            "patterns_processed": 0,
            "issues_found": 0,
            "recommendations": []
        }
        logs = []
        steps_completed = []
        steps_failed = []
        
        try:
            for step in steps:
                logs.append(f"Executing step: {step}")
                
                if step == "categorize_patterns":
                    outputs["categories"] = ["exception_handling", "imports", "code_style"]
                    steps_completed.append(step)
                    
                elif step == "prioritize_issues":
                    outputs["issues_found"] = 3  # Demo value
                    steps_completed.append(step)
                    
                elif step == "generate_report":
                    outputs["report_generated"] = True
                    steps_completed.append(step)
                    
                elif step == "list_patterns":
                    outputs["patterns_processed"] = 5  # Demo value
                    steps_completed.append(step)
                    
                elif step == "summarize":
                    outputs["summary"] = "Analysis complete"
                    steps_completed.append(step)
                    
                else:
                    steps_completed.append(step)
                
                logs.append(f"  ✓ {step} completed")
            
            # Add recommendations based on analysis
            outputs["recommendations"] = [
                "Consider refactoring broad exception handlers",
                "Add type hints to improve code quality"
            ]
            
            return {
                "status": "success",
                "outputs": outputs,
                "steps_completed": steps_completed,
                "steps_failed": steps_failed,
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"  ✗ Error: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "outputs": outputs,
                "steps_completed": steps_completed,
                "steps_failed": steps_failed + [steps[len(steps_completed)]],
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
        
        This method:
        - Calculates metrics from execution
        - Identifies patterns for future reference
        - Extracts lessons learned
        - Records everything in cognitive brain
        
        Args:
            result: Result from act()
            context: Context from perceive()
            decision: Decision from decide()
        
        Returns:
            AfterMath dictionary with metrics, patterns, and lessons
        """
        # Calculate metrics
        success = result.get("status") == "success"
        steps_completed = len(result.get("steps_completed", []))
        steps_total = len(decision.get("steps", []))
        
        metrics = {
            "success": success,
            "strategy": decision.get("strategy"),
            "completion_rate": steps_completed / steps_total if steps_total > 0 else 0,
            "files_analyzed": context["parsed_inputs"]["file_count"],
            "patterns_found": len(context.get("patterns", [])),
            "issues_found": result.get("outputs", {}).get("issues_found", 0)
        }
        
        # Identify patterns for future learning
        patterns = []
        if success:
            patterns.append(f"successful_{decision['strategy']}")
        else:
            patterns.append(f"failed_{decision['strategy']}")
        
        # Extract lessons
        lessons = []
        if success:
            lessons.append(
                f"Strategy '{decision['strategy']}' was effective for "
                f"{context['parsed_inputs']['file_count']} files"
            )
        if metrics["issues_found"] > 0:
            lessons.append(
                f"Found {metrics['issues_found']} issues requiring attention"
            )
        
        # Record in cognitive brain if available
        if self.cognitive_brain and self.session_id:
            # Record patterns
            for pattern in patterns:
                self.cognitive_brain.record_pattern(
                    session_id=self.session_id,
                    pattern_name=pattern,
                    pattern_type="execution",
                    description=f"Execution pattern from code analysis"
                )
            
            # Record lessons
            for lesson in lessons:
                self.cognitive_brain.record_lesson(
                    session_id=self.session_id,
                    lesson_text=lesson,
                    category="code_analysis",
                    confidence=0.85 if success else 0.6
                )
            
            # Record decision
            self.cognitive_brain.record_decision(
                session_id=self.session_id,
                context=context,
                decision=decision,
                rationale=decision.get("rationale"),
                outcome=result,
                success=success
            )
        
        # Store for later access
        self.analysis_results.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "patterns": patterns,
            "lessons": lessons
        })
        
        return {
            "metrics": metrics,
            "patterns": patterns,
            "lessons": lessons,
            "recommendations": result.get("outputs", {}).get("recommendations", [])
        }


def run_single_agent_demo(workspace: Path, db_path: Path):
    """Demonstrate single agent execution."""
    print("\n" + "=" * 60)
    print("DEMO 1: Single Agent Execution")
    print("=" * 60)
    
    # Initialize cognitive brain
    brain = CognitiveBrain(db_path)
    
    # Create agent
    agent = CodeAnalysisAgent(workspace)
    agent.set_cognitive_brain(brain)
    
    # Generate session ID
    session_id = f"demo-{uuid.uuid4().hex[:8]}"
    agent.set_session_id(session_id)
    
    # Start session in brain
    brain.start_session(
        session_id=session_id,
        agent_name=agent.name,
        agent_version=agent.version,
        task_type="analyze"
    )
    
    print(f"\nSession: {session_id}")
    print(f"Agent: {agent.name} v{agent.version}")
    print(f"Workspace: {workspace}")
    
    # Define task
    task = {
        "task_type": "analyze",
        "parameters": {
            "target": str(workspace)
        }
    }
    
    print("\n--- Executing PDA Loop ---")
    
    # Execute PDA loop
    result = agent.execute_pda_loop(task)
    
    # End session
    brain.end_session(session_id, result["status"], result.get("metrics"))
    
    # Print results
    print(f"\nStatus: {result['status']}")
    print(f"Execution Time: {result['metrics'].get('execution_time', 0):.2f}s")
    
    if result.get("lessons"):
        print("\nLessons Learned:")
        for lesson in result["lessons"]:
            print(f"  • {lesson}")
    
    if result.get("patterns"):
        print("\nPatterns Recorded:")
        for pattern in result["patterns"]:
            print(f"  • {pattern}")
    
    return result


async def run_orchestrated_demo(workspace: Path, db_path: Path):
    """Demonstrate orchestrated multi-agent workflow."""
    print("\n" + "=" * 60)
    print("DEMO 2: Orchestrated Multi-Agent Workflow")
    print("=" * 60)
    
    # Initialize brain
    brain = CognitiveBrain(db_path)
    
    # Create multiple agents
    agent1 = CodeAnalysisAgent(workspace)
    agent2 = CodeAnalysisAgent(workspace)
    
    agent1.set_cognitive_brain(brain)
    agent2.set_cognitive_brain(brain)
    
    # Create orchestrator
    orch = AgentOrchestrator(max_parallel=2)
    orch.register_agent("analyzer-1", agent1)
    orch.register_agent("analyzer-2", agent2)
    
    # Add tasks with dependencies
    orch.add_task(
        task_id="initial-scan",
        agent_name="analyzer-1",
        task_type="analyze",
        parameters={"target": str(workspace)},
        priority=8
    )
    
    orch.add_task(
        task_id="deep-analysis",
        agent_name="analyzer-2",
        task_type="analyze",
        parameters={"target": str(workspace)},
        dependencies=["initial-scan"],  # Depends on first scan
        priority=7
    )
    
    print("\nWorkflow:")
    print("  Task 1: initial-scan (analyzer-1) - Priority 8")
    print("  Task 2: deep-analysis (analyzer-2) - Priority 7, depends on Task 1")
    
    print("\n--- Executing Workflow ---")
    
    # Execute workflow
    result = await orch.execute_workflow()
    
    print(f"\nWorkflow Status: {result['status']}")
    print(f"Tasks Completed: {result['metrics']['successful']}/{result['metrics']['total']}")
    
    # Show summary
    summary = orch.get_workflow_summary()
    print(f"\nBy Status:")
    for status, count in summary["by_status"].items():
        print(f"  {status}: {count}")
    
    return result


def main():
    """Main entry point for the example."""
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="Example Cognitive Agent Demo")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace path to analyze (default: current directory)"
    )
    parser.add_argument(
        "--db",
        help="Path to brain database (default: temp directory)"
    )
    parser.add_argument(
        "--orchestrated",
        action="store_true",
        help="Run orchestrated multi-agent demo"
    )
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace).resolve()
    
    # Use temp database if not specified
    if args.db:
        db_path = Path(args.db)
    else:
        import tempfile
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "demo_brain.db"
    
    print("=" * 60)
    print("COGNITIVE AGENT FRAMEWORK - EXAMPLE")
    print("=" * 60)
    print(f"\nWorkspace: {workspace}")
    print(f"Database: {db_path}")
    
    # Run single agent demo
    run_single_agent_demo(workspace, db_path)
    
    # Run orchestrated demo if requested
    if args.orchestrated:
        asyncio.run(run_orchestrated_demo(workspace, db_path))
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nNext Steps:")
    print("  1. Inspect the brain database with: python brain_cli.py stats --db " + str(db_path))
    print("  2. View sessions: python brain_cli.py sessions --db " + str(db_path))
    print("  3. Check lessons: python brain_cli.py lessons --db " + str(db_path))


if __name__ == "__main__":
    main()
