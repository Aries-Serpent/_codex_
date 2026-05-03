#!/usr/bin/env python3
"""
Community Knowledge Hub

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/community_knowledge_hub.py [options]

    Examples:
    $ python scripts/cognitive/community_knowledge_hub.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Community contributed pattern"""
    pattern_id: str
    name: str
    description: str
    category: str
    code_example: str
    author: str
    submitted_date: str
    status: str  # "pending", "approved", "rejected"
    rating: float
    review_count: int
    reviews: list[dict[str, Any]]
    tags: list[str]
    effectiveness: Optional[float] = None
    use_count: int = 0


@dataclass
class Review:
    """Peer review for a pattern"""
    review_id: str
    pattern_id: str
    reviewer: str
    rating: float  # 1.0 to 5.0
    feedback: str
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str  # "approve", "revise", "reject"
    submitted_date: str


class CommunityKnowledgeHub:
    """System for community pattern contributions with peer review"""

    def __init__(
        self,
        data_path: str = "cognitive/community",
        min_reviews_for_approval: int = 3,
        min_rating_for_approval: float = 4.0
    ):
        self.data_path = Path(data_path)
        self.min_reviews = min_reviews_for_approval
        self.min_rating = min_rating_for_approval

        # Ensure directories exist
        self.data_path.mkdir(parents=True, exist_ok=True)
        (self.data_path / "patterns").mkdir(exist_ok=True)
        (self.data_path / "reviews").mkdir(exist_ok=True)
        (self.data_path / "public").mkdir(exist_ok=True)

        self.patterns: dict[str, Pattern] = {}
        self.reviews: dict[str, list[Review]] = defaultdict(list)

        self._load_patterns()
        self._load_reviews()

    def _load_patterns(self):
        """Load all patterns from disk"""
        patterns_dir = self.data_path / "patterns"
        for pattern_file in patterns_dir.glob("*.json"):
            try:
                with open(pattern_file) as f:
                    data = json.load(f)
                    pattern = Pattern(**data)
                    self.patterns[pattern.pattern_id] = pattern
            except Exception as e:
                logger.warning(f"Could not load pattern from {pattern_file}: {e}")

    def _load_reviews(self):
        """Load all reviews from disk"""
        reviews_dir = self.data_path / "reviews"
        for review_file in reviews_dir.glob("*.json"):
            try:
                with open(review_file) as f:
                    data = json.load(f)
                    review = Review(**data)
                    self.reviews[review.pattern_id].append(review)
            except Exception as e:
                logger.warning(f"Could not load review from {review_file}: {e}")

    def submit_pattern(
        self,
        name: str,
        description: str,
        category: str,
        code_example: str,
        author: str,
        tags: Optional[list[str]] = None
    ) -> Pattern:
        """
        Submit a new pattern to the community

        Args:
            name: Pattern name
            description: Detailed description
            category: Pattern category
            code_example: Code example demonstrating the pattern
            author: Author username/email
            tags: Optional list of tags

        Returns:
            Created Pattern object
        """
        logger.info(f"Submitting new pattern: {name}")

        # Generate pattern ID
        pattern_data = f"{name}{description}{author}{datetime.now().isoformat()}"
        pattern_id = hashlib.sha256(pattern_data.encode()).hexdigest()[:16]

        # Create pattern
        pattern = Pattern(
            pattern_id=pattern_id,
            name=name,
            description=description,
            category=category,
            code_example=code_example,
            author=author,
            submitted_date=datetime.now().isoformat(),
            status="pending",
            rating=0.0,
            review_count=0,
            reviews=[],
            tags=tags or [],
            effectiveness=None,
            use_count=0
        )

        # Save pattern
        self.patterns[pattern_id] = pattern
        self._save_pattern(pattern)

        logger.info(f"Pattern submitted successfully: {pattern_id}")

        return pattern

    def _save_pattern(self, pattern: Pattern):
        """Save pattern to disk"""
        pattern_file = self.data_path / "patterns" / f"{pattern.pattern_id}.json"
        with open(pattern_file, 'w') as f:
            json.dump(asdict(pattern), f, indent=2)

    def submit_review(
        self,
        pattern_id: str,
        reviewer: str,
        rating: float,
        feedback: str,
        strengths: list[str],
        weaknesses: list[str],
        recommendation: str
    ) -> Review:
        """
        Submit a peer review for a pattern

        Args:
            pattern_id: ID of pattern to review
            reviewer: Reviewer username/email
            rating: Rating score (1.0-5.0)
            feedback: Detailed feedback text
            strengths: List of pattern strengths
            weaknesses: List of pattern weaknesses
            recommendation: "approve", "revise", or "reject"

        Returns:
            Created Review object
        """
        logger.info(f"Submitting review for pattern {pattern_id}")

        if pattern_id not in self.patterns:
            raise ValueError(f"Pattern not found: {pattern_id}")

        # Validate rating
        if not (1.0 <= rating <= 5.0):
            raise ValueError("Rating must be between 1.0 and 5.0")

        # Generate review ID
        review_data = f"{pattern_id}{reviewer}{datetime.now().isoformat()}"
        review_id = hashlib.sha256(review_data.encode()).hexdigest()[:16]

        # Create review
        review = Review(
            review_id=review_id,
            pattern_id=pattern_id,
            reviewer=reviewer,
            rating=rating,
            feedback=feedback,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
            submitted_date=datetime.now().isoformat()
        )

        # Save review
        self.reviews[pattern_id].append(review)
        self._save_review(review)

        # Update pattern with review
        self._update_pattern_with_review(pattern_id, review)

        # Check if pattern should be approved
        self._check_approval_criteria(pattern_id)

        logger.info(f"Review submitted successfully: {review_id}")

        return review

    def _save_review(self, review: Review):
        """Save review to disk"""
        review_file = self.data_path / "reviews" / f"{review.review_id}.json"
        with open(review_file, 'w') as f:
            json.dump(asdict(review), f, indent=2)

    def _update_pattern_with_review(self, pattern_id: str, review: Review):
        """Update pattern with new review information"""
        pattern = self.patterns[pattern_id]

        # Add review to pattern
        pattern.reviews.append(asdict(review))
        pattern.review_count = len(self.reviews[pattern_id])

        # Recalculate average rating
        all_ratings = [r.rating for r in self.reviews[pattern_id]]
        pattern.rating = sum(all_ratings) / len(all_ratings)

        # Save updated pattern
        self._save_pattern(pattern)

    def _check_approval_criteria(self, pattern_id: str):
        """Check if pattern meets approval criteria"""
        pattern = self.patterns[pattern_id]

        if pattern.status != "pending":
            return  # Already processed

        # Check review count
        if pattern.review_count < self.min_reviews:
            logger.info(f"Pattern {pattern_id} needs more reviews: {pattern.review_count}/{self.min_reviews}")
            return

        # Check average rating
        if pattern.rating < self.min_rating:
            logger.info(f"Pattern {pattern_id} rating too low: {pattern.rating}/{self.min_rating}")
            pattern.status = "rejected"
            self._save_pattern(pattern)
            return

        # Check recommendation consensus
        approvals = sum(1 for r in self.reviews[pattern_id] if r.recommendation == "approve")
        approval_rate = approvals / pattern.review_count

        if approval_rate >= 0.67:  # 2/3 approval rate
            logger.info(f"Pattern {pattern_id} APPROVED")
            pattern.status = "approved"
            self._save_pattern(pattern)
            self._publish_to_public_library(pattern)
        else:
            logger.info(f"Pattern {pattern_id} REJECTED (low approval rate)")
            pattern.status = "rejected"
            self._save_pattern(pattern)

    def _publish_to_public_library(self, pattern: Pattern):
        """Publish approved pattern to public library"""
        public_file = self.data_path / "public" / f"{pattern.pattern_id}.json"

        # Create public-facing version (sanitized)
        public_pattern = {
            "pattern_id": pattern.pattern_id,
            "name": pattern.name,
            "description": pattern.description,
            "category": pattern.category,
            "code_example": pattern.code_example,
            "author": pattern.author,
            "submitted_date": pattern.submitted_date,
            "rating": pattern.rating,
            "review_count": pattern.review_count,
            "tags": pattern.tags,
            "effectiveness": pattern.effectiveness,
            "use_count": pattern.use_count
        }

        with open(public_file, 'w') as f:
            json.dump(public_pattern, f, indent=2)

        logger.info(f"Pattern published to public library: {pattern.pattern_id}")

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get a specific pattern by ID"""
        return self.patterns.get(pattern_id)

    def list_patterns(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> list[Pattern]:
        """
        List patterns with optional filters

        Args:
            status: Filter by status ("pending", "approved", "rejected")
            category: Filter by category
            min_rating: Minimum rating threshold

        Returns:
            List of matching patterns
        """
        patterns = list(self.patterns.values())

        # Apply filters
        if status:
            patterns = [p for p in patterns if p.status == status]

        if category:
            patterns = [p for p in patterns if p.category == category]

        if min_rating is not None:
            patterns = [p for p in patterns if p.rating >= min_rating]

        # Sort by rating (descending)
        patterns.sort(key=lambda p: p.rating, reverse=True)

        return patterns

    def get_top_patterns(self, n: int = 10) -> list[Pattern]:
        """Get top N patterns by rating"""
        approved = self.list_patterns(status="approved")
        return approved[:n]

    def record_pattern_use(self, pattern_id: str):
        """Record that a pattern was used"""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.use_count += 1
            self._save_pattern(pattern)

            # Update public library if approved
            if pattern.status == "approved":
                self._publish_to_public_library(pattern)

    def update_pattern_effectiveness(
        self,
        pattern_id: str,
        effectiveness: float
    ):
        """
        Update pattern's effectiveness score based on usage results

        Args:
            pattern_id: Pattern ID
            effectiveness: Effectiveness score (0.0-1.0)
        """
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.effectiveness = effectiveness
            self._save_pattern(pattern)

            # Update public library if approved
            if pattern.status == "approved":
                self._publish_to_public_library(pattern)

            logger.info(f"Updated effectiveness for pattern {pattern_id}: {effectiveness:.2%}")

    def generate_community_report(self) -> dict[str, Any]:
        """Generate comprehensive community report"""
        total_patterns = len(self.patterns)

        by_status = defaultdict(int)
        by_category = defaultdict(int)

        for pattern in self.patterns.values():
            by_status[pattern.status] += 1
            by_category[pattern.category] += 1

        # Top contributors
        contributors = defaultdict(int)
        for pattern in self.patterns.values():
            contributors[pattern.author] += 1

        top_contributors = sorted(
            contributors.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Top patterns
        top_patterns = self.get_top_patterns(n=10)

        # Review statistics
        total_reviews = sum(len(reviews) for reviews in self.reviews.values())

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_patterns": total_patterns,
                "total_reviews": total_reviews,
                "approved_patterns": by_status.get("approved", 0),
                "pending_patterns": by_status.get("pending", 0)
            },
            "patterns_by_status": dict(by_status),
            "patterns_by_category": dict(by_category),
            "top_contributors": [
                {"author": author, "contributions": count}
                for author, count in top_contributors
            ],
            "top_patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "name": p.name,
                    "rating": p.rating,
                    "use_count": p.use_count,
                    "effectiveness": p.effectiveness
                }
                for p in top_patterns
            ]
        }

        # Save report
        report_file = self.data_path / f"community_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Generate markdown version
        self._generate_markdown_report(report)

        logger.info(f"Community report generated: {report_file}")

        return report

    def _generate_markdown_report(self, report: dict[str, Any]):
        """Generate markdown version of community report"""
        md_content = f"""# Community Knowledge Hub Report

