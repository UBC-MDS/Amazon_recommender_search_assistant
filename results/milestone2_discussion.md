# Milestone 2 - Step 1: LLM Pipeline Choice

## Selected Model and Serving Path

We use **Ollama** with **`qwen2.5:3b`** (Qwen 2.5, 3B parameters) as the primary model for RAG generation. The HuggingFace Inference API (`Qwen/Qwen3.5-2B`) is available as a fallback.

## Why this choice

1. **Fits our hardware**
   A 3B model runs at ~15-25 tok/s on our M2 Air (16 GB RAM), keeping the demo responsive without needing a GPU.

2. **Open-source and easy to switch**  
   The model is open source, and our implementation keeps provider/model settings configurable so we can swap to Ollama or a larger HuggingFace model later without changing retrieval code.

3. **RAG-compatible chat interface**  
   We use a chat-style interface (`messages` with system + user prompts) and inject retrieved contexts from BM25/Semantic/Hybrid retrievers directly into the generation prompt.

4. **Tool-calling ready (optional)**  
   The pipeline includes optional `tools` forwarding for providers/models that support tool calling. This keeps the architecture compatible with future agentic extensions.

## Implementation summary

- Added a reusable RAG/LLM module in `src/llm_pipeline.py`:
  - Open-source provider routing: HuggingFace or Ollama
  - Prompt construction for retrieval-grounded generation
  - Single-turn RAG response object with answer + sources + optional tool calls

- Updated Streamlit app in `app/app.py`:
  - Added LLM provider and model controls
  - Added generation controls (temperature, max tokens)
  - Added a **Generate RAG answer** action that uses retrieved contexts
  - Added context/source inspection and optional tool-call output display

- Updated dependencies in `requirements.txt`:
  - `huggingface_hub`
  - `ollama`

## Notes for running

- HuggingFace route:
  - Set `HF_TOKEN` in `.env` (optional for some endpoints, recommended for reliability)
- Ollama route:
  - Install and run Ollama locally, then set provider to `ollama`
  - Optionally set `OLLAMA_HOST` for remote/local custom host

This setup gives us a working open-source RAG baseline while keeping the system flexible for future model upgrades.

## Step 2 - Semantic RAG Pipeline

### 2.1 Retrieval Step (Vector Store + Retriever)

We implemented the full semantic retrieval layer in `src/rag_pipeline.py` using the existing Milestone 1 semantic stack.

- Embeddings/vector store:
  - Uses sentence-transformers embeddings (`all-MiniLM-L6-v2`) when available.
  - Uses persisted FAISS index at `data/processed/semantic_faiss/` when present.
  - Falls back to in-memory semantic indexing when persisted index is unavailable.
- Retriever function:
  - `SemanticRAGPipeline.retrieve(query, k)` returns top-k semantic matches.
  - `SemanticRAGPipeline.retrieve_indices(query, k)` returns top-k document indices.
- Default retrieval depth is **top-5** (`k=5`).

#### Optional k experiment

We tested `k in {3, 5, 8}` on five sample queries:

- `quiet dishwasher for small apartment`
- `refrigerator water filter replacement`
- `portable countertop ice maker for home bar`
- `washing machine with low vibration`
- `energy efficient dishwasher under 500 dollars`

Observed retrieval trace (k=5, document indices):

- quiet dishwasher for small apartment -> `[25, 128, 102, 105, 75]`
- refrigerator water filter replacement -> `[63, 151, 144, 32, 38]`
- portable countertop ice maker for home bar -> `[15, 130, 42, 120, 157]`
- washing machine with low vibration -> `[51, 75, 166, 128, 175]`
- energy efficient dishwasher under 500 dollars -> `[25, 102, 128, 105, 4]`

Finding: We retained `k=5` as a practical balance for context size vs. relevance for RAG generation.

### 2.2 Context Building

`SemanticRAGPipeline.build_context(...)` converts retrieved documents into a structured, prompt-ready block with:

- `doc_id` and rank
- record/product identifiers
- title, rating, category, price
- description, features, review text
- semantic retrieval score

This improves traceability and supports source-grounded answers.

### 2.3 Prompt Template Design

We implemented 3 prompt variants in `src/rag_pipeline.py`:

- `strict`: high grounding, explicit insufficient-evidence behavior
- `concise`: short practical answers
- `analyst`: trade-offs and evidence synthesis

Findings from manual checks:

- `strict` gave the most reliable grounding and lowest hallucination risk.
- `concise` produced shorter outputs but occasionally omitted useful nuance.
- `analyst` produced richer comparisons, useful for complex product trade-offs.

Default for pipeline use is `strict`.

### 2.4 Full RAG Pipeline

Implemented in `src/rag_pipeline.py` as a custom Python class:

1. Semantic retrieval (`retrieve`)
2. Context construction (`build_context`)
3. Prompt construction (`build_prompt`)
4. LLM generation (`answer`)

The module also includes:

- `build_default_rag_pipeline(...)` project-level factory
- `analyze_k_values(...)` helper for retrieval-depth analysis

## Step 3 - Hybrid RAG: Semantic Search + BM25

### 3.1 BM25 Retriever

We reused and wrapped the Milestone 1 BM25 implementation (`src/ranking.py`) into a Step 3 retriever interface in `src/hybrid_rag_pipeline.py`:

- `BM25DocumentRetriever.retrieve(query, k)`
- Input: query string
- Output: top-k relevant documents (with indices and scores)

### 3.2 Semantic Retriever

