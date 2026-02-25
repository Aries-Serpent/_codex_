#!/bin/bash
# Test script to validate all 5 fixes for Resilient Validation Suite failures

set -e

echo "=== Testing Fix #1: Safety filters edge cases ==="
python3 -m pytest tests/safety/test_filters_edge_cases_phase26.py::TestSafetyFiltersEdgeCases::test_nested_secret_patterns -xvs 2>&1 | tee /tmp/test1.log || echo "Test 1 status: $?"

echo ""
echo "=== Testing Fix #2: Codexml CLI functional entry ==="
python3 -m pytest tests/test_codexml_cli.py::test_run_training_invokes_functional_entry -xvs 2>&1 | tee /tmp/test2.log || echo "Test 2 status: $?"

echo ""
echo "=== Testing Fix #3: Datasets module with PyTorch profiler ==="
python3 -m pytest tests/data/test_datasets_module.py::test_build_dataloaders_with_split -xvs 2>&1 | tee /tmp/test3.log || echo "Test 3 status: $?"

echo ""
echo "=== Testing Fix #4: PEFT integration ==="
python3 -m pytest tests/test_peft_integration.py::test_peft_apply_lora -xvs 2>&1 | tee /tmp/test4.log || echo "Test 4 status: $?"

echo ""
echo "=== Testing Fix #5: CLI logging integration ==="
python3 -m pytest tests/logging/test_cli_logging_integration.py::test_cli_uses_logger -xvs 2>&1 | tee /tmp/test5.log || echo "Test 5 status: $?"

echo ""
echo "=== Summary ==="
for i in 1 2 3 4 5; do
    if grep -q "PASSED" /tmp/test${i}.log 2>/dev/null; then
        echo "✅ Test $i: PASSED"
    elif grep -q "SKIPPED" /tmp/test${i}.log 2>/dev/null; then
        echo "⏭️  Test $i: SKIPPED"
    else
        echo "❌ Test $i: FAILED"
    fi
done
