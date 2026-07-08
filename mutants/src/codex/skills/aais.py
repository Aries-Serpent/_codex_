"""AAIS (Agent-Aligned Information Score) rubric and scorer.

from codex.logging.structured_logger import logger
Evaluates the quality of documentation or skill content on a 0–1 scale
across five weighted dimensions:

+---------------------+--------+----------------------------------------+
| Dimension           | Weight | Description                            |
+=====================+========+========================================+
| Concision           |  0.25  | Token/idea density; minimal redundancy |
| Acronym Discipline  |  0.20  | Defined once, reused consistently      |
| Structure           |  0.20  | Headings, bullets, schemas present     |
| Clarity             |  0.20  | Imperative/active voice; unambiguous   |
| Citation/Lineage    |  0.15  | doc_id / hash / embed_ref recorded     |
+---------------------+--------+----------------------------------------+

Formula: ``score = 0.25*C + 0.20*A + 0.20*S + 0.20*Cl + 0.15*L``

Usage::

    from codex.skills.aais import AAISScorer

    scorer = AAISScorer()
    result = scorer.score(text)
    logger.info(result.total)
    logger.info(result.concision)
"""

from __future__ import annotations

import math
import re
from collections import Counter

from .models import AAISScore

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

_RE_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_RE_BULLET = re.compile(r"^[\-\*\+]\s+\S|\d+\.\s+\S", re.MULTILINE)
_RE_CODE_BLOCK = re.compile(r"```[\s\S]*?```|`[^`]+`")
_RE_PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+ed\b", re.IGNORECASE)
_RE_ACRONYM = re.compile(r"\b([A-Z]{2,})\b")


