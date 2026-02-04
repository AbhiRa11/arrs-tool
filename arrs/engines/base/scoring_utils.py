"""Common scoring utilities."""
from typing import List, Dict, Any


def calculate_completeness_score(
    present_fields: List[str],
    expected_fields: List[str],
    max_points: float = 100.0
) -> float:
    """
    Calculate completeness score based on present vs expected fields.

    Args:
        present_fields: List of present fields
        expected_fields: List of expected fields
        max_points: Maximum points

    Returns:
        Score (0 to max_points)
    """
    if not expected_fields:
        return max_points

    present_count = len([f for f in present_fields if f in expected_fields])
    expected_count = len(expected_fields)

    ratio = present_count / expected_count
    return ratio * max_points


def calculate_richness_score(
    content: str,
    benchmark_chars: int = 500,
    max_points: float = 100.0
) -> float:
    """
    Calculate content richness based on character count.

    Args:
        content: Content text
        benchmark_chars: Benchmark character count
        max_points: Maximum points

    Returns:
        Score (0 to max_points)
    """
    char_count = len(content)
    ratio = min(1.0, char_count / benchmark_chars)
    return ratio * max_points


def calculate_ratio_score(
    numerator: float,
    denominator: float,
    max_points: float = 100.0
) -> float:
    """
    Calculate score based on a ratio.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        max_points: Maximum points

    Returns:
        Score (0 to max_points)
    """
    if denominator == 0:
        return 0.0

    ratio = min(1.0, numerator / denominator)
    return ratio * max_points


def calculate_weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Calculate weighted average score.

    Args:
        scores: Dictionary of scores
        weights: Dictionary of weights (must sum to 1.0)

    Returns:
        Weighted score
    """
    total = 0.0
    for key, score in scores.items():
        weight = weights.get(key, 0.0)
        total += score * weight

    return total


def count_semantic_html_tags(html_data: Dict[str, Any]) -> int:
    """
    Count semantic HTML tags.

    Args:
        html_data: Parsed HTML data with semantic element counts

    Returns:
        Total count of semantic elements
    """
    semantic_elements = html_data.get('semantic_elements', {})
    return sum(semantic_elements.values())
