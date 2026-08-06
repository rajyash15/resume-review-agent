"""Resume Review Agent — Streamlit web UI (Phase 7).

Run with:  streamlit run app.py

Upload a resume (PDF/DOCX), optionally paste a job description, and get
rubric-based scores, strengths, specific suggestions, and a match percentage.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from evaluation import review_resume
from match_score import analyze_match
from resume_parser import parse_resume

ALLOWED_SUFFIXES = (".pdf", ".docx")

st.set_page_config(page_title="Resume Review Agent", layout="centered")

st.title("Resume Review Agent")
st.caption(
    "Upload a resume (PDF or DOCX), optionally paste a job description, and get "
    "rubric-based scores plus specific, actionable suggestions."
)

uploaded = st.file_uploader("Your resume", type=["pdf", "docx"])
jd_text = st.text_area(
    "Job description (optional)",
    height=180,
    placeholder="Paste the job description here to also get a match score and keyword analysis...",
)

if st.button("Review My Resume", type="primary"):
    if uploaded is None:
        st.error("Please upload a resume file first.")
        st.stop()

    suffix = Path(uploaded.name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        st.error("Unsupported file type. Please upload a PDF or DOCX file.")
        st.stop()

    with st.spinner("Reading your resume..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = tmp.name
        try:
            resume_text, _sections = parse_resume(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    if not resume_text.strip():
        st.error("Could not extract any text from that file. Is it a real resume?")
        st.stop()

    has_jd = bool(jd_text and jd_text.strip())

    with st.spinner("Scoring your resume against the rubric..."):
        review = review_resume(resume_text, jd_text=jd_text if has_jd else None)
        match = analyze_match(resume_text, jd_text) if has_jd else None

    st.success("Review complete")

    # --- Overall score + match ---
    col_overall, col_match = st.columns(2)
    col_overall.metric("Overall score", f"{review.overall_score}/100")
    col_overall.progress(review.overall_score / 100)
    if match is not None:
        col_match.metric("Job match", f"{match['match_percentage']}%")
        col_match.progress(match["match_percentage"] / 100)
    else:
        col_match.metric("Job match", "Not provided")
        col_match.caption("Paste a job description to get a match score.")

    # --- Category scores ---
    st.subheader("Category scores")
    cols = st.columns(4)
    category_scores = [
        ("Formatting", review.formatting_score),
        ("Clarity", review.clarity_score),
        ("Impact", review.impact_score),
        ("Keyword match", review.keyword_match_score),
    ]
    for col, (label, value) in zip(cols, category_scores):
        if value is None:
            col.metric(label, "N/A")
            col.caption("Requires a job description")
        else:
            col.metric(label, f"{value}/100")
            col.progress(value / 100)

    # --- Strengths ---
    st.subheader("Strengths")
    for item in review.strengths:
        st.markdown(f"- {item}")

    # --- Suggestions ---
    st.subheader("Improvement suggestions")
    for item in review.improvement_suggestions:
        st.markdown(f"- {item}")

    # --- Match analysis ---
    if match is not None:
        st.subheader("How you match the job description")
        st.markdown(match["gap_analysis"])
        st.caption(f"Semantic similarity score: {match['semantic_similarity']:.3f}")

st.markdown("---")
st.caption("Built with LangChain, sentence-transformers, ChromaDB, Groq, Pydantic and Streamlit.")
