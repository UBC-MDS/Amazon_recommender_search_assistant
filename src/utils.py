"""Compatibility utilities for corpus construction and tokenization."""

from __future__ import annotations

from typing import Any

from .data_io import build_search_text, normalize_text
from .ranking import tokenize


def build_corpus(documents: list[dict[str, Any]]) -> list[str]:
    """Build a searchable text corpus from structured document records."""
    return [build_search_text(document) for document in documents]


def tokenize_text(text: str) -> list[str]:
    """Tokenize text consistently for retrieval."""
    return tokenize(text)


def normalize_and_join(values: list[Any]) -> str:
    """Normalize values and join them into a single search string."""
    return " ".join(normalize_text(value) for value in values if normalize_text(value))
