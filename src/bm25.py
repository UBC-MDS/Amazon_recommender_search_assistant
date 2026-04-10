"""BM25 retrieval module."""


def search_bm25(query: str, corpus: list[str], top_k: int = 5) -> list[str]:
    """Return top-k documents using BM25 retrieval.

    This is a placeholder function for milestone scaffolding.
    """
    if not query or not corpus:
        return []

    # TODO: Implement BM25 ranking and return ranked documents.
    return corpus[:top_k]
