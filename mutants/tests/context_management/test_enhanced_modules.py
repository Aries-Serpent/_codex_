"""
Tests for Enhanced Context Management Modules (v2)

Tests for:
- SemanticClusterer
- ContextPriorityQueue
- SlidingWindowManager
- HierarchicalMemory
- ContextCache
"""

import os
import tempfile


class TestSemanticClusterer:
    """Tests for SemanticClusterer."""

    def test_init(self):
        """Test initialization."""
        from context_management.clustering import SemanticClusterer

        clusterer = SemanticClusterer(similarity_threshold=0.85)
        assert clusterer.similarity_threshold == 0.85, "similarity_threshold is not valid"

    def test_add_statement(self):
        """Test adding statements to clusters."""
        from context_management.clustering import SemanticClusterer

        clusterer = SemanticClusterer()

        cluster_id, is_new = clusterer.add_statement("Test statement about coding")
        assert is_new is True, "is_new is not valid"
        assert cluster_id is not None, "cluster_id must be initialized"

    def test_cluster_similar_statements(self):
        """Test clustering similar statements."""
        from context_management.clustering import SemanticClusterer

        clusterer = SemanticClusterer(similarity_threshold=0.5)

        # Add similar statements
        id1, _ = clusterer.add_statement("The quick brown fox jumps")
        _id2, _ = clusterer.add_statement("The quick brown fox leaps")

        # They should be in same cluster due to high similarity
        cluster = clusterer.get_cluster(id1)
        assert cluster is not None, "cluster must be initialized"

    def test_cluster_statements_batch(self):
        """Test batch clustering."""
        from context_management.clustering import SemanticClusterer

        clusterer = SemanticClusterer()

        statements = [
            "Python is a programming language",
            "JavaScript is also a programming language",
            "The weather is nice today",
        ]

        result = clusterer.cluster_statements(statements)
        assert len(result) > 0, "Result must not be empty"

    def test_get_representatives(self):
        """Test getting representative statements."""
        from context_management.clustering import SemanticClusterer

        clusterer = SemanticClusterer(min_cluster_size=1)

        clusterer.add_statement("Test statement one")
        clusterer.add_statement("Test statement two")

        reps = clusterer.get_representative_statements(max_per_cluster=1)
        assert len(reps) > 0, "Reps must not be empty"

    def test_cluster_summary(self):
        """Test cluster summary statistics."""
        from context_management.clustering import SemanticClusterer

        clusterer = SemanticClusterer()

        clusterer.add_statement("Test statement")

        summary = clusterer.get_cluster_summary()
        assert "total_clusters" in summary, "Condition must be true"
        assert summary["total_clusters"] >= 1, "Value must be greater than zero"


class TestContextPriorityQueue:
    """Tests for ContextPriorityQueue."""

    def test_init(self):
        """Test initialization."""
        from context_management.priority_queue import ContextPriorityQueue

        queue = ContextPriorityQueue(max_items=100, max_tokens=10000)
        assert queue.max_items == 100, "Item must not be empty"
        assert queue.max_tokens == 10000, "max_tokens is not valid"

    def test_push_pop(self):
        """Test push and pop operations."""
        from context_management.priority_queue import ContextPriorityQueue, Priority

        queue = ContextPriorityQueue()

        # Push items
        queue.push("High priority content", priority=Priority.HIGH)
        queue.push("Low priority content", priority=Priority.LOW)

        assert queue.size == 2, "size is not valid"

        # Pop lowest priority
        item = queue.pop()
        assert item is not None, "item must be initialized"

    def test_priority_ordering(self):
        """Test priority-based ordering."""
        from context_management.priority_queue import ContextPriorityQueue, Priority

        queue = ContextPriorityQueue()

        queue.push("Critical", priority=Priority.CRITICAL)
        queue.push("Low", priority=Priority.LOW)
        queue.push("Medium", priority=Priority.MEDIUM)

        # Highest priority should be Critical
        highest = queue.peek_highest()
        assert highest is not None, "highest must be initialized"
        assert highest.priority == Priority.CRITICAL, "priority is not valid"

    def test_prune_to_tokens(self):
        """Test token-based pruning."""
        from context_management.priority_queue import ContextPriorityQueue, Priority

        queue = ContextPriorityQueue(max_tokens=100000)

        for i in range(50):
            queue.push(f"Content item {i} " * 100, priority=Priority.MEDIUM)

        initial_tokens = queue.token_count
        # Ensure we're over target before pruning
        assert initial_tokens > 1000, f"Initial tokens {initial_tokens} should be > 1000"

        queue.prune_to_tokens(1000)

        assert queue.token_count <= 1000, "Count must be greater than zero"

    def test_get_stats(self):
        """Test statistics."""
        from context_management.priority_queue import ContextPriorityQueue, Priority

        queue = ContextPriorityQueue()

        queue.push("Test content", priority=Priority.HIGH)

        stats = queue.get_stats()
        assert stats["size"] == 1, "Condition must be true"
        assert "priority_distribution" in stats, "Condition must be true"


