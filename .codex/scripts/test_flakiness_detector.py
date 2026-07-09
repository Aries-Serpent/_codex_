#!/usr/bin/env python3
"""Test Flakiness Detection and Stabilization Automation Tool.

Monitors newly added tests for flakiness, applies stabilization patterns,
and validates consistency across multiple runs.

Usage:
    python .codex/scripts/test_flakiness_detector.py --detect-new-tests
    python .codex/scripts/test_flakiness_detector.py --run-stability-check tests/path/to/new_test.py
    python .codex/scripts/test_flakiness_detector.py --apply-stabilization tests/path/to/new_test.py
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
import argparse
import re


class FlakinessDetector:
    """Detects flakiness patterns in new tests."""
    
    PATTERNS = {
        "random_seed_leakage": {
            "confidence": 95,
            "fix_pattern": "seed_control",
            "indicators": [r"random\.", r"np\.random", r"torch\.random"]
        },
        "threading_race": {
            "confidence": 90,
            "fix_pattern": "threading_barrier",
            "indicators": [r"Thread\(", r"threading\.", r"concurrent\.futures"]
        },
        "mock_state_carryover": {
            "confidence": 85,
            "fix_pattern": "mock_reset",
            "indicators": [r"@patch\(", r"MagicMock", r"mock\."]
        },
        "resource_leak": {
            "confidence": 99,
            "fix_pattern": "resource_cleanup",
            "indicators": [r"open\(", r"\.txt", r"tempfile"]
        },
        "non_deterministic_order": {
            "confidence": 98,
            "fix_pattern": "deterministic_ordering",
            "indicators": [r"\.items\(\)", r"\.keys\(\)", r"set\("]
        }
    }
    
    def __init__(self):
        self.codex_dir = Path(".codex")
        self.stabilization_log = self.codex_dir / "TEST_STABILIZATION_LOG.jsonl"
        self.flakiness_report = self.codex_dir / "TEST_FLAKINESS_REPORT.md"
    
    def detect_new_tests(self) -> Set[str]:
        """Detect newly added test files."""
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "--name-only", "--", "tests/"],
                capture_output=True, text=True, timeout=10
            )
            
            new_tests = set()
            for line in result.stdout.strip().split('\n'):
                if line and 'test_' in line and line.endswith('.py'):
                    new_tests.add(line)
            
            return new_tests
        except Exception as e:
            print(f"Error detecting new tests: {e}", file=sys.stderr)
            return set()
    
    def analyze_test_for_flakiness(self, test_path: str) -> Dict:
        """Analyze test code for potential flakiness patterns."""
        try:
            with open(test_path, 'r') as f:
                content = f.read()
            
            detected_patterns = []
            
            for pattern_name, pattern_info in self.PATTERNS.items():
                for indicator in pattern_info["indicators"]:
                    if re.search(indicator, content):
                        detected_patterns.append({
                            "pattern": pattern_name,
                            "confidence": pattern_info["confidence"],
                            "fix_pattern": pattern_info["fix_pattern"],
                            "indicator": indicator
                        })
            
            return {
                "test_path": test_path,
                "potential_flakiness_patterns": detected_patterns,
                "risk_level": self._calculate_risk(detected_patterns)
            }
        except Exception as e:
            print(f"Error analyzing {test_path}: {e}", file=sys.stderr)
            return {"test_path": test_path, "error": str(e)}
    
    def _calculate_risk(self, patterns: List[Dict]) -> str:
        """Calculate overall risk level."""
        if not patterns:
            return "LOW"
        
        avg_confidence = sum(p["confidence"] for p in patterns) / len(patterns)
        
        if avg_confidence >= 90:
            return "HIGH"
        elif avg_confidence >= 80:
            return "MEDIUM"
        else:
            return "LOW"
    
    def run_test_multiple_times(self, test_path: str, runs: int = 5) -> Dict:
        """Run test multiple times to detect actual flakiness."""
        results = {
            "test_path": test_path,
            "runs": runs,
            "passes": 0,
            "failures": 0,
            "pass_rate": 0.0,
            "run_details": []
        }
        
        for i in range(runs):
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
                    capture_output=True, text=True, timeout=60
                )
                
                passed = result.returncode == 0
                results["passes"] += 1 if passed else 0
                results["failures"] += 0 if passed else 1
                results["run_details"].append({
                    "run": i + 1,
                    "passed": passed,
                    "returncode": result.returncode
                })
            except subprocess.TimeoutExpired:
                results["run_details"].append({
                    "run": i + 1,
                    "passed": False,
                    "returncode": -1,
                    "error": "timeout"
                })
                results["failures"] += 1
        
        results["pass_rate"] = (results["passes"] / runs) * 100
        results["is_flaky"] = results["pass_rate"] < 100.0
        
        return results
    
    def log_stabilization(self, test_path: str, pattern: str, status: str, details: str = ""):
        """Log stabilization action."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "test_path": test_path,
            "pattern": pattern,
            "status": status,
            "details": details
        }
        
        with open(self.stabilization_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def generate_flakiness_report(self, test_results: List[Dict]) -> str:
        """Generate flakiness report."""
        report = f"""# Test Flakiness Detection Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Tests Analyzed: {len(test_results)}
- Stable Tests: {sum(1 for r in test_results if not r.get('is_flaky', False))}
- Flaky Tests: {sum(1 for r in test_results if r.get('is_flaky', False))}

## Flaky Tests Requiring Stabilization
"""
        
        flaky_tests = [r for r in test_results if r.get('is_flaky', False)]
        
        if flaky_tests:
            for result in flaky_tests:
                report += f"""
### {result['test_path']}
- Pass Rate: {result['pass_rate']:.1f}% ({result['passes']}/{result['runs']} passes)
- Status: ⚠️ FLAKY - Requires Stabilization
"""
        else:
            report += "\n✅ No flaky tests detected.\n"
        
        report += f"\n*Report generated: {datetime.now().isoformat()}*"
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Flakiness Detection and Stabilization Tool"
    )
    parser.add_argument(
        "--detect-new-tests",
        action="store_true",
        help="Detect newly added test files"
    )
    parser.add_argument(
        "--analyze",
        type=str,
        help="Analyze test file for flakiness patterns"
    )
    parser.add_argument(
        "--run-stability-check",
        type=str,
        help="Run test multiple times to check stability"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of times to run test (default: 5)"
    )
    parser.add_argument(
        "--generate-report",
        type=str,
        help="Generate flakiness report from results file"
    )
    
    args = parser.parse_args()
    detector = FlakinessDetector()
    
    if args.detect_new_tests:
        new_tests = detector.detect_new_tests()
        if new_tests:
            print(f"✅ Found {len(new_tests)} new test file(s):")
            for test in sorted(new_tests):
                print(f"  - {test}")
        else:
            print("ℹ️  No new test files detected.")
    
    elif args.analyze:
        result = detector.analyze_test_for_flakiness(args.analyze)
        print(json.dumps(result, indent=2))
    
    elif args.run_stability_check:
        print(f"Running {args.runs} times: {args.run_stability_check}")
        result = detector.run_test_multiple_times(args.run_stability_check, args.runs)
        print(json.dumps(result, indent=2))
        
        if result.get('is_flaky'):
            print(f"\n⚠️  Test is FLAKY (Pass rate: {result['pass_rate']:.1f}%)")
            sys.exit(1)
        else:
            print(f"\n✅ Test is STABLE (Pass rate: {result['pass_rate']:.1f}%)")
            sys.exit(0)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
