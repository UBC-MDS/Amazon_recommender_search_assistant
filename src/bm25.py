"""BM25 retrieval module."""

from __future__ import annotations

from .ranking import BM25Retriever, SearchResult


def search_bm25(query: str, corpus: list[str], top_k: int = 5) -> list[SearchResult]:
    """Return top-k ranked BM25 results with scores."""
    if not query or not corpus:
        return []

    documents = [
        {"record_id": str(index), "search_text": text, "title": text, "review_text": text}
        for index, text in enumerate(corpus)
    ]
    retriever = BM25Retriever(documents)
    return retriever.search(query, top_k=top_k)


def search_bm25_text(query: str, corpus: list[str], top_k: int = 5) -> list[str]:
    """Compatibility helper that returns only ranked document text."""
    return [result.document["search_text"] for result in search_bm25(query, corpus, top_k=top_k)]
