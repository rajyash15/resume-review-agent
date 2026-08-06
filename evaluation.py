"""Structured evaluation: turn a resume (+ optional JD) into fixed, rubric-scored JSON.

Phase 4 of the Resume Review Agent.

The LLM is told exactly how to score each category (the rubric) and must answer
in a fixed JSON shape. We parse its JSON, validate it against a Pydantic schema,
and if it comes back malformed we tell the model what went wrong and ask again
(output validation / retry) — a pattern used in real production AI systems.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from pydantic import BaseModel, Field, ValidationError

import config
from embeddings import chunk_text
from llm import get_llm, stream_or_invoke
from retriever import index_text, retrieve_top_k


class ResumeReview(BaseModel):
    """The fixed shape the LLM's answer must take."""

    formatting_score: int = Field(ge=0, le=100, description="Layout, consistency, scannability")
    clarity_score: int = Field(ge=0, le=100, description="How understandable the content is")
    impact_score: int = Field(ge=0, le=100, description="Quantified outcomes vs. bare duties")
    keyword_match_score: int | None = Field(
        default=None, ge=0, le=100, description="Coverage of JD requirements; null if no JD"
    )
    overall_score: int = Field(ge=0, le=100, description="Holistic summary score")
    strengths: list[str] = Field(min_length=1, description="Short, resume-grounded strengths")
    improvement_suggestions: list[str] = Field(
        min_length=1, description="Short, specific, actionable suggestions"
    )


SYSTEM_PROMPT = """You are an expert resume reviewer with deep experience in hiring and Applicant Tracking Systems (ATS). You evaluate resumes against clear, consistent rubrics and always return a structured JSON result.

Scores are integers from 0 to 100.

- formatting_score: Layout, consistency, and scannability. Reward clean section headings, consistent fonts and spacing, sensible bullet use, and contact info present. Penalize dense walls of text, missing sections, inconsistent dates, and typos.
- clarity_score: How easy it is to understand what the person did and achieved. Reward concrete, specific, unambiguous language. Penalize vague phrases such as "responsible for" or "helped with", and unexplained acronyms.
- impact_score: Does it show results, not just duties? Strongly reward quantified outcomes: numbers, percentages, dollars, time saved, scale (e.g. "reduced report time by 40%", "improved retention by 12%"). Strongly penalize duty-only bullets such as "responsible for sales".
- keyword_match_score: Only include when a job description is provided. How well the resume covers the JD's stated requirements (skills, tools, experience). Reward explicit coverage of required skills; penalize missing required skills. Use null when no job description is provided.
- overall_score: A holistic summary of the above. When a JD is provided, weigh keyword_match_score heavily.

strengths: 2-4 short, specific strengths grounded in the actual resume text.
improvement_suggestions: 3-5 short, specific, actionable suggestions. Each should reference the actual resume (e.g. "Add a metric to the first bullet under Experience") and say exactly what to do. Never give generic advice like "be more impactful".

Rules:
- Every strength and suggestion must be grounded in the provided resume text. Do not invent facts.
- Respond with ONLY a single JSON object. No markdown fences, no commentary.
- JSON schema: {"formatting_score": int, "clarity_score": int, "impact_score": int, "keyword_match_score": int or null, "overall_score": int, "strengths": [str], "improvement_suggestions": [str]}"""


def _extract_json(content: str) -> dict[str, Any]:
    """Pull the first complete JSON object out of an LLM response."""
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```[A-Za-z]*\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    start = content.find("{")
    if start == -1:
        raise ValueError("no JSON object found in response")

    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(content)):
        ch = content[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(content[start : i + 1])
    raise ValueError("unbalanced JSON object in response")


def review_resume(
    resume_text: str,
    jd_text: str | None = None,
    max_attempts: int = 3,
    on_chunk: Callable[[str], None] | None = None,
    on_event: Callable[[str], None] | None = None,
) -> ResumeReview:
    """Score a resume (and optionally its fit against a job description).

    When `jd_text` is given, the most relevant JD chunks are retrieved by
    semantic search (the "R" in RAG) and included as context for scoring.

    `on_chunk` is called with each token as the LLM streams it (live terminal),
    and `on_event` with status strings (attempt / validation / retry).
    """
    has_jd = bool(jd_text and jd_text.strip())

    jd_context = ""
    if has_jd:
        chunks = index_text(jd_text)
        if chunks:
            matches: list[str] = []
            seen: set[str] = set()
            for resume_chunk in chunk_text(resume_text):
                for doc, score in retrieve_top_k(
                    resume_chunk, k=config.RETRIEVAL_TOP_K
                ):
                    if score >= 0.30 and doc not in seen:
                        seen.add(doc)
                        matches.append(doc)
            jd_context = "\n\n".join(matches) if matches else "\n".join(chunks[:5])

    user_prompt = _build_user_prompt(resume_text, jd_context, has_jd)

    messages: list[tuple[str, str]] = [("system", SYSTEM_PROMPT), ("human", user_prompt)]
    model = get_llm()

    for attempt in range(max_attempts):
        if on_event:
            on_event(f"attempt {attempt + 1}/{max_attempts}")
        content = stream_or_invoke(model, messages, on_chunk)

        try:
            data = _extract_json(content)
            review = ResumeReview.model_validate(data)
            if not has_jd:
                review.keyword_match_score = None
            if on_event:
                on_event("output validated")
            return review
        except (json.JSONDecodeError, ValueError, ValidationError) as exc:
            if attempt == max_attempts - 1:
                raise RuntimeError(
                    f"LLM returned invalid output after {max_attempts} attempts: {exc}"
                ) from exc
            if on_event:
                on_event(f"invalid output ({type(exc).__name__}) — retrying")
            messages.append(("assistant", content))
            messages.append(
                (
                    "human",
                    f"Your previous response could not be parsed as valid JSON matching the required schema.\n"
                    f"Error: {exc}\n"
                    f"Please respond again with ONLY a single valid JSON object following the schema.",
                )
            )

    raise RuntimeError("unreachable")  # pragma: no cover


def _build_user_prompt(resume_text: str, jd_context: str, has_jd: bool) -> str:
    parts = [f"RESUME:\n{resume_text.strip()}"]
    if has_jd:
        parts.append(
            "JOB DESCRIPTION (relevant excerpts retrieved by semantic search):\n"
            + (jd_context or "(no excerpts retrieved)")
        )
    parts.append("Evaluate the resume and return the JSON result.")
    return "\n\n".join(parts)
