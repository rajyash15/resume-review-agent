"""Interactive follow-up chat: ask questions about a completed review (bonus).

The user's resume and the structured review are passed as context, so answers
stay grounded in those two sources instead of the model's general knowledge.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from llm import get_llm, stream_or_invoke

CHAT_SYSTEM_PROMPT = """You are a friendly, practical resume coach. You are given a candidate's resume and an automated review of it (JSON with scores, strengths, and improvement suggestions).

Rules:
- Answer ONLY from the resume and the review. Do not invent facts about the candidate.
- Be concrete and actionable; explain the reasoning behind advice.
- Keep answers short (3-6 sentences) unless the user asks for detail.
- If a question is not about the resume or the review, gently redirect the user.
"""


def ask_follow_up(
    resume_text: str,
    review: Any,
    question: str,
    on_chunk: Callable[[str], None] | None = None,
    on_event: Callable[[str], None] | None = None,
) -> str:
    """Answer a follow-up question grounded in the resume + review JSON."""
    review_json = json.dumps(review.model_dump(), indent=2, ensure_ascii=False)
    user_prompt = (
        f"RESUME:\n{resume_text.strip()}\n\n"
        f"AUTOMATED REVIEW (JSON):\n{review_json}\n\n"
        f"USER QUESTION: {question.strip()}\n\n"
        f"Answer the question."
    )
    model = get_llm()
    if on_event:
        on_event("coach answering")
    content = stream_or_invoke(
        model,
        [("system", CHAT_SYSTEM_PROMPT), ("human", user_prompt)],
        on_chunk,
    )
    return content.strip()
