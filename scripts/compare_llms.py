"""LLM comparison script for final submission.

Runs the same 5 queries through qwen2.5:3b and llama3.2:3b
with identical BM25-retrieved context and prompt template.
Outputs results to JSON for documentation.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_io import load_documents
from src.llm_pipeline import OpenSourceChatModel
from src.ranking import BM25Retriever, ensure_search_text
from src.rag_pipeline import PROMPT_VARIANTS


QUERIES = [
    "energy efficient dishwasher",
    "dishwasher that runs quietly at night",
    "small washing machine for apartment laundry",
    "nugget ice maker for a home bar that makes ice quickly",
    "best refrigerator water filter under 50 dollars",
]

MODELS = [
    ("qwen2.5:3b", "Qwen 2.5 (Alibaba, 3B)"),
    ("llama3.2:3b", "Llama 3.2 (Meta, 3B)"),
]

TOP_K = 5
PROMPT_VARIANT = "strict"
TEMPERATURE = 0.2
MAX_TOKENS = 350


def build_context(results: list) -> str:
    """Build context block from BM25 search results."""
    blocks = []
    for rank, sr in enumerate(results, start=1):
        doc = sr.document
        block = (
            f"[doc_id={rank}]\n"
            f"Title: {doc.get('title', 'N/A')}\n"
            f"Rating: {doc.get('rating', 'N/A')}\n"
            f"Category: {doc.get('category', 'N/A')}\n"
            f"Price: {doc.get('price', 'N/A')}\n"
            f"Description: {doc.get('description', 'N/A')}\n"
            f"Features: {doc.get('features', 'N/A')}\n"
            f"Review: {doc.get('review_text', 'N/A')}\n"
            f"BM25 Score: {sr.score:.4f}"
        )
        blocks.append(block)
    return "\n\n".join(blocks)


def build_prompt(query: str, context: str) -> str:
    """Build the prompt using the strict variant."""
    system_prompt = PROMPT_VARIANTS[PROMPT_VARIANT]
    return (
        f"SYSTEM:\n{system_prompt}\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION:\n{query}\n\n"
        "ANSWER:"
    )


def main():
    print("Loading documents...", flush=True)
    docs = ensure_search_text(load_documents())
    print(f"  {len(docs)} documents loaded", flush=True)

    print("Loading BM25 index...", flush=True)
    root = Path(__file__).resolve().parents[1]
    bm25 = BM25Retriever.load_index(root / "data" / "processed" / "bm25_index.pkl")
    print("  BM25 index loaded", flush=True)

    results_all = []

    for query in QUERIES:
        print(f"\nQuery: {query}", flush=True)

        # Retrieve once -- same context for both models
        search_results = bm25.search(query, top_k=TOP_K)
        context = build_context(search_results)
        prompt = build_prompt(query, context)

        retrieved_titles = [sr.document.get("title", "")[:80] for sr in search_results]

        query_result = {
            "query": query,
            "prompt": prompt,
            "retrieved_titles": retrieved_titles,
            "models": {},
        }

        for model_name, model_label in MODELS:
            print(f"  Running {model_label}...", flush=True)
            llm = OpenSourceChatModel(
                provider="ollama",
                model=model_name,
                temperature=TEMPERATURE,
                max_new_tokens=MAX_TOKENS,
            )
            messages = [{"role": "user", "content": prompt}]

            start = time.time()
            answer, _ = llm.chat(messages=messages)
            elapsed = time.time() - start

            query_result["models"][model_name] = {
                "label": model_label,
                "answer": answer.strip(),
                "time_seconds": round(elapsed, 1),
            }
            print(f"    Done in {elapsed:.1f}s", flush=True)

        results_all.append(query_result)

    # Save results
    output_path = root / "results" / "llm_comparison.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results_all, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}", flush=True)


if __name__ == "__main__":
    main()
