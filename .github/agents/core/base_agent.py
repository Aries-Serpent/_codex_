"""
Cognitive Agent Base Class
Abstract base class implementing the PDA Loop pattern for all cognitive agents.

#AFTERMATH_PATTERN_IDENTIFIED: PDA Loop (Perception-Decision-Action-AfterMath)
This pattern ensures consistent cognitive processing across all agents.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class CognitiveAgent(ABC):
    """
    Abstract base class for all cognitive agents in the _codex_ ecosystem.

    Implements the core PDA Loop pattern:
    1. PERCEPTION: Gather and analyze context
    2. DECISION: Determine optimal action
    3. ACTION: Execute with guardrails
    4. AFTERMATH: Learn and persist insights

    All agents must implement the four core methods and follow the
    established patterns for cognitive brain integration.
    """

    def __init__(self, name: str, version: str, workspace: Optional[Path] = None):
        """
        Initialize cognitive agent.

        Args:
            name: Agent identifier (e.g., 'ci-testing-agent')
            version: Agent version (semantic versioning)
            workspace: Repository workspace path (default: current directory)
        """
        self.name = name
        self.version = version
        self.workspace = workspace or Path.cwd()
        self.session_id = None
        self.cognitive_brain = None

    def execute_pda_loop(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute one complete PDA cycle with AfterMath learning.

        This is the main entry point that orchestrates the cognitive process:
        1. Perception: Analyze inputs and gather context
        2. Decision: Plan optimal response
        3. Action: Execute the plan
        4. AfterMath: Learn from results and update cognitive brain

        Args:
            task: Task specification dictionary with:
                - task_type: Type of task to execute
                - parameters: Task-specific parameters
                - metadata: Optional metadata

        Returns:
            Dictionary with:
                - status: 'success', 'failure', or 'error'
                - result: Task execution result
                - metrics: Performance metrics
                - lessons: Lessons learned (AfterMath)

        #AFTERMATH_DECISION_RATIONALE: PDA loop ensures consistent execution
        across all agents with built-in learning and feedback mechanisms.
        """
        start_time = datetime.now()

        try:
            # 1. PERCEPTION: Gather and analyze context
            context = self.perceive(task)

            # 2. DECISION: Determine optimal action
            decision = self.decide(context)

            # 3. ACTION: Execute with guardrails
            result = self.act(decision)

            # 4. AFTERMATH: Learn and persist insights
            aftermath = self.aftermath(result, context, decision)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "status": "success",
                "result": result,
                "metrics": {
                    "execution_time": execution_time,
                    **aftermath.get("metrics", {})
                },
                "lessons": aftermath.get("lessons", []),
                "patterns": aftermath.get("patterns", [])
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            # Even failures go through aftermath for learning
            error_context = {
                "error": str(e),
                "error_type": type(e).__name__,
                "task": task,
                "execution_time": execution_time
            }

            aftermath = self.aftermath({"status": "error", "error": error_context}, {}, {})

            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "metrics": {"execution_time": execution_time},
                "lessons": aftermath.get("lessons", [])
            }

    @abstractmethod
    def perceive(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        PERCEPTION Phase: Gather and analyze context.

        This method should:
        - Parse input data (code, logs, metrics)
        - Extract patterns using AST/regex/ML
        - Identify gaps, risks, and opportunities
        - Query cognitive brain for historical context

        Args:
            task: Task specification

        Returns:
            Context dictionary with:
                - parsed_inputs: Structured input data
                - patterns: Identified patterns
                - risks: Identified risks
                - opportunities: Identified opportunities
                - history: Relevant historical data from cognitive brain

        Example:
            >>> context = agent.perceive({"task_type": "debug_ci_failure"})
            >>> context["patterns"]  # ['timeout_pattern', 'import_error']
        """
        pass

    @abstractmethod
    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        DECISION Phase: Determine optimal action based on context.

        This method should:
        - Prioritize based on impact/risk/effort
        - Select strategy (generate/fix/report/skip)
        - Plan execution steps
        - Estimate resource requirements

        Args:
            context: Context from perception phase

        Returns:
            Decision dictionary with:
                - strategy: Selected strategy name
                - steps: Execution steps (ordered list)
                - priority: Priority level (1-5, 5=highest)
                - rationale: Reasoning for this decision
                - estimated_time: Estimated execution time (seconds)

        Example:
            >>> decision = agent.decide(context)
            >>> decision["strategy"]  # 'fix_import_error'
            >>> decision["steps"]  # ['identify_module', 'add_import', 'run_tests']
        """
        pass

    @abstractmethod
    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        ACTION Phase: Execute the decision with guardrails.

        This method should:
        - Execute in sandbox/safe environment
        - Apply guardrails (timeouts, resource limits)
        - Validate outputs at each step
        - Handle failures gracefully
        - Provide detailed execution logs

        Args:
            decision: Decision from decision phase

        Returns:
            Result dictionary with:
                - status: 'success', 'partial_success', or 'failure'
                - outputs: Generated outputs (files, reports, fixes)
                - steps_completed: List of completed steps
                - steps_failed: List of failed steps (if any)
                - logs: Detailed execution logs

        Example:
            >>> result = agent.act(decision)
            >>> result["status"]  # 'success'
            >>> result["outputs"]  # {'tests': ['test_new.py'], 'coverage': 95.2}
        """
        pass

    @abstractmethod
    def aftermath(
        self,
        result: dict[str, Any],
        context: dict[str, Any],
        decision: dict[str, Any]
    ) -> dict[str, Any]:
        """
        AFTERMATH Phase: Learn from execution and persist insights.

        This method should:
        - Tag metrics using #AFTERMATH_METRIC
        - Identify patterns using #AFTERMATH_PATTERN_IDENTIFIED
        - Extract lessons using #AFTERMATH_LESSON_LEARNED
        - Update cognitive brain with learnings
        - Generate after-action report

        Args:
            result: Result from action phase
            context: Context from perception phase
            decision: Decision from decision phase

        Returns:
            AfterMath dictionary with:
                - metrics: Performance metrics (tagged)
                - patterns: Identified patterns (tagged)
                - lessons: Lessons learned (tagged)
                - recommendations: Future recommendations
                - cognitive_updates: Updates to persist in cognitive brain

        Example:
            >>> aftermath = agent.aftermath(result, context, decision)
            >>> aftermath["metrics"]  # {'tests_generated': 5, 'coverage_delta': +3.2}
            >>> aftermath["lessons"]  # ['Import errors common in test files']

        #AFTERMATH_METRIC: aftermath_calls_total
        #AFTERMATH_PATTERN_IDENTIFIED: aftermath_reporting_pattern
        """
        pass

    def set_cognitive_brain(self, cognitive_brain):
        """
        Attach cognitive brain instance for centralized learning.

        Args:
            cognitive_brain: CognitiveBrain instance
        """
        self.cognitive_brain = cognitive_brain

    def set_session_id(self, session_id: str):
        """
        Set session identifier for tracking.

        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id

    def get_metadata(self) -> dict[str, Any]:
        """
        Get agent metadata.

        Returns:
            Dictionary with agent name, version, and capabilities
        """
        return {
            "name": self.name,
            "version": self.version,
            "pda_loop_enabled": True,
            "aftermath_enabled": True,
            "cognitive_brain_connected": self.cognitive_brain is not None
        }
