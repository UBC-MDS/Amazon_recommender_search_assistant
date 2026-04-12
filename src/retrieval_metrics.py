"""Retrieval metrics module."""

from __future__ import annotations

import math


def precision_at_k(relevant_flags: list[int], k: int) -> float:
    """Compute Precision@k given binary relevance flags."""
    if k <= 0:
        return 0.0
    top_k = relevant_flags[:k]
    if not top_k:
        return 0.0
    return sum(top_k) / len(top_k)


def recall_at_k(relevant_flags: list[int], k: int, total_relevant: int) -> float:
    """Compute Recall@k."""
    if k <= 0 or total_relevant <= 0:
        return 0.0
    return sum(relevant_flags[:k]) / total_relevant


def mean_reciprocal_rank(relevant_flags: list[int]) -> float:
    """Compute reciprocal rank for the first relevant item."""
    for index, flag in enumerate(relevant_flags, start=1):
        if flag:
            return 1.0 / index
    return 0.0


def ndcg_at_k(relevant_flags: list[int], k: int) -> float:
    """Compute normalized discounted cumulative gain at k."""
    if k <= 0:
        return 0.0

    gains = relevant_flags[:k]
    dcg = sum((gain / math.log2(position + 1)) for position, gain in enumerate(gains, start=2))
    ideal = sorted(relevant_flags, reverse=True)[:k]
    idcg = sum((gain / math.log2(position + 1)) for position, gain in enumerate(ideal, start=2))
    return dcg / idcg if idcg else 0.0
