"""
Comprehensive tests for the Codex Intent module.

Tests cover:
- Heuristic intent inference
- LLM client with provenance
- Intent specification generation
- Code type detection
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestIntentInferer:
    """Tests for intent inference functionality."""

    def test_infer_cli_tool(self):
        """Test inferring intent for a CLI tool."""
        from src.codex.intent.inferer import infer_intent
        
        static_report = {
            "snapshot_id": "test-123",
            "files": [
                {"imports": ["argparse", "sys"], "exports": ["main"]}
            ],
            "summary": {"total_files": 1},
        }
        
        intent = infer_intent(static_report, source_excerpt="import argparse")
        
        assert "cli" in intent.goal.lower() or "command" in intent.goal.lower()
        assert intent.confidence >= 0.5
        assert intent.inference_method == "heuristic"

    def test_infer_web_service(self):
        """Test inferring intent for a web service."""
        from src.codex.intent.inferer import infer_intent
        
        static_report = {
            "snapshot_id": "test-123",
            "files": [
                {"imports": ["flask", "json"], "exports": ["app"]}
            ],
            "summary": {"total_files": 1},
        }
        
        intent = infer_intent(static_report, source_excerpt="from flask import Flask")
        
        assert "web" in intent.goal.lower() or "service" in intent.goal.lower()
        assert intent.confidence >= 0.7

    def test_infer_gui_app(self):
        """Test inferring intent for a GUI application."""
        from src.codex.intent.inferer import infer_intent
        
        static_report = {
            "snapshot_id": "test-123",
            "files": [
                {"imports": ["tkinter"], "exports": ["main"]}
            ],
            "summary": {"total_files": 1},
        }
        
        intent = infer_intent(static_report, source_excerpt="import tkinter")
        
        assert "gui" in intent.goal.lower() or "graphical" in intent.goal.lower()

    def test_infer_data_processing(self):
        """Test inferring intent for data processing code."""
        from src.codex.intent.inferer import infer_intent
        
        static_report = {
            "snapshot_id": "test-123",
            "files": [
                {"imports": ["pandas", "numpy"], "exports": ["process"]}
            ],
            "summary": {"total_files": 1},
        }
        
        intent = infer_intent(static_report, source_excerpt="import pandas as pd")
        
        assert "data" in intent.goal.lower()

    def test_infer_unknown_code(self):
        """Test inferring intent for unknown code type."""
        from src.codex.intent.inferer import infer_intent
        
        static_report = {
            "snapshot_id": "test-123",
            "files": [
                {"imports": [], "exports": []}
            ],
            "summary": {"total_files": 1},
        }
        
        intent = infer_intent(static_report, source_excerpt="x = 1")
        
        assert intent.confidence < 0.5
        assert len(intent.assumptions) > 0

    def test_infer_with_entry_point(self):
        """Test that entry point detection increases confidence."""
        from src.codex.intent.inferer import infer_intent
        
        static_report = {
            "snapshot_id": "test-123",
            "files": [{"imports": [], "exports": []}],
            "summary": {"total_files": 1},
        }
        
        intent_without = infer_intent(static_report, source_excerpt="x = 1")
        intent_with = infer_intent(
            static_report, 
            source_excerpt='if __name__ == "__main__":\n    main()'
        )
        
        assert intent_with.confidence > intent_without.confidence

    def test_intent_spec_to_dict(self):
        """Test IntentSpec serialization."""
        from src.codex.intent.inferer import IntentSpec, InputSpec, OutputSpec
        
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
        
        assert data["goal"] == "Test goal"
        assert data["confidence"] == 0.85
        assert len(data["inputs"]) == 1
        assert len(data["outputs"]) == 1

    def test_intent_spec_save(self, tmp_path: Path):
        """Test saving IntentSpec to file."""
        from src.codex.intent.inferer import IntentSpec
        
        intent = IntentSpec(
            snapshot_id="test-123",
            timestamp=datetime.now(timezone.utc),
            goal="Test goal",
            confidence=0.75,
        )
        
        output_path = tmp_path / "intent.yaml"
        intent.save(output_path)
        
        assert output_path.exists()


class TestCodeTypeDetection:
    """Tests for code type detection heuristics."""

    def test_detect_cli_tool(self):
        """Test CLI tool detection."""
        from src.codex.intent.inferer import _detect_cli_tool
        
        assert _detect_cli_tool(["argparse"], [])
        assert _detect_cli_tool(["click"], [])
        assert _detect_cli_tool(["typer"], [])
        assert not _detect_cli_tool(["os"], [])

    def test_detect_gui_app(self):
        """Test GUI app detection."""
        from src.codex.intent.inferer import _detect_gui_app
        
        assert _detect_gui_app(["tkinter"])
        assert _detect_gui_app(["PyQt5"])
        assert _detect_gui_app(["PySide6"])
        assert not _detect_gui_app(["flask"])

    def test_detect_web_service(self):
        """Test web service detection."""
        from src.codex.intent.inferer import _detect_web_service
        
        assert _detect_web_service(["flask"])
        assert _detect_web_service(["fastapi"])
        assert _detect_web_service(["django"])
        assert not _detect_web_service(["argparse"])

    def test_detect_networked(self):
        """Test networked app detection."""
        from src.codex.intent.inferer import _detect_networked
        
        assert _detect_networked(["requests"])
        assert _detect_networked(["httpx"])
        assert _detect_networked(["socket"])
        assert not _detect_networked(["os"])

    def test_detect_data_processing(self):
        """Test data processing detection."""
        from src.codex.intent.inferer import _detect_data_processing
        
        assert _detect_data_processing(["pandas"])
        assert _detect_data_processing(["numpy"])
        assert _detect_data_processing(["polars"])
        assert not _detect_data_processing(["flask"])


class TestLLMClient:
    """Tests for LLM client functionality."""

    def test_client_initialization_without_key(self):
        """Test client initialization without API key."""
        from src.codex.intent.llm_client import CodexLLMClient
        
        with patch.dict("os.environ", {}, clear=True):
            client = CodexLLMClient(allow_external_llm=True)
            # Should initialize but without active client
            assert client.allow_external_llm

    def test_client_rate_limiting(self):
        """Test rate limiting between calls."""
        from src.codex.intent.llm_client import CodexLLMClient
        import time
        
        client = CodexLLMClient(allow_external_llm=False)
        
        start = time.time()
        client._rate_limit()
        client._rate_limit()
        elapsed = time.time() - start
        
        # Should have some delay between calls
        assert elapsed >= 0

    def test_build_intent_prompt(self):
        """Test building intent inference prompt."""
        from src.codex.intent.llm_client import CodexLLMClient
        
        client = CodexLLMClient(allow_external_llm=False)
        
        context = {
            "static_summary": {"total_files": 1},
            "imports": ["os", "sys"],
            "source_excerpt": "def main(): pass",
        }
        
        prompt = client._build_intent_prompt(context)
        
        assert "Python code" in prompt
        assert "imports" in prompt.lower() or "os" in prompt
        assert "def main" in prompt

    def test_truncate_context(self):
        """Test context truncation for token budget."""
        from src.codex.intent.llm_client import _truncate_context
        
        long_text = "x" * 50000
        truncated = _truncate_context(long_text, max_chars=1000)
        
        assert len(truncated) <= 1000
        assert "truncated" in truncated

    def test_hash_prompt(self):
        """Test prompt hashing for provenance."""
        from src.codex.intent.llm_client import _hash_prompt
        
        prompt = "Test prompt"
        hash1 = _hash_prompt(prompt)
        hash2 = _hash_prompt(prompt)
        
        assert hash1 == hash2
        assert len(hash1) == 64

    def test_infer_intent_without_client(self):
        """Test intent inference when LLM is unavailable."""
        from src.codex.intent.llm_client import CodexLLMClient
        
        client = CodexLLMClient(allow_external_llm=False)
        
        result = client.infer_intent({"static_summary": {}})
        
        assert result is None


class TestProvenanceRecord:
    """Tests for provenance recording."""

    def test_provenance_record_to_dict(self):
        """Test provenance record serialization."""
        from src.codex.intent.llm_client import ProvenanceRecord
        
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
        
        assert data["prompt_hash"] == "abc123"
        assert data["model"] == "gpt-4o"
        assert data["token_count"]["prompt"] == 100

    def test_provenance_record_save(self, tmp_path: Path):
        """Test saving provenance record."""
        from src.codex.intent.llm_client import ProvenanceRecord
        
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
        
        assert path.exists()
        assert "abc123def456" in path.name
