# Debugging Test Failures

This prompt helps AI Agents systematically debug test failures in the Codex repository.

## Context

Use this prompt when tests fail in CI/CD or local development to diagnose and fix issues efficiently.

## Prompt Template

```
I need help debugging a test failure in the Codex repository.

**Test Information:**
- Test file: [path/to/test_file.py]
- Test name: [test_function_name]
- Failure type: [AssertionError / Exception / Timeout / etc.]
- Error message: [paste error message here]

**Steps to Debug:**

1. **Understand the Test**
   - Read the test file: [path/to/test_file.py]
   - Identify what the test is testing
   - Check test dependencies and fixtures

2. **Reproduce Locally**
   ```bash
   # Run the specific test
   pytest path/to/test_file.py::test_function_name -v
   
   # Run with more debugging info
   pytest path/to/test_file.py::test_function_name -vv -s
   ```

3. **Analyze the Failure**
   - Check if it's a test issue or code issue
   - Look for recent changes that might have caused it
   - Check if environment variables are set correctly
   - Verify dependencies are installed

4. **Check Related Code**
   - Find the code being tested
   - Review recent commits to that code
   - Check for related tests that pass/fail

5. **Common Issues and Solutions**

   **Import Errors:**
   - Check if modules are installed: `pip list | grep [module]`
   - Verify PYTHONPATH is set correctly
   - Check for circular imports

   **Assertion Failures:**
   - Print actual vs expected values
   - Check if test data has changed
   - Verify mock configurations

   **Timeout Issues:**
   - Increase timeout values if legitimate
   - Check for infinite loops
   - Look for blocking I/O operations

   **Fixture Issues:**
   - Check conftest.py for fixture definitions
   - Verify fixture scope (function, module, session)
   - Look for fixture dependency issues

6. **Fix and Verify**
   - Make minimal changes to fix the issue
   - Run the test again to verify fix
   - Run related tests to ensure no regression
   - Run full test suite if significant changes

7. **Document the Fix**
   - Add comments explaining the fix if non-obvious
   - Update test documentation if needed
   - Consider adding regression test if appropriate

**Useful Commands:**
```bash
# Run tests with coverage
pytest path/to/test_file.py --cov=src/codex_ml --cov-report=term

# Run tests in verbose mode with output
pytest path/to/test_file.py -vv -s

# Run specific test pattern
pytest -k "test_pattern" -v

# Run with debugging on failure
pytest path/to/test_file.py --pdb

# List all tests without running
pytest --collect-only path/to/test_file.py
```

**Repository-Specific Debugging:**

For Codex-specific issues:
- Check `AGENTS.md` for testing conventions
- Review `tests/conftest.py` for custom fixtures
- Check `.pytest.ini` for test configuration
- Look at `pyproject.toml` for test settings

**Next Steps:**
- Fix the identified issue
- Run tests to verify
- Commit with clear message explaining the fix
```

## Examples

### Example 1: Import Error

```
Test file: tests/test_training.py
Test name: test_gradient_accumulation
Failure: ImportError: cannot import name 'TrainingConfig' from 'training.config'

Diagnosis:
- Module path may be incorrect
- Check if training/config.py exists
- Verify __init__.py files in path
- Check for circular imports

Fix: Update import path or add missing __init__.py
```

### Example 2: Assertion Failure

```
Test file: tests/test_tokenization.py
Test name: test_tokenizer_parity
Failure: AssertionError: assert [1, 2, 3] == [1, 2, 3, 4]

Diagnosis:
- Fast tokenizer adding extra token
- Check tokenizer configuration
- Verify test data hasn't changed
- Review recent tokenizer changes

Fix: Update test expectation or fix tokenizer behavior
```

### Example 3: Fixture Error

```
Test file: tests/test_evaluation.py
Test name: test_metric_computation
Failure: fixture 'mock_model' not found

Diagnosis:
- Fixture not defined in conftest.py
- Fixture in wrong scope
- Import issue with fixture file

Fix: Add missing fixture or import fixture module
```

## Related Prompts

- [Resolving Merge Conflicts](./resolve-merge-conflicts.md)
- [Performance Optimization](./performance-optimization.md)
- [Security Vulnerability Remediation](./security-remediation.md)

## Automation

This debugging process can be automated using the workflow navigator:

```python
from agents.workflow_navigator import WorkflowNavigator

navigator = WorkflowNavigator()
navigator.execute('DEBUG_TEST')  # Future: automated test debugging
```

## References

- [pytest documentation](https://docs.pytest.org/)
- [Python debugging guide](https://docs.python.org/3/library/pdb.html)
- [Codex testing conventions](../../../AGENTS.md#testing)
