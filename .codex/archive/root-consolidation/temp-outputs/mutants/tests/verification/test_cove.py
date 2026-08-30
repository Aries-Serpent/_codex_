"""Tests for verification components."""

from __future__ import annotations

import pytest


class TestClaimExtractor:
    """Test suite for ClaimExtractor."""

    @pytest.fixture
    def extractor(self):
        """Create a claim extractor for testing."""
        from verification.cove import ClaimExtractor

        return ClaimExtractor()

    def test_extract_empty_text(self, extractor):
        """Test extraction from empty text."""
        claims = extractor.extract_claims("")
        assert claims == [], "claims is not valid"

    def test_extract_none_text(self, extractor):
        """Test extraction from None text."""
        claims = extractor.extract_claims(None)
        assert claims == [], "claims is not valid"

    def test_extract_factual_claim(self, extractor):
        """Test extracting a factual claim."""
        text = "Python was created by Guido van Rossum."
        claims = extractor.extract_claims(text)

        assert len(claims) >= 1, "Claims must not be empty"
        assert any("Python" in c.text for c in claims), "Condition must be true"

    def test_extract_numerical_claim(self, extractor):
        """Test extracting numerical claims."""
        text = "The system processes 100% of requests."
        claims = extractor.extract_claims(text)

        numerical_claims = [c for c in claims if c.claim_type == "numerical"]
        assert len(numerical_claims) >= 1, "Numerical_claims must not be empty"

    def test_claim_ids_are_unique(self, extractor):
        """Test that claim IDs are unique."""
        text = "Python is popular. Java is also popular. Rust is growing."
        claims = extractor.extract_claims(text)

        ids = [c.id for c in claims]
        assert len(ids) == len(set(ids)), "Ids must not be empty"


class TestCoVeEngine:
    """Test suite for CoVeEngine."""

    @pytest.fixture
    def engine(self):
        """Create a CoVe engine for testing."""
        from verification.cove import CoVeEngine

        return CoVeEngine()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_verify_empty_response(self, engine):
        """Test verification of empty response."""
        result = await engine.verify_response("")

        assert result.response_id == "empty", "Response must not be empty"
        assert result.overall_score == 0.0, "Result must not be empty"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_verify_with_context(self, engine):
        """Test verification with supporting context."""
        response = "Python was created by Guido van Rossum in 1991."
        context = ["Python was first released in 1991 by Guido van Rossum."]

        result = await engine.verify_response(response, context)

        assert result.claims is not None, "claims must be initialized"
        assert len(result.verifications) == len(result.claims), "Collection must not be empty"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_stats_tracking(self, engine):
        """Test that stats are tracked."""
        await engine.verify_response("Test response one.")
        await engine.verify_response("Test response two.")

        stats = engine.get_stats()

        assert stats["total_verifications"] == 2, "Condition must be true"
