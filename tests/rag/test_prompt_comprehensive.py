"""Comprehensive tests for RAG prompt assembly module."""

from codex.rag.prompt import (
    PromptConfig,
    PromptTemplate,
    _count_tokens,
    _truncate_to_tokens,
    build_prompt,
)


class TestTokenHelpers:
    """Test suite for token counting and truncation helpers."""

    def test_count_tokens_no_tokenizer(self):
        """Test counting tokens with heuristic (word count)."""
        text = "This is a test sentence"
        count = _count_tokens(text, tokenizer=None)
        assert count == 5, "Count must be greater than zero"

    def test_count_tokens_with_tokenizer(self):
        """Test counting tokens with custom tokenizer."""

        def tokenizer(text):
            return list(range(10))  # Returns 10 tokens

        count = _count_tokens("any text", tokenizer=tokenizer)
        assert count == 10, "Count must be greater than zero"

    def test_count_tokens_empty_string(self):
        """Test counting tokens in empty string."""
        count = _count_tokens("", tokenizer=None)
        assert count == 0, "Count must be greater than zero"

    def test_truncate_to_tokens_no_truncation_needed(self):
        """Test truncation when text is within limit."""
        text = "Short text"
        result = _truncate_to_tokens(text, max_tokens=10, tokenizer=None)
        assert result == text, "Result must not be empty"

    def test_truncate_to_tokens_truncates_long_text(self):
        """Test truncation of text exceeding token limit."""
        text = "This is a very long sentence that needs truncation"
        result = _truncate_to_tokens(text, max_tokens=5, tokenizer=None)

        # Should truncate to 5 words
        words = result.replace("...", "").split()
        assert len(words) <= 5, "Words must not be empty"

    def test_truncate_to_tokens_zero_max(self):
        """Test truncation with zero max tokens returns empty."""
        text = "Some text"
        result = _truncate_to_tokens(text, max_tokens=0, tokenizer=None)
        assert result == "", "Result must not be empty"

    def test_truncate_to_tokens_negative_max(self):
        """Test truncation with negative max tokens returns empty."""
        text = "Some text"
        result = _truncate_to_tokens(text, max_tokens=-5, tokenizer=None)
        assert result == "", "Result must not be empty"

    def test_truncate_to_tokens_with_tokenizer(self):
        """Test truncation using custom tokenizer."""

        def tokenizer(text):
            return list(range(len(text.split())))

        text = "One two three four five"

        result = _truncate_to_tokens(text, max_tokens=3, tokenizer=tokenizer)
        # Should be truncated
        assert len(result) < len(text), "Result must not be empty"