class AAISScorer:
    """Compute AAIS scores for text content.

    All scoring heuristics are entirely text-based and require no external
    models or network calls.
    """

    # Weights (must sum to 1.0)
    _W_CONCISION = 0.25
    _W_ACRONYM = 0.20
    _W_STRUCTURE = 0.20
    _W_CLARITY = 0.20
    _W_CITATION = 0.15

    # Target words-per-sentence for "ideal concision" (Gunning-Fog inspired)
    _IDEAL_WORDS_PER_SENTENCE = 18.0

    def score(self, text: str) -> AAISScore:
        """Score *text* and return an :class:`~codex.skills.models.AAISScore`.

        Parameters
        ----------
        text:
            Raw document or skill content (Markdown/plain text supported).
        """
        if not text or not text.strip():
            return AAISScore(
                concision=0.0,
                acronym_discipline=0.0,
                structure=0.0,
                clarity=0.0,
                citation_lineage=0.0,
            )

        return AAISScore(
            concision=self._score_concision(text),
            acronym_discipline=self._score_acronym(text),
            structure=self._score_structure(text),
            clarity=self._score_clarity(text),
            citation_lineage=self._score_citation(text),
        )

    # ------------------------------------------------------------------
    # Dimension scorers
    # ------------------------------------------------------------------

    def _score_concision(self, text: str) -> float:
        """Measure token/idea density.

        Heuristic:
        1. Split into sentences; compute mean words/sentence.
        2. Score peaks at _IDEAL_WORDS_PER_SENTENCE; penalise for
           very short (< 5 words) or very long (> 40 words) sentences.
        3. Bonus for high type/token ratio (vocabulary richness).
        """
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", text) if s.strip()]
        if not sentences:
            return 0.5

        word_counts = [len(re.findall(r"\w+", s)) for s in sentences]
        valid = [w for w in word_counts if w > 0]
        if not valid:
            return 0.5

        mean_wps = sum(valid) / len(valid)
        # Gaussian-style score centred on ideal
        ideal = self._IDEAL_WORDS_PER_SENTENCE
        sigma = 12.0
        wps_score = math.exp(-((mean_wps - ideal) ** 2) / (2 * sigma**2))

        # Type/token ratio (vocabulary diversity)
        words = re.findall(r"\w+", text.lower())
        ttr = len(set(words)) / len(words) if words else 0.5
        # Normalise TTR: typically 0.3–0.8 for natural text; map [0.3, 0.8] → [0, 1]
        ttr_score = max(0.0, min(1.0, (ttr - 0.2) / 0.5))

        return round(0.6 * wps_score + 0.4 * ttr_score, 4)

    def _score_acronym(self, text: str) -> float:
        """Score acronym discipline: defined-once, reused consistently.

        Strategy:
        - Find all UPPERCASE sequences ≥ 2 chars.
        - Check how many appear to be defined (followed or preceded by
          '(' or ')' or a colon on first occurrence).
        - Penalise drift: acronym appearing many times without definition.
        """
        acronyms = _RE_ACRONYM.findall(text)
        if not acronyms:
            return 1.0  # No acronyms = perfect discipline

        freq: Counter[str] = Counter(acronyms)
        # Look for definition patterns: "ACRONYM (definition)" or "(definition) ACRONYM"
        defined_pattern = re.compile(r"\b([A-Z]{2,})\b\s*[\(\-:]|[\(\-:]\s*\b([A-Z]{2,})\b")
        defined = set()
        for match in defined_pattern.finditer(text):
            grp = match.group(1) or match.group(2)
            if grp:
                defined.add(grp)

        total_unique = len(freq)
        defined_count = sum(1 for a in freq if a in defined)
        defined_ratio = defined_count / total_unique if total_unique else 1.0

        # Penalise high-frequency undeclared acronyms
        undefined_high_freq = sum(
            cnt for acr, cnt in freq.items() if acr not in defined and cnt >= 3
        )
        word_count = len(re.findall(r"\w+", text))
        penalty = min(1.0, undefined_high_freq / max(word_count, 1) * 5)

        score = max(0.0, defined_ratio - penalty)
        return round(min(1.0, score), 4)

    def _score_structure(self, text: str) -> float:
        """Score structural richness: headings, bullets, code blocks, schemas.

        Each structural element type adds to the score:
        - headings present: +0.30
        - bullets present: +0.30
        - code/schema blocks present: +0.20
        - multiple sections (≥ 3 headings): +0.20
        """
        score = 0.0
        headings = _RE_HEADING.findall(text)
        bullets = _RE_BULLET.findall(text)
        code_blocks = _RE_CODE_BLOCK.findall(text)

        if headings:
            score += 0.30
        if bullets:
            score += 0.30
        if code_blocks:
            score += 0.20
        if len(headings) >= 3:
            score += 0.20

        return round(min(1.0, score), 4)

    def _score_clarity(self, text: str) -> float:
        """Score clarity: imperative/active voice, low ambiguity.

        Heuristics:
        - Low passive-voice density: penalise passive constructions.
        - Imperative sentence ratio: sentences starting with verbs.
        - Penalise vague hedging words (maybe, possibly, perhaps, etc.).
        """
        words_all = re.findall(r"\w+", text)
        total_words = len(words_all)
        if total_words == 0:
            return 0.5

        # Passive voice penalty
        passive_matches = len(_RE_PASSIVE.findall(text))
        passive_density = passive_matches / total_words
        passive_score = max(0.0, 1.0 - passive_density * 20)

        # Hedging words penalty
        _HEDGE_WORDS = {
            "maybe",
            "perhaps",
            "possibly",
            "might",
            "could",
            "should",
            "somewhat",
            "generally",
            "typically",
            "usually",
            "often",
        }
        hedge_count = sum(1 for w in words_all if w.lower() in _HEDGE_WORDS)
        hedge_density = hedge_count / total_words
        hedge_score = max(0.0, 1.0 - hedge_density * 30)

        # Sentence length variance (high variance = unclear structure)
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", text) if s.strip()]
        if len(sentences) > 1:
            lens = [len(re.findall(r"\w+", s)) for s in sentences]
            mean_len = sum(lens) / len(lens)
            variance = sum((n - mean_len) ** 2 for n in lens) / len(lens)
            # Normalise: variance < 25 is ideal (std ≈ 5), penalise > 100
            variance_score = max(0.0, 1.0 - variance / 200)
        else:
            variance_score = 0.8

        return round((passive_score + hedge_score + variance_score) / 3, 4)

    def _score_citation(self, text: str) -> float:
        """Score presence of citation/lineage fields.

        Checks for: doc_id, hash, embed_index_ref, aais_score, token_count.
        Each distinct citation type found contributes to the score.
        """
        citation_types = [
            r"doc[_\-]?id",
            r"sha[_\-]?256|hash[:\s]+[0-9a-f]{6,}",
            r"embed[_\-]index[_\-]?ref",
            r"aais[_\-]?score",
            r"token[_\-]?count",
        ]
        found = sum(1 for pattern in citation_types if re.search(pattern, text, re.IGNORECASE))
        return round(min(1.0, found / len(citation_types)), 4)


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def score_text(text: str) -> AAISScore:
    """Score *text* using the default :class:`AAISScorer`.

    Returns an :class:`~codex.skills.models.AAISScore` with a ``.total``
    property for the weighted aggregate.
    """
    return AAISScorer().score(text)


__all__ = ["AAISScore", "AAISScorer", "score_text"]
