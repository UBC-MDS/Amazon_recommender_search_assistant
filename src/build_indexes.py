"""Build and persist BM25 and semantic indexes for the app."""

from __future__ import annotations

from pathlib import Path

from .data_io import load_documents
from .ranking import BM25Retriever, SemanticRetriever, ensure_search_text


def main() -> None:
    """Build and persist BM25 and semantic indexes under data/processed."""
    root = Path(__file__).resolve().parents[1]
    processed_dir = root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    documents = ensure_search_text(load_documents())

    bm25 = BM25Retriever(documents)
    bm25_path = processed_dir / "bm25_index.pkl"
    bm25.save_index(bm25_path)

    semantic = SemanticRetriever(documents)
    semantic_dir = processed_dir / "semantic_faiss"
    try:
        semantic.save_index(semantic_dir)
        semantic_status = f"saved semantic FAISS index to {semantic_dir}"
    except Exception as error:
        semantic_status = f"semantic index not persisted ({error})"

    print(f"saved BM25 index to {bm25_path}")
    print(semantic_status)


if __name__ == "__main__":
    main()
