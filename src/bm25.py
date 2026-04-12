"""BM25 retrieval module."""

from __future__ import annotations

from .ranking import BM25Retriever


def search_bm25(query: str, corpus: list[str], top_k: int = 5) -> list[str]:
    """Return top-k documents using BM25 retrieval."""
    if not query or not corpus:
        return []

    documents = [
        {"record_id": str(index), "search_text": text, "title": text, "review_text": text}
        for index, text in enumerate(corpus)
    ]
    retriever = BM25Retriever(documents)
    return [result.document["search_text"] for result in retriever.search(query, top_k=top_k)]
