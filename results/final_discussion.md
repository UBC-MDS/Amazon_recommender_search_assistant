# Final Discussion

## Step 1: Improve Your Workflow

### Dataset Scaling

- **Number of products used:** 94,282
- **Category:** Amazon Appliances (full category, no sampling)
- **Data source:** McAuley Lab UCSD review dataset, streamed via DuckDB
- **Aggregation:** Product-level records with top 5 reviews per product ranked by helpfulness vote count
- **Changes from previous milestones:** None. We have been working with the full 94K corpus since Milestone 2.

### LLM Experiment

#### Models Compared

| Property | Model A | Model B |
|----------|---------|---------|
| Name | `qwen2.5:3b` | `llama3.2:3b` |
| Family | Qwen 2.5 (Alibaba) | Llama 3.2 (Meta) |
| Parameters | 3B | 3B |
| Serving | Ollama (local) | Ollama (local) |
| Quantization | Q4_K_M (default) | Q4_K_M (default) |

**Rationale for comparison:** Both are 3B-parameter models that fit comfortably on our M2 Air (16 GB RAM), but they come from different model families with different training data and architectures. Comparing them tells us whether model family matters more than size for our RAG use case.

#### Prompt Used

```
SYSTEM:
You are a helpful Amazon shopping assistant. Answer using ONLY the provided context. If context is insufficient, say 'I do not have enough evidence'. Cite supporting products with [doc_id].

CONTEXT:
[BM25 top-5 retrieved products with title, rating, category, price, description, features, review, and score]

QUESTION:
[user query]

ANSWER:
```

#### Results

Each query was run with identical BM25-retrieved context (top-5) and the same prompt template (strict variant).

**Query 1: "energy efficient dishwasher"**

| | Qwen 2.5 (18.3s) | Llama 3.2 (26.5s) |
|---|---|---|
| Answer | Noted no specific match, but cited [doc_id=3] (Whirlpool Energy Star dishwasher) as relevant. | Cited [doc_id=2] (Samsung Energy Star) with specific details (4 gallons/load, Tier 1 compliance) and [doc_id=3] for exceeding federal standards by 15%. |
| Citations | 1 product | 2 products |
| Grounding | Weak -- hedged unnecessarily | Strong -- pulled specific specs from reviews |

**Query 2: "dishwasher that runs quietly at night"**

| | Qwen 2.5 (19.9s) | Llama 3.2 (29.2s) |
|---|---|---|
| Answer | Recommended Maytag MDB6769PAB, noted mixed reviews about quiet performance. | Recommended Amana ADB1300AFB, directly quoted review text "super quiet when it runs." |
| Citations | 1 product | 1 product |
| Grounding | Moderate -- mentioned negative reviews | Strong -- direct review quotes |

**Query 3: "small washing machine for apartment laundry"**

| | Qwen 2.5 (32.0s) | Llama 3.2 (43.7s) |
|---|---|---|
| Answer | Listed ZENY (5.0 rating) and Frestec with brief summaries. | Listed ZENY, Frestec, and Wonder Washer with capacity details and portability features. |
| Citations | 2 products | 3 products |
| Grounding | Good -- used ratings | Good -- used specs and features |

**Query 4: "nugget ice maker for a home bar that makes ice quickly"**

| | Qwen 2.5 (43.6s) | Llama 3.2 (61.6s) |
|---|---|---|
| Answer | Recommended Silonn (4.1 rating, 6 min first round, 47 dB). Noted drawbacks (melting, draining). | Recommended Silonn (33 lbs/day, self-cleaning, 47 dB). Compared against Kndko and OUTGAVA. |
| Citations | 1 product + drawbacks | 3 products with comparison |
| Grounding | Strong -- balanced pros/cons | Strong -- comparative analysis |

**Query 5: "best refrigerator water filter under 50 dollars"**

| | Qwen 2.5 (52.7s) | Llama 3.2 (52.6s) |
|---|---|---|
| Answer | Listed GLACIER FRESH ($22.99) and Waterspecialist. Discussed NSF certification. | Recommended GLACIER FRESH ($22.99, 4.5 rating). Compared against Denali Pure and WF-50. |
| Citations | 2 products | 3 products |
| Grounding | Good -- mentioned certifications | Good -- cited ratings and price |

#### Performance Summary

