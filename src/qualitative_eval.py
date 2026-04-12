"""Generate the Step 4 qualitative evaluation report."""

from __future__ import annotations

from pathlib import Path

from .data_io import format_rating_stars, load_documents, truncate_text
from .ranking import BM25Retriever, SemanticRetriever, ensure_search_text


QUERY_SET = [
    ("Easy", "wireless bluetooth headphones"),
    ("Easy", "stainless steel water bottle 1 liter"),
    ("Easy", "kids lego star wars set"),
    ("Medium", "headphones that block airplane noise"),
    ("Medium", "something to keep water cold all day"),
    ("Medium", "toy for a child who likes space battles"),
    ("Complex", "best headphones for long flights under 200 dollars"),
    ("Complex", "what is a good educational toy for a 7-year-old interested in space"),
    ("Complex", "useful kitchen appliance for quick healthy meals in a small apartment"),
    ("Complex", "portable speaker for outdoor use with long battery life"),
]

COMPARISON_QUERIES = [
    "headphones that block airplane noise",
    "something to keep water cold all day",
    "toy for a child who likes space battles",
    "best headphones for long flights under 200 dollars",
    "what is a good educational toy for a 7-year-old interested in space",
]


def _format_result_list(results) -> str:
    lines = []
    for index, result in enumerate(results, start=1):
        document = result.document
        rating = document.get("rating")
        lines.append(
            f"{index}. **{document.get('title', 'Untitled')}**  \n"
            f"   - Review: {truncate_text(document.get('review_text', ''), 200)}  \n"
            f"   - Rating: {format_rating_stars(rating)} ({rating if rating is not None else 'n/a'})  \n"
            f"   - Score: {result.score:.4f}"
        )
    return "\n".join(lines)


def generate_report(output_path: Path | None = None, data_path: Path | str | None = None, top_k: int = 5) -> Path:
    documents = ensure_search_text(load_documents(data_path=data_path))
    bm25 = BM25Retriever(documents)
    semantic = SemanticRetriever(documents)

    output_path = output_path or Path(__file__).resolve().parents[1] / "results" / "milestone1_discussion.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Step 4: Qualitative Evaluation")
    lines.append("")
    lines.append("This report was generated from the currently available corpus. If no processed project corpus was found, the built-in demo corpus was used so the workflow remains runnable.")
    lines.append("")
    lines.append("## 4.1 Query Set")
    lines.append("")
    lines.append("| Difficulty | Query |")
    lines.append("|---|---|")
    for difficulty, query in QUERY_SET:
        lines.append(f"| {difficulty} | {query} |")
    lines.append("")
    lines.append("## 4.2 Retrieve Results")
    lines.append("")
    for difficulty, query in QUERY_SET:
        bm25_results = bm25.search(query, top_k=top_k)
        semantic_results = semantic.search(query, top_k=top_k)
        lines.append(f"### {query}")
        lines.append("")
        lines.append(f"**Difficulty:** {difficulty}")
        lines.append("")
        lines.append("**BM25 Top 5**")
        lines.append("")
        lines.append(_format_result_list(bm25_results) if bm25_results else "No results returned.")
        lines.append("")
        lines.append("**Semantic Top 5**")
        lines.append("")
        lines.append(_format_result_list(semantic_results) if semantic_results else "No results returned.")
        lines.append("")

    lines.append("## 4.3 Compare Results")
    lines.append("")
    for query in COMPARISON_QUERIES:
        bm25_results = bm25.search(query, top_k=top_k)
        semantic_results = semantic.search(query, top_k=top_k)
        lines.append(f"### {query}")
        lines.append("")
        lines.append("**BM25**")
        lines.append("")
        lines.append(_format_result_list(bm25_results) if bm25_results else "No results returned.")
        lines.append("")
        lines.append("**Semantic Search**")
        lines.append("")
        lines.append(_format_result_list(semantic_results) if semantic_results else "No results returned.")
        lines.append("")
        lines.append("**Comments**")
        lines.append("")
        lines.append("- BM25 is strongest when the query uses the same keywords that appear in the document text.")
        lines.append("- Semantic search is stronger for intent-driven phrasing and paraphrases.")
        lines.append("- Queries with constraints such as price, age, or use case may benefit from reranking or a hybrid approach.")
        lines.append("")

    lines.append("## 4.4 Summarize Insights")
    lines.append("")
    lines.append("- BM25 is generally strongest for short keyword queries with obvious lexical overlap.")
    lines.append("- Semantic retrieval handles broader intent better, but can surface loosely related results when the query is too vague.")
    lines.append("- Both methods can struggle when the query contains multiple constraints such as price, audience, and usage scenario.")
    lines.append("- Hybrid ranking or reranking would likely improve the hardest queries.")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main() -> None:
    generate_report()


if __name__ == "__main__":
    main()
