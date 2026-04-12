"""Semantic retrieval module."""

from __future__ import annotations

from .ranking import SemanticRetriever


def search_semantic(query: str, corpus: list[str], top_k: int = 5) -> list[str]:
    """Return top-k documents using semantic retrieval."""
    if not query or not corpus:
        return []

    documents = [
        {"record_id": str(index), "search_text": text, "title": text, "review_text": text}
        for index, text in enumerate(corpus)
    ]
    retriever = SemanticRetriever(documents)
    return [result.document["search_text"] for result in retriever.search(query, top_k=top_k)]
