#!/usr/bin/env python3
"""
Phase 7A Wave 3 Lane 3.2: Comprehensive Mutation Testing Script
Executes mutation testing on Wave 1+2 tests to achieve ≥75% mutation score
"""

import subprocess
import sys
from datetime import datetime


def run_mutation_tests(config_file):
    """Run mutation tests and collect results"""
    print(f"\n{'='*70}")
    print("PHASE 7A WAVE 3 LANE 3.2: MUTATION TESTING EXECUTION")
    print(f"{'='*70}\n")

    print(f"Starting mutation testing at {datetime.now().isoformat()}")
    print(f"Config: {config_file}")
    print("Target: ≥75% mutation score (ideal: 80-85%)")
    print()

    # Run mutmut
    cmd = [
        "python3", "-m", "mutmut",
        "run",
        "--config-file", config_file,
        "--paths-to-mutate", "src/",
        "--tests-dir", "tests/",
        "--quiet"
    ]

    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode

if __name__ == "__main__":
    exit_code = run_mutation_tests(".mutmut-comprehensive.ini")
    sys.exit(exit_code)
