# Resume Review Agent

**Under construction — Phase 0 (environment setup) complete.**

A free web app that reviews your resume: upload a resume (PDF/DOCX), optionally
paste a job description, and get structured scores (formatting, clarity,
impact, keyword match) plus specific improvement suggestions — in ~30 seconds.

## Stack

Python, LangChain, sentence-transformers (all-MiniLM-L6-v2), ChromaDB,
Groq/Gemini APIs, Pydantic, Streamlit.

## Concepts implemented (as the project is built)

Document processing, embeddings, vector search, RAG, prompt engineering,
structured output, evaluation.

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
```

API keys go in a `.env` file (see `.env.example`). They are never committed.

## Roadmap

- [x] Phase 1 — Document processing (PDF/DOCX → clean text + sections)
- [x] Phase 2 — Embeddings
- [x] Phase 3 — Vector DB + retrieval (ChromaDB)
- [x] Phase 4 — Structured evaluation (LLM + Pydantic)
- [x] Phase 5 — Job-description match score
- [x] Phase 6 — Suggestions engine
- [x] Phase 7 — Streamlit UI
- [ ] Phase 8 — Deployment (Streamlit Community Cloud)
- [ ] Phase 9 — Evaluation
- [ ] Phase 10 — README + CV packaging
