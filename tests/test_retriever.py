"""Phase 3 tests: ChromaDB indexes job-description chunks and retrieves by meaning."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retriever import has_index, index_text, retrieve_top_k

JD = """Senior Data Analyst

We are looking for a Senior Data Analyst to join our analytics team. You will
own data pipelines and reporting, and help the company make data-driven decisions.

Responsibilities
- Build and maintain SQL pipelines that transform raw data into clean tables
- Create dashboards in Tableau and Power BI for leadership review
- Work closely with engineering teams to define core product metrics
- Design A/B tests and analyze experiment results
- Present findings to stakeholders and executives in plain language
- Mentor and lead a small team of junior analysts

Requirements
- 4+ years of experience writing production SQL
- Proficiency in Tableau or Power BI
- Python and Pandas for data analysis
- Strong written and verbal communication skills
- Experience leading small analytics teams

Nice to have
- Experience with dbt or Airflow
- Familiarity with e-commerce funnel analytics
"""


def test_index_and_retrieve_teamwork() -> None:
    chunks = index_text(JD)
    print(f"  indexed {len(chunks)} chunks")
    assert has_index()
    assert len(chunks) >= 2

    # This query shares almost no exact words with the JD's leadership bullets,
    # but means nearly the same thing. It should retrieve the teamwork chunks.
    results = retrieve_top_k(
        "I led a team of five engineers and analysts building data pipelines",
        k=3,
    )
    for chunk, score in results:
        print(f"  [{score:.3f}] {chunk[:80]}")
    top_text = results[0][0].lower()
    assert any(word in top_text for word in ("team", "analyst", "engineer"))


def test_retrieve_sql_query_finds_sql_chunk() -> None:
    index_text(JD)
    results = retrieve_top_k("I write SQL queries every day and know Tableau", k=1)
    assert "sql" in results[0][0].lower() or "tableau" in results[0][0].lower()


def test_index_is_replaced() -> None:
    index_text("Full-stack web developer position focused on React, Node.js, and Kubernetes.")
    results = retrieve_top_k("What do they want me to know?", k=1)
    print(f"  after re-index, top chunk: {results[0][0][:60]}")
    assert "react" in results[0][0].lower() or "kubernetes" in results[0][0].lower()
    assert "sql" not in results[0][0].lower()


if __name__ == "__main__":
    test_index_and_retrieve_teamwork()
    test_retrieve_sql_query_finds_sql_chunk()
    test_index_is_replaced()
    print("All Phase 3 tests passed.")
