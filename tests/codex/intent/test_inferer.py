"""
Tests for codex.intent.inferer module.

This module contains tests for the Intent Inferer that combines
heuristics and LLM-based analysis for code intent inference.
"""

from datetime import datetime, timezone


class TestInputSpec:
    """Tests for InputSpec dataclass."""

    def test_required_fields(self):
        """Test InputSpec with required fields only."""
        from codex.intent.inferer import InputSpec

        spec = InputSpec(name="arg1", type="cli_arg")

        assert spec.name == "arg1", "name is not valid"
        assert spec.type == "cli_arg", "type is not valid"
        assert spec.required is True, "required is not valid"

    def test_optional_required(self):
        """Test InputSpec with required=False."""
        from codex.intent.inferer import InputSpec

        spec = InputSpec(name="optional_arg", type="env_var", required=False)

        assert spec.required is False, "required is not valid"

    def test_all_input_types(self):
        """Test all valid input types."""
        from codex.intent.inferer import InputSpec

        types = ["cli_arg", "stdin", "file", "env_var", "network"]

        for input_type in types:
            spec = InputSpec(name="test", type=input_type)
            assert spec.type == input_type, "type is not valid"


class TestOutputSpec:
    """Tests for OutputSpec dataclass."""

    def test_basic_creation(self):
        """Test OutputSpec basic creation."""
        from codex.intent.inferer import OutputSpec

        spec = OutputSpec(name="result", type="stdout")

        assert spec.name == "result", "Result must not be empty"
        assert spec.type == "stdout", "type is not valid"

    def test_all_output_types(self):
        """Test all valid output types."""
        from codex.intent.inferer import OutputSpec

        types = ["stdout", "stderr", "file", "network", "return_value"]

        for output_type in types:
            spec = OutputSpec(name="test", type=output_type)
            assert spec.type == output_type, "type is not valid"


class TestIntentSpec:
    """Tests for IntentSpec dataclass."""

    def test_basic_creation(self):
        """Test IntentSpec with minimal fields."""
        from codex.intent.inferer import IntentSpec

        spec = IntentSpec(
            snapshot_id="snap_123", timestamp=datetime.now(timezone.utc), goal="Process input data"
        )

        assert spec.snapshot_id == "snap_123", "snapshot_id is not valid"
        assert spec.goal == "Process input data", "Data must not be empty"
        assert spec.confidence == 0.5, "confidence is not valid"
        assert spec.inference_method == "heuristic", "inference_method is not valid"

    def test_default_lists(self):
        """Test IntentSpec default list values."""
        from codex.intent.inferer import IntentSpec

        spec = IntentSpec(
            snapshot_id="snap_123", timestamp=datetime.now(timezone.utc), goal="Test goal"
        )

        assert spec.actors == [], "actors is not valid"
        assert spec.inputs == [], "inputs is not valid"
        assert spec.outputs == [], "outputs is not valid"
        assert spec.constraints == [], "constraints is not valid"
        assert spec.side_effects == [], "side_effects is not valid"
        assert spec.assumptions == [], "assumptions is not valid"

    def test_with_inputs_outputs(self):
        """Test IntentSpec with inputs and outputs."""
        from codex.intent.inferer import InputSpec, IntentSpec, OutputSpec

        inputs = [InputSpec(name="data", type="stdin")]
        outputs = [OutputSpec(name="result", type="stdout")]

        spec = IntentSpec(
            snapshot_id="snap_456",
            timestamp=datetime.now(timezone.utc),
            goal="Transform data",
            inputs=inputs,
            outputs=outputs,
        )

        assert len(spec.inputs) == 1, "Collection must not be empty"
        assert len(spec.outputs) == 1, "Collection must not be empty"

    def test_inference_methods(self):
        """Test all valid inference methods."""
        from codex.intent.inferer import IntentSpec

        methods = ["heuristic", "llm", "hybrid"]

        for method in methods:
            spec = IntentSpec(
                snapshot_id="snap",
                timestamp=datetime.now(timezone.utc),
                goal="Test",
                inference_method=method,
            )
            assert spec.inference_method == method, "inference_method is not valid"

    def test_confidence_bounds(self):
        """Test confidence score values."""
        from codex.intent.inferer import IntentSpec

        # Low confidence
        spec_low = IntentSpec(
            snapshot_id="snap", timestamp=datetime.now(timezone.utc), goal="Test", confidence=0.1
        )
        assert spec_low.confidence == 0.1, "confidence is not valid"

        # High confidence
        spec_high = IntentSpec(
            snapshot_id="snap", timestamp=datetime.now(timezone.utc), goal="Test", confidence=0.95
        )
        assert spec_high.confidence == 0.95, "confidence is not valid"

    def test_llm_provenance(self):
        """Test LLM provenance reference."""
        from codex.intent.inferer import IntentSpec

        spec = IntentSpec(
            snapshot_id="snap",
            timestamp=datetime.now(timezone.utc),
            goal="Test",
            inference_method="llm",
            llm_provenance_ref="prov_abc123",
        )

        assert spec.llm_provenance_ref == "prov_abc123", "llm_provenance_ref is not valid"

    def test_to_dict(self):
        """Test IntentSpec serialization."""
        from codex.intent.inferer import InputSpec, IntentSpec, OutputSpec

        now = datetime.now(timezone.utc)
        spec = IntentSpec(
            snapshot_id="snap_789",
            timestamp=now,
            goal="Parse config",
            actors=["user", "system"],
            inputs=[InputSpec(name="config", type="file")],
            outputs=[OutputSpec(name="parsed", type="return_value")],
            constraints=["Must be valid JSON"],
            side_effects=["Logs to file"],
            confidence=0.8,
            inference_method="hybrid",
            assumptions=["Input is UTF-8 encoded"],
        )

        result = spec.to_dict()

        assert result["snapshot_id"] == "snap_789", "Result must not be empty"
        assert result["goal"] == "Parse config", "Result must not be empty"
        assert result["confidence"] == 0.8, "Result must not be empty"
        assert "actors" in result, "Result must not be empty"
        assert "inputs" in result, "Result must not be empty"


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.intent.inferer import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.intent.inferer", "name is not valid"
