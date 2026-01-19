#!/usr/bin/env python3
"""
Simple test runner for batch-triage-agent tests.
Bypasses pytest's conftest.py to run tests directly.
"""

import sys
import importlib.util
from pathlib import Path

# Add paths
AGENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENT_DIR / "src"))
sys.path.insert(0, str(AGENT_DIR.parent.parent.parent))

# Import test modules
print("=" * 70)
print("BATCH-TRIAGE-AGENT TEST RUNNER")
print("=" * 70)

test_count = 0
passed_count = 0
failed_count = 0

def run_test(test_func, test_name):
    """Run a single test function."""
    global test_count, passed_count, failed_count
    test_count += 1
    try:
        test_func()
        print(f"✓ {test_name}")
        passed_count += 1
        return True
    except Exception as e:
        print(f"✗ {test_name}: {e}")
        failed_count += 1
        return False

def load_test_module(module_name, file_path):
    """Load a test module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load and run test_analyzer tests
print("\n--- test_analyzer.py ---")
test_analyzer = load_test_module("test_analyzer", AGENT_DIR / "tests" / "test_analyzer.py")
run_test(test_analyzer.test_analyzer_initialization, "test_analyzer_initialization")
run_test(test_analyzer.test_analyze_with_confidence, "test_analyze_with_confidence")
run_test(test_analyzer.test_enrich_with_historical_context, "test_enrich_with_historical_context")
run_test(test_analyzer.test_calculate_group_confidence, "test_calculate_group_confidence")
run_test(test_analyzer.test_get_metrics, "test_get_metrics")
run_test(test_analyzer.test_export_for_learning, "test_export_for_learning")

# Load and run test_pattern_learner tests
print("\n--- test_pattern_learner.py ---")
test_pattern_learner = load_test_module("test_pattern_learner", AGENT_DIR / "tests" / "test_pattern_learner.py")
run_test(test_pattern_learner.test_pattern_learner_initialization, "test_pattern_learner_initialization")
run_test(test_pattern_learner.test_failure_pattern_dataclass, "test_failure_pattern_dataclass")
run_test(test_pattern_learner.test_record_triage_outcome, "test_record_triage_outcome")
run_test(test_pattern_learner.test_pattern_extraction, "test_pattern_extraction")
run_test(test_pattern_learner.test_track_remediation_outcome, "test_track_remediation_outcome")
run_test(test_pattern_learner.test_get_pattern, "test_get_pattern")
run_test(test_pattern_learner.test_get_best_remediation, "test_get_best_remediation")
run_test(test_pattern_learner.test_cleanup_expired_patterns, "test_cleanup_expired_patterns")
run_test(test_pattern_learner.test_get_statistics, "test_get_statistics")

# Load and run test_remediation_engine tests
print("\n--- test_remediation_engine.py ---")
test_remediation_engine = load_test_module("test_remediation_engine", AGENT_DIR / "tests" / "test_remediation_engine.py")
run_test(test_remediation_engine.test_remediation_engine_initialization, "test_remediation_engine_initialization")
run_test(test_remediation_engine.test_remediation_action_dataclass, "test_remediation_action_dataclass")
run_test(test_remediation_engine.test_generate_test_failure_remediations, "test_generate_test_failure_remediations")
run_test(test_remediation_engine.test_generate_import_error_remediations, "test_generate_import_error_remediations")
run_test(test_remediation_engine.test_generate_lint_error_remediations, "test_generate_lint_error_remediations")
run_test(test_remediation_engine.test_classify_risk, "test_classify_risk")
run_test(test_remediation_engine.test_filter_by_risk, "test_filter_by_risk")
run_test(test_remediation_engine.test_apply_action_dry_run, "test_apply_action_dry_run")
run_test(test_remediation_engine.test_apply_action_requires_approval, "test_apply_action_requires_approval")
run_test(test_remediation_engine.test_generate_report, "test_generate_report")

# Load and run test_notifier tests
print("\n--- test_notifier.py ---")
test_notifier = load_test_module("test_notifier", AGENT_DIR / "tests" / "test_notifier.py")
run_test(test_notifier.test_notifier_initialization, "test_notifier_initialization")
run_test(test_notifier.test_notification_dataclass, "test_notification_dataclass")
run_test(test_notifier.test_notify_batch_triage_complete, "test_notify_batch_triage_complete")
run_test(test_notifier.test_notify_remediation_available, "test_notify_remediation_available")
run_test(test_notifier.test_notify_remediation_applied_success, "test_notify_remediation_applied_success")
run_test(test_notifier.test_notify_remediation_applied_failure, "test_notify_remediation_applied_failure")
run_test(test_notifier.test_notify_escalation, "test_notify_escalation")
run_test(test_notifier.test_get_statistics, "test_get_statistics")
run_test(test_notifier.test_priority_based_routing, "test_priority_based_routing")
run_test(test_notifier.test_build_triage_summary_message, "test_build_triage_summary_message")

# Summary
print("\n" + "=" * 70)
print(f"TEST RESULTS: {passed_count}/{test_count} passed, {failed_count} failed")
print("=" * 70)

if failed_count > 0:
    sys.exit(1)
else:
    print("\n✅ ALL TESTS PASSED!")
    sys.exit(0)
