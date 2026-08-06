"""Resume Review Agent — Streamlit web UI (Phase 7, wemakedevs-style redesign).

Run with:  streamlit run app.py

Upload a resume (PDF/DOCX), optionally paste a job description, and get
rubric-based scores, strengths, specific suggestions, and a match percentage.
The review streams into a live terminal, results persist across reruns, and
you can chat with a follow-up coach about the review.
"""

from __future__ import annotations

import html as _html
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

import chat
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

CATEGORY_TIPS = {
    "formatting": (
        "Layout, consistency, and scannability. Rewards clean section headings, "
        "consistent fonts/spacing, and sensible bullet use; penalizes walls of "
        "text, missing sections, inconsistent dates, and typos."
    ),
    "clarity": (
        "How easy it is to understand what you did. Rewards concrete, specific "
        "language; penalizes vague phrases like 'responsible for' and "
        "unexplained acronyms."
    ),
    "impact": (
        "Shows results, not just duties. Strongly rewards quantified outcomes "
        "(numbers, percentages, dollars, time saved); penalizes duty-only bullets."
    ),
    "keyword_match": (
        "How well the resume covers the job description's required skills and "
        "tools. Only scored when a job description is provided."
    ),
}

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

# ---- session state ----
st.session_state.setdefault("review_done", False)
st.session_state.setdefault("chat", [])

# Hide stale results when the inputs change.
_inputs = (uploaded.name if uploaded else None, jd_text.strip())
if st.session_state.get("_inputs") != _inputs:
    st.session_state["_inputs"] = _inputs
    st.session_state["review_done"] = False
    st.session_state["chat"] = []

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

    with st.expander("Live agent output (terminal)", expanded=True):
        terminal = st.empty()

    terminal_buf: list[str] = []

    def _emit(text: str) -> None:
        terminal_buf.append(text)
        terminal.markdown(
            f'<div class="wmd-terminal">{_html.escape("".join(terminal_buf))}</div>',
            unsafe_allow_html=True,
        )

    def _on_chunk(piece: str) -> None:
        _emit(piece)

    def _on_event(msg: str) -> None:
        _emit(f"\n[ {msg} ]\n")

    with st.spinner("Scoring your resume against the rubric..."):
        review = review_resume(
            resume_text,
            jd_text=jd_text if has_jd else None,
            on_chunk=_on_chunk,
            on_event=_on_event,
        )
        match = None
        if has_jd:
            _on_event("computing match + gap analysis")
            match = analyze_match(resume_text, jd_text, on_chunk=_on_chunk)

    st.session_state["last_review"] = review
    st.session_state["last_resume_text"] = resume_text
    st.session_state["last_match"] = match
    st.session_state["review_done"] = True
    st.session_state.setdefault("history", []).append(
        {
            "ts": datetime.now().strftime("%H:%M:%S"),
            "overall": review.overall_score,
            "formatting": review.formatting_score,
            "clarity": review.clarity_score,
            "impact": review.impact_score,
            "keyword_match": review.keyword_match_score,
            "match_pct": match["match_percentage"] if match else None,
        }
    )


def _render_review() -> None:
    review = st.session_state["last_review"]
    match = st.session_state.get("last_match")

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
                f'<div class="wmd-card-label">Job Match'
                f'<span class="wmd-tip" title="How closely your resume fits the job description">?</span></div>'
                f'<div class="wmd-card-score" style="color:{ACCENT_PURPLE}">{pct}'
                f'<span style="font-size:1rem;color:#9f9fa9">%</span></div>'
                f'<div class="wmd-bar"><div class="wmd-bar-fill" style="width:{pct}%;'
                f'background:linear-gradient(90deg,{ACCENT_PURPLE},{ACCENT_PURPLE})"></div></div>'
                f'<div style="color:#9f9fa9;font-size:.8rem;margin-top:.4rem">'
                f"Semantic similarity: {match['semantic_similarity']:.3f}</div>"
                f"</div>"
            )
        else:
            score_card(
                "Job Match",
                None,
                accent=ACCENT_PURPLE,
                note="Paste a job description to get a match score.",
                tip="How closely your resume fits a job description. Requires a JD.",
            )

    st.caption(
        "Overall is a holistic summary; when a job description is given, "
        "keyword match is weighed heavily."
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
            score_card(label, value, accent=CATEGORY_ACCENTS[key], note=note, tip=CATEGORY_TIPS[key])

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

    # ---- 06 / Score history ----
    history = st.session_state.get("history", [])
    if history:
        eyebrow("06", "Score History")
        for i, entry in enumerate(history, 1):
            prev = history[i - 2]["overall"] if i >= 2 else None
            delta_html = ""
            if prev is not None:
                diff = entry["overall"] - prev
                if diff > 0:
                    cls, sym, d = "up", "▲", f"+{diff}"
                elif diff < 0:
                    cls, sym, d = "down", "▼", f"{diff}"
                else:
                    cls, sym, d = "same", "=", "0"
                delta_html = f' <span class="wmd-delta {cls}">({sym}{d})</span>'
            match_html = (
                f' · Match {entry["match_pct"]}%'
                if entry["match_pct"] is not None
                else ""
            )
            html(
                f'<div class="wmd-item"><span class="wmd-item-mark">#{i}</span>'
                f"<span>Run {i} &middot; {entry['ts']} &middot; Overall "
                f"<b>{entry['overall']}</b>/100{match_html}{delta_html}</span></div>"
            )
        if st.button("Clear history", key="clear_history"):
            st.session_state["history"] = []
            st.rerun()

    # ---- 07 / Ask about your review ----
    eyebrow("07", "Ask About Your Review")
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask anything about your resume or the review...")
    if prompt:
        st.session_state["chat"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            holder = st.empty()
            chat_buf: list[str] = []

            def _chat_emit(piece: str) -> None:
                chat_buf.append(piece)
                holder.markdown("".join(chat_buf))

            chat.ask_follow_up(
                st.session_state["last_resume_text"],
                st.session_state["last_review"],
                prompt,
                on_chunk=_chat_emit,
            )
            st.session_state["chat"].append(
                {"role": "assistant", "content": "".join(chat_buf)}
            )


if st.session_state["review_done"]:
    _render_review()

divider()
footer("Built with LangChain · sentence-transformers · ChromaDB · Groq · Streamlit")
