#!/usr/bin/env python3
"""
Phase 3 Campaign Orchestrator — Agent Output Grading Rubric (0-100)
Evaluates each agent's fix attempt on standardized criteria
"""

from dataclasses import dataclass
from enum import Enum

class GradingCriterion(Enum):
    """Grading criteria with point allocations"""
    FAILURE_REDUCTION = 40     # Each failure fixed = 40/N points
    NO_REGRESSIONS = 25        # Full score if no new failures; -25 if regression
    POLICY_COMPLIANCE = 20     # No xfail, no bare except, etc.
    DOCUMENTATION = 10         # Tracking log + commit SHA
    LINT_CLEAN = 5             # ruff + imports clean

@dataclass
class GradingResult:
    """Result of grading an agent's work"""
    agent_type: str
    original_failures: int
    fixed_failures: int
    new_failures: int
    policy_violations: int
    docs_updated: bool
    lint_clean: bool
    
    raw_scores: dict  # {criterion: points}
    final_score: int  # 0-100
    recommendation: str  # auto-approve, review, reject

class PhaseAGrader:
    """Grader for Phase 3 agent outputs"""
    
    @staticmethod
    def grade(result: GradingResult) -> GradingResult:
        """
        Grade an agent's fix attempt
        
        Scoring:
        - ≥90: Auto-approve for merge
        - 70-89: Human review recommended
        - <70: Send back to agent with feedback
        """
        scores = {}
        
        # 1. Failure Reduction (40 points)
        if result.original_failures > 0:
            reduction_score = int((result.fixed_failures / result.original_failures) * 40)
            scores['failure_reduction'] = reduction_score
        else:
            scores['failure_reduction'] = 40  # No failures to fix
        
        # 2. No Regressions (25 points)
        if result.new_failures == 0:
            scores['no_regressions'] = 25
        else:
            # -25 if any regression
            scores['no_regressions'] = max(0, 25 - (result.new_failures * 5))
        
        # 3. Policy Compliance (20 points)
        # -5 per violation
        scores['policy_compliance'] = max(0, 20 - (result.policy_violations * 5))
        
        # 4. Documentation (10 points)
        scores['documentation'] = 10 if result.docs_updated else 0
        
        # 5. Lint Clean (5 points)
        scores['lint_clean'] = 5 if result.lint_clean else 0
        
        # Calculate final score
        final_score = sum(scores.values())
        
        # Determine recommendation
        if final_score >= 90:
            recommendation = "✅ AUTO-APPROVE FOR MERGE"
        elif final_score >= 70:
            recommendation = "🔄 HUMAN REVIEW RECOMMENDED"
        else:
            recommendation = "❌ SEND BACK TO AGENT"
        
        result.raw_scores = scores
        result.final_score = final_score
        result.recommendation = recommendation
        
        return result
    
    @staticmethod
    def format_report(result: GradingResult) -> str:
        """Format a human-readable grading report"""
        return f"""
╔════════════════════════════════════════════════════════════════════════════╗
║ PHASE 3 AGENT ASSESSMENT — {result.agent_type}                           ║
╚════════════════════════════════════════════════════════════════════════════╝

FAILURE METRICS:
  • Original Failures Detected: {result.original_failures}
  • Failures Fixed by Agent: {result.fixed_failures}
  • New Failures Introduced: {result.new_failures}
  • Net Impact: {result.fixed_failures - result.new_failures}

COMPLIANCE METRICS:
  • Policy Violations Found: {result.policy_violations}
  • Documentation Updated: {'✅ Yes' if result.docs_updated else '❌ No'}
  • Lint Status (ruff + imports): {'✅ Clean' if result.lint_clean else '❌ Violations'}

SCORING BREAKDOWN (100 points total):
  ┌─────────────────────────────────────┬─────────────────┐
  │ Criterion                           │ Score           │
  ├─────────────────────────────────────┼─────────────────┤
  │ Failure Reduction (40 max)          │ {result.raw_scores.get('failure_reduction', 0):>3}/40        │
  │ No Regressions (25 max)             │ {result.raw_scores.get('no_regressions', 0):>3}/25        │
  │ Policy Compliance (20 max)          │ {result.raw_scores.get('policy_compliance', 0):>3}/20        │
  │ Documentation (10 max)              │ {result.raw_scores.get('documentation', 0):>3}/10        │
  │ Lint Clean (5 max)                  │ {result.raw_scores.get('lint_clean', 0):>3}/5         │
  ├─────────────────────────────────────┼─────────────────┤
  │ TOTAL SCORE                         │ {result.final_score:>3}/100      │
  └─────────────────────────────────────┴─────────────────┘

RECOMMENDATION: {result.recommendation}

NEXT STEPS:
{'  ✅ This agent\'s work is approved for merge.' if result.final_score >= 90 
  else '🔄 Route to human reviewer for assessment.' if result.final_score >= 70
  else '❌ Return to agent with specific feedback on low-scoring areas.'}
"""

# Test Example
if __name__ == '__main__':
    test_result = GradingResult(
        agent_type='ci-testing-agent',
        original_failures=3,
        fixed_failures=3,
        new_failures=0,
        policy_violations=0,
        docs_updated=True,
        lint_clean=True
    )
    
    graded = PhaseAGrader.grade(test_result)
    print(PhaseAGrader.format_report(graded))
    
    print("\n" + "="*80)
    print("TEST: Partial Fix (2 of 3 failures fixed)")
    print("="*80)
    
    test_result2 = GradingResult(
        agent_type='codebase-health-guardian',
        original_failures=3,
        fixed_failures=2,
        new_failures=0,
        policy_violations=1,
        docs_updated=False,
        lint_clean=False
    )
    
    graded2 = PhaseAGrader.grade(test_result2)
    print(PhaseAGrader.format_report(graded2))
