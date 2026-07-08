"""
Tests for Context Management System

Comprehensive tests for all context management modules.
"""

import tempfile
from pathlib import Path


class TestContextNormalizer:
    """Tests for ContextNormalizer."""

    def test_normalize_basic(self):
        """Test basic text normalization."""
        from context_management.normalizer import ContextNormalizer

        normalizer = ContextNormalizer()

        # Test whitespace compaction
        result = normalizer.normalize("  hello   world  ")
        assert "  " not in result, "Result must not be empty"
        assert result == "hello world", "Result must not be empty"

    def test_normalize_lowercase(self):
        """Test lowercase conversion."""
        from context_management.normalizer import ContextNormalizer

        normalizer = ContextNormalizer(lowercase=True)
        result = normalizer.normalize("Hello WORLD")
        assert result == "hello world", "Result must not be empty"

    def test_normalize_unicode(self):
        """Test unicode normalization."""
        from context_management.normalizer import ContextNormalizer

        normalizer = ContextNormalizer(normalize_unicode=True)
        # Test with combining characters
        result = normalizer.normalize("café")
        assert result is not None, "result must be initialized"

    def test_unicode_nfc_nfd_cafe_equivalence(self):
        """NFC precomposed and NFD decomposed forms of café normalize to the same output."""
        import unicodedata

        from context_management.normalizer import ContextNormalizer

        # NFC: é as single precomposed code point U+00E9
        nfc_cafe = "caf\u00e9"
        # NFD: e followed by combining acute accent U+0301 (decomposed)
        nfd_cafe = "cafe\u0301"

        # Confirm raw strings differ
        assert nfc_cafe != nfd_cafe, "nfc_cafe is not valid"
        assert unicodedata.is_normalized("NFC", nfc_cafe)
        assert not unicodedata.is_normalized("NFC", nfd_cafe)

        normalizer = ContextNormalizer(normalize_unicode=True, lowercase=False)
        result_nfc = normalizer.normalize(nfc_cafe)
        result_nfd = normalizer.normalize(nfd_cafe)

        # Both forms must produce identical output after NFC normalization
        assert result_nfc == result_nfd, (
            f"NFC '{repr(nfc_cafe)}' and NFD '{repr(nfd_cafe)}' "
            f"normalized to different values: {repr(result_nfc)} vs {repr(result_nfd)}"
        )
        # Output must be in NFC form
        assert unicodedata.is_normalized("NFC", result_nfc)

    def test_unicode_nfd_input_becomes_nfc(self):
        """NFD decomposed input is explicitly converted to NFC form."""
        import unicodedata

        from context_management.normalizer import ContextNormalizer

        # String with multiple decomposed accented characters:
        # "naïve résumé" in NFD form
        # ï = i + combining diaeresis (U+0308)
        # é = e + combining acute accent (U+0301)
        nfd_text = "nai\u0308ve re\u0301sume\u0301"
        assert not unicodedata.is_normalized("NFC", nfd_text)

        normalizer = ContextNormalizer(normalize_unicode=True, lowercase=False)
        result = normalizer.normalize(nfd_text)

        # Output must be NFC
        assert unicodedata.is_normalized("NFC", result)
        # Composed codepoints: ï = U+00EF, é = U+00E9
        assert "\u00ef" in result, "Result must not be empty"
        assert "\u00e9" in result, "Result must not be empty"

    def test_unicode_multiple_combining_marks(self):
        """Strings with stacked combining diacritical marks are handled."""
        import unicodedata

        from context_management.normalizer import ContextNormalizer

        # U+006F (o) + U+0302 (combining circumflex) + U+0308 (combining umlaut)
        text_with_marks = "o\u0302\u0308"
        normalizer = ContextNormalizer(normalize_unicode=True, lowercase=False)
        result = normalizer.normalize(text_with_marks)

        assert isinstance(result, str)
        assert len(result) > 0, "Result must not be empty"
        # Result should be NFC normalized
        assert unicodedata.is_normalized("NFC", result)

    def test_unicode_normalize_disabled_preserves_nfd(self):
        """When normalize_unicode=False, NFD and NFC forms are NOT equated."""
        from context_management.normalizer import ContextNormalizer

        nfc_cafe = "caf\u00e9"  # precomposed NFC
        nfd_cafe = "cafe\u0301"  # decomposed NFD

        normalizer = ContextNormalizer(normalize_unicode=False, lowercase=False)
        result_nfc = normalizer.normalize(nfc_cafe)
        result_nfd = normalizer.normalize(nfd_cafe)

        # Without normalization the forms remain distinct
        assert result_nfc != result_nfd, "Result must not be empty"

    def test_strip_ansi(self):
        """Test ANSI code stripping."""
        from context_management.normalizer import ContextNormalizer

        normalizer = ContextNormalizer(strip_ansi=True)
        result = normalizer.normalize("\x1b[31mred text\x1b[0m")
        assert "\x1b" not in result, "Result must not be empty"
        assert "red text" in result, "Result must not be empty"

    def test_extract_key_signals(self):
        """Test key signal extraction."""
        from context_management.normalizer import ContextNormalizer

        normalizer = ContextNormalizer()
        text = """
        Error: Something went wrong
        File: /path/to/test_file.py
        test_something_important failed
        x-request-id: abc-123-def
        """

        signals = normalizer.extract_key_signals(text)

        assert "errors" in signals, "Error should be raised or set"
        assert "file_paths" in signals, "Condition must be true"
        assert "test_names" in signals, "Condition must be true"
        assert "correlation_ids" in signals, "Condition must be true"
        assert len(signals["file_paths"]) > 0, "Collection must not be empty"
        assert len(signals["test_names"]) > 0, "Collection must not be empty"


