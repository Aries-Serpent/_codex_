"""
Tests for codex.archive.score module.

This module contains tests for archive scoring functionality.
"""


class TestScoreInput:
    """Tests for ScoreInput dataclass."""

    def test_basic_creation(self):
        """Test ScoreInput basic creation."""
        from codex.archive.score import ScoreInput

        score_input = ScoreInput(
            age_days=100, ref_count=5, coverage=0.75, has_deprecation_tag=False
        )

        assert score_input.age_days == 100, "age_days is not valid"
        assert score_input.ref_count == 5, "Count must be greater than zero"
        assert score_input.coverage == 0.75, "coverage is not valid"
        assert score_input.has_deprecation_tag is False, "has_deprecation_tag is not valid"

    def test_with_deprecation_tag(self):
        """Test ScoreInput with deprecation tag."""
        from codex.archive.score import ScoreInput

        score_input = ScoreInput(age_days=200, ref_count=0, coverage=0.0, has_deprecation_tag=True)

        assert score_input.has_deprecation_tag is True, "has_deprecation_tag is not valid"


class TestArchiveScore:
    """Tests for archive_score function."""

    def test_high_score_all_criteria(self):
        """Test score when all criteria are met."""
        from codex.archive.score import ScoreInput, archive_score

        inp = ScoreInput(
            age_days=200,  # > 180
            ref_count=0,  # no references
            coverage=0.0,  # no coverage
            has_deprecation_tag=True,
        )

        score = archive_score(inp)

        # All weights should contribute: 0.4 + 0.3 + 0.2 + 0.1 = 1.0
        assert score == 1.0, "score is not valid"

    def test_low_score_no_criteria(self):
        """Test score when no criteria are met."""
        from codex.archive.score import ScoreInput, archive_score

        inp = ScoreInput(
            age_days=30,  # < 180
            ref_count=10,  # has references
            coverage=0.9,  # has coverage
            has_deprecation_tag=False,
        )

        score = archive_score(inp)

        assert score == 0.0, "score is not valid"

    def test_partial_score_age_only(self):
        """Test score when only age criteria is met."""
        from codex.archive.score import ScoreInput, archive_score

        inp = ScoreInput(
            age_days=200,  # > 180
            ref_count=5,  # has references
            coverage=0.5,  # has coverage
            has_deprecation_tag=False,
        )

        score = archive_score(inp)

        # Only w1 (0.4) contributes
        assert score == 0.4, "score is not valid"

    def test_partial_score_ref_only(self):
        """Test score when only ref count criteria is met."""
        from codex.archive.score import ScoreInput, archive_score

        inp = ScoreInput(
            age_days=30,  # < 180
            ref_count=0,  # no references
            coverage=0.5,  # has coverage
            has_deprecation_tag=False,
        )

        score = archive_score(inp)

        # Only w2 (0.3) contributes
        assert score == 0.3, "score is not valid"

    def test_custom_weights(self):
        """Test score with custom weights."""
        from codex.archive.score import ScoreInput, archive_score

        inp = ScoreInput(age_days=200, ref_count=0, coverage=0.0, has_deprecation_tag=True)

        # Custom weights that sum to 1
        score = archive_score(inp, w1=0.25, w2=0.25, w3=0.25, w4=0.25)

        assert score == 1.0, "score is not valid"

    def test_custom_tau(self):
        """Test score with custom tau (age threshold)."""
        from codex.archive.score import ScoreInput, archive_score

        inp = ScoreInput(
            age_days=100,  # Below default 180, above custom 90
            ref_count=5,
            coverage=0.5,
            has_deprecation_tag=False,
        )

        # With tau=90, age criteria is met
        score_custom = archive_score(inp, tau=90)
        # With default tau=180, age criteria not met
        score_default = archive_score(inp)

        assert score_custom == 0.4, "score_custom is not valid"
        assert score_default == 0.0, "score_default is not valid"

    def test_score_rounding(self):
        """Test that scores are properly rounded."""
        from codex.archive.score import ScoreInput, archive_score

        inp = ScoreInput(age_days=200, ref_count=0, coverage=0.0, has_deprecation_tag=False)

        # 0.4 + 0.3 + 0.2 = 0.9
        score = archive_score(inp)

        assert score == 0.9, "score is not valid"
        # Should be rounded to 3 decimal places
        assert isinstance(score, float)

    def test_score_clamping(self):
        """Test that scores are clamped between 0 and 1."""
        from codex.archive.score import ScoreInput, archive_score

        inp = ScoreInput(age_days=200, ref_count=0, coverage=0.0, has_deprecation_tag=True)

        # Even with high weights, should be clamped to 1.0
        score = archive_score(inp, w1=2.0, w2=2.0, w3=2.0, w4=2.0)

        assert score == 1.0, "score is not valid"
