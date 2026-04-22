"""Streamlit app -- Amazon Product Query Assistant."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_io import format_rating_stars, load_documents, truncate_text  # noqa: E402
from src.feedback import append_feedback  # noqa: E402
from src.hybrid_rag_pipeline import FusionConfig, HybridRAGPipeline  # noqa: E402
from src.ranking import BM25Retriever, HybridRetriever, SemanticRetriever, ensure_search_text  # noqa: E402


# --------------- cached loaders ---------------

@st.cache_resource(show_spinner="Loading corpus and indexes ...")
def load_indexes():
    processed = ROOT / "data" / "processed"
    documents = ensure_search_text(load_documents())

    bm25_path = processed / "bm25_index.pkl"
    bm25 = BM25Retriever.load_index(bm25_path) if bm25_path.exists() else BM25Retriever(documents)

    sem_dir = processed / "semantic_faiss"
    if (sem_dir / "index.faiss").exists():
        try:
            semantic = SemanticRetriever.load_index(sem_dir)
        except Exception:
            semantic = SemanticRetriever(documents)
    else:
        semantic = SemanticRetriever(documents)

    hybrid = HybridRetriever(documents, bm25=bm25, semantic=semantic)
    return documents, bm25, semantic, hybrid


def _select_retriever(mode, bm25, semantic, hybrid):
    if mode == "BM25":
        return bm25
    if mode == "Semantic":
        return semantic
    return hybrid


def _render_search_result(result, rank, query, mode, feedback_path):
    doc = result.document
    title = doc.get("title", "Untitled")
    rating = doc.get("rating")
    review = doc.get("review_text", "")
    score = result.score
    record_id = doc.get("record_id", "")

    st.markdown(f"**{rank}. {title}**")
    col1, col2 = st.columns([3, 1])
    col1.write(truncate_text(review, 200))
    col2.metric("Rating", f"{rating}/5" if rating else "N/A")
    st.caption(f"Retrieval score: {score:.4f}")

    fb1, fb2 = st.columns(2)
    if fb1.button("thumbs up", key=f"s_{mode}_{query}_{rank}_up"):
        append_feedback(feedback_path, {"query": query, "mode": mode, "rank": rank,
                                         "record_id": record_id, "title": title,
                                         "score": f"{score:.6f}", "rating": rating or "", "feedback": "up"})
        st.success("Saved")
    if fb2.button("thumbs down", key=f"s_{mode}_{query}_{rank}_dn"):
        append_feedback(feedback_path, {"query": query, "mode": mode, "rank": rank,
                                         "record_id": record_id, "title": title,
                                         "score": f"{score:.6f}", "rating": rating or "", "feedback": "down"})
        st.warning("Saved")
    st.divider()


# --------------- main ---------------

def main():
    load_dotenv()
    st.set_page_config(page_title="Amazon Product Query Assistant", layout="wide")
    st.title("Amazon Product Query Assistant")

    documents, bm25, semantic, hybrid = load_indexes()
    st.sidebar.write(f"Corpus: **{len(documents)}** products")

    # ---- LLM settings in sidebar ----
    st.sidebar.subheader("LLM Settings (RAG Mode)")
    llm_provider = st.sidebar.selectbox("Provider", ["ollama", "huggingface"], index=0)
    if llm_provider == "ollama":
        model_name = st.sidebar.text_input("Model", value="llama3.2:3b")
        ollama_host = st.sidebar.text_input("Ollama host", value=os.getenv("OLLAMA_HOST", ""))
        hf_token = None
    else:
        model_name = st.sidebar.text_input("Model", value="Qwen/Qwen3.5-2B")
        hf_token = st.sidebar.text_input("HF token", value="", type="password")
        ollama_host = None
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.sidebar.slider("Max tokens", 64, 1024, 350, 32)

    # ---- Tabs ----
    search_tab, rag_tab = st.tabs(["Search Only", "RAG Mode"])

    # ==================== SEARCH TAB ====================
    with search_tab:
        query_s = st.text_input("Enter a search query", key="search_q",
                                placeholder="e.g. energy efficient dishwasher")
        mode = st.radio("Retrieval method", ["BM25", "Semantic", "Hybrid"], horizontal=True, key="search_mode")
        top_k = st.slider("Top-k results", 1, 10, 3, key="search_k")

        if query_s:
            retriever = _select_retriever(mode, bm25, semantic, hybrid)
            results = retriever.search(query_s, top_k=top_k)
            if not results:
                st.warning("No results found.")
            else:
                fb_path = ROOT / "data" / "processed" / "feedback.csv"
                for rank, r in enumerate(results, 1):
                    _render_search_result(r, rank, query_s, mode, fb_path)
        else:
            st.info("Type a query above to search the product corpus.")

    # ==================== RAG TAB ====================
    with rag_tab:
        query_r = st.text_input("Enter a question for the assistant", key="rag_q",
                                placeholder="e.g. What is the best quiet dishwasher for a small apartment?")
        prompt_variant = st.selectbox("Prompt style", ["strict", "concise", "analyst"], key="rag_prompt")

        # fusion settings
        fusion_mode = st.selectbox("Hybrid fusion", ["rrf", "merge-dedup", "simple-merge"], key="rag_fusion")
        col_w1, col_w2 = st.columns(2)
        bm25_w = col_w1.slider("BM25 weight", 0.0, 1.0, 0.4, 0.05, key="rag_bw")
        sem_w = col_w2.slider("Semantic weight", 0.0, 1.0, 0.6, 0.05, key="rag_sw")
        rag_k = st.slider("Top-k retrieval", 1, 10, 5, key="rag_k")

        if query_r and st.button("Generate Answer", type="primary"):
            with st.spinner("Retrieving documents and generating answer ..."):
                try:
                    pipeline = HybridRAGPipeline(
                        documents=documents,
                        provider=llm_provider,
                        model=model_name,
                        default_k=rag_k,
                        temperature=temperature,
                        max_new_tokens=max_tokens,
                        hf_token=hf_token or None,
                        ollama_host=ollama_host or None,
                        bm25=bm25,
                        semantic=semantic,
                        fusion=FusionConfig(mode=fusion_mode, bm25_weight=bm25_w, semantic_weight=sem_w),
                    )
                    result = pipeline.answer(query_r, k=rag_k, prompt_variant=prompt_variant)
                except Exception as exc:
                    st.error(f"RAG generation failed: {exc}")
                    return

            # RAG answer panel -- prominently above retrieved docs
            st.subheader("Answer")
            st.markdown(result.answer or "_No answer returned by the model._")

            # Source documents below
            st.subheader("Retrieved Sources")
            for idx, sr in enumerate(result.retrieved_results, 1):
                doc = sr.document
                title = doc.get("title", "Untitled")
                rating = doc.get("rating")
                review = truncate_text(doc.get("review_text", ""), 200)
                st.markdown(f"**[{idx}] {title}**")
                st.caption(f"Rating: {format_rating_stars(rating)} ({rating if rating else 'N/A'}) | "
                           f"Score: {sr.score:.4f} | Method: {sr.method}")
                st.write(review)
                st.divider()

        elif not query_r:
            st.info("Type a question above, then click Generate Answer to use the Hybrid RAG pipeline.")


if __name__ == "__main__":
    main()