We reused the semantic retriever from Step 2 and integrated it directly into the hybrid retriever.

### 3.3 Combining BM25 + Semantic Results

We implemented a custom `HybridDocumentRetriever` (non-LangChain) in `src/hybrid_rag_pipeline.py` with three combination modes:

1. `simple-merge`: concatenate top-k from both retrievers
2. `merge-dedup`: merge then remove duplicates
3. `rrf`: Reciprocal Rank Fusion re-ranking (default)

Default fusion setup:

- Mode: `rrf`
- Weights: BM25 = `0.4`, Semantic = `0.6`
- Rank constant: `rrf_k = 60`

Rationale: RRF is robust to score-scale mismatch between BM25 and embedding similarity and gives a clean unified ranking.

### 3.4 Hybrid RAG Pipeline

We added a complete hybrid pipeline in `src/hybrid_rag_pipeline.py`:

1. Hybrid retrieval (`HybridDocumentRetriever`)
2. Context building (`HybridRAGPipeline.build_context`)
3. Prompt template (`HybridRAGPipeline.build_prompt`, prompt variants from Step 2)
4. LLM generation (`HybridRAGPipeline.answer`)

Factory function:

- `build_default_hybrid_rag_pipeline(...)`

This provides a second full RAG path where Step 2 semantic retrieval is replaced by hybrid retrieval.

## Step 5 - Qualitative Evaluation of Hybrid RAG

We ran the Hybrid RAG pipeline (BM25 retrieval + Ollama `qwen2.5:3b` generation, k=5, prompt variant `strict`) on 5 queries from our Milestone 1 query set against the full 94,282-product corpus.

### Evaluation Queries and Results

| # | Query | Accurate? | Complete? | Fluent? |
|---|-------|-----------|-----------|----------|
| 1 | energy efficient dishwasher | Partial | No | Yes |
| 2 | dishwasher that runs quietly at night | Yes | Partial | Yes |
| 3 | small washing machine for apartment laundry | Yes | Yes | Yes |
| 4 | nugget ice maker for a home bar that makes ice quickly | Yes | Yes | Yes |
| 5 | best refrigerator water filter under 50 dollars | Partial | No | Yes |

### Per-Query Analysis

**Query 1: "energy efficient dishwasher"**

Retrieved products included a Samsung Energy Star dishwasher and two Whirlpool Energy Star dishwashers, but also two unrelated range hoods (Windster). The model correctly noted that the context was insufficient and cited [2],[3], but it could have pulled more information from the Energy Star dishwashers that were retrieved. The range hoods appearing in the top-5 is a BM25 issue -- the term "energy" matched their specs.

**Query 2: "dishwasher that runs quietly at night"**

The model correctly identified the Maytag MDB6769PAB from position [4] as having a review mentioning "Runs quietly." The citation was accurate. However, the answer was very brief and didn't compare noise levels across the retrieved options, making it incomplete for a shopping decision.

**Query 3: "small washing machine for apartment laundry"**

This was the best result. All 5 retrieved products were portable/compact washing machines. The model recommended the ZENY (rating 5.0) and Frestec (rating 4.4) with reasoning grounded in the reviews. The answer was well-structured and directly useful for someone apartment shopping.

**Query 4: "nugget ice maker for a home bar that makes ice quickly"**

All 5 retrieved products were nugget ice makers, showing strong retrieval quality. The model recommended the Silonn (rating 4.1) and noted its quick ice-making capability while also mentioning a limitation (melting issues). Good balance of pros and cons drawn from actual reviews.

**Query 5: "best refrigerator water filter under 50 dollars"**

The retriever found relevant water filter products, but the model struggled with the price constraint since price data wasn't consistently available in the reviews. It hedged by listing options without confirming prices. This is a structural limitation -- price filtering requires structured metadata, not just text matching.

### Observations

- Queries 3 and 4 worked well because the query terms directly matched product titles and review text, giving BM25 strong retrieval quality.
- Queries 1 and 5 exposed weaknesses: vague or multi-attribute queries ("energy efficient" + "dishwasher", or "under 50 dollars") lead to noisy retrieval when BM25 matches individual terms rather than intent.
- The model consistently refused to hallucinate when context was weak (queries 1 and 5), which is the desired behavior for the `strict` prompt variant.

### Limitations of the Hybrid RAG Pipeline

1. **No structured attribute filtering.** Queries involving price ranges, numerical ratings, or specific feature constraints (e.g., "under $50", "energy efficient") are poorly served by text-only retrieval. BM25 matches tokens like "50" or "energy" without understanding they're constraints. A production system would need metadata-aware filtering before or after retrieval to handle these queries well.

2. **Context window dilution with irrelevant hits.** When BM25 retrieves off-topic products (e.g., range hoods for a dishwasher query), the LLM's context window gets wasted on irrelevant text. With k=5, even one or two bad retrievals noticeably degrade answer quality because the model either ignores the noise (losing coverage) or tries to incorporate it (losing accuracy).

### Suggested Improvements

- Adding a reranker (e.g., a cross-encoder) between retrieval and generation would help filter out irrelevant hits before they reach the LLM context. This would directly address the context dilution problem.
- Implementing structured pre-filters on price, category, and rating before retrieval would handle constraint-based queries much more effectively than relying on text matching alone.
- Using the semantic retriever (or the full hybrid with RRF fusion) instead of BM25-only would likely improve queries 1 and 5, since semantic embeddings capture intent better than keyword overlap.
