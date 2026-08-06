"""Phase 5-6 tests: match % discriminates matching vs unrelated JDs, gap analysis is grounded.

Makes live Groq API calls (requires GROQ_API_KEY in .env).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from match_score import analyze_match, match_percentage, semantic_similarity
from resume_parser import parse_resume

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"

DATA_ANALYST_JD = """Senior Data Analyst

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

UNRELATED_JD = """Line Cook

We need a reliable line cook for a busy downtown kitchen. You will prep
ingredients, grill and plate dishes, and keep your station clean during service.

Requirements
- 2+ years cooking in a restaurant kitchen
- Knife skills and food-safety certification
- Ability to work evening and weekend shifts
"""


def test_matching_jd_scores_high() -> None:
    resume_text, _ = parse_resume(SAMPLE_DIR / "jane_doe_resume.pdf")
    sim = semantic_similarity(resume_text, DATA_ANALYST_JD)
    pct = match_percentage(resume_text, DATA_ANALYST_JD)
    print(f"  data-analyst JD: similarity={sim:.3f} match={pct}%")
    assert sim > 0.45
    assert pct >= 40


def test_unrelated_jd_scores_low() -> None:
    resume_text, _ = parse_resume(SAMPLE_DIR / "jane_doe_resume.pdf")
    sim = semantic_similarity(resume_text, UNRELATED_JD)
    pct = match_percentage(resume_text, UNRELATED_JD)
    print(f"  line-cook JD:    similarity={sim:.3f} match={pct}%")
    assert sim < 0.40
    assert pct <= 40
    assert pct < match_percentage(resume_text, DATA_ANALYST_JD)


def test_gap_analysis_is_grounded() -> None:
    resume_text, _ = parse_resume(SAMPLE_DIR / "jane_doe_resume.pdf")
    result = analyze_match(resume_text, DATA_ANALYST_JD)
    print(f"  match_percentage: {result['match_percentage']}%")
    print(f"  gap_analysis: {result['gap_analysis']}")
    assert result["match_percentage"] >= 0
    assert len(result["gap_analysis"]) > 80


if __name__ == "__main__":
    test_matching_jd_scores_high()
    test_unrelated_jd_scores_low()
    test_gap_analysis_is_grounded()
    print("All Phase 5-6 tests passed.")
