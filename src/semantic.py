"""Semantic retrieval module."""


def search_semantic(query: str, corpus: list[str], top_k: int = 5) -> list[str]:
    """Return top-k documents using semantic retrieval.

    This is a placeholder function for milestone scaffolding.
    """
    if not query or not corpus:
        return []

    # TODO: Implement embedding + similarity search.
    return corpus[:top_k]
