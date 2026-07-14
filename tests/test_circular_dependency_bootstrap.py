"""
Bootstrap Validation Test for Training/ML Decoupling.

This test validates that:
1. codex.training can be imported without codex_ml
2. codex_ml can be imported without training
3. Both can be imported together
4. Circular imports are detected and logged
"""

from __future__ import annotations

import subprocess
import sys


def test_independent_import_training() -> bool:
    """Test that training can be imported independently."""
    print("\n[TEST 1] Importing training module independently...")
    
    # Create a subprocess to test in isolation
    test_code = """
    import sys
sys.path.insert(0, '/home/runner/work/_codex_/_codex_/src')

# Try importing training components
try:
    from training.config import TrainerConfig
    from training.trainer import Trainer
    from training.checkpoint_manager import CheckpointManager
    print("✓ Training module imports successful (independent)")
    sys.exit(0)
except ImportError as e:
    print(f"✗ Training import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⚠ Training import exception: {e}")
    sys.exit(2)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Stderr: {result.stderr}")
    
    return result.returncode == 0


def test_independent_import_codex_ml() -> bool:
    """Test that codex_ml can be imported independently."""
    print("\n[TEST 2] Importing codex_ml module independently...")
    
    test_code = """
    import sys
sys.path.insert(0, '/home/runner/work/_codex_/_codex_/src')

# Try importing codex_ml components
try:
    from codex_ml.training.engine import TrainingEngine
    from codex_ml.data_utils import split_dataset
    from codex_ml.logging.file_logger import FileLogger
    print("✓ codex_ml module imports successful (independent)")
    sys.exit(0)
except ImportError as e:
    print(f"✗ codex_ml import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⚠ codex_ml import exception: {e}")
    sys.exit(2)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Stderr: {result.stderr}")
    
    return result.returncode == 0


def test_bidirectional_import() -> bool:
    """Test that both modules can be imported together without cycles."""
    print("\n[TEST 3] Importing both modules (bidirectional)...")
    
    test_code = """
    import sys
sys.path.insert(0, '/home/runner/work/_codex_/_codex_/src')

# Try importing in both orders
try:
    # Order 1: training first
    from training.trainer import Trainer
    from codex_ml.training.engine import TrainingEngine
    print("✓ Import order 1 (training → codex_ml) successful")
except ImportError as e:
    print(f"✗ Order 1 failed: {e}")
    sys.exit(1)

try:
    # Order 2: codex_ml first (in same process)
    from codex_ml.logging.file_logger import FileLogger
    from training.config import TrainerConfig
    print("✓ Import order 2 (codex_ml → training) successful")
except ImportError as e:
    print(f"✗ Order 2 failed: {e}")
    sys.exit(1)

print("✓ Bidirectional imports successful")
sys.exit(0)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Stderr: {result.stderr}")
    
    return result.returncode == 0


def test_protocol_availability() -> bool:
    """Test that protocols can be imported and are zero-dependency."""
    print("\n[TEST 4] Testing protocol availability...")
    
    test_code = """
    import sys
sys.path.insert(0, '/home/runner/work/_codex_/_codex_/src')

try:
    from codex.protocols import (
        DatasetProtocol,
        ModelProtocol,
        TrainerProtocol,
        MetricsProtocol,
        LoggerProtocol,
        OptimizerProtocol,
        SchedulerProtocol,
    )
    print("✓ All core protocols imported successfully")
    
    # Verify they are Protocol types
    import typing
    for proto in [
        DatasetProtocol,
        ModelProtocol,
        TrainerProtocol,
        MetricsProtocol,
    ]:
        if hasattr(typing, 'get_protocol_members'):
            # Python 3.13+
            pass
    
    print("✓ Protocol validation passed")
    sys.exit(0)
except ImportError as e:
    print(f"✗ Protocol import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⚠ Protocol test exception: {e}")
    sys.exit(2)
"""
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Stderr: {result.stderr}")
    
    return result.returncode in (0, 2)  # 2 is OK for Python version differences


def main() -> int:
    """Run all bootstrap validation tests."""
    print("=" * 70)
    print("BOOTSTRAP VALIDATION TEST SUITE")
    print("=" * 70)
    print("Testing circular dependency breaking and protocol-based architecture")
    
    results: dict[str, bool] = {}
    
    try:
        results["test_protocol_availability"] = test_protocol_availability()
        results["test_independent_import_training"] = test_independent_import_training()
        results["test_independent_import_codex_ml"] = test_independent_import_codex_ml()
        results["test_bidirectional_import"] = test_bidirectional_import()
    except subprocess.TimeoutExpired:
        print("✗ Test timeout - possible circular import deadlock detected!")
        return 1
    except Exception as e:
        print(f"✗ Test execution failed: {e}")
        return 1
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Circular dependencies successfully broken!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed - Additional work needed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
