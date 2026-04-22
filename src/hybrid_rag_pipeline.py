"""Hybrid RAG pipeline: BM25 + semantic retrieval -> context -> prompt -> LLM."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .data_io import load_documents
from .llm_pipeline import OpenSourceChatModel
from .rag_pipeline import PROMPT_VARIANTS, RagResult, RetrievedDoc
from .ranking import BM25Retriever, SearchResult, SemanticRetriever, ensure_search_text


@dataclass(frozen=True)
class FusionConfig:
    """Configuration for combining BM25 and semantic retrieval signals."""

    mode: str = "rrf"
    bm25_weight: float = 0.4
    semantic_weight: float = 0.6
    rrf_k: int = 60
    initial_fetch_k: int = 25


class BM25DocumentRetriever:
    """Top-k BM25 retriever returning project-style RetrievedDoc objects."""

    def __init__(self, documents: list[dict[str, Any]], bm25: BM25Retriever | None = None):
        self.documents = ensure_search_text(documents)
        self.retriever = bm25 or BM25Retriever(self.documents)
        self.documents = self.retriever.documents
        self._doc_index = {id(document): index for index, document in enumerate(self.documents)}

    def retrieve(self, query: str, k: int = 5) -> list[RetrievedDoc]:
        """Retrieve top-k BM25 documents as RetrievedDoc objects."""
        results = self.retriever.search(query, top_k=k)
        return [RetrievedDoc(index=self._doc_index.get(id(result.document), -1), result=result) for result in results]


class HybridDocumentRetriever:
    """Hybrid retriever that combines BM25 and semantic results."""

    def __init__(
        self,
        documents: list[dict[str, Any]],
        bm25: BM25Retriever | None = None,
        semantic: SemanticRetriever | None = None,
        fusion: FusionConfig | None = None,
    ):
        self.documents = ensure_search_text(documents)
        self.bm25 = bm25 or BM25Retriever(self.documents)
        self.semantic = semantic or SemanticRetriever(self.documents)
        self.fusion = fusion or FusionConfig()
        self.documents = self.bm25.documents
        self._doc_index = {id(document): index for index, document in enumerate(self.documents)}

    def _dedup_by_index(self, results: list[SearchResult]) -> list[SearchResult]:
        """Remove duplicate documents while preserving first-seen order."""
        seen: set[int] = set()
        deduped: list[SearchResult] = []
        for result in results:
            index = self._doc_index.get(id(result.document), -1)
            if index in seen:
                continue
            seen.add(index)
            deduped.append(result)
        return deduped

    def _combine_simple_merge(self, bm25_results: list[SearchResult], semantic_results: list[SearchResult], top_k: int) -> list[SearchResult]:
        """Merge BM25 and semantic lists by concatenation and truncation."""
        merged = bm25_results[:top_k] + semantic_results[:top_k]
        return merged[:top_k]

    def _combine_merge_dedup(self, bm25_results: list[SearchResult], semantic_results: list[SearchResult], top_k: int) -> list[SearchResult]:
        """Merge both lists and drop duplicates by document identity."""
        merged = bm25_results + semantic_results
        deduped = self._dedup_by_index(merged)
        return deduped[:top_k]

    def _combine_rrf(self, bm25_results: list[SearchResult], semantic_results: list[SearchResult], top_k: int) -> list[SearchResult]:
        """Fuse rankings with weighted Reciprocal Rank Fusion (RRF)."""
        # Reciprocal Rank Fusion: score = sum(weight / (rrf_k + rank)).
        scores_by_index: dict[int, float] = {}
        docs_by_index: dict[int, dict[str, Any]] = {}

        for rank, result in enumerate(bm25_results, start=1):
            index = self._doc_index.get(id(result.document), -1)
            if index < 0:
                continue
            docs_by_index[index] = result.document
            scores_by_index[index] = scores_by_index.get(index, 0.0) + self.fusion.bm25_weight * (1.0 / (self.fusion.rrf_k + rank))

        for rank, result in enumerate(semantic_results, start=1):
            index = self._doc_index.get(id(result.document), -1)
            if index < 0:
                continue
            docs_by_index[index] = result.document
            scores_by_index[index] = scores_by_index.get(index, 0.0) + self.fusion.semantic_weight * (1.0 / (self.fusion.rrf_k + rank))

        ranked = sorted(scores_by_index.items(), key=lambda item: item[1], reverse=True)[:top_k]
        return [
            SearchResult(document=docs_by_index[index], score=float(score), method="Hybrid-RRF")
            for index, score in ranked
        ]

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Run hybrid retrieval and combine results using configured fusion."""
        if not query:
            return []

        fetch_k = max(top_k, self.fusion.initial_fetch_k)
        bm25_results = self.bm25.search(query, top_k=fetch_k)
        semantic_results = self.semantic.search(query, top_k=fetch_k)

        if self.fusion.mode == "simple-merge":
            return self._combine_simple_merge(bm25_results, semantic_results, top_k)
        if self.fusion.mode == "merge-dedup":
            return self._combine_merge_dedup(bm25_results, semantic_results, top_k)
        return self._combine_rrf(bm25_results, semantic_results, top_k)

    def retrieve(self, query: str, k: int = 5) -> list[RetrievedDoc]:
        """Return top-k hybrid results with mapped document indices."""
        return [
            RetrievedDoc(index=self._doc_index.get(id(result.document), -1), result=result)
            for result in self.search(query, top_k=k)
        ]


