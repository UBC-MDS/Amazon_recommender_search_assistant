# Milestone 2 - Step 1: LLM Pipeline Choice

## Selected Model and Serving Path

We selected **`Qwen/Qwen3.5-2B`** via the **HuggingFace Inference API** as the primary model for the initial RAG pipeline.

## Why this choice

1. **Fits typical student compute constraints**  
   A 2B model is a practical quality/performance trade-off for laptop-class setups.

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