class TestSlidingWindowManager:
    """Tests for SlidingWindowManager."""

    def test_init(self):
        """Test initialization."""
        from context_management.sliding_window import SlidingWindowManager

        window = SlidingWindowManager(max_tokens=10000)
        assert window.max_tokens == 10000, "max_tokens is not valid"

    def test_add_content(self):
        """Test adding content to window."""
        from context_management.sliding_window import SlidingWindowManager

        window = SlidingWindowManager()

        success, _warning = window.add("Test content", priority=1)
        assert success is True, "success is not valid"
        assert window.entry_count == 1, "Count must be greater than zero"

    def test_get_window(self):
        """Test getting window contents."""
        from context_management.sliding_window import SlidingWindowManager

        window = SlidingWindowManager()

        window.add("Content 1")
        window.add("Content 2")

        contents = window.get_window()
        assert len(contents) == 2, "Contents must not be empty"

    def test_window_overflow(self):
        """Test window overflow handling."""
        from context_management.sliding_window import (
            SlidingWindowManager,
            WindowStrategy,
        )

        window = SlidingWindowManager(max_tokens=100, strategy=WindowStrategy.DROP_OLDEST)

        # Add content that exceeds capacity
        for i in range(10):
            window.add(f"Content item {i} " * 20)

        assert window.total_tokens <= window.max_tokens, "total_tokens is not valid"

    def test_get_state(self):
        """Test window state."""
        from context_management.sliding_window import SlidingWindowManager

        window = SlidingWindowManager()

        window.add("Test content")

        state = window.get_state()
        assert state.entry_count == 1, "Count must be greater than zero"
        assert state.total_tokens > 0, "total_tokens must be greater than zero"

    def test_prune_to_tokens(self):
        """Test pruning to target tokens."""
        from context_management.sliding_window import SlidingWindowManager

        window = SlidingWindowManager(max_tokens=10000)

        for i in range(10):
            window.add(f"Content {i} " * 50)

        window.prune_to_tokens(1000)
        assert window.total_tokens <= 1000, "total_tokens is not valid"


