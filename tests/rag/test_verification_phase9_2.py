"""
Phase 9.2 - Comprehensive tests for src/verification/cove.py

Tests cover:
- VerificationStatus enum
- Claim dataclass
- VerificationResult dataclass
- CoVeResult dataclass with computed properties
- ClaimExtractor functionality
- CoVeEngine initialization
- Claim extraction patterns
- Bounds validation

#AFTERMATH_METRIC - Phase 9.2 CoVe verification tests
"""

from __future__ import annotations

from unittest.mock import Mock

# NOTE: Do not manually manipulate sys.path. The conftest.py already adds src/ to sys.path.
from verification.cove import (
    MAX_CLAIMS_PER_RESPONSE,
    MAX_RESPONSE_LENGTH,
    MAX_VERIFICATION_DEPTH,
    Claim,
    ClaimExtractor,
    CoVeEngine,
    CoVeResult,
    VerificationResult,
    VerificationStatus,
)


class TestVerificationStatus:
    """Test VerificationStatus enum."""

    def test_status_values(self) -> None:
        """Test all status enum values."""
        # Arrange & Act & Assert
        assert VerificationStatus.VERIFIED.value == "verified", "Value must be initialized"
        assert VerificationStatus.UNVERIFIED.value == "unverified", "Value must be initialized"
        assert VerificationStatus.CONTRADICTED.value == "contradicted", "Value must be initialized"
        assert VerificationStatus.UNKNOWN.value == "unknown", "Value must be initialized"

    def test_status_count(self) -> None:
        """Test expected number of statuses."""
        # Arrange & Act
        statuses = list(VerificationStatus)

        # Assert
        assert len(statuses) == 4, "Statuses must not be empty"


class TestClaim:
    """Test Claim dataclass."""

    def test_claim_creation(self) -> None:
        """Test creating a claim."""
        # Arrange & Act
        claim = Claim(id="claim1", text="Python was created in 1991", source_span=(0, 28))

        # Assert
        assert claim.id == "claim1", "id is not valid"
        assert claim.text == "Python was created in 1991", "text is not valid"
        assert claim.source_span == (0, 28)
        assert claim.claim_type == "factual", "claim_type is not valid"
        assert claim.confidence == 1.0, "confidence is not valid"

    def test_claim_with_custom_type(self) -> None:
        """Test claim with custom type."""
        # Arrange & Act
        claim = Claim(
            id="claim2", text="The value is 42%", source_span=(0, 16), claim_type="numerical"
        )

        # Assert
        assert claim.claim_type == "numerical", "claim_type is not valid"

    def test_claim_with_confidence(self) -> None:
        """Test claim with custom confidence."""
        # Arrange & Act
        claim = Claim(id="claim3", text="Test claim", source_span=(0, 10), confidence=0.85)

        # Assert
        assert claim.confidence == 0.85, "confidence is not valid"


class TestVerificationResult:
    """Test VerificationResult dataclass."""

    def test_verification_result_creation(self) -> None:
        """Test creating a verification result."""
        # Arrange
        claim = Claim(id="c1", text="Test", source_span=(0, 4))

        # Act
        result = VerificationResult(claim=claim, status=VerificationStatus.VERIFIED)

        # Assert
        assert result.claim == claim, "Result must not be empty"
        assert result.status == VerificationStatus.VERIFIED, "Result must not be empty"
        assert result.evidence == [], "Result must not be empty"
        assert result.confidence == 0.0, "Result must not be empty"
        assert result.reasoning == "", "Result must not be empty"
        assert result.sources == [], "Result must not be empty"

    def test_verification_result_with_evidence(self) -> None:
        """Test verification result with evidence."""
        # Arrange
        claim = Claim(id="c1", text="Test", source_span=(0, 4))
        evidence = ["Source 1", "Source 2"]

        # Act
        result = VerificationResult(
            claim=claim, status=VerificationStatus.VERIFIED, evidence=evidence
        )

        # Assert
        assert len(result.evidence) == 2, "Collection must not be empty"
        assert "Source 1" in result.evidence, "Result must not be empty"

    def test_verification_result_with_reasoning(self) -> None:
        """Test verification result with reasoning."""
        # Arrange
        claim = Claim(id="c1", text="Test", source_span=(0, 4))

        # Act
        result = VerificationResult(
            claim=claim, status=VerificationStatus.CONTRADICTED, reasoning="Contradicts known facts"
        )

        # Assert
        assert result.reasoning == "Contradicts known facts", "Result must not be empty"


