"""Tests for RAG prompt assembly"""

from codex.rag.prompt import (
    PromptConfig,
    PromptTemplate,
    _count_tokens,
    _truncate_to_tokens,
    build_prompt,
)


def test_count_tokens_without_tokenizer():
    """Test token counting with word-based heuristic"""
    text = "This is a test"
    count = _count_tokens(text, tokenizer=None)
    assert count == 4, "Count must be greater than zero"


def test_count_tokens_with_tokenizer():
    """Test token counting with custom tokenizer"""
    text = "This is a test"

    def tokenizer(t):
        return t.split()  # Simple mock tokenizer

    count = _count_tokens(text, tokenizer)
    assert count == 4, "Count must be greater than zero"


def test_count_tokens_empty_text():
    """Test token counting with empty text"""
    count = _count_tokens("", tokenizer=None)
    assert count == 0, "Count must be greater than zero"


def test_count_tokens_single_word():
    """Test token counting with single word"""
    count = _count_tokens("hello", tokenizer=None)
    assert count == 1, "Count must be greater than zero"


def test_truncate_to_tokens_no_truncation():
    """Test truncation when text is within limit"""
    text = "Short text"
    result = _truncate_to_tokens(text, max_tokens=10, tokenizer=None)
    assert result == text, "Result must not be empty"


def test_truncate_to_tokens_with_truncation():
    """Test truncation when text exceeds limit"""
    text = "This is a very long text that should be truncated"
    result = _truncate_to_tokens(text, max_tokens=5, tokenizer=None)
    assert len(result.split()) <= 6, "Collection must not be empty"
    assert "..." in result, "Result must not be empty"


def test_truncate_to_tokens_zero_max():
    """Test truncation with zero max tokens"""
    text = "Some text"
    result = _truncate_to_tokens(text, max_tokens=0, tokenizer=None)
    assert result == "", "Result must not be empty"


def test_truncate_to_tokens_exact_limit():
    """Test truncation at exact token limit"""
    text = "One two three four five"
    result = _truncate_to_tokens(text, max_tokens=5, tokenizer=None)
    assert result == text, "Result must not be empty"


def test_truncate_to_tokens_with_custom_tokenizer():
    """Test truncation with custom tokenizer"""
    text = "This is a test text"

    def tokenizer(t):
        return t.split()

    result = _truncate_to_tokens(text, max_tokens=3, tokenizer=tokenizer)
    # Should be truncated to ~3 tokens
    assert "..." in result or len(result.split()) <= 4, "Collection must not be empty"


