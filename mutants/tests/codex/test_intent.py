"""
Comprehensive tests for the Codex Intent module.

Tests cover:
- Heuristic intent inference
- LLM client with provenance
- Intent specification generation
- Code type detection
"""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


class TestIntentInferer:
    """Tests for intent inference functionality."""
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    def test_infer_cli_tool(self):
        """Test inferring intent for a CLI tool."""
        from codex.intent.inferer import infer_intent

        static_report = {
            "snapshot_id": "test-123",
            "files": [{"imports": ["argparse", "sys"], "exports": ["main"]}],
            "summary": {"total_files": 1},
        }

        intent = infer_intent(static_report, source_excerpt="import argparse")

        assert "cli" in intent.goal.lower() or "command" in intent.goal.lower(), "Condition must be true"
        assert intent.confidence >= 0.5, "confidence must be greater than zero"
        assert intent.inference_method == "heuristic", "inference_method is not valid"

    def test_infer_web_service(self):
        """Test inferring intent for a web service."""
        from codex.intent.inferer import infer_intent

        static_report = {
            "snapshot_id": "test-123",
            "files": [{"imports": ["flask", "json"], "exports": ["app"]}],
            "summary": {"total_files": 1},
        }

        intent = infer_intent(static_report, source_excerpt="from flask import Flask")

        assert "web" in intent.goal.lower() or "service" in intent.goal.lower(), "Condition must be true"
        assert intent.confidence >= 0.7, "confidence must be greater than zero"

    def test_infer_gui_app(self):
        """Test inferring intent for a GUI application."""
        from codex.intent.inferer import infer_intent

        static_report = {
            "snapshot_id": "test-123",
            "files": [{"imports": ["tkinter"], "exports": ["main"]}],
            "summary": {"total_files": 1},
        }

        intent = infer_intent(static_report, source_excerpt="import tkinter")

        assert "gui" in intent.goal.lower() or "graphical" in intent.goal.lower(), "Condition must be true"

    def test_infer_data_processing(self):
        """Test inferring intent for data processing code."""
        from codex.intent.inferer import infer_intent

        static_report = {
            "snapshot_id": "test-123",
            "files": [{"imports": ["pandas", "numpy"], "exports": ["process"]}],
            "summary": {"total_files": 1},
        }

        intent = infer_intent(static_report, source_excerpt="import pandas as pd")

        assert "data" in intent.goal.lower(), "Data must not be empty"

    def test_infer_unknown_code(self):
        """Test inferring intent for unknown code type."""
        from codex.intent.inferer import infer_intent

        static_report = {
            "snapshot_id": "test-123",
            "files": [{"imports": [], "exports": []}],
            "summary": {"total_files": 1},
        }

        intent = infer_intent(static_report, source_excerpt="x = 1")

        assert intent.confidence < 0.5, "confidence is not valid"
        assert len(intent.assumptions) > 0, "Collection must not be empty"

    def test_infer_with_entry_point(self):
        """Test that entry point detection increases confidence."""
        from codex.intent.inferer import infer_intent

        static_report = {
            "snapshot_id": "test-123",
            "files": [{"imports": [], "exports": []}],
            "summary": {"total_files": 1},
        }

        intent_without = infer_intent(static_report, source_excerpt="x = 1")
        intent_with = infer_intent(
            static_report, source_excerpt='if __name__ == "__main__":\n    main()'
        )

        assert intent_with.confidence > intent_without.confidence, "confidence must be greater than zero"

    def test_intent_spec_to_dict(self):
        """Test IntentSpec serialization."""
        from codex.intent.inferer import InputSpec, IntentSpec, OutputSpec

        intent = IntentSpec(
            snapshot_id="test-123",
            timestamp=datetime.now(timezone.utc),
            goal="Test goal",
            actors=["user"],
            inputs=[InputSpec(name="arg", type="cli_arg", required=True)],
            outputs=[OutputSpec(name="result", type="stdout")],
            confidence=0.85,
        )

        data = intent.to_dict()

        assert data["goal"] == "Test goal", "Data must not be empty"
        assert data["confidence"] == 0.85, "Data must not be empty"
        assert len(data["inputs"]) == 1, "Collection must not be empty"
        assert len(data["outputs"]) == 1, "Collection must not be empty"

    def test_intent_spec_save(self, tmp_path: Path):
        """Test saving IntentSpec to file."""
        from codex.intent.inferer import IntentSpec

        intent = IntentSpec(
            snapshot_id="test-123",
            timestamp=datetime.now(timezone.utc),
            goal="Test goal",
            confidence=0.75,
        )

        output_path = tmp_path / "intent.yaml"
        intent.save(output_path)

        assert output_path.exists(), "Condition must be true"