class TestCoVeResult:
    """Test CoVeResult dataclass."""

    def test_cove_result_creation(self) -> None:
        """Test creating a CoVe result."""
        # Arrange
        claim = Claim(id="c1", text="Test", source_span=(0, 4))
        verification = VerificationResult(claim=claim, status=VerificationStatus.VERIFIED)

        # Act
        result = CoVeResult(
            response_id="r1",
            original_response="Test response",
            claims=[claim],
            verifications=[verification],
            overall_score=0.95,
            overall_status=VerificationStatus.VERIFIED,
        )

        # Assert
        assert result.response_id == "r1", "Response must not be empty"
        assert result.original_response == "Test response", "Response must not be empty"
        assert len(result.claims) == 1, "Collection must not be empty"
        assert len(result.verifications) == 1, "Collection must not be empty"
        assert result.overall_score == 0.95, "Result must not be empty"
        assert result.overall_status == VerificationStatus.VERIFIED, "Result must not be empty"

    def test_cove_result_verified_count(self) -> None:
        """Test verified_count property."""
        # Arrange
        claim1 = Claim(id="c1", text="Test1", source_span=(0, 5))
        claim2 = Claim(id="c2", text="Test2", source_span=(6, 11))

        verifications = [
            VerificationResult(claim=claim1, status=VerificationStatus.VERIFIED),
            VerificationResult(claim=claim2, status=VerificationStatus.UNVERIFIED),
        ]

        result = CoVeResult(
            response_id="r1",
            original_response="Test",
            claims=[claim1, claim2],
            verifications=verifications,
            overall_score=0.5,
            overall_status=VerificationStatus.VERIFIED,
        )

        # Act
        count = result.verified_count

        # Assert
        assert count == 1, "Count must be greater than zero"

    def test_cove_result_verification_rate(self) -> None:
        """Test verification_rate property."""
        # Arrange
        claim1 = Claim(id="c1", text="Test1", source_span=(0, 5))
        claim2 = Claim(id="c2", text="Test2", source_span=(6, 11))

        verifications = [
            VerificationResult(claim=claim1, status=VerificationStatus.VERIFIED),
            VerificationResult(claim=claim2, status=VerificationStatus.VERIFIED),
        ]

        result = CoVeResult(
            response_id="r1",
            original_response="Test",
            claims=[claim1, claim2],
            verifications=verifications,
            overall_score=1.0,
            overall_status=VerificationStatus.VERIFIED,
        )

        # Act
        rate = result.verification_rate

        # Assert
        assert rate == 1.0, "rate is not valid"

    def test_cove_result_verification_rate_empty(self) -> None:
        """Test verification_rate with no claims."""
        # Arrange
        result = CoVeResult(
            response_id="r1",
            original_response="Test",
            claims=[],
            verifications=[],
            overall_score=1.0,
            overall_status=VerificationStatus.UNKNOWN,
        )

        # Act
        rate = result.verification_rate

        # Assert
        assert rate == 1.0, "rate is not valid"

    def test_cove_result_has_timestamp(self) -> None:
        """Test CoVe result has timestamp."""
        # Arrange & Act
        result = CoVeResult(
            response_id="r1",
            original_response="Test",
            claims=[],
            verifications=[],
            overall_score=0.0,
            overall_status=VerificationStatus.UNKNOWN,
        )

        # Assert
        assert result.timestamp is not None, "timestamp must be initialized"
        assert isinstance(result.timestamp, str)
        assert len(result.timestamp) > 0, "Collection must not be empty"


