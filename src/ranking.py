"""Shared ranking logic for BM25, semantic, and hybrid retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from math import sqrt
from pathlib import Path
from typing import Any
import json
import pickle
import re

import numpy as np
from rank_bm25 import BM25Okapi

from .data_io import normalize_text


@dataclass(frozen=True)
class SearchResult:
    """A single ranked result."""

    document: dict[str, Any]
    score: float
    method: str


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalize_text(text).lower())


def _safe_min_max(values: list[float]) -> list[float]:
    if not values:
        return []
    minimum = min(values)
    maximum = max(values)
    if maximum == minimum:
        return [0.0 for _ in values]
    return [(value - minimum) / (maximum - minimum) for value in values]


class BM25Retriever:
    """BM25 retriever backed by rank_bm25."""

    def __init__(self, documents: list[dict[str, Any]], text_field: str = "search_text", k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.text_field = text_field
        self.k1 = k1
        self.b = b
        self._doc_tokens: list[list[str]] = []
        self._doc_lengths: list[int] = []
        self._doc_freq: dict[str, int] = {}
        self._avg_doc_length = 0.0
        self._bm25: BM25Okapi | None = None
        self.fit()

    def fit(self) -> "BM25Retriever":
        self._doc_tokens = [tokenize(document.get(self.text_field, "")) for document in self.documents]
        self._doc_lengths = [len(tokens) for tokens in self._doc_tokens]
        self._avg_doc_length = sum(self._doc_lengths) / len(self._doc_lengths) if self._doc_lengths else 0.0

        self._doc_freq = {}
        for tokens in self._doc_tokens:
            for token in set(tokens):
                self._doc_freq[token] = self._doc_freq.get(token, 0) + 1

        # rank_bm25 handles IDF and BM25 scoring internals.
        self._bm25 = BM25Okapi(self._doc_tokens, k1=self.k1, b=self.b)

        return self

    def _idf(self, token: str) -> float:
        total_docs = len(self._doc_tokens)
        document_frequency = self._doc_freq.get(token, 0)
        return log((total_docs - document_frequency + 0.5) / (document_frequency + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not query:
            return []

        query_tokens = tokenize(query)
        if not query_tokens or self._bm25 is None:
            return []

        scores = np.asarray(self._bm25.get_scores(query_tokens), dtype=float)
        ranked_indices = np.argsort(scores)[::-1]
        ranked = [(int(index), float(scores[index])) for index in ranked_indices if scores[index] > 0.0][:top_k]
        return [SearchResult(document=self.documents[index], score=float(score), method="BM25") for index, score in ranked]

    def save_index(self, output_path: str | Path) -> Path:
        """Persist BM25 index state to disk using pickle."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "documents": self.documents,
            "text_field": self.text_field,
            "k1": self.k1,
            "b": self.b,
            "doc_tokens": self._doc_tokens,
            "doc_lengths": self._doc_lengths,
            "doc_freq": self._doc_freq,
            "avg_doc_length": self._avg_doc_length,
            "bm25_model": self._bm25,
        }
        with path.open("wb") as handle:
            pickle.dump(payload, handle)
        return path

    @classmethod
    def load_index(cls, input_path: str | Path) -> "BM25Retriever":
        """Load a persisted BM25 index from disk."""
        path = Path(input_path)
        with path.open("rb") as handle:
            payload = pickle.load(handle)

        retriever = cls.__new__(cls)
        retriever.documents = payload["documents"]
        retriever.text_field = payload["text_field"]
        retriever.k1 = payload["k1"]
        retriever.b = payload["b"]
        retriever._doc_tokens = payload["doc_tokens"]
        retriever._doc_lengths = payload.get("doc_lengths", [len(tokens) for tokens in retriever._doc_tokens])
        retriever._doc_freq = payload.get("doc_freq", {})
        retriever._avg_doc_length = payload.get("avg_doc_length", 0.0)
        retriever._bm25 = payload.get("bm25_model")
        if retriever._bm25 is None:
            retriever._bm25 = BM25Okapi(retriever._doc_tokens, k1=retriever.k1, b=retriever.b)
        return retriever


