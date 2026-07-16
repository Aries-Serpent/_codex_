#!/usr/bin/env python3
"""
Batch 3 Flaky Test Diagnosis Script
Analyzes and categorizes flaky tests and edge-case errors (Errors 111-142)
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def find_flaky_patterns():
    """Find tests with timing dependencies, network calls, etc."""
    
    test_root = Path("tests")
    patterns = {
        "timing_issues": [],
        "network_deps": [],
        "external_services": [],
        "race_conditions": [],
        "syntax_errors": [],
    }
    
    # Pattern matchers
    timing_pattern = re.compile(r'(time\.sleep|time\.time|\.wait\(|timeout|\.start\(\)|\.stop\(\))')
    network_pattern = re.compile(r'(requests\.|http\.|socket\.|\.get\(|\.post\(|\.request\()')
    external_pattern = re.compile(r'(mock\.|monkeypatch|patch|MagicMock)')
    race_pattern = re.compile(r'(async|await|threading|concurrent|lock|Event\()')
    
    for test_file in test_root.rglob("test_*.py"):
        try:
            content = test_file.read_text()
            
            # Skip files that are already marked as flaky
            if '@pytest.mark.flaky' in content or '@flaky' in content:
                continue
                
            # Check for timing issues
            if timing_pattern.search(content):
                patterns["timing_issues"].append(str(test_file))
                
            # Check for network dependencies
            if network_pattern.search(content):
                patterns["network_deps"].append(str(test_file))
                
            # Check for external service mocking
            if external_pattern.search(content):
                patterns["external_services"].append(str(test_file))
                
            # Check for concurrency/race conditions
            if race_pattern.search(content):
                patterns["race_conditions"].append(str(test_file))
                
        except Exception as e:
            print(f"Error processing {test_file}: {e}")
    
    return patterns

def categorize_flaky_tests():
    """Categorize flaky tests into batches"""
    patterns = find_flaky_patterns()
    
    # Top 10 files with timing issues (most prone to flakiness)
    timing_files = patterns["timing_issues"][:10]
    network_files = patterns["network_deps"][:5]
    race_condition_files = patterns["race_conditions"][:5]
    
    return {
        "timing_dependent": timing_files,
        "network_dependent": network_files,
        "race_conditions": race_condition_files,
    }

def main():
    print("=" * 80)
    print("BATCH 3 FLAKY TEST DIAGNOSIS")
    print("=" * 80)
    
    patterns = find_flaky_patterns()
    
    print(f"\n📊 PATTERN ANALYSIS:")
    print(f"  Timing Issues (time.sleep, timeouts): {len(patterns['timing_issues'])}")
    print(f"  Network Dependencies (requests, http): {len(patterns['network_deps'])}")
    print(f"  External Service Mocking: {len(patterns['external_services'])}")
    print(f"  Race Conditions (async, threading): {len(patterns['race_conditions'])}")
    
    categorized = categorize_flaky_tests()
    
    print(f"\n🎯 TOP TIMING-DEPENDENT TESTS (candidates for freezegun):")
    for i, test_file in enumerate(categorized["timing_dependent"][:5], 1):
        print(f"  {i}. {test_file}")
    
    print(f"\n🎯 TOP NETWORK-DEPENDENT TESTS (candidates for mocking):")
    for i, test_file in enumerate(categorized["network_dependent"][:5], 1):
        print(f"  {i}. {test_file}")
    
    print(f"\n🎯 TOP RACE CONDITION TESTS (candidates for polling):")
    for i, test_file in enumerate(categorized["race_conditions"][:5], 1):
        print(f"  {i}. {test_file}")
    
    print("\n✅ Diagnosis complete. See details in categorized output above.")

if __name__ == "__main__":
    main()