class TestPromptConfig:
    """Test PromptConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = PromptConfig()
        assert config.max_context_tokens == 2048, "max_context_tokens is not valid"
        assert config.max_snippet_tokens == 512, "max_snippet_tokens is not valid"
        assert config.include_sources is True, "include_sources is not valid"
        assert config.use_legacy_delimiters is True, "use_legacy_delimiters is not valid"

    def test_custom_config(self):
        """Test custom configuration values"""
        config = PromptConfig(
            max_context_tokens=1024, max_snippet_tokens=256, include_sources=False
        )
        assert config.max_context_tokens == 1024, "max_context_tokens is not valid"
        assert config.max_snippet_tokens == 256, "max_snippet_tokens is not valid"
        assert config.include_sources is False, "include_sources is not valid"


class TestPromptTemplate:
    """Test PromptTemplate class"""

    def test_init_default_config(self):
        """Test initialization with default config"""
        template = PromptTemplate()
        assert template.config is not None, "config must be initialized"
        assert template.config.max_context_tokens == 2048, "max_context_tokens is not valid"

    def test_init_custom_config(self):
        """Test initialization with custom config"""
        config = PromptConfig(max_context_tokens=1024)
        template = PromptTemplate(config=config)
        assert template.config.max_context_tokens == 1024, "max_context_tokens is not valid"

    def test_init_with_tokenizer(self):
        """Test initialization with custom tokenizer"""

        def tokenizer(t):
            return t.split()

        template = PromptTemplate(tokenizer=tokenizer)
        assert template.tokenizer is tokenizer, "tokenizer is not valid"

    def test_format_context_snippet(self):
        """Test context snippet formatting"""
        template = PromptTemplate()
        doc = {"content": "This is a test document.", "metadata": {"source_id": "doc1"}}
        result = template._format_context_snippet(doc, 1)
        assert "Document 1:" in result, "Result must not be empty"
        assert "This is a test document." in result, "Result must not be empty"
        assert "[Source: doc1]" in result, "Result must not be empty"

    def test_format_context_snippet_without_sources(self):
        """Test snippet formatting without source references"""
        config = PromptConfig(include_sources=False)
        template = PromptTemplate(config=config)
        doc = {"content": "Content", "metadata": {"source_id": "doc1"}}
        result = template._format_context_snippet(doc, 1)
        assert "[Source:" not in result, "Result must not be empty"
        assert "Content" in result, "Result must not be empty"

    def test_format_context_snippet_long_content(self):
        """Test snippet formatting with long content (truncation)"""
        config = PromptConfig(max_snippet_tokens=5)
        template = PromptTemplate(config=config)
        doc = {
            "content": "This is a very long document that should be truncated because it exceeds the token limit",
            "metadata": {"source_id": "doc1"},
        }
        result = template._format_context_snippet(doc, 1)
        # Should be truncated
        assert "..." in result or len(result.split()) < 20, "Collection must not be empty"

    def test_format_context_snippet_no_metadata(self):
        """Test snippet formatting without metadata"""
        template = PromptTemplate()
        doc = {"content": "Content only"}
        result = template._format_context_snippet(doc, 1)
        assert "Document 1:" in result, "Result must not be empty"
        assert "Content only" in result, "Result must not be empty"

    def test_build_context_section_empty(self):
        """Test building context section with no documents"""
        template = PromptTemplate()
        result = template._build_context_section([])
        assert result == "", "Result must not be empty"

    def test_build_context_section_with_docs(self):
        """Test building context section with documents"""
        template = PromptTemplate()
        docs = [
            {"content": "Doc 1 content", "metadata": {"source_id": "d1"}},
            {"content": "Doc 2 content", "metadata": {"source_id": "d2"}},
        ]
        result = template._build_context_section(docs)
        assert "RETRIEVED CONTEXT START" in result, "Result must not be empty"
        assert "Document 1:" in result, "Result must not be empty"
        assert "Document 2:" in result, "Result must not be empty"
        assert "RETRIEVED CONTEXT END" in result, "Result must not be empty"

    def test_build_context_section_without_legacy_delimiters(self):
        """Test building context section without legacy delimiters"""
        config = PromptConfig(use_legacy_delimiters=False)
        template = PromptTemplate(config=config)
        docs = [{"content": "Doc content", "metadata": {"source_id": "d1"}}]
        result = template._build_context_section(docs)
        assert config.context_header in result, "Result must include the configured context header"
        assert "RETRIEVED CONTEXT START" not in result, "Result must not be empty"

    def test_build_context_section_token_budget(self):
        """Test context section respects token budget"""
        config = PromptConfig(max_context_tokens=50)
        template = PromptTemplate(config=config)
        # Create many documents
        docs = [
            {"content": f"Document {i} with some content here", "metadata": {"source_id": f"d{i}"}}
            for i in range(20)
        ]
        result = template._build_context_section(docs)
        # Should not include all documents due to budget
        assert "Document 1:" in result, "Result must not be empty"
        # Likely won't have all 20 documents
        assert result.count("Document") < 20, "Result must not be empty"

    def test_assemble_rag_prompt_basic(self):
        """Test basic RAG prompt assembly"""
        template = PromptTemplate()
        query = "What is the answer?"
        docs = [{"content": "Answer is 42", "metadata": {"source_id": "doc1"}}]

        prompt = template.assemble_rag_prompt(query, docs)

        assert "What is the answer?" in prompt, "What is not valid"
        assert "Answer is 42" in prompt, "Answer is not valid"
        assert "USER QUERY START" in prompt, "Condition must be true"

    def test_assemble_rag_prompt_with_system_prompt(self):
        """Test RAG prompt with system prompt"""
        template = PromptTemplate()
        system_prompt = "You are a helpful assistant."
        query = "Test query"
        docs = [{"content": "Content", "metadata": {"source_id": "d1"}}]

        prompt = template.assemble_rag_prompt(query, docs, system_prompt=system_prompt)

        assert "You are a helpful assistant." in prompt, "Condition must be true"
        assert "Test query" in prompt, "Condition must be true"

    def test_assemble_rag_prompt_with_instructions(self):
        """Test RAG prompt with custom instructions"""
        template = PromptTemplate()
        query = "Query"
        docs = [{"content": "Content", "metadata": {"source_id": "d1"}}]
        instructions = "Be concise."

        prompt = template.assemble_rag_prompt(query, docs, instructions=instructions)

        assert "Be concise." in prompt, "Condition must be true"

    def test_assemble_rag_prompt_no_docs(self):
        """Test RAG prompt with no documents"""
        template = PromptTemplate()
        query = "Query without docs"

        prompt = template.assemble_rag_prompt(query, [])

        assert "Query without docs" in prompt, "Condition must be true"
        assert "RETRIEVED CONTEXT START" not in prompt, "Condition must be true"

    def test_assemble_rag_prompt_default_instruction(self):
        """Test RAG prompt includes default instruction"""
        template = PromptTemplate()
        query = "Test query"
        docs = [{"content": "Content", "metadata": {"source_id": "d1"}}]

        prompt = template.assemble_rag_prompt(query, docs)

        assert "Based on the retrieved context" in prompt, "Condition must be true"

    def test_assemble_rag_prompt_no_legacy_delimiters(self):
        """Test RAG prompt without legacy delimiters"""
        config = PromptConfig(use_legacy_delimiters=False)
        template = PromptTemplate(config=config)
        query = "Query"
        docs = [{"content": "Content", "metadata": {"source_id": "d1"}}]

        prompt = template.assemble_rag_prompt(query, docs)

        assert config.prompt_header in prompt, "Prompt must include the configured prompt header"
        assert "USER QUERY START" not in prompt, "Condition must be true"

    def test_assemble_simple_prompt(self):
        """Test simple prompt without RAG"""
        query = "Simple query"
        system_prompt = "System message"

        prompt = PromptTemplate.assemble_simple_prompt(query, system_prompt)

        assert "Simple query" in prompt, "Condition must be true"
        assert "System message" in prompt, "Condition must be true"

    def test_assemble_simple_prompt_no_system(self):
        """Test simple prompt without system message"""
        query = "Just the query"
        prompt = PromptTemplate.assemble_simple_prompt(query)
        assert prompt == "Just the query", "prompt is not valid"

    def test_legacy_class_attributes(self):
        """Test legacy class attributes are available"""
        assert hasattr(PromptTemplate, "CONTEXT_START")
        assert hasattr(PromptTemplate, "CONTEXT_END")
        assert hasattr(PromptTemplate, "QUERY_START")
        assert hasattr(PromptTemplate, "QUERY_END")


def test_build_prompt_with_rag():
    """Test build_prompt convenience function with RAG"""
    query = "Test query"
    docs = [{"content": "Test content", "metadata": {"source_id": "d1"}}]

    prompt = build_prompt(query, retrieved_docs=docs, use_rag=True)

    assert "Test query" in prompt, "Condition must be true"
    assert "Test content" in prompt, "Content must not be empty"


def test_build_prompt_without_rag():
    """Test build_prompt without RAG"""
    query = "Simple query"
    prompt = build_prompt(query, use_rag=False)
    assert query in prompt, "Condition must be true"


def test_build_prompt_with_config():
    """Test build_prompt with custom config"""
    config = PromptConfig(max_snippet_tokens=100)
    query = "Query"
    docs = [{"content": "Content", "metadata": {"source_id": "d1"}}]

    prompt = build_prompt(query, docs, use_rag=True, config=config)
    assert "Query" in prompt, "Condition must be true"


def test_build_prompt_with_system_prompt():
    """Test build_prompt with system prompt"""
    query = "Query"
    system_prompt = "System instructions"
    docs = [{"content": "Content", "metadata": {"source_id": "d1"}}]

    prompt = build_prompt(query, docs, system_prompt=system_prompt, use_rag=True)
    assert "System instructions" in prompt, "Condition must be true"
    assert "Query" in prompt, "Condition must be true"


def test_build_prompt_no_docs_with_rag_false():
    """Test build_prompt without docs when RAG is disabled"""
    query = "Simple query"
    prompt = build_prompt(query, retrieved_docs=None, use_rag=False)
    assert query in prompt, "Condition must be true"


def test_build_prompt_with_tokenizer():
    """Test build_prompt with custom tokenizer"""
    query = "Query"
    docs = [{"content": "Content", "metadata": {"source_id": "d1"}}]

    def tokenizer(t):
        return t.split()

    prompt = build_prompt(query, docs, use_rag=True, tokenizer=tokenizer)
    assert "Query" in prompt, "Condition must be true"


def test_build_prompt_empty_query():
    """Test build_prompt with empty query"""
    prompt = build_prompt("", use_rag=False)
    assert prompt == "", "prompt is not valid"


def test_build_prompt_rag_with_empty_docs():
    """Test build_prompt with RAG but empty docs list"""
    query = "Query"
    prompt = build_prompt(query, retrieved_docs=[], use_rag=True)
    assert "Query" in prompt, "Condition must be true"
    # Should still assemble prompt, just without context section


def test_truncate_to_tokens_with_tokenizer_binary_search():
    """Test truncation uses binary search with custom tokenizer"""
    text = "One two three four five six seven eight nine ten"

    def tokenizer(t):
        return t.split()

    result = _truncate_to_tokens(text, max_tokens=5, tokenizer=tokenizer)
    # Should be truncated to approximately 5 tokens
    tokens = result.replace("...", "").split()
    assert len(tokens) <= 6, "Tokens must not be empty"


def test_format_context_snippet_missing_content():
    """Test snippet formatting when content key is missing"""
    template = PromptTemplate()
    doc = {"metadata": {"source_id": "doc1"}}
    result = template._format_context_snippet(doc, 1)
    assert "Document 1:" in result, "Result must not be empty"
    # Should handle missing content gracefully


def test_build_context_section_single_doc():
    """Test context section with single document"""
    template = PromptTemplate()
    docs = [{"content": "Single doc", "metadata": {"source_id": "d1"}}]
    result = template._build_context_section(docs)
    assert "Document 1:" in result, "Result must not be empty"
    assert "Single doc" in result, "Result must not be empty"


def test_assemble_rag_prompt_all_sections():
    """Test RAG prompt with all sections populated"""
    template = PromptTemplate()
    query = "What is AI?"
    docs = [{"content": "AI is artificial intelligence", "metadata": {"source_id": "wiki"}}]
    system_prompt = "You are an AI expert."
    instructions = "Provide a clear explanation."

    prompt = template.assemble_rag_prompt(
        query=query, retrieved_docs=docs, system_prompt=system_prompt, instructions=instructions
    )

    assert "You are an AI expert." in prompt, "Condition must be true"
    assert "AI is artificial intelligence" in prompt, "AI is not valid"
    assert "Provide a clear explanation." in prompt, "Condition must be true"
    assert "What is AI?" in prompt, "What is not valid"


def test_config_custom_headers():
    """Test custom headers in configuration"""
    config = PromptConfig(
        use_legacy_delimiters=False,
        context_header="## Retrieved Documents",
        instructions_header="## Task",
        prompt_header="## User Question",
    )
    template = PromptTemplate(config=config)
    docs = [{"content": "Content", "metadata": {"source_id": "d1"}}]
    query = "Query"
    instructions = "Instruct"

    prompt = template.assemble_rag_prompt(query, docs, instructions=instructions)

    assert "## Retrieved Documents" in prompt, "Prompt must include the configured context header"
    assert "## Task" in prompt, "Prompt must include the configured instructions header"
    assert "## User Question" in prompt, "Prompt must include the configured prompt header"