class HybridRAGPipeline:
    """RAG pipeline using a hybrid BM25 + semantic retriever."""

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
        bm25: BM25Retriever | None = None,
        semantic: SemanticRetriever | None = None,
        fusion: FusionConfig | None = None,
    ):
        self.documents = ensure_search_text(documents)
        self.default_k = default_k
        self.hybrid_retriever = HybridDocumentRetriever(
            documents=self.documents,
            bm25=bm25,
            semantic=semantic,
            fusion=fusion,
        )
        self.documents = self.hybrid_retriever.documents
        self.llm = OpenSourceChatModel(
            provider=provider,
            model=model,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            hf_token=hf_token,
            ollama_host=ollama_host,
        )

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
        bm25_index_path: str | Path | None = None,
        semantic_index_dir: str | Path | None = None,
        fusion: FusionConfig | None = None,
    ) -> "HybridRAGPipeline":
        documents = ensure_search_text(load_documents(data_path=data_path))
        bm25: BM25Retriever | None = None
        semantic: SemanticRetriever | None = None

        root = Path(__file__).resolve().parents[1]
        if bm25_index_path is None and data_path is None:
            default_bm25 = root / "data" / "processed" / "bm25_index.pkl"
            bm25_index_path = default_bm25 if default_bm25.exists() else None
        if semantic_index_dir is None and data_path is None:
            default_semantic = root / "data" / "processed" / "semantic_faiss"
            semantic_index_dir = default_semantic if default_semantic.exists() else None

        if bm25_index_path is not None:
            try:
                bm25 = BM25Retriever.load_index(bm25_index_path)
            except Exception:
                bm25 = None

        if semantic_index_dir is not None:
            index_dir = Path(semantic_index_dir)
            if (index_dir / "index.faiss").exists() and (index_dir / "metadata.json").exists():
                try:
                    semantic = SemanticRetriever.load_index(index_dir)
                except Exception:
                    semantic = None

        if semantic is not None:
            documents = semantic.documents
        elif bm25 is not None:
            documents = bm25.documents

        return cls(
            documents=documents,
            provider=provider,
            model=model,
            default_k=default_k,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            hf_token=hf_token,
            ollama_host=ollama_host,
            bm25=bm25,
            semantic=semantic,
            fusion=fusion,
        )

    def retrieve(self, query: str, k: int | None = None) -> list[RetrievedDoc]:
        """Retrieve top-k hybrid results using the project retriever."""
        return self.hybrid_retriever.retrieve(query=query, k=k or self.default_k)

    def retrieve_indices(self, query: str, k: int | None = None) -> list[int]:
        """Return only retrieved document indices for evaluation workflows."""
        return [item.index for item in self.retrieve(query=query, k=k)]

    def build_context(self, retrieved_docs: list[RetrievedDoc]) -> str:
        """Format retrieved records into a context block for prompting."""
        blocks: list[str] = []
        for rank, item in enumerate(retrieved_docs, start=1):
            document = item.result.document
            block = (
                f"[doc_id={item.index} | rank={rank}]\n"
                f"Record ID: {document.get('record_id', 'N/A')}\n"
                f"Title: {document.get('title', '')}\n"
                f"Rating: {document.get('rating', 'N/A')}\n"
                f"Category: {document.get('category', 'N/A')}\n"
                f"Price: {document.get('price', 'N/A')}\n"
                f"Description: {document.get('description', 'N/A')}\n"
                f"Features: {document.get('features', 'N/A')}\n"
                f"Review: {document.get('review_text', 'N/A')}\n"
                f"Hybrid Score: {item.result.score:.4f}\n"
                f"Source Method: {item.result.method}"
            )
            blocks.append(block)
        return "\n\n".join(blocks)

    def build_prompt(self, query: str, context: str, prompt_variant: str = "strict") -> str:
        """Build final prompt string using a selected project prompt variant."""
        system_prompt = PROMPT_VARIANTS.get(prompt_variant, PROMPT_VARIANTS["strict"])
        return (
            f"SYSTEM:\n{system_prompt}\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{query}\n\n"
            "ANSWER:"
        )

    def answer(self, query: str, k: int | None = None, prompt_variant: str = "strict") -> RagResult:
        """Run end-to-end hybrid retrieval and LLM generation."""
        retrieved_docs = self.retrieve(query=query, k=k)
        context = self.build_context(retrieved_docs)
        prompt = self.build_prompt(query=query, context=context, prompt_variant=prompt_variant)
        answer_text, _ = self.llm.chat(messages=[{"role": "user", "content": prompt}])

        return RagResult(
            answer=answer_text.strip(),
            query=query,
            prompt_variant=prompt_variant,
            retrieved_indices=[item.index for item in retrieved_docs],
            retrieved_results=[item.result for item in retrieved_docs],
            context=context,
            prompt=prompt,
        )