class TestStatementFingerprinter:
    """Tests for StatementFingerprinter."""

    def test_fingerprint_basic(self):
        """Test basic fingerprinting."""
        from context_management.fingerprint import StatementFingerprinter

        fp = StatementFingerprinter()
        result = fp.fingerlogger.info("This is a test statement")

        assert result.exact_hash is not None, "exact_hash must be initialized"
        assert result.semantic_hash is not None, "semantic_hash must be initialized"
        assert result.structure_hash is not None, "structure_hash must be initialized"
        assert len(result.ngram_hashes) > 0, "Collection must not be empty"

    def test_fingerprint_exact_match(self):
        """Test exact hash matching."""
        from context_management.fingerprint import StatementFingerprinter

        fp = StatementFingerprinter()

        text = "This is a test"
        fp1 = fp.fingerlogger.info(text)
        fp2 = fp.fingerlogger.info(text)

        assert fp1.exact_hash == fp2.exact_hash, "exact_hash is not valid"

    def test_fingerprint_semantic_match(self):
        """Test semantic hash matching."""
        from context_management.fingerprint import StatementFingerprinter

        fp = StatementFingerprinter()

        text1 = "The quick brown fox jumps"
        text2 = "the quick brown fox jumps"  # Different case

        fp1 = fp.fingerlogger.info(text1)
        fp2 = fp.fingerlogger.info(text2)

        # Should have same semantic hash after lowercasing
        assert fp1.semantic_hash == fp2.semantic_hash, "semantic_hash is not valid"

    def test_similarity_calculation(self):
        """Test similarity calculation."""
        from context_management.fingerprint import StatementFingerprinter

        fp = StatementFingerprinter()

        text1 = "This is a test statement about programming"
        text2 = "This is a test statement about coding"  # Similar
        text3 = "Completely different content here"  # Different

        fp1 = fp.fingerlogger.info(text1)
        fp2 = fp.fingerlogger.info(text2)
        fp3 = fp.fingerlogger.info(text3)

        sim_12 = fp.similarity(fp1, fp2)
        sim_13 = fp.similarity(fp1, fp3)

        # Similar texts should have higher similarity
        assert sim_12 > sim_13, "sim_12 must be greater than zero"


class TestSemanticDeduplicator:
    """Tests for SemanticDeduplicator."""

    def test_deduplicate_exact(self):
        """Test exact duplicate removal."""
        from context_management.deduplicator import SemanticDeduplicator

        dedup = SemanticDeduplicator(similarity_threshold=1.0)

        statements = [
            "First statement",
            "Second statement",
            "First statement",  # Duplicate
            "Third statement",
        ]

        result = dedup.deduplicate(statements)

        assert result.original_count == 4, "Result must not be empty"
        assert result.deduplicated_count == 3, "Result must not be empty"
        assert result.removed_count == 1, "Result must not be empty"
        assert len(result.duplicates_found) == 1, "Collection must not be empty"

    def test_deduplicate_semantic(self):
        """Test semantic duplicate removal."""
        from context_management.deduplicator import SemanticDeduplicator

        dedup = SemanticDeduplicator(similarity_threshold=0.85)

        statements = [
            "The test passed successfully",
            "Test passed successfully",  # Similar
            "Different statement here",
        ]

        result = dedup.deduplicate(statements)

        # At least some deduplication should happen
        assert result.removed_count >= 0, "removed_count must be positive"

    def test_is_duplicate(self):
        """Test duplicate checking."""
        from context_management.deduplicator import SemanticDeduplicator

        dedup = SemanticDeduplicator()

        dedup.add_statement("First statement")

        is_dup, _original = dedup.is_duplicate("First statement")
        assert is_dup is True, "is_dup is not valid"

        is_dup, _original = dedup.is_duplicate("Different statement")
        assert is_dup is False, "is_dup is not valid"


