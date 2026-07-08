"""Tests for AAISScorer."""

from __future__ import annotations

import pytest

from codex.skills.aais import AAISScorer, score_text
from codex.skills.models import AAISScore


@pytest.fixture
def scorer():
    return AAISScorer()


class TestAAISScorerTotal:
    def test_empty_text_returns_zeros(self, scorer):
        result = scorer.score("")
        assert result.total == 0.0, "Result must not be empty"

    def test_whitespace_only_returns_zeros(self, scorer):
        result = scorer.score("   \n  ")
        assert result.total == 0.0, "Result must not be empty"

    def test_total_is_weighted_sum(self, scorer):
        result = scorer.score("Some sample text with structure.")
        expected = round(
            0.25 * result.concision
            + 0.20 * result.acronym_discipline
            + 0.20 * result.structure
            + 0.20 * result.clarity
            + 0.15 * result.citation_lineage,
            4,
        )
        assert result.total == pytest.approx(expected, abs=0.0001)

    def test_total_between_0_and_1(self, scorer):
        samples = [
            "# Title\n\nSome text with bullets:\n- item\n- item\n",
            "plain short text",
            "AAIS (Agent-Aligned Information Score) measures quality.\n\n## Structure\n- bullet",
        ]
        for text in samples:
            result = scorer.score(text)
            assert 0.0 <= result.total <= 1.0, f"Out of range for: {text[:50]}"


class TestConcision:
    def test_reasonable_sentence_length_scores_higher(self, scorer):
        # ~18 words per sentence is ideal
        good = "The system processes requests and returns structured results to the calling agent efficiently."
        short = "Go. Stop. Yes. No. Run."
        good_score = scorer.score(good).concision
        short_score = scorer.score(short).concision
        assert good_score >= short_score, "good_score must be greater than zero"

    def test_very_long_sentences_penalised(self, scorer):
        long_text = (
            "This is an extremely long sentence that goes on and on with many words that make it hard to read and understand and parse and the information density is extremely low because so many words are used to convey very little actual information about the topic at hand."
            * 3
        )
        normal_text = "Use structured data. Define clear interfaces. Apply consistent naming."
        long_score = scorer.score(long_text).concision
        normal_score = scorer.score(normal_text).concision
        assert normal_score >= long_score, "normal_score must be greater than zero"


class TestAcronymDiscipline:
    def test_no_acronyms_returns_perfect_score(self, scorer):
        result = scorer.score("This document describes how the system works.")
        assert result.acronym_discipline == 1.0, "Result must not be empty"

    def test_defined_acronym_scores_higher(self, scorer):
        defined = "The Agent-Aligned Information Score (AAIS) measures quality. AAIS uses five dimensions."
        undefined = "The AAIS measures quality. AAIS uses FIVE DIMS with NO DEF."
        defined_score = scorer.score(defined).acronym_discipline
        undefined_score = scorer.score(undefined).acronym_discipline
        assert defined_score >= undefined_score, "defined_score must be greater than zero"


class TestStructure:
    def test_heading_adds_to_score(self, scorer):
        with_heading = "# Title\n\nSome content here."
        without_heading = "Some content here."
        assert scorer.score(with_heading).structure > scorer.score(without_heading).structure, "structure must be greater than zero"

    def test_bullets_add_to_score(self, scorer):
        with_bullets = "Items:\n- first\n- second\n- third"
        without_bullets = "Items: first, second, third."
        assert scorer.score(with_bullets).structure > scorer.score(without_bullets).structure, "structure must be greater than zero"

    def test_multiple_headings_bonus(self, scorer):
        rich = "# H1\n\nText.\n\n## H2\n\nText.\n\n### H3\n\nText."
        single = "# H1\n\nText."
        assert scorer.score(rich).structure > scorer.score(single).structure, "structure must be greater than zero"

    def test_code_block_adds_to_score(self, scorer):
        with_code = "Example:\n```python\nlogger.info('hello')\n```"
        without_code = "Example: print hello"
        assert scorer.score(with_code).structure > scorer.score(without_code).structure, "structure must be greater than zero"


class TestClarity:
    def test_passive_voice_penalised(self, scorer):
        active = "The system validates all inputs. Execute the handler. Return the result."
        passive = (
            "Inputs are validated by the system. The handler is executed. The result is returned."
        )
        active_score = scorer.score(active).clarity
        passive_score = scorer.score(passive).clarity
        assert active_score >= passive_score, "active_score must be greater than zero"

    def test_hedge_words_penalised(self, scorer):
        hedged = "This might possibly work perhaps. Maybe it could sometimes be useful."
        direct = "This works. It is useful. Use it."
        assert scorer.score(direct).clarity >= scorer.score(hedged).clarity, "clarity must be greater than zero"


class TestCitationLineage:
    def test_all_citation_fields_present(self, scorer):
        text = "doc_id: my_doc  hash: abc123def456  embed_index_ref: indexes/v1  aais_score: 0.9  token_count: 1000"
        result = scorer.score(text)
        assert result.citation_lineage == 1.0, "Result must not be empty"

    def test_no_citation_fields(self, scorer):
        text = "This document has no identifiers whatsoever."
        result = scorer.score(text)
        assert result.citation_lineage == 0.0, "Result must not be empty"

    def test_partial_citation(self, scorer):
        text = "doc_id: my_doc  aais_score: 0.85"
        result = scorer.score(text)
        assert 0.0 < result.citation_lineage < 1.0, "Result must not be empty"


class TestScoreText:
    def test_score_text_convenience_function(self):
        result = score_text("# Title\n\n- bullet\n\ndoc_id: test")
        assert isinstance(result, AAISScore)
        assert result.total >= 0.0, "total must be greater than zero"
