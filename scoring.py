# scoring.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple


RAG = Literal["Green", "Amber", "Red"]
Rating = Literal["Good", "Average", "Weak"]


@dataclass(frozen=True)
class MetricRating:
    rating: Rating
    score: int  # 1..3
    rag: RAG


def rate_metric(
    value: float,
    benchmark: float,
    *,
    better_is_higher: bool,
    tolerance: float = 0.10,
) -> MetricRating:
    """
    Simple, explainable rating:
    - For better_is_higher metrics:
        Good   if value >= benchmark*(1+tolerance)
        Avg    if value >= benchmark*(1-tolerance)
        Weak   otherwise
    - For better_is_lower metrics:
        Good   if value <= benchmark*(1-tolerance)
        Avg    if value <= benchmark*(1+tolerance)
        Weak   otherwise
    """
    if benchmark == 0:
        # Avoid divide-by-zero style issues; fall back to neutral.
        return MetricRating("Average", 2, "Amber")

    if better_is_higher:
        if value >= benchmark * (1 + tolerance):
            return MetricRating("Good", 3, "Green")
        if value >= benchmark * (1 - tolerance):
            return MetricRating("Average", 2, "Amber")
        return MetricRating("Weak", 1, "Red")
    else:
        if value <= benchmark * (1 - tolerance):
            return MetricRating("Good", 3, "Green")
        if value <= benchmark * (1 + tolerance):
            return MetricRating("Average", 2, "Amber")
        return MetricRating("Weak", 1, "Red")


def priority_from_rating(rag: RAG) -> str:
    return {"Red": "High", "Amber": "Medium", "Green": "Low"}[rag]