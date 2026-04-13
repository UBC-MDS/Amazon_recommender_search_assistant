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
