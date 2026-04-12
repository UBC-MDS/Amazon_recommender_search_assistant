"""Shared ranking logic for BM25, semantic, and hybrid retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from math import sqrt
from typing import Any
import re

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
    """Small BM25 implementation that does not depend on external ranking packages."""

    def __init__(self, documents: list[dict[str, Any]], text_field: str = "search_text", k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.text_field = text_field
        self.k1 = k1
        self.b = b
        self._doc_tokens: list[list[str]] = []
        self._doc_lengths: list[int] = []
        self._doc_freq: dict[str, int] = {}
        self._avg_doc_length = 0.0
        self.fit()

    def fit(self) -> "BM25Retriever":
        self._doc_tokens = [tokenize(document.get(self.text_field, "")) for document in self.documents]
        self._doc_lengths = [len(tokens) for tokens in self._doc_tokens]
        self._avg_doc_length = sum(self._doc_lengths) / len(self._doc_lengths) if self._doc_lengths else 0.0

        self._doc_freq = {}
        for tokens in self._doc_tokens:
            for token in set(tokens):
                self._doc_freq[token] = self._doc_freq.get(token, 0) + 1

        return self

    def _idf(self, token: str) -> float:
        total_docs = len(self._doc_tokens)
        document_frequency = self._doc_freq.get(token, 0)
        return log((total_docs - document_frequency + 0.5) / (document_frequency + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not query:
            return []

        query_tokens = tokenize(query)
        scores: list[float] = []
        for doc_index, tokens in enumerate(self._doc_tokens):
            score = 0.0
            doc_length = self._doc_lengths[doc_index] or 1
            token_counts = {token: tokens.count(token) for token in set(tokens)}
            for token in query_tokens:
                frequency = token_counts.get(token, 0)
                if frequency == 0:
                    continue
                idf = self._idf(token)
                numerator = frequency * (self.k1 + 1.0)
                denominator = frequency + self.k1 * (1.0 - self.b + self.b * doc_length / (self._avg_doc_length or 1.0))
                score += idf * (numerator / denominator)
            scores.append(score)

        ranked = [item for item in sorted(enumerate(scores), key=lambda item: item[1], reverse=True) if item[1] > 0.0][:top_k]
        return [SearchResult(document=self.documents[index], score=float(score), method="BM25") for index, score in ranked]


class SemanticRetriever:
    """Semantic retriever using sentence-transformers when available, with TF-IDF fallback."""

    def __init__(self, documents: list[dict[str, Any]], text_field: str = "search_text"):
        self.documents = documents
        self.text_field = text_field
        self._texts = [normalize_text(document.get(self.text_field, "")) for document in documents]
        self._doc_vectors: list[dict[str, float]] = []
        self._doc_norms: list[float] = []
        self._term_document_frequency: dict[str, int] = {}
        self._document_count = len(self._texts)
        self.fit()

    def fit(self) -> "SemanticRetriever":
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

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not query:
            return []

        query_tokens = tokenize(query)
        query_vector = self._build_tfidf_vector(query_tokens)
        query_norm = sqrt(sum(weight * weight for weight in query_vector.values()))
        scores = [self._cosine_similarity(query_vector, query_norm, document_vector, document_norm) for document_vector, document_norm in zip(self._doc_vectors, self._doc_norms)]

        ranked = [item for item in sorted(enumerate(scores), key=lambda item: item[1], reverse=True) if item[1] > 0.0][:top_k]
        return [SearchResult(document=self.documents[index], score=float(score), method="Semantic") for index, score in ranked]


class HybridRetriever:
    """Combine BM25 and semantic scores using normalized score fusion."""

    def __init__(self, documents: list[dict[str, Any]], bm25_weight: float = 0.5, semantic_weight: float = 0.5):
        self.documents = documents
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        self.bm25 = BM25Retriever(documents)
        self.semantic = SemanticRetriever(documents)

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
