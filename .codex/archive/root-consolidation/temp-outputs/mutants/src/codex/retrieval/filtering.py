"""
Metadata filtering for vector stores

Provides post-filtering capabilities for vector search results based on metadata.
Supports equality, range, exists, and logical operators.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class FilterOperator:
    """Filter operator types"""

    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal
    IN = "in"  # In list
    NIN = "nin"  # Not in list
    EXISTS = "exists"  # Field exists
    AND = "and"  # Logical AND
    OR = "or"  # Logical OR


def matches_filter(metadata: dict[str, Any], filter_spec: dict[str, Any]) -> bool:
    """Check if metadata matches filter specification

    Supports MongoDB-style filter syntax:

    Equality:
        {"category": "tech"}  # category == "tech"

    Range operators:
        {"score": {"$gte": 0.5}}  # score >= 0.5
        {"score": {"$gt": 0.5, "$lt": 1.0}}  # 0.5 < score < 1.0

    Exists:
        {"field": {"$exists": True}}  # field exists
        {"field": {"$exists": False}}  # field does not exist

    In/Not In:
        {"category": {"$in": ["tech", "news"]}}  # category in list
        {"category": {"$nin": ["spam"]}}  # category not in list

    Logical operators:
        {"$and": [{"score": {"$gte": 0.5}}, {"category": "tech"}]}
        {"$or": [{"category": "tech"}, {"category": "news"}]}

    Args:
        metadata: Metadata dictionary to check
        filter_spec: Filter specification

    Returns:
        True if metadata matches filter, False otherwise
    """
    if not filter_spec:
        return True  # Empty filter matches everything

    # Handle logical operators
    if "$and" in filter_spec:
        return all(matches_filter(metadata, f) for f in filter_spec["$and"])

    if "$or" in filter_spec:
        return any(matches_filter(metadata, f) for f in filter_spec["$or"])

    # Check each field filter
    for field, condition in filter_spec.items():
        if field.startswith("$"):
            continue  # Skip logical operators

        # Get field value from metadata
        field_value = metadata.get(field)

        # Handle operator conditions
        if isinstance(condition, dict):
            for operator, target in condition.items():
                if operator == "$eq":
                    if field_value != target:
                        return False
                elif operator == "$ne":
                    if field_value == target:
                        return False
                elif operator == "$gt":
                    if field_value is None or field_value <= target:
                        return False
                elif operator == "$gte":
                    if field_value is None or field_value < target:
                        return False
                elif operator == "$lt":
                    if field_value is None or field_value >= target:
                        return False
                elif operator == "$lte":
                    if field_value is None or field_value > target:
                        return False
                elif operator == "$in":
                    if field_value not in target:
                        return False
                elif operator == "$nin":
                    if field_value in target:
                        return False
                elif operator == "$exists":
                    field_exists = field in metadata
                    if field_exists != target:
                        return False
                else:
                    logger.warning(f"Unknown operator: {operator}")
        else:
            # Simple equality
            if field_value != condition:
                return False

    return True


def apply_filters(
    results: list[dict[str, Any]],
    filters: Optional[dict[str, Any]] = None,
    max_results: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Apply filters to search results

    Args:
        results: list of search results with metadata
        filters: Filter specification (MongoDB-style)
        max_results: Maximum number of results to return after filtering

    Returns:
        Filtered results
    """
    if not filters:
        if max_results:
            return results[:max_results]
        return results

    # Apply filters
    filtered = [r for r in results if matches_filter(r.get("metadata", {}), filters)]

    # Limit results
    if max_results:
        filtered = filtered[:max_results]

    logger.debug(f"Filtered {len(results)} results to {len(filtered)}")

    return filtered


def calculate_fetch_multiplier(filters: Optional[dict[str, Any]] = None) -> int:
    """Calculate how many results to fetch to account for filtering

    Args:
        filters: Filter specification

    Returns:
        Multiplier for initial fetch (1-10)
    """
    if not filters:
        return 1

    # Count filter conditions
    num_conditions = len(filters)

    # Adjust multiplier based on complexity
    if num_conditions == 0:
        return 1
    if num_conditions == 1:
        return 3  # Fetch 3x for single condition
    if num_conditions == 2:
        return 5  # Fetch 5x for two conditions
    return 10  # Fetch 10x for complex filters