class SemanticRetriever:
    """Semantic retriever using sentence-transformers when available, with TF-IDF fallback."""

    def __init__(self, documents: list[dict[str, Any]], text_field: str = "search_text"):
        self.documents = documents
        self.text_field = text_field
        self._texts = [normalize_text(document.get(self.text_field, "")) for document in documents]
        self._backend = "tfidf"
        self._model_name = "all-MiniLM-L6-v2"
        self._model = None
        self._embeddings: list[list[float]] = []
        self._faiss_index = None
        self._doc_vectors: list[dict[str, float]] = []
        self._doc_norms: list[float] = []
        self._term_document_frequency: dict[str, int] = {}
        self._document_count = len(self._texts)
        self.fit()

    def fit(self) -> "SemanticRetriever":
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            embeddings = self._model.encode(self._texts, normalize_embeddings=True)
            self._embeddings = [list(vector) for vector in embeddings.tolist()]
            self._backend = "sentence-transformers"
            return self
        except Exception:
            self._backend = "tfidf"

        self._term_document_frequency = {}
        tokenized_documents = [tokenize(text) for text in self._texts]
        for tokens in tokenized_documents:
            for token in set(tokens):
                self._term_document_frequency[token] = self._term_document_frequency.get(token, 0) + 1

        self._doc_vectors = [self._build_tfidf_vector(tokens) for tokens in tokenized_documents]
        self._doc_norms = [sqrt(sum(weight * weight for weight in vector.values())) for vector in self._doc_vectors]
        return self

    def _idf(self, token: str) -> float:
        document_frequency = self._term_document_frequency.get(token, 0)
        return log((self._document_count + 1.0) / (document_frequency + 1.0)) + 1.0

    def _build_tfidf_vector(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        token_counts: dict[str, int] = {}
        for token in tokens:
            token_counts[token] = token_counts.get(token, 0) + 1
        total_tokens = len(tokens)
        vector: dict[str, float] = {}
        for token, count in token_counts.items():
            tf = count / total_tokens
            vector[token] = tf * self._idf(token)
        return vector

    def _cosine_similarity(self, query_vector: dict[str, float], query_norm: float, document_vector: dict[str, float], document_norm: float) -> float:
        if not query_vector or not document_vector or query_norm == 0.0 or document_norm == 0.0:
            return 0.0
        overlap = set(query_vector).intersection(document_vector)
        dot_product = sum(query_vector[token] * document_vector[token] for token in overlap)
        return dot_product / (query_norm * document_norm)

    def _cosine_dense(self, query_vector: list[float], document_vector: list[float]) -> float:
        if not query_vector or not document_vector:
            return 0.0
        dot_product = sum(query_value * document_value for query_value, document_value in zip(query_vector, document_vector))
        query_norm = sqrt(sum(value * value for value in query_vector))
        document_norm = sqrt(sum(value * value for value in document_vector))
        if query_norm == 0.0 or document_norm == 0.0:
            return 0.0
        return dot_product / (query_norm * document_norm)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not query:
            return []

        if self._backend == "faiss" and self._model is not None and self._faiss_index is not None:
            query_embedding = self._model.encode([query], normalize_embeddings=True)
            query_vector = np.asarray(query_embedding, dtype="float32")
            scores, indices = self._faiss_index.search(query_vector, min(top_k, len(self.documents)))
            ranked = [
                (int(index), float(score))
                for index, score in zip(indices[0].tolist(), scores[0].tolist())
                if index >= 0 and score > 0.0
            ]
            return [SearchResult(document=self.documents[index], score=score, method="Semantic") for index, score in ranked]

        if self._backend == "sentence-transformers" and self._model is not None:
            query_embedding = self._model.encode([query], normalize_embeddings=True)
            query_vector = list(query_embedding.tolist()[0])
            scores = [self._cosine_dense(query_vector, document_vector) for document_vector in self._embeddings]
        else:
            query_tokens = tokenize(query)
            query_vector = self._build_tfidf_vector(query_tokens)
            query_norm = sqrt(sum(weight * weight for weight in query_vector.values()))
            scores = [self._cosine_similarity(query_vector, query_norm, document_vector, document_norm) for document_vector, document_norm in zip(self._doc_vectors, self._doc_norms)]

        ranked = [item for item in sorted(enumerate(scores), key=lambda item: item[1], reverse=True) if item[1] > 0.0][:top_k]
        return [SearchResult(document=self.documents[index], score=float(score), method="Semantic") for index, score in ranked]

    def save_index(self, index_dir: str | Path) -> Path:
        """Persist semantic FAISS index and metadata to disk."""
        if self._backend != "sentence-transformers" or not self._embeddings:
            raise ValueError("Semantic FAISS index requires sentence-transformers embeddings.")

        import faiss

        directory = Path(index_dir)
        directory.mkdir(parents=True, exist_ok=True)
        index_path = directory / "index.faiss"
        metadata_path = directory / "metadata.json"

        matrix = np.asarray(self._embeddings, dtype="float32")
        faiss.normalize_L2(matrix)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        faiss.write_index(index, str(index_path))

        metadata = {
            "documents": self.documents,
            "text_field": self.text_field,
            "model_name": self._model_name,
        }
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        return directory

    @classmethod
    def load_index(cls, index_dir: str | Path) -> "SemanticRetriever":
        """Load a persisted FAISS semantic index and model."""
        import faiss
        from sentence_transformers import SentenceTransformer

        directory = Path(index_dir)
        index_path = directory / "index.faiss"
        metadata_path = directory / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        retriever = cls.__new__(cls)
        retriever.documents = metadata["documents"]
        retriever.text_field = metadata.get("text_field", "search_text")
        retriever._texts = [normalize_text(document.get(retriever.text_field, "")) for document in retriever.documents]
        retriever._backend = "faiss"
        retriever._model_name = metadata.get("model_name", "all-MiniLM-L6-v2")
        retriever._model = SentenceTransformer(retriever._model_name)
        retriever._embeddings = []
        retriever._faiss_index = faiss.read_index(str(index_path))
        retriever._doc_vectors = []
        retriever._doc_norms = []
        retriever._term_document_frequency = {}
        retriever._document_count = len(retriever._texts)
        return retriever


class HybridRetriever:
    """Combine BM25 and semantic scores using normalized score fusion."""

    def __init__(
        self,
        documents: list[dict[str, Any]],
        bm25_weight: float = 0.5,
        semantic_weight: float = 0.5,
        bm25: BM25Retriever | None = None,
        semantic: SemanticRetriever | None = None,
    ):
        self.documents = documents
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        self.bm25 = bm25 or BM25Retriever(documents)
        self.semantic = semantic or SemanticRetriever(documents)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not query:
            return []

        bm25_results = self.bm25.search(query, top_k=len(self.documents))
        semantic_results = self.semantic.search(query, top_k=len(self.documents))

        bm25_normalized = dict(zip([result.document.get("record_id") for result in bm25_results], _safe_min_max([result.score for result in bm25_results])))
        semantic_normalized = dict(zip([result.document.get("record_id") for result in semantic_results], _safe_min_max([result.score for result in semantic_results])))

        document_lookup = {document.get("record_id"): document for document in self.documents}
        combined: list[SearchResult] = []
        for record_id, document in document_lookup.items():
            combined_score = (
                self.bm25_weight * bm25_normalized.get(record_id, 0.0)
                + self.semantic_weight * semantic_normalized.get(record_id, 0.0)
            )
            if combined_score > 0.0:
                combined.append(SearchResult(document=document, score=combined_score, method="Hybrid"))

        return sorted(combined, key=lambda result: result.score, reverse=True)[:top_k]


def build_search_text(document: dict[str, Any]) -> str:
    parts = [document.get("title", ""), document.get("review_text", ""), document.get("description", ""), document.get("features", ""), document.get("category", "")]
    return " ".join(part for part in parts if part)


def ensure_search_text(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared = []
    for document in documents:
        prepared_document = dict(document)
        prepared_document.setdefault("search_text", build_search_text(prepared_document))
        prepared.append(prepared_document)
    return prepared