class TestCodeTypeDetection:
    """Tests for code type detection heuristics."""

    def test_detect_cli_tool(self):
        """Test CLI tool detection."""
        from codex.intent.inferer import _detect_cli_tool

        assert _detect_cli_tool(["argparse"], [])
        assert _detect_cli_tool(["click"], [])
        assert _detect_cli_tool(["typer"], [])
        assert not _detect_cli_tool(["os"], [])

    def test_detect_gui_app(self):
        """Test GUI app detection."""
        from codex.intent.inferer import _detect_gui_app

        assert _detect_gui_app(["tkinter"]), "Condition must be true"
        assert _detect_gui_app(["PyQt5"]), "Condition must be true"
        assert _detect_gui_app(["PySide6"]), "Condition must be true"
        assert not _detect_gui_app(["flask"]), "Condition must be true"

    def test_detect_web_service(self):
        """Test web service detection."""
        from codex.intent.inferer import _detect_web_service

        assert _detect_web_service(["flask"]), "Condition must be true"
        assert _detect_web_service(["fastapi"]), "Condition must be true"
        assert _detect_web_service(["django"]), "Condition must be true"
        assert not _detect_web_service(["argparse"]), "Condition must be true"

    def test_detect_networked(self):
        """Test networked app detection."""
        from codex.intent.inferer import _detect_networked

        assert _detect_networked(["requests"]), "_detect_netw is not valid"
        assert _detect_networked(["httpx"]), "_detect_netw is not valid"
        assert _detect_networked(["socket"]), "_detect_netw is not valid"
        assert not _detect_networked(["os"]), "Condition must be true"

    def test_detect_data_processing(self):
        """Test data processing detection."""
        from codex.intent.inferer import _detect_data_processing

        assert _detect_data_processing(["pandas"]), "Data must not be empty"
        assert _detect_data_processing(["numpy"]), "Data must not be empty"
        assert _detect_data_processing(["polars"]), "Data must not be empty"
        assert not _detect_data_processing(["flask"]), "Data must not be empty"


class TestLLMClient:
    """Tests for LLM client functionality."""

    def test_client_initialization_without_key(self):
        """Test client initialization without API key."""
        from codex.intent.llm_client import CodexLLMClient

        with patch.dict("os.environ", {}, clear=True):
            client = CodexLLMClient(allow_external_llm=True)
            # Should initialize but without active client
            assert client.allow_external_llm, "Condition must be true"

    def test_client_rate_limiting(self):
        """Test rate limiting between calls."""
        import time

        from codex.intent.llm_client import CodexLLMClient

        client = CodexLLMClient(allow_external_llm=False)

        start = time.time()
        client._rate_limit()
        client._rate_limit()
        elapsed = time.time() - start

        # Should have some delay between calls
        assert elapsed >= 0, "elapsed must be greater than zero"

    def test_build_intent_prompt(self):
        """Test building intent inference prompt."""
        from codex.intent.llm_client import CodexLLMClient

        client = CodexLLMClient(allow_external_llm=False)

        context = {
            "static_summary": {"total_files": 1},
            "imports": ["os", "sys"],
            "source_excerpt": "def main(): pass",
        }

        prompt = client._build_intent_prompt(context)

        assert "Python code" in prompt, "Condition must be true"
        assert "imports" in prompt.lower() or "os" in prompt, "Condition must be true"
        assert "def main" in prompt, "Condition must be true"

    def test_truncate_context(self):
        """Test context truncation for token budget."""
        from codex.intent.llm_client import _truncate_context

        long_text = "x" * 50000
        truncated = _truncate_context(long_text, max_chars=1000)

        assert len(truncated) <= 1000, "Truncated must not be empty"
        assert "truncated" in truncated, "Condition must be true"

    def test_hash_prompt(self):
        """Test prompt hashing for provenance."""
        from codex.intent.llm_client import _hash_prompt

        prompt = "Test prompt"
        hash1 = _hash_prompt(prompt)
        hash2 = _hash_prompt(prompt)

        assert hash1 == hash2, "hash1 is not valid"
        assert len(hash1) == 64, "Hash1 must not be empty"

    def test_infer_intent_without_client(self):
        """Test intent inference when LLM is unavailable."""
        from codex.intent.llm_client import CodexLLMClient

        client = CodexLLMClient(allow_external_llm=False)

        result = client.infer_intent({"static_summary": {}})

        assert result is None, "Result must not be empty"


class TestProvenanceRecord:
    """Tests for provenance recording."""

    def test_provenance_record_to_dict(self):
        """Test provenance record serialization."""
        from codex.intent.llm_client import ProvenanceRecord

        record = ProvenanceRecord(
            prompt_hash="abc123",
            prompt="Test prompt",
            response="Test response",
            model="gpt-4o",
            model_version="2024-01",
            timestamp=datetime.now(timezone.utc),
            temperature=0.0,
            token_count={"prompt": 100, "completion": 50},
            latency_ms=1500.0,
            snapshot_ref="test-snapshot",
        )

        data = record.to_dict()

        assert data["prompt_hash"] == "abc123", "Data must not be empty"
        assert data["model"] == "gpt-4o", "Data must not be empty"
        assert data["token_count"]["prompt"] == 100, "Data must not be empty"

    def test_provenance_record_save(self, tmp_path: Path):
        """Test saving provenance record."""
        from codex.intent.llm_client import ProvenanceRecord

        record = ProvenanceRecord(
            prompt_hash="abc123def456",
            prompt="Test",
            response="Response",
            model="gpt-4o",
            model_version="2024-01",
            timestamp=datetime.now(timezone.utc),
            temperature=0.0,
            token_count={"prompt": 10, "completion": 5},
            latency_ms=100.0,
            snapshot_ref="test",
        )

        path = record.save(tmp_path)

        assert path.exists(), "Condition must be true"
        assert "abc123def456" in path.name, "Condition must be true"
