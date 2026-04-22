"""Feedback persistence helpers for the app."""

from __future__ import annotations

from csv import DictWriter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def append_feedback(csv_path: Path, row: dict[str, Any]) -> None:
    """Append one feedback record to CSV, creating parent dirs and header."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = DictWriter(
            handle,
            fieldnames=["timestamp", "query", "mode", "rank", "record_id", "title", "score", "rating", "feedback", "source"],
        )
        if not file_exists:
            writer.writeheader()
        payload = {"timestamp": datetime.now(timezone.utc).isoformat(), **row}
        writer.writerow(payload)