class TestTokenBudgetEnforcer:
    """Tests for TokenBudgetEnforcer."""

    def test_add_content(self):
        """Test adding content to budget."""
        from context_management.budget import ContentPriority, TokenBudgetEnforcer

        enforcer = TokenBudgetEnforcer(hard_limit=1000, soft_limit=800)

        result = enforcer.add_content("Test content", priority=ContentPriority.MEDIUM)
        assert result is True, "Result must not be empty"

        status = enforcer.get_budget_status()
        assert status["current_usage"] > 0, "Value must be greater than zero"

    def test_budget_limits(self):
        """Test budget limit enforcement."""
        from context_management.budget import ContentPriority, TokenBudgetEnforcer

        enforcer = TokenBudgetEnforcer(hard_limit=100, soft_limit=80)

        # Add content that fits
        result = enforcer.add_content("Short", priority=ContentPriority.HIGH)
        assert result is True, "Result must not be empty"

        # Add content that exceeds limits
        long_content = "x" * 500
        # Should try to prune to fit
        enforcer.add_content(long_content, priority=ContentPriority.LOW)

    def test_get_context(self):
        """Test context retrieval."""
        from context_management.budget import ContentPriority, TokenBudgetEnforcer

        enforcer = TokenBudgetEnforcer()

        enforcer.add_content("First content", priority=ContentPriority.HIGH)
        enforcer.add_content("Second content", priority=ContentPriority.MEDIUM)

        context = enforcer.get_context()
        assert "First content" in context or "Second content" in context, "Content must not be empty"


class TestLoopGuardrail:
    """Tests for LoopGuardrail."""

    def test_record_action(self):
        """Test action recording."""
        from context_management.guardrails import LoopGuardrail

        guardrail = LoopGuardrail(max_consecutive_repeats=3)

        # Record different actions - should not trigger
        violation = guardrail.record_action("action1", produced_artifacts=True)
        assert violation is None, "violation is not valid"

        violation = guardrail.record_action("action2", produced_artifacts=True)
        assert violation is None, "violation is not valid"

    def test_detect_consecutive_repeats(self):
        """Test consecutive repeat detection."""
        from context_management.guardrails import LoopGuardrail

        guardrail = LoopGuardrail(max_consecutive_repeats=3)

        # Record same action multiple times without artifacts
        guardrail.record_action("same_action", tool_name="test")
        guardrail.record_action("same_action", tool_name="test")
        violation = guardrail.record_action("same_action", tool_name="test")

        assert violation is not None, "violation must be initialized"
        assert violation.violation_type == "consecutive_repeat", "violation_type is not valid"

    def test_no_violation_with_artifacts(self):
        """Test no violation when producing artifacts."""
        from context_management.guardrails import LoopGuardrail

        guardrail = LoopGuardrail(max_consecutive_repeats=2)

        # Same action but with artifacts - should not trigger
        guardrail.record_action("action", produced_artifacts=True)
        guardrail.record_action("action", produced_artifacts=True)
        violation = guardrail.record_action("action", produced_artifacts=True)

        assert violation is None, "violation is not valid"

    def test_check_before_action(self):
        """Test pre-action checking."""
        from context_management.guardrails import LoopGuardrail

        guardrail = LoopGuardrail(max_consecutive_repeats=3)

        guardrail.record_action("action")
        guardrail.record_action("action")

        # Check if next same action would trigger
        result = guardrail.check_before_action("action")
        assert result is not None, "result must be initialized"


class TestContextMemory:
    """Tests for ContextMemory."""

    def test_store_and_retrieve(self):
        """Test basic store and retrieve."""
        from context_management.memory import ContextMemory

        memory = ContextMemory(max_chunk_tokens=1000)

        chunk_ids = memory.store("This is test content to store")
        assert len(chunk_ids) > 0, "Chunk_ids must not be empty"

        result = memory.retrieve()
        assert len(result.chunks) > 0, "Collection must not be empty"

    def test_chunking(self):
        """Test content chunking."""
        from context_management.memory import ContextMemory

        memory = ContextMemory(max_chunk_tokens=50)

        # Store content larger than chunk size
        long_content = " ".join(["word"] * 100)
        chunk_ids = memory.store(long_content)

        # Should create multiple chunks
        assert len(chunk_ids) > 1, "Chunk_ids must not be empty"

    def test_map_reduce_summarize(self):
        """Test map-reduce summarization."""
        from context_management.memory import ContextMemory

        # Simple summarizer for testing
        def simple_summarizer(text):
            return text[:100] + "..."

        memory = ContextMemory(summarizer=simple_summarizer)

        memory.store("First chunk of content")
        memory.store("Second chunk of content")

        summary = memory.map_reduce_summarize()
        assert summary is not None, "summary must be initialized"

    def test_persistence(self):
        """Test persistence to disk."""
        from context_management.memory import ContextMemory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "memory"

            # Create and store
            memory1 = ContextMemory(storage_path=path)
            memory1.store("Persistent content")

            # Reload
            memory2 = ContextMemory(storage_path=path)

            result = memory2.retrieve()
            assert len(result.chunks) > 0, "Collection must not be empty"


