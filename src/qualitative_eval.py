"""Generate the Step 4 qualitative evaluation report."""

from __future__ import annotations

from pathlib import Path

from .data_io import discover_data_file, format_rating_stars, load_documents, project_root, truncate_text
from .ranking import BM25Retriever, SemanticRetriever, SearchResult, ensure_search_text


QUERY_SET = [
    ("Easy", "energy efficient dishwasher"),
    ("Easy", "refrigerator water filter replacement"),
    ("Easy", "portable countertop ice maker"),
    ("Medium", "dishwasher that runs quietly at night"),
    ("Medium", "small washing machine for apartment laundry"),
    ("Medium", "fridge filter that improves water taste"),
    ("Complex", "best compact dishwasher for a small apartment with low noise"),
    ("Complex", "nugget ice maker for a home bar that makes ice quickly"),
    ("Complex", "how to reduce washer vibration and noise during spin cycle"),
    ("Complex", "best refrigerator water filter under 50 dollars"),
]

COMPARISON_QUERIES = [
    "dishwasher that runs quietly at night",
    "small washing machine for apartment laundry",
    "fridge filter that improves water taste",
    "nugget ice maker for a home bar that makes ice quickly",
    "best refrigerator water filter under 50 dollars",
]


def _format_result_list(results: list[SearchResult]) -> str:
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


def _result_ids(results: list[SearchResult]) -> list[str]:
    return [str(result.document.get("record_id", "")) for result in results]


def _comparison_comments(query: str, bm25_results: list[SearchResult], semantic_results: list[SearchResult], top_k: int) -> list[str]:
    """Per-query observations derived from ranked lists (no external ground truth)."""
    bullets: list[str] = []
    if not bm25_results and not semantic_results:
        return ["- Neither method returned results for this query."]

    b_ids = _result_ids(bm25_results)
    s_ids = _result_ids(semantic_results)
    overlap = set(b_ids) & set(s_ids)

    if bm25_results and semantic_results:
        b1, s1 = bm25_results[0], semantic_results[0]
        t_b = b1.document.get("title", "Untitled")
        t_s = s1.document.get("title", "Untitled")
        if b_ids[0] == s_ids[0]:
            bullets.append(
                f"- **Agreement:** Both methods rank the same item first (**{t_b}**). BM25 score {b1.score:.4f} vs semantic {s1.score:.4f}."
            )
        else:
            bullets.append(
                f"- **Disagreement at rank 1:** BM25 prefers **{t_b}** (score {b1.score:.4f}); semantic prefers **{t_s}** (score {s1.score:.4f}). "
                "Lexical overlap can differ from embedding similarity when wording is indirect."
            )

    bullets.append(
        f"- **Top-{top_k} overlap:** {len(overlap)} distinct document(s) appear in both ranked lists "
        f"({'high' if len(overlap) >= 3 else 'moderate' if len(overlap) >= 2 else 'low'} agreement)."
    )

    b_set, s_set = set(b_ids), set(s_ids)
    only_b = b_set - s_set
    only_s = s_set - b_set
    if only_b:
        extras = [r.document.get("title", "") for r in bm25_results if str(r.document.get("record_id", "")) in only_b][:2]
        titles = ", ".join(f"**{t}**" for t in extras if t)
        if titles:
            bullets.append(
                f"- **BM25-only (in top-{top_k} for BM25, not semantic):** {titles}. "
                "Typical when rare tokens from the query match product text strongly while embeddings treat the overall intent as a weaker match."
            )
    if only_s:
        extras = [r.document.get("title", "") for r in semantic_results if str(r.document.get("record_id", "")) in only_s][:2]
        titles = ", ".join(f"**{t}**" for t in extras if t)
        if titles:
            bullets.append(
                f"- **Semantic-only (in top-{top_k} for semantic, not BM25):** {titles}. "
                "Shows cases where paraphrase or intent aligns in vector space without the exact query keywords."
            )

    lowered = query.lower()
    if any(word in lowered for word in ("$", "dollar", "under", "budget", "price")):
        bullets.append(
            "- **Constraint note:** Our indexed `search_text` does not include numeric **price** fields, so neither method truly optimizes for “under $X”; "
            "both approximate via words like “budget” or product copy if present. A reranker or metadata filter would help."
        )

    if len(semantic_results) >= 3 and semantic_results[0].score > 0:
        spread = semantic_results[0].score - semantic_results[-1].score
        if spread < 0.05:
            bullets.append(
                "- **Semantic scores:** Top scores are very close, so small embedding differences reorder items; ties/near-ties are common on short corpora."
            )

    if not bullets:
        bullets.append("- Compare the two ranked lists above for overlap and ordering differences.")

    return bullets


