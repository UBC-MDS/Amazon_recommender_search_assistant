"""Download full Appliances dataset and build product-level parquet."""

from __future__ import annotations

from pathlib import Path

import duckdb

CATEGORY = "Appliances"
BASE_URL = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw"
REVIEWS_URL = f"{BASE_URL}/review_categories/{CATEGORY}.jsonl.gz"
META_URL = f"{BASE_URL}/meta_categories/meta_{CATEGORY}.jsonl.gz"

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def main():
    """Download Appliances review/meta files and write product-level parquet."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()

    reviews_path = str(RAW_DIR / "reviews_full.parquet")
    if Path(reviews_path).exists():
        print("reviews parquet already exists, skipping download")
    else:
        print("downloading full reviews ...")
        con.execute(f"""
            COPY (SELECT * FROM read_json_auto('{REVIEWS_URL}'))
            TO '{reviews_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
    n_reviews = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{reviews_path}')"
    ).fetchone()[0]
    print(f"  reviews: {n_reviews} rows")

    meta_path = str(RAW_DIR / "meta_full.parquet")
    if Path(meta_path).exists():
        print("metadata parquet already exists, skipping download")
    else:
        print("downloading full metadata ...")
        con.execute(f"""
            COPY (
                SELECT * FROM read_json_auto(
                    '{META_URL}',
                    union_by_name=true,
                    ignore_errors=true
                )
            )
            TO '{meta_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
    n_meta = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{meta_path}')"
    ).fetchone()[0]
    print(f"  metadata: {n_meta} rows")

    merged_path = str(PROCESSED_DIR / "appliances_merged_full.parquet")
    print("merging reviews + metadata ...")
    con.execute(f"""
        COPY (
            SELECT
                r.rating,
                r.title  AS review_title,
                r.text   AS review_text,
                r.asin,
                r.parent_asin,
                r.helpful_vote,
                r.verified_purchase,
                m.title  AS product_title,
                m.description  AS product_description,
                m.features     AS product_features,
                m.price,
                m.average_rating,
                m.main_category
            FROM read_parquet('{reviews_path}') r
            LEFT JOIN read_parquet('{meta_path}') m USING (parent_asin)
            WHERE r.text IS NOT NULL
              AND LENGTH(TRIM(r.text)) > 0
              AND m.title IS NOT NULL
        )
        TO '{merged_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    n_merged = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{merged_path}')"
    ).fetchone()[0]
    print(f"  merged: {n_merged} rows")

    product_path = str(PROCESSED_DIR / "appliances_products.parquet")
    print("aggregating to product-level documents ...")
    con.execute(f"""
        COPY (
            WITH ranked AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY parent_asin
                        ORDER BY helpful_vote DESC, rating DESC
                    ) AS rn
                FROM read_parquet('{merged_path}')
            )
            SELECT
                parent_asin,
                FIRST(product_title)       AS title,
                FIRST(product_description) AS product_description,
                FIRST(product_features)    AS product_features,
                FIRST(price)               AS price,
                FIRST(average_rating)      AS rating,
                FIRST(main_category)       AS main_category,
                COUNT(*)                   AS review_count,
                STRING_AGG(
                    CASE WHEN rn <= 5 THEN review_text END,
                    ' [SEP] '
                ) AS review_text
            FROM ranked
            GROUP BY parent_asin
        )
        TO '{product_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    n_products = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{product_path}')"
    ).fetchone()[0]
    print(f"  product-level docs: {n_products}")
    print("done")


if __name__ == "__main__":
    main()