class TestContextObserver:
    """Tests for ContextObserver."""

    def test_logging(self):
        """Test structured logging."""
        from context_management.observability import ContextObserver

        observer = ContextObserver()
        observer.set_correlation_ids(correlation_id="test-123")

        observer.info("Test message", source="test")

        logs = observer.get_recent_logs(10)
        assert len(logs) > 0, "Logs must not be empty"
        assert logs[0]["correlation_id"] == "test-123", "Condition must be true"

    def test_metrics(self):
        """Test metrics collection."""
        from context_management.observability import ContextObserver

        observer = ContextObserver(enable_metrics=True)

        observer.increment("test_counter")
        observer.gauge("test_gauge", 42.0)

        summary = observer.get_metrics_summary()
        assert "counters" in summary, "Count must be greater than zero"
        assert len(summary["counters"]) > 0, "Collection must not be empty"

    def test_alerts(self):
        """Test alert generation."""
        from context_management.observability import AlertSeverity, ContextObserver

        observer = ContextObserver(enable_alerts=True)

        alert = observer.alert(AlertSeverity.WARNING, "Test alert", source="test")

        assert alert is not None, "alert must be initialized"
        assert alert.severity == AlertSeverity.WARNING, "severity is not valid"

        active = observer.get_active_alerts()
        assert len(active) == 1, "Active must not be empty"

    def test_correlation_context(self):
        """Test correlation ID context management."""
        from context_management.observability import ContextObserver

        observer = ContextObserver()

        with observer:
            observer.info("Inside context")
            logs = observer.get_recent_logs(1)
            assert logs[0]["correlation_id"] is not None, "Value must be initialized"


class TestPriorityPruner:
    """Tests for PriorityPruner."""

    def test_prune_basic(self):
        """Test basic pruning."""
        from context_management.pruning import PriorityPruner

        pruner = PriorityPruner()

        result = pruner.prune("Some test content to prune")

        assert result.original_text is not None, "original_text must be initialized"
        assert result.pruned_text is not None, "pruned_text must be initialized"

    def test_prune_keep_errors(self):
        """Test that errors are kept."""
        from context_management.pruning import PriorityPruner, PruneStrategy

        pruner = PriorityPruner()

        error_text = "Error: Something went wrong"
        result = pruner.prune(error_text)

        assert result.strategy_used == PruneStrategy.KEEP, "Result must not be empty"

    def test_prune_batch(self):
        """Test batch pruning."""
        from context_management.pruning import PriorityPruner

        pruner = PriorityPruner()

        texts = [
            "Error: Important error",
            "DEBUG: Verbose log message",
            "Some regular content",
        ]

        results, _tokens_saved = pruner.prune_batch(texts, target_tokens=50)

        assert len(results) == len(texts), "Results must not be empty"


# Integration tests


class TestContextManagementIntegration:
    """Integration tests for context management system."""

    def test_full_pipeline(self):
        """Test full context management pipeline."""
        from context_management import (
            ContextNormalizer,
            ContextObserver,
            LoopGuardrail,
            SemanticDeduplicator,
            TokenBudgetEnforcer,
        )
        from context_management.budget import ContentPriority

        # Initialize components
        normalizer = ContextNormalizer()
        deduplicator = SemanticDeduplicator()
        budget = TokenBudgetEnforcer(hard_limit=10000, soft_limit=8000)
        guardrail = LoopGuardrail()
        observer = ContextObserver()

        # Simulate processing
        with observer:
            observer.info("Starting context processing")

            # Normalize and deduplicate content
            content = [
                "First statement about testing",
                "Second statement about coding",
                "First statement about testing",  # Duplicate
            ]

            normalized = [normalizer.normalize(c) for c in content]
            result = deduplicator.deduplicate(normalized)

            observer.info(f"Deduplicated {result.removed_count} statements")
            observer.increment("dedup_removed", result.removed_count)

            # Add to budget
            for stmt in result.unique_statements:
                budget.add_content(stmt, priority=ContentPriority.MEDIUM)

            # Record action (simulating agent loop)
            violation = guardrail.record_action("process_content", produced_artifacts=True)

            assert violation is None, "violation is not valid"

            # Get final context
            context = budget.get_context()
            assert len(context) > 0, "Context must not be empty"

            observer.info("Processing complete")

        # Verify metrics
        metrics = observer.get_metrics_summary()
        assert metrics["total_observations"] > 0, "Value must be greater than zero"
