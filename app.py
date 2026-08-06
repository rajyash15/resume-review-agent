"""Resume Review Agent — Streamlit web UI (Phase 7, wemakedevs-style redesign).

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
from theme import (
    ACCENT_PURPLE,
    CATEGORY_ACCENTS,
    brackets,
    divider,
    eyebrow,
    footer,
    html,
    inject_theme,
    item_list,
    ring,
    score_card,
)

ALLOWED_SUFFIXES = (".pdf", ".docx")

st.set_page_config(page_title="Resume Review Agent", layout="wide")
inject_theme()

html(
    '<div class="wmd-hero">'
    '<div class="wmd-eyebrow" style="margin-top:0">AI Resume Review</div>'
    '<h1>Build a resume that <span class="wmd-shimmer">ships.</span></h1>'
    '<p style="color:#9f9fa9;max-width:34rem;font-size:1.05rem;line-height:1.6">'
    "Upload your resume, optionally paste a job description, and get rubric-based "
    "scores, strengths and specific fixes in ~30 seconds.</p></div>"
)

uploaded = st.file_uploader("Resume (PDF or DOCX)", type=["pdf", "docx"])
jd_text = st.text_area(
    "Job description (optional)",
    height=160,
    placeholder="Paste the job description here to also get a match score and keyword analysis...",
)

if st.button("Review My Resume", type="primary", use_container_width=True):
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

    # ---- 01 / Score ----
    eyebrow("01", "Score")
    col_ring, col_match = st.columns([1, 2])
    with col_ring:
        ring(review.overall_score, "Overall Score")
    with col_match:
        if match is not None:
            pct = match["match_percentage"]
            html(
                f'<div class="wmd-card">{brackets()}'
                f'<div class="wmd-card-label">Job Match</div>'
                f'<div class="wmd-card-score" style="color:{ACCENT_PURPLE}">{pct}'
                f'<span style="font-size:1rem;color:#9f9fa9">%</span></div>'
                f'<div class="wmd-bar"><div class="wmd-bar-fill" style="width:{pct}%;'
                f'background:linear-gradient(90deg,{ACCENT_PURPLE},{ACCENT_PURPLE})"></div></div>'
                f'</div>'
            )
        else:
            score_card(
                "Job Match",
                None,
                accent=ACCENT_PURPLE,
                note="Paste a job description to get a match score.",
            )

    # ---- 02 / Breakdown ----
    eyebrow("02", "Breakdown")
    cols = st.columns(4)
    category_data = [
        ("Formatting", review.formatting_score, "formatting"),
        ("Clarity", review.clarity_score, "clarity"),
        ("Impact", review.impact_score, "impact"),
        ("Keyword Match", review.keyword_match_score, "keyword_match"),
    ]
    for col, (label, value, key) in zip(cols, category_data):
        with col:
            note = "Requires a job description" if value is None else None
            score_card(label, value, accent=CATEGORY_ACCENTS[key], note=note)

    # ---- 03 / Strengths ----
    eyebrow("03", "Strengths")
    item_list(review.strengths, variant="", mark="+")

    # ---- 04 / Improvement Suggestions ----
    eyebrow("04", "Improvement Suggestions")
    item_list(review.improvement_suggestions, variant="orange", mark="->")

    # ---- 05 / How you match ----
    if match is not None:
        eyebrow("05", "How You Match")
        item_list([match["gap_analysis"]], variant="purple", mark="*")
        st.caption(f"Semantic similarity score: {match['semantic_similarity']:.3f}")

    divider()
    footer("Built with LangChain · sentence-transformers · ChromaDB · Groq · Streamlit")
