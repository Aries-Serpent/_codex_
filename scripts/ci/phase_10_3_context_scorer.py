#!/usr/bin/env python3
"""
Phase 10.3: Context Injection & OODA Loop Enhancement
Context Relevance Scoring Engine

Scores LTM patterns by relevance to current session metadata:
- TF-IDF domain matching
- Recency weighting (time decay)
- Success rate (patterns that led to successful outcomes)
- Execution count (popularity)
- Agent-specific applicability

Usage:
  python3 scripts/ci/phase_10_3_context_scorer.py \
    --session-metadata path/to/metadata.json \
    --patterns path/to/patterns.yaml \
    --ltm-db path/to/ltm.db \
    --output path/to/scores.json \
    --top-k 15 \
    --min-score 0.65
"""

import argparse
import json
import logging
import math
import os
import sqlite3
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(".codex/phase_10_3_context_scorer.log"),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ScoredPattern:
    """Pattern with relevance score and metadata."""

    pattern_id: str
    name: str
    score: float
    recency_score: float
    domain_score: float
    success_score: float
    popularity_score: float
    applicability_score: float
    last_seen: str
    success_rate: float
    execution_count: int
    agent_types: List[str]
    improvement_area: str
    description: str


class TFIDFScorer:
    """TF-IDF based domain relevance scoring."""

    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.document_frequencies: Dict[str, int] = {}
        self.num_documents = 0

    def build_vocab(self, documents: List[str]) -> None:
        """Build vocabulary from documents."""
        self.num_documents = len(documents)

        for doc in documents:
            terms = self._tokenize(doc)
            seen = set()
            for term in terms:
                if term not in self.vocabulary:
                    self.vocabulary[term] = len(self.vocabulary)
                if term not in seen:
                    self.document_frequencies[term] = (
                        self.document_frequencies.get(term, 0) + 1
                    )
                    seen.add(term)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r"\w+", text)
        return [t for t in tokens if len(t) > 2]  # Filter short tokens

    def score_similarity(self, query: str, target: str) -> float:
        """Score similarity between query and target documents."""
        if not self.vocabulary:
            return 0.0

        query_terms = self._tokenize(query)
        target_terms = self._tokenize(target)

        if not query_terms or not target_terms:
            return 0.0

        # Calculate TF-IDF vectors
        query_tfidf = self._calculate_tfidf(query_terms)
        target_tfidf = self._calculate_tfidf(target_terms)

        # Calculate cosine similarity
        dot_product = sum(
            query_tfidf.get(term, 0) * target_tfidf.get(term, 0)
            for term in query_tfidf.keys()
        )

        query_magnitude = math.sqrt(sum(v**2 for v in query_tfidf.values()))
        target_magnitude = math.sqrt(sum(v**2 for v in target_tfidf.values()))

        if query_magnitude == 0 or target_magnitude == 0:
            return 0.0

        return dot_product / (query_magnitude * target_magnitude)

    def _calculate_tfidf(self, terms: List[str]) -> Dict[str, float]:
        """Calculate TF-IDF scores for terms."""
        tfidf = {}
        term_count = Counter(terms)

        for term, count in term_count.items():
            if term not in self.vocabulary:
                continue

            # TF: term frequency
            tf = count / len(terms)

            # IDF: inverse document frequency
            if term in self.document_frequencies:
                idf = math.log(
                    self.num_documents / (1 + self.document_frequencies[term])
                )
            else:
                idf = 0

            tfidf[term] = tf * idf

        return tfidf


