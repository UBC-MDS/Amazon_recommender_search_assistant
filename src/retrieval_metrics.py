"""Retrieval metrics module."""


def precision_at_k(relevant_flags: list[int], k: int) -> float:
    """Compute Precision@k given binary relevance flags."""
    if k <= 0:
        return 0.0
    top_k = relevant_flags[:k]
    if not top_k:
        return 0.0
    return sum(top_k) / len(top_k)
