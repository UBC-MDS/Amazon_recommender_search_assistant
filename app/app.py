"""Streamlit app for interactive retrieval search."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_io import format_rating_stars, load_documents, truncate_text  # noqa: E402
from src.feedback import append_feedback  # noqa: E402
from src.ranking import BM25Retriever, HybridRetriever, SemanticRetriever, ensure_search_text  # noqa: E402


def _build_indexes(data_path: str | None = None):
    documents = ensure_search_text(load_documents(data_path=data_path))
    processed_dir = ROOT / "data" / "processed"
    bm25_index_path = processed_dir / "bm25_index.pkl"
    semantic_index_dir = processed_dir / "semantic_faiss"

    if data_path is None and bm25_index_path.exists():
        bm25 = BM25Retriever.load_index(bm25_index_path)
    else:
        bm25 = BM25Retriever(documents)

    if data_path is None and (semantic_index_dir / "index.faiss").exists() and (semantic_index_dir / "metadata.json").exists():
        try:
            semantic = SemanticRetriever.load_index(semantic_index_dir)
        except Exception:
            semantic = SemanticRetriever(documents)
    else:
        semantic = SemanticRetriever(documents)

    hybrid = HybridRetriever(documents, bm25=bm25, semantic=semantic)
    return documents, bm25, semantic, hybrid


@st.cache_resource(show_spinner=False)
def load_indexes(data_path: str | None = None):
    return _build_indexes(data_path)


def _render_result(result, rank: int, query: str, mode: str, feedback_path: Path) -> None:
    document = result.document
    title = document.get("title", "Untitled")
    review_text = document.get("review_text", "")
    rating = document.get("rating")
    score = result.score
    record_id = document.get("record_id", "")
    source = document.get("source", "")

    st.markdown(f"### {rank}. {title}")
    st.write(truncate_text(review_text, 200))
    st.caption(f"Rating: {format_rating_stars(rating)} ({rating if rating is not None else 'n/a'})")
    st.caption(f"Retrieval score: {score:.4f}")

    feedback_cols = st.columns(2)
    if feedback_cols[0].button("👍", key=f"{mode}_{query}_{rank}_up"):
        append_feedback(
            feedback_path,
            {
                "query": query,
                "mode": mode,
                "rank": rank,
                "record_id": record_id,
                "title": title,
                "score": f"{score:.6f}",
                "rating": rating if rating is not None else "",
                "feedback": "up",
                "source": source,
            },
        )
        st.success("Saved thumbs-up feedback")
    if feedback_cols[1].button("👎", key=f"{mode}_{query}_{rank}_down"):
        append_feedback(
            feedback_path,
            {
                "query": query,
                "mode": mode,
                "rank": rank,
                "record_id": record_id,
                "title": title,
                "score": f"{score:.6f}",
                "rating": rating if rating is not None else "",
                "feedback": "down",
                "source": source,
            },
        )
        st.warning("Saved thumbs-down feedback")


def main() -> None:
    st.set_page_config(page_title="Amazon Product Query Assistant", page_icon="🔎", layout="wide")

    st.title("Amazon Product Query Assistant")
    st.write("Search products with BM25, semantic retrieval, or a hybrid blend. Feedback is stored locally in CSV format.")

    data_path_input = st.sidebar.text_input("Optional data path", value="")
    documents, bm25, semantic, hybrid = load_indexes(data_path_input or None)

    st.sidebar.subheader("Corpus")
    st.sidebar.write(f"Loaded documents: {len(documents)}")
    st.sidebar.write(f"Feedback file: {ROOT / 'data' / 'processed' / 'feedback.csv'}")

    query = st.text_input("Enter a query", placeholder="e.g. best headphones for long flights under 200 dollars")
    mode = st.radio("Search mode", ["BM25", "Semantic", "Hybrid"], horizontal=True)

    if not query:
        st.info("Enter a query to see the top results.")
        return

    if mode == "BM25":
        results = bm25.search(query, top_k=3)
    elif mode == "Semantic":
        results = semantic.search(query, top_k=3)
    else:
        results = hybrid.search(query, top_k=3)

    if not results:
        st.warning("No results found.")
        return

    feedback_path = ROOT / "data" / "processed" / "feedback.csv"
    for rank, result in enumerate(results, start=1):
        _render_result(result, rank, query, mode, feedback_path)
        st.divider()


if __name__ == "__main__":
    main()