| Metric | Qwen 2.5:3b | Llama 3.2:3b |
|--------|-------------|--------------|
| Avg response time | 33.3s | 42.7s |
| Avg answer length | 567 chars | 817 chars |
| Avg citations per answer | 1.4 | 2.4 |
| Hallucination instances | 0 | 0 |
| Direct review quotes | 1/5 queries | 3/5 queries |

#### Key Observations

1. **Llama 3.2 provides richer, better-grounded answers.** It consistently cited more products (2.4 vs 1.4 on average), pulled specific specs and review quotes, and made comparisons across retrieved products rather than focusing on a single item.

2. **Qwen 2.5 is faster but more conservative.** It was ~28% faster on average (33.3s vs 42.7s) but often hedged when context was ambiguous (e.g., "there is no specific product that matches" for Query 1 when there were relevant products in context).

3. **Neither model hallucinated.** Both respected the strict prompt's instruction to use only provided context. When evidence was weak, both acknowledged limitations rather than fabricating information.

4. **Llama 3.2 is better at extractive grounding.** It directly quoted review text in 3 of 5 queries (e.g., "super quiet when it runs"), whereas Qwen paraphrased more often. For a product recommendation system, direct quotes from real reviews build more user trust.

5. **Response time difference is noticeable but acceptable.** The ~10s difference per query (33s vs 43s) is perceptible in interactive use but not a dealbreaker for a RAG assistant where retrieval is already the bottleneck.

#### Model Choice

We updated the default model to **`llama3.2:3b`** based on this experiment. While Qwen 2.5 is faster, Llama 3.2's stronger grounding, richer citations, and comparative analysis style make it a better fit for a product recommendation assistant where answer quality matters more than latency.


## Step 2: Additional Feature -- Option 3 (Scale to 100K+ Products)

We chose **Option 3: Scale to >= 100K products** because our pipeline already processes 94,282 products from the full Amazon Appliances category.

### What We Implemented

The core challenge was making the retrieval pipeline work on a dataset where naive approaches (full-corpus encoding in one pass, full-document serialization) cause out-of-memory crashes or segfaults on laptop hardware (M2 Air, 16 GB RAM).

#### Problem 1: OOM during semantic encoding

Encoding 94K documents with `sentence-transformers` (`all-MiniLM-L6-v2`) in a single batch required ~6 GB of intermediate tensors, exceeding available memory when combined with the model weights and other data structures.

**Solution:** Batched encoding in `src/ranking.py`. Documents are encoded in batches of 512, and embeddings are vstacked incrementally:

```python
embeddings_list = []
for start in range(0, len(texts), batch_size):
    batch = texts[start : start + batch_size]
    batch_emb = self.model.encode(batch, show_progress_bar=False)
    embeddings_list.append(batch_emb)
embeddings = np.vstack(embeddings_list)
```

This keeps peak memory under 2 GB regardless of corpus size.

#### Problem 2: Segfault during FAISS index serialization

The original `save_index` method serialized full document dicts (title, review, description, features, etc.) into a JSON metadata file. With 94K products, this produced a ~400 MB JSON file. Python's JSON serializer segfaulted when writing this to disk.

**Solution:** Lightweight metadata in `src/ranking.py`. Instead of storing full documents, we store only the record IDs and a field name indicating the source:

```python
metadata = {"field": field, "record_ids": [doc.get("record_id") for doc in self.documents]}
```

At load time, `load_index` reconstructs full documents from the parquet data via `data_io.load_documents()`, matching by record ID. This reduces the metadata file from ~400 MB to ~3 MB.

#### Problem 3: Slow index rebuilds

Building both indexes from scratch takes ~12 minutes (BM25: ~2 min, FAISS: ~10 min). Rebuilding on every app start was unacceptable for interactive use.

**Solution:** Persisted indexes via `src/build_indexes.py`. BM25 is pickled to `data/processed/bm25_index.pkl` (631 MB). FAISS is saved to `data/processed/semantic_faiss/` (138 MB). The app loads these at startup in ~30 seconds.

#### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Batch size 512 | Trade-off: smaller batches use less memory but are slower. 512 keeps encoding under 2 GB while finishing in ~10 min. |
| Record ID metadata | Avoids duplicating the full corpus in JSON. Disk I/O is cheaper than memory. |
| Pickle for BM25 | `rank_bm25` objects are not JSON-serializable. Pickle is the standard approach. |
| FAISS flat index (no IVF) | At 94K vectors, brute-force search is fast enough (~5ms). IVF adds complexity without meaningful speedup below 1M vectors. |

