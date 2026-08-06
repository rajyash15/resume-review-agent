"""LLM client factory: builds the chat model used for evaluation (Phase 4).

Only Groq is wired up for now, but the provider is chosen in one place
(`config.LLM_PROVIDER`) so adding a backup provider later is a small change.
"""

from __future__ import annotations

import os
from typing import Any

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
