#!/usr/bin/env python3
"""Compare determinism test results from two runs."""
import json
import sys


def compare_test_results(results_file1: str, results_file2: str) -> int:
    """
    Compare test outcomes from two JSON result files.

    Args:
        results_file1: Path to first results JSON file
        results_file2: Path to second results JSON file

    Returns:
        0 if results match, 1 if differences found
    """
    with open(results_file1) as f:
        results1 = json.load(f)
    with open(results_file2) as f:
        results2 = json.load(f)

    # Compare test outcomes
    outcomes1 = {test['nodeid']: test['outcome'] for test in results1.get('tests', [])}
    outcomes2 = {test['nodeid']: test['outcome'] for test in results2.get('tests', [])}

    differences = []
    for nodeid in set(outcomes1.keys()) | set(outcomes2.keys()):
        if outcomes1.get(nodeid) != outcomes2.get(nodeid):
            differences.append(f"  - {nodeid}: {outcomes1.get(nodeid)} vs {outcomes2.get(nodeid)}")

    if differences:
        print("❌ Determinism check FAILED - test outcomes differ:")
        for diff in differences:
            print(diff)
        return 1
    print("✅ Determinism check PASSED - all tests are deterministic")
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <results1.json> <results2.json>")
        sys.exit(1)

    sys.exit(compare_test_results(sys.argv[1], sys.argv[2]))
