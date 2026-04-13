"""Open-source chat and RAG pipeline utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import os

from .ranking import SearchResult


DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful product assistant. Use only the retrieved context to answer questions "
    "about products. If the context is insufficient, say so clearly and suggest a follow-up query."
)


@dataclass(frozen=True)
class RAGResponse:
    """Final answer plus the retrieved evidence used to generate it."""

    answer: str
    contexts: list[SearchResult]
    tool_calls: list[dict[str, Any]] | None = None


class OpenSourceChatModel:
    """Small chat wrapper for open-source models via HuggingFace or Ollama."""

    def __init__(
        self,
        provider: str = "huggingface",
        model: str = "Qwen/Qwen3.5-2B",
        temperature: float = 0.2,
        max_new_tokens: int = 350,
        hf_token: str | None = None,
        ollama_host: str | None = None,
    ):
        self.provider = provider.lower().strip()
        self.model = model.strip()
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST")

    def chat(self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None) -> tuple[str, list[dict[str, Any]] | None]:
        if self.provider == "huggingface":
            return self._chat_huggingface(messages, tools=tools)
        if self.provider == "ollama":
            return self._chat_ollama(messages, tools=tools)
        raise ValueError(f"Unsupported provider: {self.provider}. Choose 'huggingface' or 'ollama'.")

    def _chat_huggingface(
        self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None
    ) -> tuple[str, list[dict[str, Any]] | None]:
        try:
            from huggingface_hub import InferenceClient
        except Exception as exc:
            raise RuntimeError("huggingface_hub is required for HuggingFace chat.") from exc

        client = InferenceClient(model=self.model, token=self.hf_token)
        request: dict[str, Any] = {
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_new_tokens,
        }
        if tools:
            request["tools"] = tools

        response = client.chat.completions.create(**request)
        message = response.choices[0].message
        content = message.content or ""
        raw_tool_calls = getattr(message, "tool_calls", None)
        tool_calls = [call.model_dump() if hasattr(call, "model_dump") else dict(call) for call in raw_tool_calls] if raw_tool_calls else None
        return content, tool_calls

    def _chat_ollama(
        self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None
    ) -> tuple[str, list[dict[str, Any]] | None]:
        try:
            import ollama
        except Exception as exc:
            raise RuntimeError("The 'ollama' Python package is required for Ollama chat.") from exc

        options = {"temperature": self.temperature}
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "options": options,
        }
        if tools:
            payload["tools"] = tools

        if self.ollama_host:
            client = ollama.Client(host=self.ollama_host)
            response = client.chat(**payload)
        else:
            response = ollama.chat(**payload)

        message = response.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls")
        return content, tool_calls


def build_rag_messages(
    question: str,
    contexts: list[SearchResult],
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> list[dict[str, str]]:
    """Build a compact RAG prompt with numbered evidence blocks."""

    context_lines: list[str] = []
    for idx, result in enumerate(contexts, start=1):
        document = result.document
        title = document.get("title", "Untitled")
        review_text = str(document.get("review_text", "")).strip()
        snippet = review_text[:500]
        context_lines.append(f"[{idx}] Title: {title}")
        context_lines.append(f"[{idx}] Snippet: {snippet}")
        context_lines.append(f"[{idx}] Retrieval score: {result.score:.4f}")

    context_block = "\n".join(context_lines) if context_lines else "No context retrieved."
    user_prompt = (
        "Answer the question using only the context below. "
        "If context is insufficient, explain what is missing. "
        "Cite evidence as [1], [2], etc.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def run_rag_chat(
    question: str,
    contexts: list[SearchResult],
    provider: str = "huggingface",
    model: str = "Qwen/Qwen3.5-2B",
    temperature: float = 0.2,
    max_new_tokens: int = 350,
    hf_token: str | None = None,
    ollama_host: str | None = None,
    tools: list[dict[str, Any]] | None = None,
) -> RAGResponse:
    """Run a single RAG chat turn with an open-source model backend."""

    chat_model = OpenSourceChatModel(
        provider=provider,
        model=model,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        hf_token=hf_token,
        ollama_host=ollama_host,
    )
    messages = build_rag_messages(question=question, contexts=contexts)
    answer, tool_calls = chat_model.chat(messages=messages, tools=tools)
    return RAGResponse(answer=answer.strip(), contexts=contexts, tool_calls=tool_calls)