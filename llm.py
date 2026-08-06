"""LLM client factory: builds the chat model used for evaluation (Phase 4).

Only Groq is wired up for now, but the provider is chosen in one place
(`config.LLM_PROVIDER`) so adding a backup provider later is a small change.
"""

from __future__ import annotations

import os
from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv()

import config


def get_api_key(name: str) -> str:
    """Look up an API key, checking (in order) Streamlit secrets then env vars.

    On Streamlit Community Cloud the key lives in the app's Secrets settings
    (`st.secrets`); locally it lives in `.env` (loaded into os.environ by
    dotenv). Accessing `st.secrets` outside a running Streamlit script raises,
    so it is guarded.
    """
    key = ""
    try:
        import streamlit as st

        try:
            key = st.secrets.get(name, "")
        except Exception:
            key = ""
    except Exception:
        key = ""
    if not key:
        key = os.environ.get(name, "")
    return (key or "").strip()


def get_llm() -> Any:
    """Return a LangChain chat model for the configured provider."""
    provider = config.LLM_PROVIDER.lower()

    if provider == "groq":
        api_key = get_api_key("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to the .env file locally, or to "
                "Streamlit Cloud Secrets when deployed (see README Phase 8)."
            )
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=config.LLM_MODEL,
            api_key=api_key,
            temperature=config.LLM_TEMPERATURE,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}")


def stream_or_invoke(
    model: Any,
    messages: list[tuple[str, str]],
    on_chunk: Callable[[str], None] | None = None,
) -> str:
    """Send `messages` to `model`, streaming the reply token-by-token.

    Each token is passed to `on_chunk` as soon as it arrives so the UI can show
    a live terminal. When `on_chunk` is None (or streaming is unsupported) the
    model is invoked as a single call and the full text is returned.
    """
    if on_chunk is None:
        response = model.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    streamer = getattr(model, "stream", None)
    if streamer is None:
        response = model.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        on_chunk(content)
        return content

    parts: list[str] = []
    try:
        for chunk in streamer(messages):
            piece = chunk.content if hasattr(chunk, "content") else str(chunk)
            parts.append(piece)
            on_chunk(piece)
    except NotImplementedError:
        response = model.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        on_chunk(content)
        return content
    return "".join(parts)