def build_default_hybrid_rag_pipeline(
    data_path: str | Path | None = None,
    provider: str = "huggingface",
    model: str = "Qwen/Qwen3.5-2B",
    default_k: int = 5,
    temperature: float = 0.2,
    max_new_tokens: int = 350,
    hf_token: str | None = None,
    ollama_host: str | None = None,
    bm25_index_path: str | Path | None = None,
    semantic_index_dir: str | Path | None = None,
    fusion: FusionConfig | None = None,
) -> HybridRAGPipeline:
    """Construct a HybridRAGPipeline with project defaults and saved indexes."""
    return HybridRAGPipeline.from_project_data(
        data_path=data_path,
        provider=provider,
        model=model,
        default_k=default_k,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        hf_token=hf_token,
        ollama_host=ollama_host,
        bm25_index_path=bm25_index_path,
        semantic_index_dir=semantic_index_dir,
        fusion=fusion,
    )


def run_example() -> None:
    """Run a local smoke-test query through the hybrid pipeline."""
    pipeline = build_default_hybrid_rag_pipeline(
        fusion=FusionConfig(mode="rrf", bm25_weight=0.4, semantic_weight=0.6),
    )
    query = "quiet dishwasher for a small apartment"
    result = pipeline.answer(query=query, k=5, prompt_variant="strict")
    print("Query:", result.query)
    print("Retrieved indices:", result.retrieved_indices)
    print("Answer:\n", result.answer)


if __name__ == "__main__":
    run_example()