class ContextScorer:
    """Main context scoring engine for pattern relevance."""

    def __init__(
        self,
        ltm_db_path: Optional[str] = None,
        pattern_file: Optional[str] = None,
    ):
        """Initialize scorer with LTM database and pattern file paths."""
        self.ltm_db_path = ltm_db_path or os.environ.get(
            "CODEX_LTM_DB_PATH", ".codex/ltm.db"
        )
        self.pattern_file = pattern_file or ".codex/patterns/ci_failure_patterns.yaml"
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.ltm_entries: List[Dict[str, Any]] = []
        self.tfidf = TFIDFScorer()
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load patterns from YAML file."""
        try:
            import yaml

            if Path(self.pattern_file).exists():
                with open(self.pattern_file, "r") as f:
                    patterns = yaml.safe_load(f) or {}
                    self.patterns = patterns.get("patterns", {})
                    logger.info(f"Loaded {len(self.patterns)} patterns from file")
            else:
                logger.warning(f"Pattern file not found: {self.pattern_file}")
        except ImportError:
            logger.warning("PyYAML not available, using empty patterns")
        except Exception as e:
            logger.warning(f"Error loading patterns: {e}")

    def _load_ltm_entries(self) -> None:
        """Load LTM entries from SQLite database."""
        if not Path(self.ltm_db_path).exists():
            logger.warning(f"LTM database not found: {self.ltm_db_path}")
            return

        try:
            conn = sqlite3.connect(self.ltm_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Try to load from ltm_entries table
            try:
                cursor.execute(
                    """
                    SELECT * FROM ltm_entries
                    WHERE timestamp > datetime('now', '-90 days')
                    ORDER BY timestamp DESC
                    LIMIT 500
                """
                )
                self.ltm_entries = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Loaded {len(self.ltm_entries)} LTM entries")
            except sqlite3.OperationalError:
                logger.info("ltm_entries table not found, using empty list")

            conn.close()
        except Exception as e:
            logger.warning(f"Error loading LTM entries: {e}")

    def score_pattern(
        self,
        pattern: Dict[str, Any],
        session_metadata: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """Score a single pattern against session metadata."""
        if weights is None:
            weights = {
                "domain": 0.30,
                "recency": 0.25,
                "success": 0.20,
                "popularity": 0.15,
                "applicability": 0.10,
            }

        scores = {
            "domain": self._compute_domain_score(pattern, session_metadata),
            "recency": self._compute_recency_score(pattern),
            "success": self._compute_success_score(pattern),
            "popularity": self._compute_popularity_score(pattern),
            "applicability": self._compute_applicability_score(
                pattern, session_metadata
            ),
        }

        # Weighted sum
        total_score = sum(scores[k] * weights[k] for k in weights.keys())

        return total_score

    def _compute_domain_score(
        self, pattern: Dict[str, Any], session_metadata: Dict[str, Any]
    ) -> float:
        """Compute domain relevance score (0-1) using TF-IDF."""
        if not session_metadata:
            return 0.5

        # Extract task description or domain keywords
        task_description = session_metadata.get("task_description", "")
        task_domain = session_metadata.get("domain", "")
        query = f"{task_description} {task_domain}".strip()

        if not query:
            return 0.5

        # Pattern description
        pattern_desc = pattern.get("description", "")
        pattern_name = pattern.get("name", "")
        target = f"{pattern_name} {pattern_desc}".strip()

        if not target:
            return 0.5

        # Calculate similarity
        return max(0.0, min(1.0, self.tfidf.score_similarity(query, target)))

    def _compute_recency_score(self, pattern: Dict[str, Any]) -> float:
        """Compute recency score with time decay (0-1)."""
        last_seen = pattern.get("last_seen")
        if not last_seen:
            return 0.5

        try:
            last_seen_dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
            now = datetime.now(last_seen_dt.tzinfo)
            age_days = (now - last_seen_dt).days

            # Exponential decay: score halves every 30 days
            decay_rate = 0.5 ** (age_days / 30.0)
            return max(0.1, min(1.0, decay_rate))
        except (ValueError, AttributeError):
            return 0.5

    def _compute_success_score(self, pattern: Dict[str, Any]) -> float:
        """Compute success rate score (0-1)."""
        success_rate = pattern.get("success_rate", 0.5)
        # Normalize to 0-1 range (assuming success_rate is 0-100)
        if success_rate > 1:
            success_rate = success_rate / 100.0
        return max(0.0, min(1.0, success_rate))

    def _compute_popularity_score(self, pattern: Dict[str, Any]) -> float:
        """Compute popularity score based on execution count."""
        execution_count = pattern.get("execution_count", 0)
        # Log scale: normalize to 0-1
        # Assume 100+ executions is max popularity
        if execution_count == 0:
            return 0.1
        popularity = min(1.0, math.log10(execution_count + 1) / 2.0)
        return max(0.0, popularity)

    def _compute_applicability_score(
        self, pattern: Dict[str, Any], session_metadata: Dict[str, Any]
    ) -> float:
        """Compute agent/context applicability score."""
        pattern_agents = pattern.get("agent_types", [])
        session_agents = session_metadata.get("agent_types", [])

        if not pattern_agents or not session_agents:
            return 0.5

        # Calculate overlap
        overlap = len(set(pattern_agents) & set(session_agents))
        max_overlap = max(len(pattern_agents), len(session_agents))

        if max_overlap == 0:
            return 0.5

        return overlap / max_overlap

    def score_patterns(
        self,
        session_metadata: Dict[str, Any],
        patterns: Optional[List[Dict[str, Any]]] = None,
    ) -> List[ScoredPattern]:
        """Score all patterns against session metadata."""
        self._load_ltm_entries()

        if patterns is None:
            patterns = list(self.patterns.values())

        scored_patterns = []

        for pattern in patterns:
            score = self.score_pattern(pattern, session_metadata)

            scored_pattern = ScoredPattern(
                pattern_id=pattern.get("id", f"pattern_{len(scored_patterns)}"),
                name=pattern.get("name", "unknown"),
                score=score,
                recency_score=self._compute_recency_score(pattern),
                domain_score=self._compute_domain_score(pattern, session_metadata),
                success_score=self._compute_success_score(pattern),
                popularity_score=self._compute_popularity_score(pattern),
                applicability_score=self._compute_applicability_score(
                    pattern, session_metadata
                ),
                last_seen=pattern.get("last_seen", "unknown"),
                success_rate=pattern.get("success_rate", 0.0),
                execution_count=pattern.get("execution_count", 0),
                agent_types=pattern.get("agent_types", []),
                improvement_area=pattern.get("improvement_area", "unknown"),
                description=pattern.get("description", ""),
            )

            scored_patterns.append(scored_pattern)

        # Sort by score descending
        scored_patterns.sort(key=lambda x: x.score, reverse=True)

        return scored_patterns

    def select_patterns(
        self,
        session_metadata: Dict[str, Any],
        top_k: int = 15,
        min_score: float = 0.65,
        patterns: Optional[List[Dict[str, Any]]] = None,
    ) -> List[ScoredPattern]:
        """Select top-K patterns for injection."""
        scored = self.score_patterns(session_metadata, patterns)

        # Filter by minimum score
        filtered = [p for p in scored if p.score >= min_score]

        # Return top-K
        return filtered[:top_k]


def extract_session_metadata() -> Dict[str, Any]:
    """Extract session metadata from GitHub Actions context and environment."""
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "github_ref": os.environ.get("GITHUB_REF", "unknown"),
        "github_event_name": os.environ.get("GITHUB_EVENT_NAME", "unknown"),
        "task_description": os.environ.get("COPILOT_TASK_DESCRIPTION", ""),
        "domain": os.environ.get("COPILOT_DOMAIN", ""),
        "agent_types": [
            os.environ.get("COPILOT_AGENT_TYPE", "general-purpose")
        ],
        "pr_number": os.environ.get("GITHUB_PR_NUMBER", ""),
        "branch": os.environ.get("GITHUB_HEAD_REF", ""),
        "base_branch": os.environ.get("GITHUB_BASE_REF", ""),
    }

    # Load from manifest if available
    manifest_path = ".codex/session_context_manifest.json"
    if Path(manifest_path).exists():
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                metadata["task_description"] = manifest.get(
                    "task_description", metadata["task_description"]
                )
                metadata["domain"] = manifest.get("domain", metadata["domain"])
                metadata["agent_types"] = manifest.get(
                    "agent_types", metadata["agent_types"]
                )
        except Exception as e:
            logger.warning(f"Error loading manifest: {e}")

    return metadata


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Phase 10.3: Context Relevance Scoring Engine"
    )
    parser.add_argument(
        "--session-metadata",
        type=str,
        help="Path to session metadata JSON file",
    )
    parser.add_argument(
        "--patterns",
        type=str,
        default=".codex/patterns/ci_failure_patterns.yaml",
        help="Path to patterns YAML file",
    )
    parser.add_argument(
        "--ltm-db",
        type=str,
        help="Path to LTM SQLite database",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=".codex/phase_10_3_scored_patterns.json",
        help="Output path for scored patterns",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=15,
        help="Number of top patterns to select (default: 15)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.65,
        help="Minimum relevance score threshold (default: 0.65)",
    )
    parser.add_argument(
        "--json-metadata",
        type=str,
        help="Inline JSON metadata (as alternative to --session-metadata file)",
    )

    args = parser.parse_args()

    start_time = time.time()

    # Extract session metadata
    if args.session_metadata and Path(args.session_metadata).exists():
        with open(args.session_metadata, "r") as f:
            session_metadata = json.load(f)
        logger.info(f"Loaded session metadata from {args.session_metadata}")
    elif args.json_metadata:
        session_metadata = json.loads(args.json_metadata)
        logger.info("Using inline JSON metadata")
    else:
        session_metadata = extract_session_metadata()
        logger.info("Extracted session metadata from environment")

    # Initialize scorer
    scorer = ContextScorer(ltm_db_path=args.ltm_db, pattern_file=args.patterns)

    # Score patterns
    logger.info(f"Scoring patterns with top_k={args.top_k}, min_score={args.min_score}")
    selected = scorer.select_patterns(
        session_metadata, top_k=args.top_k, min_score=args.min_score
    )

    # Prepare output
    output = {
        "timestamp": datetime.now().isoformat(),
        "session_metadata": session_metadata,
        "selected_patterns": [asdict(p) for p in selected],
        "pattern_count": len(selected),
        "avg_score": (
            sum(p.score for p in selected) / len(selected) if selected else 0.0
        ),
        "execution_time_ms": (time.time() - start_time) * 1000,
    }

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(
        f"✅ Wrote {len(selected)} patterns to {args.output} "
        f"(avg score: {output['avg_score']:.2f}, "
        f"time: {output['execution_time_ms']:.1f}ms)"
    )

    # Print summary
    print("\n" + "=" * 80)
    print("PHASE 10.3: CONTEXT INJECTION SCORING SUMMARY")
    print("=" * 80)
    print(f"Session: {session_metadata.get('github_ref', 'unknown')}")
    print(f"Domain: {session_metadata.get('domain', 'unknown')}")
    print(f"Agents: {', '.join(session_metadata.get('agent_types', []))}")
    print(f"\nSelected {len(selected)} patterns (threshold: {args.min_score})")
    print(f"Average relevance score: {output['avg_score']:.2f}")
    print(f"Scoring time: {output['execution_time_ms']:.1f}ms")

    if selected:
        print("\nTop 5 patterns:")
        for i, p in enumerate(selected[:5], 1):
            print(
                f"  {i}. {p.name} (score: {p.score:.2f}, "
                f"success_rate: {p.success_rate:.1%}, executions: {p.execution_count})"
            )

    print("=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