class TestHierarchicalMemory:
    """Tests for HierarchicalMemory."""

    def test_init(self):
        """Test initialization."""
        from context_management.hierarchical_memory import HierarchicalMemory

        memory = HierarchicalMemory()
        assert memory is not None, "memory must be initialized"

    def test_store_working(self):
        """Test storing in working memory."""
        from context_management.hierarchical_memory import (
            HierarchicalMemory,
            MemoryLayer,
        )

        memory = HierarchicalMemory()

        success, _msg = memory.store("Test content", layer=MemoryLayer.WORKING)
        assert success is True, "success is not valid"

    def test_store_all_layers(self):
        """Test storing in all memory layers."""
        from context_management.hierarchical_memory import (
            HierarchicalMemory,
            MemoryLayer,
        )

        memory = HierarchicalMemory()

        memory.store("Working content", layer=MemoryLayer.WORKING)
        memory.store("Episodic content", layer=MemoryLayer.EPISODIC)
        memory.store("Semantic content", layer=MemoryLayer.SEMANTIC)

        stats = memory.get_stats()
        assert stats["working"].item_count == 1, "Item must not be empty"
        assert stats["episodic"].item_count == 1, "Item must not be empty"
        assert stats["semantic"].item_count == 1, "Item must not be empty"

    def test_retrieve(self):
        """Test retrieval from memory."""
        from context_management.hierarchical_memory import HierarchicalMemory

        memory = HierarchicalMemory()

        memory.store("Important information about Python")

        results = memory.retrieve(query="Python")
        assert len(results) == 1, "Results must not be empty"

    def test_retrieve_by_layer(self):
        """Test retrieval from specific layer."""
        from context_management.hierarchical_memory import (
            HierarchicalMemory,
            MemoryLayer,
        )

        memory = HierarchicalMemory()

        memory.store("Working item", layer=MemoryLayer.WORKING)
        memory.store("Semantic item", layer=MemoryLayer.SEMANTIC)

        results = memory.retrieve(layer=MemoryLayer.WORKING)
        assert all(r.layer == MemoryLayer.WORKING for r in results), "Result must not be empty"

    def test_deduplication(self):
        """Test cross-layer deduplication."""
        from context_management.hierarchical_memory import HierarchicalMemory

        memory = HierarchicalMemory()

        memory.store("Duplicate content")
        success, msg = memory.store("Duplicate content")

        assert success is True, "success is not valid"
        assert "Duplicate" in msg, "Condition must be true"

    def test_get_working_context(self):
        """Test getting working context."""
        from context_management.hierarchical_memory import (
            HierarchicalMemory,
            MemoryLayer,
        )

        memory = HierarchicalMemory()

        memory.store("Context item 1", layer=MemoryLayer.WORKING)
        memory.store("Context item 2", layer=MemoryLayer.WORKING)

        context = memory.get_working_context()
        assert len(context) == 2, "Context must not be empty"

    def test_clear_layer(self):
        """Test clearing a layer."""
        from context_management.hierarchical_memory import (
            HierarchicalMemory,
            MemoryLayer,
        )

        memory = HierarchicalMemory()

        memory.store("Item 1", layer=MemoryLayer.WORKING)
        memory.store("Item 2", layer=MemoryLayer.WORKING)

        memory.clear_layer(MemoryLayer.WORKING)

        stats = memory.get_stats()
        assert stats["working"].item_count == 0, "Item must not be empty"