class TestPromptConfig:
    """Test suite for PromptConfig dataclass."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = PromptConfig()

        assert config.max_context_tokens == 2048, "max_context_tokens is not valid"
        assert config.max_snippet_tokens == 512, "max_snippet_tokens is not valid"
        assert config.include_sources is True, "include_sources is not valid"
        assert config.use_legacy_delimiters is True, "use_legacy_delimiters is not valid"

    def test_config_custom_values(self):
        """Test configuration with custom values."""
        config = PromptConfig(
            max_context_tokens=4000,
            max_snippet_tokens=1000,
            include_sources=False,
            use_legacy_delimiters=False,
        )

        assert config.max_context_tokens == 4000, "max_context_tokens is not valid"
        assert config.max_snippet_tokens == 1000, "max_snippet_tokens is not valid"
        assert config.include_sources is False, "include_sources is not valid"
        assert config.use_legacy_delimiters is False, "use_legacy_delimiters is not valid"


class TestPromptTemplate:
    """Test suite for PromptTemplate class."""

    def test_template_initialization_defaults(self):
        """Test template initialization with defaults."""
        template = PromptTemplate()

        assert template.config is not None, "config must be initialized"
        assert template.tokenizer is None, "tokenizer is not valid"

    def test_template_initialization_custom(self):
        """Test template initialization with custom config."""
        config = PromptConfig(max_context_tokens=1000)

        def tokenizer(x):
            return [1, 2, 3]

        template = PromptTemplate(config=config, tokenizer=tokenizer)

        assert template.config.max_context_tokens == 1000, "max_context_tokens is not valid"
        assert template.tokenizer is tokenizer, "tokenizer is not valid"

    def test_assemble_rag_prompt_basic(self):
        """Test assembling basic RAG prompt."""
        template = PromptTemplate()
        retrieved_docs = [
            {"content": "Python is a programming language", "metadata": {"source_id": "intro.md"}}
        ]

        prompt = template.assemble_rag_prompt(
            query="What is Python?", retrieved_docs=retrieved_docs
        )

        assert "What is Python?" in prompt, "What is not valid"
        assert "Python is a programming language" in prompt, "Python is not valid"

    def test_assemble_rag_prompt_with_system(self):
        """Test RAG prompt with system prompt."""
        template = PromptTemplate()

        prompt = template.assemble_rag_prompt(
            query="Test", system_prompt="You are a helpful assistant.", retrieved_docs=[]
        )

        assert "You are a helpful assistant" in prompt, "Condition must be true"
        assert "Test" in prompt, "Condition must be true"

    def test_assemble_rag_prompt_empty_docs(self):
        """Test RAG prompt with no documents."""
        template = PromptTemplate()

        prompt = template.assemble_rag_prompt(query="Test query", retrieved_docs=[])

        assert "Test query" in prompt, "Condition must be true"

    def test_assemble_simple_prompt(self):
        """Test assembling simple (non-RAG) prompt."""
        prompt = PromptTemplate.assemble_simple_prompt(
            query="What is 2+2?", system_prompt="You are a math tutor."
        )

        assert "What is 2+2?" in prompt, "What is not valid"
        assert "You are a math tutor" in prompt, "Condition must be true"


class TestBuildPromptFunction:
    """Test suite for build_prompt convenience function."""

    def test_build_prompt_basic(self):
        """Test basic prompt building."""
        retrieved_docs = [
            {"content": "Context 1", "metadata": {"source_id": "file1.py"}},
            {"content": "Context 2", "metadata": {"source_id": "file2.py"}},
        ]

        prompt = build_prompt(query="What is RAG?", retrieved_docs=retrieved_docs)

        assert "What is RAG?" in prompt, "What is not valid"
        assert "Context 1" in prompt or "Document 1" in prompt, "Condition must be true"

    def test_build_prompt_with_system(self):
        """Test prompt with system prompt."""
        prompt = build_prompt(
            query="Test", system_prompt="You are an AI assistant.", retrieved_docs=[]
        )

        assert "You are an AI assistant" in prompt, "Condition must be true"
        assert "Test" in prompt, "Condition must be true"

    def test_build_prompt_without_rag(self):
        """Test simple prompt without RAG."""
        prompt = build_prompt(query="Simple question", use_rag=False)

        assert "Simple question" in prompt, "Condition must be true"

    def test_build_prompt_with_config(self):
        """Test prompt with custom configuration."""
        config = PromptConfig(max_context_tokens=100)

        prompt = build_prompt(query="Query", retrieved_docs=[], config=config)

        assert prompt is not None, "prompt must be initialized"

    def test_build_prompt_no_docs(self):
        """Test prompt building with no documents."""
        prompt = build_prompt(query="Test query", retrieved_docs=None)

        assert "Test query" in prompt, "Condition must be true"


class TestPromptBackwardCompatibility:
    """Test suite for backward compatibility features."""

    def test_legacy_delimiters_present(self):
        """Test that legacy safety delimiters are defined."""
        from codex.rag.prompt import (
            CONTEXT_END,
            CONTEXT_START,
            QUERY_END,
            QUERY_START,
        )

        assert CONTEXT_START is not None, "CONTEXT_START must be initialized"
        assert CONTEXT_END is not None, "CONTEXT_END must be initialized"
        assert QUERY_START is not None, "QUERY_START must be initialized"
        assert QUERY_END is not None, "QUERY_END must be initialized"

    def test_legacy_format_compatibility(self):
        """Test that prompts can use legacy format if needed."""
        # This tests that old delimiter constants still exist
        from codex.rag.prompt import CONTEXT_END, CONTEXT_START

        # Basic check that they can be used in string formatting
        prompt = f"{CONTEXT_START}\nContent\n{CONTEXT_END}"
        assert "CONTEXT START" in prompt, "Condition must be true"
        assert "CONTEXT END" in prompt, "Condition must be true"