#### Code References

- Batched encoding: [`src/ranking.py`](../src/ranking.py), `SemanticRetriever.fit()` method
- Lightweight metadata: [`src/ranking.py`](../src/ranking.py), `SemanticRetriever.save_index()` and `load_index()`
- Index builder: [`src/build_indexes.py`](../src/build_indexes.py)


## Step 3: Documentation and Code Quality

We ran a code quality audit across all `src/*.py` modules and applied cleanup where needed.

### 3.1 Audit Checklist Results

| Check | Status | Evidence / Action |
|---|---|---|
| No hardcoded file paths | Pass | Modules resolve paths from project root using `pathlib.Path` (e.g., `src/data_io.py`, `src/build_indexes.py`, `src/download_full.py`). |
| No API keys in source | Pass | LLM credentials are pulled from environment variables (`HF_TOKEN`, `OLLAMA_HOST`) and optional Streamlit input; no hardcoded secrets in source. |
| Functions have docstrings | Updated | Added missing docstrings in `src/data_io.py`, `src/ranking.py`, `src/hybrid_rag_pipeline.py`, `src/llm_pipeline.py`, `src/qualitative_eval.py`, `src/build_indexes.py`, `src/feedback.py`, and `src/download_full.py`. |
| Environment files up to date | Pass | `requirements.txt` and `environment.yml` are present and aligned with project dependencies (DuckDB, rank-bm25, sentence-transformers/FAISS path, Streamlit, Ollama/HF support). |
| No temp/junk tracked | Pass | Data folders are used for runtime artifacts and repository remains clean of OS temp-path assumptions. |

### 3.2 README and Documentation Consistency

README currently reflects final-state usage:

- Default local model set to `llama3.2:3b`
- Alternative model/provider behavior documented
- Final comparison and scale discussion referenced via `results/final_discussion.md`
- Reproduction and app run steps remain valid

### 3.3 Code Quality Summary

Primary cleanup was documentation completeness (docstrings) with no behavioral changes. This improves maintainability and grading clarity by making helper intent explicit across retrieval, indexing, and evaluation modules.


## Step 4: Cloud Deployment Plan

Below is a production-oriented deployment plan for this RAG system on AWS-class infrastructure.

### 4.1 Data Storage

| Asset | Service | Justification |
|---|---|---|
| Raw `.jsonl.gz` review + metadata files | S3 (`s3://dsci575-raw/`) | Low-cost, durable object storage; easy versioning and lifecycle policies. |
| Processed parquet tables | S3 (`s3://dsci575-processed/`) | Columnar format + object storage works well with DuckDB/Athena style reads. |
| FAISS index (~138 MB) | EFS (primary) or S3 + local cache | Fast shared access for app tasks; can be cached on startup from S3 if needed. |
| BM25 index (~631 MB) | EFS (primary) or S3 + local cache | Large artifact loaded at app startup; EFS avoids repeated large downloads per task. |

### 4.2 Compute and Serving

| Component | Service | Notes |
|---|---|---|
| Streamlit application | ECS Fargate or EC2 (`t3.xlarge` baseline) | Needs enough RAM to load BM25 + FAISS and serve multiple user sessions. |
| Retrieval/index loading | App container startup + shared volume | Load persisted indexes at boot rather than rebuilding online. |
| LLM inference | Managed external endpoint (AWS Bedrock, Together AI, or HF Inference) | Running local Ollama inside autoscaled containers is operationally heavy. |
| Traffic/concurrency | ALB + ECS auto scaling | Scale task count on CPU/RAM/request metrics. |

### 4.3 Streaming Updates and Re-indexing

1. New review/meta files are uploaded to S3 raw bucket.
2. S3 event triggers Lambda (or Step Functions) to validate and register new batch.
3. Scheduled ECS batch task (e.g., weekly/nightly) rebuilds parquet + BM25 + FAISS artifacts.
4. New indexes are written to versioned S3 prefix and promoted to EFS cache path.
5. Application tasks pick up updated indexes on rolling restart.

### 4.4 Operational Notes

- Keep index artifacts versioned (`index_version=YYYYMMDD`) for rollback safety.
- Add CloudWatch dashboards for startup time, retrieval latency, and generation latency.
- Add a health check that validates both BM25 and semantic retrieval on a probe query before marking task healthy.
- If load increases substantially, split retrieval API and frontend into separate services.
