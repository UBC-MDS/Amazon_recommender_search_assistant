# Milestone 2 Discussion

## Step 1: Build LLM Pipeline

### Model choice

Selected model: **Qwen/Qwen3.5-2B** via **HuggingFace Inference API** as the primary path, with an **Ollama** backend option in code.

Rationale:

1. Good quality/performance trade-off for laptop-class constraints.
2. Open-source model family and easy provider/model switching.
3. Chat interface supports retrieval-grounded prompts and optional tool-calling pass-through.

Implementation references:

- `src/llm_pipeline.py`
- `app/app.py`

## Step 2: Semantic RAG Pipeline

### 2.1 Retrieval step

- Implemented in `src/rag_pipeline.py` with a custom class (`SemanticRAGPipeline`).
- Reuses Milestone 1 semantic retrieval and FAISS persistence where available.
- Retriever outputs top-k document indices with `retrieve_indices(query, k)`.
- Default `k=5`.

Optional k analysis summary (sample queries):

- Tested `k={3,5,8}`.
- Retained `k=5` as balance between context size and relevance.

### 2.2 Context building

- Implemented with `build_context(...)` in `SemanticRAGPipeline`.
- Context includes doc id/rank, metadata fields, review text, and semantic score.

### 2.3 Prompt template design

Implemented 3 system prompt variants:

- `strict`
- `concise`
- `analyst`

Findings:

- `strict` had strongest grounding behavior.
- `concise` improved brevity but could lose nuance.
- `analyst` was best for trade-off explanations.

### 2.4 Full semantic RAG pipeline

Implemented end-to-end chain:

1. Semantic retrieval
2. Context construction
3. Prompt building
4. LLM generation

Workflow diagram added to `README.md`.

## Step 3: Hybrid RAG (BM25 + Semantic)

### 3.1 BM25 retriever

- Implemented `BM25DocumentRetriever` in `src/hybrid_rag_pipeline.py`.
- Input: query
- Output: top-k relevant results with indices/scores

### 3.2 Semantic retriever

- Reused semantic retriever from Step 2 in hybrid pipeline.

### 3.3 Combination strategy

Implemented custom `HybridDocumentRetriever` with:

1. `simple-merge`
2. `merge-dedup`
3. `rrf` (Reciprocal Rank Fusion, default)

Default fusion weights: BM25 `0.4`, semantic `0.6`.

### 3.4 Hybrid RAG pipeline

Implemented `HybridRAGPipeline` in `src/hybrid_rag_pipeline.py` with full flow:

1. Hybrid retrieval
2. Context building
3. Prompt template
4. LLM generation

Workflow diagram added to `README.md`.

## Integration status

The Streamlit app (`app/app.py`) now supports three generation backends:

1. Direct context RAG
2. Semantic RAG pipeline
3. Hybrid RAG pipeline

This ensures the Step 1, Step 2, and Step 3 implementations are connected and runnable from the app.
