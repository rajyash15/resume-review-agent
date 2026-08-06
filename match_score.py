"""Job-description match score: how well a resume fits a specific job (Phase 5).

Combines two signals into a single, readable "Match: N%" result:
  1. Semantic similarity — cosine similarity between the whole-resume embedding
     and the whole-job-description embedding (meaning-based, not keyword-based).
  2. Gap analysis — a short LLM paragraph naming what the JD asks for that the
     resume is missing or understates.

The Suggestions Engine (Phase 6) lives in `evaluation.review_resume`, whose
rubric forces specific, actionable suggestions in the same LLM call as scoring.
"""

from __future__ import annotations

from typing import Callable

from embeddings import cosine_similarity, embed_text
from llm import get_llm, stream_or_invoke

GAP_ANALYSIS_PROMPT = """You are an expert recruiter comparing a candidate's resume against a job description.

Based ONLY on the provided texts, write a short gap analysis (3-5 sentences, plain language) that:
1. Names the key requirements from the job description the resume clearly satisfies.
2. Names the specific requirements the resume misses or does not prove (e.g. tools, skills, years of experience).
3. Ends with one practical sentence on the highest-impact thing the candidate could add or change.

Do not invent requirements that are not in the job description. Do not invent facts about the candidate.
"""


def semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Cosine similarity (0..1) between the whole resume and whole JD embeddings."""
    return cosine_similarity(embed_text(resume_text), embed_text(jd_text))


def match_percentage(resume_text: str, jd_text: str) -> int:
    """Map semantic similarity to a friendly 0-100 match percentage."""
    similarity = semantic_similarity(resume_text, jd_text)
    # With MiniLM, on-topic resume/JD pairs typically score ~0.55-0.8 and
    # off-topic pairs ~0.15-0.35, so scale into a more intuitive 0-100 range.
    lower, upper = 0.30, 0.75
    scaled = (similarity - lower) / (upper - lower)
    pct = round(max(0.0, min(1.0, scaled)) * 100)
    return pct


def gap_analysis(
    resume_text: str,
    jd_text: str,
    match: int,
    on_chunk: Callable[[str], None] | None = None,
) -> str:
    """Ask the LLM for a grounded gap analysis paragraph."""
    user_prompt = (
        f"Semantic match between resume and job description: {match}%\n\n"
        f"RESUME:\n{resume_text.strip()}\n\n"
        f"JOB DESCRIPTION:\n{jd_text.strip()}\n\n"
        f"Write the gap analysis."
    )
    model = get_llm()
    content = stream_or_invoke(
        model, [("system", GAP_ANALYSIS_PROMPT), ("human", user_prompt)], on_chunk
    )
    return content.strip()


def analyze_match(
    resume_text: str,
    jd_text: str,
    on_chunk: Callable[[str], None] | None = None,
) -> dict:
    """Compute the full match result for a resume + job description.

    Returns {"match_percentage": int, "semantic_similarity": float, "gap_analysis": str}.
    """
    similarity = semantic_similarity(resume_text, jd_text)
    pct = match_percentage(resume_text, jd_text)
    analysis = gap_analysis(resume_text, jd_text, pct, on_chunk)
    return {
        "match_percentage": pct,
        "semantic_similarity": round(similarity, 4),
        "gap_analysis": analysis,
    }
