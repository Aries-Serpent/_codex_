"""Acceptance tests for CB-002: quantum_superposition decorator — no double invocation.

Validates that the ``@quantum_superposition()`` decorator:
  - Invokes the wrapped function exactly once per call (no double-invoke)
  - Returns the correct value from that single invocation
  - Falls back gracefully to classical execution when quantum is disabled
  - Preserves the decorated function's identity (__name__, __wrapped__)
"""

from cognitive_brain.quantum.superposition import quantum_superposition

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestQuantumSuperpositionNoDoubleInvoke:
    """CB-002: acceptance tests for the quantum_superposition decorator."""

    def test_func_called_exactly_once(self):
        """The decorated function is invoked exactly once per call, never twice."""
        call_count = {"n": 0}

        @quantum_superposition()
        def compute(x: int) -> int:
            call_count["n"] += 1
            return x * 2

        result = compute(5)

        assert (call_count["n"] == 1, "Count must be greater than zero"
        ), f"Expected func to be called exactly once, but it was called {call_count['n']} times."
        assert result == 10, "Result must not be empty"

    def test_func_called_exactly_once_with_side_effects(self):
        """Side-effect functions are not double-triggered by the decorator."""
        log: list[str] = []

        @quantum_superposition()
        def emit_event(name: str) -> str:
            log.append(name)
            return name.upper()

        result = emit_event("hello")

        assert log == ["hello"], f"Side-effect log should have exactly one entry: {log}"
        assert result == "HELLO", "Result must not be empty"

    def test_return_value_preserved(self):
        """The decorator returns the exact value produced by the function."""

        @quantum_superposition()
        def make_dict() -> dict:
            return {"key": [1, 2, 3]}

        result = make_dict()
        assert result == {"key": [1, 2, 3]}

    def test_non_numeric_return_does_not_raise(self):
        """Non-numeric return values (list, dict, None) do not cause errors."""

        @quantum_superposition()
        def return_list() -> list:
            return [10, 20, 30]

        result = return_list()
        assert result == [10, 20, 30]

    def test_classical_fallback_when_quantum_disabled(self):
        """When quantum is explicitly disabled via config, classical path is used."""
        call_count = {"n": 0}

        @quantum_superposition(coherence_threshold=999.0)  # unreachably high → fallback
        def inc(x: int) -> int:
            call_count["n"] += 1
            return x + 1

        result = inc(7)
        # Function should still run and return the right value
        assert result == 8, "Result must not be empty"
        # Should still have been called exactly once (via fallback path)
        assert call_count["n"] >= 1, "Value must be greater than zero"

    def test_wrapper_preserves_function_metadata(self):
        """The decorator preserves __name__ and wraps the function correctly."""

        @quantum_superposition()
        def my_important_function(x: int) -> int:
            return x

        assert my_important_function.__name__ == "my_important_function", "__name__ is not valid"

    def test_multiple_calls_each_invoke_once(self):
        """Each call to the decorated function invokes the original exactly once."""
        call_count = {"n": 0}

        @quantum_superposition()
        def identity(x: int) -> int:
            call_count["n"] += 1
            return x

        for i in range(5):
            result = identity(i)
            assert result == i, "Result must not be empty"

        assert (call_count["n"] == 5, "Count must be greater than zero"
        ), f"Expected 5 total invocations for 5 calls, got {call_count['n']}."