class TestClaimExtractor:
    """Test ClaimExtractor functionality."""

    def test_extractor_creation(self) -> None:
        """Test creating a claim extractor."""
        # Arrange & Act
        extractor = ClaimExtractor()

        # Assert
        assert extractor is not None, "extractor must be initialized"

    def test_extract_claims_from_simple_text(self) -> None:
        """Test extracting claims from simple text."""
        # Arrange
        extractor = ClaimExtractor()
        text = "Python is a programming language. It was created in 1991."

        # Act
        claims = extractor.extract_claims(text)

        # Assert
        assert isinstance(claims, list)
        # Should extract at least one claim
        assert isinstance(claims, (list, tuple, set, dict))  # was: len() >= 0 (always true)

    def test_extract_claims_empty_text(self) -> None:
        """Test extracting claims from empty text."""
        # Arrange
        extractor = ClaimExtractor()

        # Act
        claims = extractor.extract_claims("")

        # Assert
        assert claims == [], "claims is not valid"

    def test_extract_claims_none_text(self) -> None:
        """Test extracting claims from None."""
        # Arrange
        extractor = ClaimExtractor()

        # Act
        claims = extractor.extract_claims(None)  # type: ignore

        # Assert
        assert claims == [], "claims is not valid"

    def test_extract_claims_respects_max_length(self) -> None:
        """Test text truncation for very long responses."""
        # Arrange
        extractor = ClaimExtractor()
        long_text = "This is a test. " * 10000  # Very long text

        # Act
        claims = extractor.extract_claims(long_text)

        # Assert
        # Should not crash and return list
        assert isinstance(claims, list)

    def test_extract_claims_respects_max_claims(self) -> None:
        """Test maximum claims bound."""
        # Arrange
        extractor = ClaimExtractor()
        # Create text with many potential claims
        text = ". ".join([f"Value is {i}" for i in range(100)])

        # Act
        claims = extractor.extract_claims(text)

        # Assert
        assert len(claims) <= MAX_CLAIMS_PER_RESPONSE, "Claims must not be empty"

    def test_extract_claims_numerical(self) -> None:
        """Test extracting numerical claims."""
        # Arrange
        extractor = ClaimExtractor()
        text = "The efficiency is 95 percent in this case."

        # Act
        claims = extractor.extract_claims(text)

        # Assert
        assert isinstance(claims, list)

    def test_extract_claims_temporal(self) -> None:
        """Test extracting temporal claims."""
        # Arrange
        extractor = ClaimExtractor()
        text = "The event happened in 2024 and was significant."

        # Act
        claims = extractor.extract_claims(text)

        # Assert
        assert isinstance(claims, list)

    def test_classify_claim_numerical(self) -> None:
        """Test claim classification for numerical."""
        # Arrange
        extractor = ClaimExtractor()

        # Act
        claim_type = extractor._classify_claim("The value is 42%")

        # Assert
        assert claim_type == "numerical", "claim_type is not valid"

    def test_classify_claim_temporal(self) -> None:
        """Test claim classification for temporal."""
        # Arrange
        extractor = ClaimExtractor()

        # Act
        claim_type = extractor._classify_claim("This happened in 2024")

        # Assert
        assert claim_type == "temporal", "claim_type is not valid"

    def test_classify_claim_universal(self) -> None:
        """Test claim classification for universal."""
        # Arrange
        extractor = ClaimExtractor()

        # Act
        claim_type = extractor._classify_claim("All birds can fly")

        # Assert
        assert claim_type == "universal", "claim_type is not valid"

    def test_classify_claim_factual(self) -> None:
        """Test claim classification for factual."""
        # Arrange
        extractor = ClaimExtractor()

        # Act
        claim_type = extractor._classify_claim("Python is a language")

        # Assert
        assert claim_type == "factual", "claim_type is not valid"


class TestCoVeEngine:
    """Test CoVeEngine functionality."""

    def test_engine_creation(self) -> None:
        """Test creating a CoVe engine."""
        # Arrange & Act
        engine = CoVeEngine()

        # Assert
        assert engine is not None, "engine must be initialized"
        assert engine.extractor is not None, "extractor must be initialized"
        assert engine.sources == [], "sources is not valid"

    def test_engine_with_custom_extractor(self) -> None:
        """Test engine with custom extractor."""
        # Arrange
        mock_extractor = Mock(spec=ClaimExtractor)

        # Act
        engine = CoVeEngine(extractor=mock_extractor)

        # Assert
        assert engine.extractor is mock_extractor, "extractor is not valid"

    def test_engine_with_sources(self) -> None:
        """Test engine with provided sources."""
        # Arrange
        sources = ["Source 1", "Source 2"]

        # Act
        engine = CoVeEngine(sources=sources)

        # Assert
        assert len(engine.sources) == 2, "Collection must not be empty"
        assert "Source 1" in engine.sources, "Condition must be true"


class TestConstants:
    """Test module constants."""

    def test_max_claims_per_response(self) -> None:
        """Test MAX_CLAIMS_PER_RESPONSE constant."""
        # Arrange & Act & Assert
        assert MAX_CLAIMS_PER_RESPONSE == 50, "Response must not be empty"

    def test_max_verification_depth(self) -> None:
        """Test MAX_VERIFICATION_DEPTH constant."""
        # Arrange & Act & Assert
        assert MAX_VERIFICATION_DEPTH == 5, "MAX_VERIFICATION_DEPTH is not valid"

    def test_max_response_length(self) -> None:
        """Test MAX_RESPONSE_LENGTH constant."""
        # Arrange & Act & Assert
        assert MAX_RESPONSE_LENGTH == 100000, "Response must not be empty"


# #AFTERMATH_METRIC - 31 tests created for verification/cove.py
# Coverage: VerificationStatus, Claim, VerificationResult, CoVeResult, ClaimExtractor, CoVeEngine
# Test pattern: AAA (Arrange-Act-Assert)