class TestContextCache:
    """Tests for ContextCache."""

    def test_init(self):
        """Test initialization."""
        from context_management.context_cache import ContextCache

        cache = ContextCache()
        assert cache is not None, "cache must be initialized"

    def test_set_get(self):
        """Test set and get operations."""
        from context_management.context_cache import ContextCache

        cache = ContextCache()

        cache.set("key1", "value1")
        result = cache.get("key1")

        assert result == "value1", "Result must not be empty"

    def test_get_nonexistent(self):
        """Test getting nonexistent key."""
        from context_management.context_cache import ContextCache

        cache = ContextCache()

        result = cache.get("nonexistent")
        assert result is None, "Result must not be empty"

    def test_invalidate(self):
        """Test invalidation."""
        from context_management.context_cache import ContextCache

        cache = ContextCache()

        cache.set("key1", "value1")
        cache.invalidate("key1")

        result = cache.get("key1")
        assert result is None, "Result must not be empty"

    def test_get_or_set(self):
        """Test get_or_set pattern."""
        from context_management.context_cache import ContextCache

        cache = ContextCache()

        # First call should compute
        result1 = cache.get_or_set("key1", lambda: "computed_value")
        assert result1 == "computed_value", "Result must not be empty"

        # Second call should use cache
        call_count = [0]

        def compute():
            call_count[0] += 1
            return "new_value"

        result2 = cache.get_or_set("key1", compute)
        assert result2 == "computed_value", "Result must not be empty"
        assert call_count[0] == 0, "Count must be greater than zero"

    def test_cache_stats(self):
        """Test cache statistics."""
        from context_management.context_cache import ContextCache

        cache = ContextCache()

        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats.hit_count == 1, "Count must be greater than zero"
        assert stats.miss_count == 1, "Count must be greater than zero"

    def test_invalidate_by_tag(self):
        """Test tag-based invalidation."""
        from context_management.context_cache import ContextCache

        cache = ContextCache()

        cache.set("key1", "value1", tags=["group1"])
        cache.set("key2", "value2", tags=["group1"])
        cache.set("key3", "value3", tags=["group2"])

        removed = cache.invalidate_by_tag("group1")

        assert removed == 2, "removed is not valid"
        assert cache.get("key1") is None, "Condition must be true"
        assert cache.get("key2") is None, "Condition must be true"
        assert cache.get("key3") == "value3", "Value must be initialized"

    def test_lru_eviction(self):
        """Test LRU eviction."""
        from context_management.context_cache import ContextCache

        cache = ContextCache(max_entries=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it recently used
        cache.get("key1")

        # Add new entry, should evict least recently used
        cache.set("key4", "value4")

        # key1 should still be there (recently accessed)
        assert cache.get("key1") is not None, "Value must be initialized"

    def test_persistence(self):
        """Test disk persistence."""
        from context_management.context_cache import ContextCache

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            persist_path = f.name

        try:
            # Create and populate cache
            cache1 = ContextCache(persist_path=persist_path)
            cache1.set("key1", "value1")

            # Create new cache from same path
            cache2 = ContextCache(persist_path=persist_path)

            result = cache2.get("key1")
            assert result == "value1", "Result must not be empty"
        finally:
            os.unlink(persist_path)


class TestEnhancedModulesIntegration:
    """Integration tests for enhanced modules."""

    def test_hierarchical_memory_with_cache(self):
        """Test hierarchical memory with context cache."""
        from context_management.context_cache import ContextCache
        from context_management.hierarchical_memory import (
            HierarchicalMemory,
            MemoryLayer,
        )

        memory = HierarchicalMemory()
        cache = ContextCache()

        # Cache static context
        system_prompt = "You are a helpful assistant."
        cache.set("system_prompt", system_prompt)

        # Store dynamic context in memory
        memory.store("User asked about Python", layer=MemoryLayer.WORKING)

        # Retrieve combined context
        cached_prompt = cache.get("system_prompt")
        working_context = memory.get_working_context()

        assert cached_prompt == system_prompt, "cached_prompt is not valid"
        assert len(working_context) > 0, "Working_context must not be empty"

    def test_priority_queue_with_sliding_window(self):
        """Test priority queue with sliding window."""
        from context_management.priority_queue import ContextPriorityQueue, Priority
        from context_management.sliding_window import SlidingWindowManager

        queue = ContextPriorityQueue()
        window = SlidingWindowManager(max_tokens=1000)

        # Add items to queue
        queue.push("High priority error message", priority=Priority.HIGH)
        queue.push("Low priority log", priority=Priority.LOW)
        queue.push("Medium context", priority=Priority.MEDIUM)

        # Transfer high priority items to window
        while queue.size > 0:
            item = queue.pop_highest()
            if item:
                window.add(item.content, priority=item.priority.value)

        assert window.entry_count == 3, "Count must be greater than zero"

    def test_clusterer_with_deduplicator(self):
        """Test semantic clusterer with deduplicator."""
        from context_management.clustering import SemanticClusterer
        from context_management.deduplicator import SemanticDeduplicator

        deduplicator = SemanticDeduplicator()
        clusterer = SemanticClusterer()

        statements = [
            "Python is a programming language",
            "Python is a programming language",  # Exact duplicate
            "JavaScript is also a language",
            "The weather is nice",
        ]

        # First deduplicate
        result = deduplicator.deduplicate(statements)

        # Then cluster unique statements
        clusters = clusterer.cluster_statements(result.unique_statements)

        assert len(result.unique_statements) < len(statements), "Statements must not be empty"
        assert len(clusters) > 0, "Clusters must not be empty"