def _relative_to_repo(path: Path) -> str:
    root = project_root()
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _corpus_banner(data_path: Path | str | None, document_count: int) -> str:
    if data_path is not None:
        return f"**Data source:** `{_relative_to_repo(Path(data_path))}` — **{document_count}** documents after loading."
    discovered = discover_data_file()
    if discovered is not None:
        return f"**Data source:** `{_relative_to_repo(discovered)}` — **{document_count}** documents after loading."
    return (
        "**Data source:** built-in demo corpus (no parquet found under `data/processed/`). "
        f"**{document_count}** documents. Regenerate this report after `notebooks/milestone1_exploration.ipynb` "
        "produces `appliances_merged.parquet` (or run `python -m src.qualitative_eval` with `--data-path`)."
    )


def _resolve_eval_corpus(data_path: Path | str | None) -> tuple[list[dict[str, object]], Path | None]:
    """Return documents and the effective source path used for evaluation."""
    if data_path is not None:
        path = Path(data_path)
        return ensure_search_text(load_documents(data_path=path)), path

    discovered = discover_data_file()
    documents = ensure_search_text(load_documents())

    # If the default clean file is very small, prefer merged parquet for richer qualitative comparisons.
    if discovered is not None and discovered.name == "appliances_clean.parquet" and len(documents) < 20:
        merged_candidate = discovered.parent / "appliances_merged.parquet"
        if merged_candidate.exists():
            return ensure_search_text(load_documents(data_path=merged_candidate)), merged_candidate

    return documents, discovered


def generate_report(output_path: Path | None = None, data_path: Path | str | None = None, top_k: int = 5) -> Path:
    documents, effective_data_path = _resolve_eval_corpus(data_path)
    bm25 = BM25Retriever(documents)
    semantic = SemanticRetriever(documents)

    output_path = output_path or Path(__file__).resolve().parents[1] / "results" / "milestone1_discussion.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Step 4: Qualitative Evaluation")
    lines.append("")
    lines.append(_corpus_banner(effective_data_path, len(documents)))
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
        for bullet in _comparison_comments(query, bm25_results, semantic_results, top_k):
            lines.append(bullet)
        lines.append("")

    lines.append("## 4.4 Summarize Insights")
    lines.append("")
    lines.append(
        "- **BM25:** Best when the user query contains tokens that literally appear in titles or reviews (easy keyword queries). "
        "It can over-promote incidental keyword overlap (e.g., shared words across unrelated appliances)."
    )
    lines.append(
        "- **Semantic search:** Best when the query is phrased by intent (“quiet operation at night”) rather than exact product names. "
        "It can still return plausible-but-wrong items when many products share broad semantics in a small corpus."
    )
    lines.append(
        "- **Where BM25 tends to fail:** Synonyms and paraphrases that do not share stems with the document text; semantic search often recovers these."
    )
    lines.append(
        "- **Where semantic tends to fail:** Very specific SKU-like strings, rare brand tokens, or when every document looks moderately similar in embedding space; BM25 can be sharper."
    )
    lines.append(
        "- **Hard for both:** Multi-constraint questions (price + audience + scenario) without explicit features in the indexed text; hybrid fusion, metadata filters, or a reranker are natural next steps."
    )
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate results/milestone1_discussion.md from the current corpus.")
    parser.add_argument(
        "--data-path",
        type=str,
        default=None,
        help="Optional path to parquet/JSONL/CSV of documents (defaults to data/processed discovery).",
    )
    args = parser.parse_args()
    path = Path(args.data_path) if args.data_path else None
    out = generate_report(data_path=path)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
