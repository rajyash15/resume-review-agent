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


def get_llm() -> Any:
    """Return a LangChain chat model for the configured provider."""
    provider = config.LLM_PROVIDER.lower()

    if provider == "groq":
        api_key = (os.environ.get("GROQ_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to the .env file (see .env.example)."
            )
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=config.LLM_MODEL,
            api_key=api_key,
            temperature=config.LLM_TEMPERATURE,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}")
