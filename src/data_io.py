"""Data loading utilities for the retrieval project."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import csv
import gzip
import json
import re


@dataclass(frozen=True)
class DocumentRecord:
    """Canonical document representation used by the retrievers."""

    record_id: str
    title: str
    review_text: str
    rating: float | None = None
    category: str | None = None
    price: str | None = None
    description: str | None = None
    features: str | None = None
    source: str | None = None

    @property
    def search_text(self) -> str:
        parts = [self.title, self.review_text, self.description, self.features, self.category]
        return " ".join(part for part in parts if part)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "title": self.title,
            "review_text": self.review_text,
            "rating": self.rating,
            "category": self.category,
            "price": self.price,
            "description": self.description,
            "features": self.features,
            "source": self.source,
            "search_text": self.search_text,
        }


SAMPLE_DOCUMENTS: list[DocumentRecord] = [
    DocumentRecord("demo-1", "Noise Cancelling Wireless Headphones", "Blocks engine noise on long flights and has comfortable ear pads for all-day listening.", 4.7, "electronics", description="Wireless over-ear headphones with active noise cancellation.", source="demo"),
    DocumentRecord("demo-2", "Insulated Stainless Steel Water Bottle 1 Liter", "Keeps water cold all day during hikes and fits easily into a backpack side pocket.", 4.8, "outdoor", description="Vacuum insulated bottle for hot and cold drinks.", source="demo"),
    DocumentRecord("demo-3", "Star Space Battle Building Set", "A fun educational toy for kids who like space ships, missions, and creative building.", 4.6, "toys", description="Building blocks inspired by space adventures.", source="demo"),
    DocumentRecord("demo-4", "Compact Air Fryer Oven", "Great for quick healthy meals and fits well in a small apartment kitchen.", 4.5, "kitchen", description="Countertop appliance for roasting, baking, and air frying.", source="demo"),
    DocumentRecord("demo-5", "Travel Neck Pillow with Memory Foam", "Makes long flights more comfortable and supports the neck without taking much luggage space.", 4.3, "travel", description="Soft neck pillow with removable cover.", source="demo"),
    DocumentRecord("demo-6", "Smart Blender for Smoothies", "Blends frozen fruit smoothly and the preset modes are easy to use every morning.", 4.4, "kitchen", description="High-speed blender for smoothies and soups.", source="demo"),
    DocumentRecord("demo-7", "Bluetooth Speaker for Outdoor Use", "Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.", 4.2, "electronics", description="Portable speaker with strong bass.", source="demo"),
    DocumentRecord("demo-8", "Educational Science Kit for Children", "Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.", 4.6, "toys", description="STEM learning kit with experiments.", source="demo"),
    DocumentRecord("demo-9", "Desk Lamp with Adjustable Brightness", "Useful for reading and working at night because the light levels are easy to adjust.", 4.1, "home", description="LED desk lamp with multiple brightness settings.", source="demo"),
    DocumentRecord("demo-10", "Budget Dishwasher Cleaner Tablets", "Keeps the dishwasher fresh and works well for regular maintenance.", 4.0, "home", description="Cleaning tablets for dishwashers.", source="demo"),
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value != value:
        return ""
    if isinstance(value, list):
        return " ".join(str(item) for item in value if item)
    return re.sub(r"\s+", " ", str(value)).strip()


def _open_text(path: Path):
    if path.suffix.lower() == ".gz" or path.name.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open("r", encoding="utf-8", newline="")


def _load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = "".join(path.suffixes).lower()
    if suffix.endswith(".csv"):
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    if suffix.endswith(".jsonl") or suffix.endswith(".jsonl.gz"):
        with _open_text(path) as handle:
            return [json.loads(line) for line in handle if line.strip()]
    if suffix.endswith(".json") or suffix.endswith(".json.gz"):
        with _open_text(path) as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return [payload]
        return []
    if suffix.endswith(".parquet"):
        try:
            import pandas as pd  # type: ignore

            dataframe = pd.read_parquet(path)
            return dataframe.to_dict(orient="records")
        except Exception:
            return []
    return []


def _to_document_records(rows: Iterable[dict[str, Any]], source: str) -> list[DocumentRecord]:
    rows = list(rows)
    if not rows:
        return []

    column_lookup = {str(column).lower(): column for column in rows[0].keys()}

    def pick(*names: str) -> str | None:
        for name in names:
            if name in column_lookup:
                return column_lookup[name]
        return None

    title_col = pick("title", "product_title", "name")
    text_col = pick("review_text", "text", "content", "description")
    rating_col = pick("rating", "overall", "stars")
    category_col = pick("category", "categories")
    price_col = pick("price")
    description_col = pick("description")
    features_col = pick("features", "feature")
    record_id_col = pick("record_id", "parent_asin", "asin", "id")

    records: list[DocumentRecord] = []
    for index, row in enumerate(rows):
        title = normalize_text(row.get(title_col)) if title_col else f"Document {index + 1}"
        review_text = normalize_text(row.get(text_col)) if text_col else normalize_text(row.get("review_text", ""))
        if not title and not review_text:
            continue

        record_id_value = normalize_text(row.get(record_id_col)) if record_id_col else str(index)
        rating_value = None
        if rating_col is not None:
            try:
                rating_value = float(row.get(rating_col))
            except (TypeError, ValueError):
                rating_value = None

        records.append(
            DocumentRecord(
                record_id=record_id_value or str(index),
                title=title,
                review_text=review_text,
                rating=rating_value,
                category=normalize_text(row.get(category_col)) if category_col else None,
                price=normalize_text(row.get(price_col)) if price_col else None,
                description=normalize_text(row.get(description_col)) if description_col else None,
                features=normalize_text(row.get(features_col)) if features_col else None,
                source=source,
            )
        )

    return records


def discover_data_file(data_dir: Path | None = None) -> Path | None:
    root = data_dir or (project_root() / "data" / "processed")
    if not root.exists():
        return None

    for pattern in ("*.csv", "*.parquet", "*.jsonl.gz", "*.jsonl", "*.json.gz", "*.json"):
        matches = sorted(root.glob(pattern))
        if matches:
            return matches[0]
    return None


def load_documents(data_path: Path | str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    """Load project documents or fall back to the included demo corpus."""

    if data_path is None:
        data_path = discover_data_file()

    if data_path is None:
        records = SAMPLE_DOCUMENTS.copy()
    else:
        path = Path(data_path)
        rows = _load_rows(path)
        records = _to_document_records(rows, path.name)
        if not records:
            records = SAMPLE_DOCUMENTS.copy()

    if limit is not None:
        records = records[:limit]

    return [record.to_dict() for record in records]


def format_rating_stars(rating: float | None) -> str:
    if rating is None:
        return "No rating"
    filled = max(0, min(5, int(round(rating))))
    return "★" * filled + "☆" * (5 - filled)


def truncate_text(text: str, max_chars: int = 200) -> str:
    clean_text = normalize_text(text)
    if len(clean_text) <= max_chars:
        return clean_text
    return clean_text[: max_chars - 1].rstrip() + "…"
