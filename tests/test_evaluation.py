"""Phase 4 tests: real LLM review on the sample resume, with and without a JD.

These make live Groq API calls (requires GROQ_API_KEY in .env).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluation import ResumeReview, review_resume
from resume_parser import parse_resume

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"

JD = """Senior Data Analyst

We are looking for a Senior Data Analyst to join our analytics team. You will
own data pipelines and reporting, and help the company make data-driven decisions.

Responsibilities
- Build and maintain SQL pipelines that transform raw data into clean tables
- Create dashboards in Tableau and Power BI for leadership review
- Work closely with engineering teams to define core product metrics
- Design A/B tests and analyze experiment results
- Present findings to stakeholders and executives in plain language

Requirements
- 4+ years of experience writing production SQL
- Proficiency in Tableau or Power BI
- Python and Pandas for data analysis
- Strong written and verbal communication skills
"""


def test_review_without_jd() -> None:
    resume_text, _ = parse_resume(SAMPLE_DIR / "jane_doe_resume.pdf")
    review = review_resume(resume_text)
    assert isinstance(review, ResumeReview)
    assert review.keyword_match_score is None
    for name, score in (
        ("formatting", review.formatting_score),
        ("clarity", review.clarity_score),
        ("impact", review.impact_score),
        ("overall", review.overall_score),
    ):
        assert 0 <= score <= 100, f"{name} score out of range: {score}"
        print(f"  {name:9s}: {score}")
    print(f"  strengths: {review.strengths}")
    print(f"  suggestions: {review.improvement_suggestions}")
    assert len(review.strengths) >= 2
    assert len(review.improvement_suggestions) >= 2


def test_review_with_jd() -> None:
    resume_text, _ = parse_resume(SAMPLE_DIR / "jane_doe_resume.pdf")
    review = review_resume(resume_text, jd_text=JD)
    assert review.keyword_match_score is not None
    assert 0 <= review.keyword_match_score <= 100
    print(f"  keyword_match: {review.keyword_match_score}")
    print(f"  overall:       {review.overall_score}")


if __name__ == "__main__":
    print("--- review WITHOUT job description ---")
    test_review_without_jd()
    print("--- review WITH job description ---")
    test_review_with_jd()
    print("All Phase 4 tests passed.")
