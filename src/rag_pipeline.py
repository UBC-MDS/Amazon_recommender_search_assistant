"""Semantic RAG pipeline for Milestone 2.

This module implements a custom Python RAG workflow:
retrieval -> context building -> prompt templating -> LLM generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .data_io import load_documents
from .llm_pipeline import OpenSourceChatModel
from .ranking import SearchResult, SemanticRetriever, ensure_search_text


PROMPT_VARIANTS: dict[str, str] = {
    "strict": (
        "You are a helpful Amazon shopping assistant. "
        "Answer using ONLY the provided context. "
        "If context is insufficient, say 'I do not have enough evidence'. "
        "Cite supporting products with [doc_id]."
    ),
    "concise": (
        "You answer customer product questions with short, practical recommendations. "
        "Use only the provided context, avoid speculation, and cite [doc_id]."
    ),
    "analyst": (
        "You are a product review analyst. "
        "Summarize evidence from context, mention trade-offs, and cite [doc_id] for each key claim."
    ),
}


@dataclass(frozen=True)
class RetrievedDoc:
    """Structured retrieval output used by downstream RAG steps."""

    index: int
    result: SearchResult


@dataclass(frozen=True)
class RagResult:
    """Final RAG output with answer and traceable retrieval artifacts."""

    answer: str
    query: str
    prompt_variant: str
    retrieved_indices: list[int]
    retrieved_results: list[SearchResult]
    context: str
    prompt: str


class SemanticRAGPipeline:
    """Custom semantic RAG pipeline built on the project semantic retriever."""

    def __init__(
        self,
        documents: list[dict[str, Any]],
        provider: str = "huggingface",
        model: str = "Qwen/Qwen3.5-2B",
        default_k: int = 5,
        temperature: float = 0.2,
        max_new_tokens: int = 350,
        hf_token: str | None = None,
        ollama_host: str | None = None,
        retriever: SemanticRetriever | None = None,
    ):
        self.documents = ensure_search_text(documents)
        self.default_k = default_k
        self.retriever = retriever or SemanticRetriever(self.documents)
        # Keep document views aligned with whichever retriever backend is active.
        self.documents = self.retriever.documents
        self.llm = OpenSourceChatModel(
            provider=provider,
            model=model,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            hf_token=hf_token,
            ollama_host=ollama_host,
        )
        self._doc_index = {id(document): index for index, document in enumerate(self.documents)}

    @classmethod
    def from_project_data(
        cls,
        data_path: str | Path | None = None,
        provider: str = "huggingface",
        model: str = "Qwen/Qwen3.5-2B",
        default_k: int = 5,
        temperature: float = 0.2,
        max_new_tokens: int = 350,
        hf_token: str | None = None,
        ollama_host: str | None = None,
        semantic_index_dir: str | Path | None = None,
    ) -> "SemanticRAGPipeline":
        documents = load_documents(data_path=data_path)
        retriever: SemanticRetriever | None = None

        if semantic_index_dir is None and data_path is None:
            root = Path(__file__).resolve().parents[1]
            default_dir = root / "data" / "processed" / "semantic_faiss"
            semantic_index_dir = default_dir if default_dir.exists() else None

        if semantic_index_dir is not None:
            index_dir = Path(semantic_index_dir)
            if (index_dir / "index.faiss").exists() and (index_dir / "metadata.json").exists():
                try:
                    retriever = SemanticRetriever.load_index(index_dir)
                    documents = retriever.documents
                except Exception:
                    retriever = None

        return cls(
            documents=documents,
            provider=provider,
            model=model,
            default_k=default_k,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            hf_token=hf_token,
            ollama_host=ollama_host,
            retriever=retriever,
        )

    def retrieve(self, query: str, k: int | None = None) -> list[RetrievedDoc]:
        """Run semantic retrieval and return top-k indices + SearchResults."""
        top_k = k or self.default_k
        results = self.retriever.search(query, top_k=top_k)
        retrieved: list[RetrievedDoc] = []
        for result in results:
            index = self._doc_index.get(id(result.document), -1)
            retrieved.append(RetrievedDoc(index=index, result=result))
        return retrieved

    def retrieve_indices(self, query: str, k: int | None = None) -> list[int]:
        """Return only top-k document indices for evaluation/reporting."""
        return [item.index for item in self.retrieve(query=query, k=k)]

    def build_context(self, retrieved_docs: list[RetrievedDoc]) -> str:
        """Convert retrieved docs into a prompt-ready context block."""
        blocks: list[str] = []
        for rank, item in enumerate(retrieved_docs, start=1):
            document = item.result.document
            record_id = document.get("record_id", "N/A")
            title = document.get("title", "")
            rating = document.get("rating")
            category = document.get("category")
            price = document.get("price")
            review_text = document.get("review_text", "")
            description = document.get("description", "")
            features = document.get("features", "")

            block = (
                f"[doc_id={item.index} | rank={rank}]\n"
                f"Record ID: {record_id}\n"
                f"Title: {title}\n"
                f"Rating: {rating if rating is not None else 'N/A'}\n"
                f"Category: {category if category else 'N/A'}\n"
                f"Price: {price if price else 'N/A'}\n"
                f"Description: {description if description else 'N/A'}\n"
                f"Features: {features if features else 'N/A'}\n"
                f"Review: {review_text if review_text else 'N/A'}\n"
                f"Semantic Score: {item.result.score:.4f}"
            )
            blocks.append(block)
        return "\n\n".join(blocks)

    def build_prompt(self, query: str, context: str, prompt_variant: str = "strict") -> str:
        """Build prompt text from query and retrieved context."""
        system_prompt = PROMPT_VARIANTS.get(prompt_variant, PROMPT_VARIANTS["strict"])
        return (
            f"SYSTEM:\n{system_prompt}\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{query}\n\n"
            "ANSWER:"
        )

    def answer(
        self,
        query: str,
        k: int | None = None,
        prompt_variant: str = "strict",
    ) -> RagResult:
        """Run the full semantic RAG pipeline and return traceable artifacts."""
        retrieved_docs = self.retrieve(query=query, k=k)
        context = self.build_context(retrieved_docs)
        prompt = self.build_prompt(query=query, context=context, prompt_variant=prompt_variant)

        messages = [{"role": "user", "content": prompt}]
        answer_text, _ = self.llm.chat(messages=messages)

        return RagResult(
            answer=answer_text.strip(),
            query=query,
            prompt_variant=prompt_variant,
            retrieved_indices=[item.index for item in retrieved_docs],
            retrieved_results=[item.result for item in retrieved_docs],
            context=context,
            prompt=prompt,
        )


def build_default_rag_pipeline(
    data_path: str | Path | None = None,
    provider: str = "huggingface",
    model: str = "Qwen/Qwen3.5-2B",
    default_k: int = 5,
    temperature: float = 0.2,
    max_new_tokens: int = 350,
    hf_token: str | None = None,
    ollama_host: str | None = None,
    semantic_index_dir: str | Path | None = None,
) -> SemanticRAGPipeline:
    """Project-level factory for a semantic RAG pipeline instance."""
    return SemanticRAGPipeline.from_project_data(
        data_path=data_path,
        provider=provider,
        model=model,
        default_k=default_k,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        hf_token=hf_token,
        ollama_host=ollama_host,
        semantic_index_dir=semantic_index_dir,
    )


def analyze_k_values(
    pipeline: SemanticRAGPipeline,
    queries: list[str],
    k_values: list[int] | None = None,
) -> dict[int, dict[str, float]]:
    """Simple retrieval analysis for selecting k.

    Returns average top score and average unique category count per query for each k.
    """
    if not queries:
        return {}

    k_values = k_values or [3, 5, 8]
    summary: dict[int, dict[str, float]] = {}

    for k in k_values:
        top_scores: list[float] = []
        diversities: list[float] = []
        for query in queries:
            retrieved_docs = pipeline.retrieve(query=query, k=k)
            if not retrieved_docs:
                top_scores.append(0.0)
                diversities.append(0.0)
                continue
            top_scores.append(retrieved_docs[0].result.score)
            categories = {
                str(item.result.document.get("category", "")).strip().lower()
                for item in retrieved_docs
                if str(item.result.document.get("category", "")).strip()
            }
            diversities.append(float(len(categories)))

        summary[k] = {
            "avg_top_score": sum(top_scores) / len(top_scores),
            "avg_category_diversity": sum(diversities) / len(diversities),
        }

    return summary


def run_example() -> None:
    """CLI-friendly sanity check for local development."""
    pipeline = build_default_rag_pipeline()
    query = "Energy efficient dishwasher under 500 dollars"
    result = pipeline.answer(query=query, k=5, prompt_variant="strict")
    print("Query:", result.query)
    print("Retrieved indices:", result.retrieved_indices)
    print("Answer:\n", result.answer)


if __name__ == "__main__":
    run_example()