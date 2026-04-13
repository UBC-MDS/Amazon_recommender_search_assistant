"""Semantic retrieval module."""

from __future__ import annotations

from .ranking import SearchResult, SemanticRetriever


def search_semantic(query: str, corpus: list[str], top_k: int = 5) -> list[SearchResult]:
    """Return top-k ranked semantic results with scores."""
    if not query or not corpus:
        return []

    documents = [
        {"record_id": str(index), "search_text": text, "title": text, "review_text": text}
        for index, text in enumerate(corpus)
    ]
    retriever = SemanticRetriever(documents)
    return retriever.search(query, top_k=top_k)


def search_semantic_text(query: str, corpus: list[str], top_k: int = 5) -> list[str]:
    """Compatibility helper that returns only ranked document text."""
    return [result.document["search_text"] for result in search_semantic(query, corpus, top_k=top_k)]
