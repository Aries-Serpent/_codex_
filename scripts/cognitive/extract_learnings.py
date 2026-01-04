#!/usr/bin/env python3
"""
Cognitive Brain - Learning Extractor
Part of AfterMath - extracts learnings from evaluations
"""
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def extract_learnings(
    evaluation_path: str,
    output_path: str,
    patterns: str = "success,failure,optimization"
) -> Dict[str, Any]:
    """
    Extract learnings from evaluation results.
    
    Args:
        evaluation_path: Path to evaluation.json
        output_path: Path to save learnings
        patterns: Types of patterns to extract
    
    Returns:
        Extracted learnings
    """
    # Load evaluation
    with open(evaluation_path) as f:
        evaluation = json.load(f)
    
    # Extract learnings
    learnings = {
        "extraction_timestamp": datetime.now().isoformat(),
        "patterns_extracted": patterns.split(","),
        "learnings": [],
        "actionable_insights": [],
        "knowledge_contributions": []
    }
    
    pattern_list = patterns.split(",")
    
    # Extract success patterns
    if "success" in pattern_list:
        for strength in evaluation.get("performance_assessment", {}).get("strengths", []):
            learnings["learnings"].append({
                "type": "success_pattern",
                "description": strength,
                "confidence": 0.90,
                "actionable": True,
                "recommendation": f"Continue and reinforce: {strength}"
            })
    
    # Extract failure patterns
    if "failure" in pattern_list:
        for weakness in evaluation.get("performance_assessment", {}).get("weaknesses", []):
            learnings["learnings"].append({
                "type": "failure_pattern",
                "description": weakness,
                "confidence": 0.85,
                "actionable": True,
                "recommendation": f"Address weakness: {weakness}"
            })
    
    # Extract optimization opportunities
    if "optimization" in pattern_list:
        for improvement in evaluation.get("improvement_areas", []):
            learnings["learnings"].append({
                "type": "optimization_opportunity",
                "area": improvement.get("area"),
                "current_value": improvement.get("current"),
                "target_value": improvement.get("target"),
                "confidence": 0.80,
                "priority": improvement.get("priority", "medium")
            })
    
    # Generate actionable insights
    learnings["actionable_insights"] = [
        {
            "insight": "Focus on improving metrics below target",
            "priority": "high",
            "estimated_impact": "20-30% improvement",
            "implementation_effort": "medium"
        },
        {
            "insight": "Replicate successful patterns across similar tasks",
            "priority": "medium",
            "estimated_impact": "10-15% improvement",
            "implementation_effort": "low"
        },
        {
            "insight": "Optimize resource allocation based on performance data",
            "priority": "medium",
            "estimated_impact": "15-20% improvement",
            "implementation_effort": "medium"
        }
    ]
    
    # Knowledge contributions for shared memory
    learnings["knowledge_contributions"] = [
        {
            "contribution_type": "best_practice",
            "description": "Successful task execution patterns",
            "source": "cycle_evaluation",
            "confidence": 0.88,
            "applicable_to": ["all_agents"]
        },
        {
            "contribution_type": "anti_pattern",
            "description": "Patterns that led to failures",
            "source": "cycle_evaluation",
            "confidence": 0.82,
            "applicable_to": ["all_agents"]
        }
    ]
    
    # Summary
    learnings["summary"] = {
        "total_learnings": len(learnings["learnings"]),
        "success_patterns": sum(1 for l in learnings["learnings"] if l.get("type") == "success_pattern"),
        "failure_patterns": sum(1 for l in learnings["learnings"] if l.get("type") == "failure_pattern"),
        "optimization_opportunities": sum(1 for l in learnings["learnings"] if l.get("type") == "optimization_opportunity"),
        "actionable_insights": len(learnings["actionable_insights"])
    }
    
    # Save learnings
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(learnings, f, indent=2)
    
    print(f"✅ Learning extraction complete")
    print(f"   Total learnings: {learnings['summary']['total_learnings']}")
    print(f"   Success patterns: {learnings['summary']['success_patterns']}")
    print(f"   Optimization opportunities: {learnings['summary']['optimization_opportunities']}")
    print(f"   Actionable insights: {learnings['summary']['actionable_insights']}")
    
    return learnings


def main():
    parser = argparse.ArgumentParser(description="Extract learnings from evaluation")
    parser.add_argument("--evaluation", required=True, help="Path to evaluation JSON")
    parser.add_argument("--output", required=True, help="Output path")
    parser.add_argument("--patterns", default="success,failure,optimization", help="Patterns to extract")
    args = parser.parse_args()
    
    extract_learnings(args.evaluation, args.output, args.patterns)


if __name__ == "__main__":
    main()