**Generated**: {report['generated_at']}

## Summary

- **Total Patterns**: {report['summary']['total_patterns']}
- **Total Reviews**: {report['summary']['total_reviews']}
- **Approved Patterns**: {report['summary']['approved_patterns']}
- **Pending Patterns**: {report['summary']['pending_patterns']}

## Patterns by Category

"""

        for category, count in report['patterns_by_category'].items():
            md_content += f"- **{category}**: {count} patterns\n"

        md_content += "\n## Top Contributors\n\n"

        for i, contrib in enumerate(report['top_contributors'], 1):
            md_content += f"{i}. **{contrib['author']}**: {contrib['contributions']} contributions\n"

        md_content += "\n## Top Rated Patterns\n\n"

        for i, pattern in enumerate(report['top_patterns'], 1):
            effectiveness_str = f"{pattern['effectiveness']:.1%}" if pattern['effectiveness'] else "N/A"
            md_content += f"{i}. **{pattern['name']}** (Rating: {pattern['rating']:.1f}/5.0, Uses: {pattern['use_count']}, Effectiveness: {effectiveness_str})\n"

        # Save markdown
        md_file = self.data_path / f"community_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(md_file, 'w') as f:
            f.write(md_content)


def main():
    """Main entry point for community knowledge hub"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Community Knowledge Hub for pattern sharing"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Submit pattern command
    submit_parser = subparsers.add_parser("submit", help="Submit a new pattern")
    submit_parser.add_argument("--name", required=True, help="Pattern name")
    submit_parser.add_argument("--description", required=True, help="Pattern description")
    submit_parser.add_argument("--category", required=True, help="Pattern category")
    submit_parser.add_argument("--code", required=True, help="Code example file path")
    submit_parser.add_argument("--author", required=True, help="Author name/email")

    # Review pattern command
    review_parser = subparsers.add_parser("review", help="Submit a pattern review")
    review_parser.add_argument("--pattern-id", required=True, help="Pattern ID to review")
    review_parser.add_argument("--reviewer", required=True, help="Reviewer name/email")
    review_parser.add_argument("--rating", type=float, required=True, help="Rating (1.0-5.0)")
    review_parser.add_argument("--feedback", required=True, help="Review feedback")
    review_parser.add_argument("--recommendation", required=True, choices=["approve", "revise", "reject"])

    # List patterns command
    list_parser = subparsers.add_parser("list", help="List patterns")
    list_parser.add_argument("--status", choices=["pending", "approved", "rejected"])
    list_parser.add_argument("--category", help="Filter by category")

    # Report command
    subparsers.add_parser("report", help="Generate community report")

    args = parser.parse_args()

    # Initialize hub
    hub = CommunityKnowledgeHub()

    # Execute command
    if args.command == "submit":
        # Read code example from file
        with open(args.code) as f:
            code_example = f.read()

        pattern = hub.submit_pattern(
            name=args.name,
            description=args.description,
            category=args.category,
            code_example=code_example,
            author=args.author
        )

        print("\n✅ Pattern submitted successfully!")
        print(f"Pattern ID: {pattern.pattern_id}")
        print(f"Status: {pattern.status}")

    elif args.command == "review":
        review = hub.submit_review(
            pattern_id=args.pattern_id,
            reviewer=args.reviewer,
            rating=args.rating,
            feedback=args.feedback,
            strengths=["strength1"],  # Could be enhanced with CLI input
            weaknesses=["weakness1"],
            recommendation=args.recommendation
        )

        print("\n✅ Review submitted successfully!")
        print(f"Review ID: {review.review_id}")

    elif args.command == "list":
        patterns = hub.list_patterns(
            status=args.status if hasattr(args, 'status') else None,
            category=args.category if hasattr(args, 'category') else None
        )

        print(f"\n📋 Found {len(patterns)} pattern(s):\n")
        for pattern in patterns:
            print(f"- {pattern.name} ({pattern.pattern_id})")
            print(f"  Status: {pattern.status}, Rating: {pattern.rating:.1f}/5.0, Reviews: {pattern.review_count}")
            print()

    elif args.command == "report":
        report = hub.generate_community_report()

        print(f"\n{'='*60}")
        print("COMMUNITY KNOWLEDGE HUB REPORT")
        print(f"{'='*60}\n")
        print(json.dumps(report, indent=2))

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
