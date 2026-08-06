# Resume Review Agent

A free web app that reviews your resume: upload a resume (PDF/DOCX), optionally
paste a job description, and get structured scores (formatting, clarity,
impact, keyword match) plus specific improvement suggestions — in ~30 seconds.

## Stack

Python, LangChain, sentence-transformers (all-MiniLM-L6-v2), ChromaDB,
Groq/Gemini APIs, Pydantic, Streamlit.

## Concepts implemented (as the project is built)

Document processing, embeddings, vector search, RAG, prompt engineering,
structured output, evaluation.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
# copy .env.example to .env and add GROQ_API_KEY
.venv\Scripts\python -m streamlit run app.py
```

API keys go in a `.env` file (see `.env.example`). They are never committed.

## Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io (or the Streamlit Community Cloud dashboard)
   and create a new app from that GitHub repo.
3. In **Advanced settings → Secrets**, add:
   `GROQ_API_KEY = "your_key_here"` (this becomes available to the app as a
   secret; it is never stored in the repo).
4. Deploy. The embedding model downloads on first use; the first review may be
   slow while it loads.

## Roadmap

- [x] Phase 1 — Document processing (PDF/DOCX → clean text + sections)
- [x] Phase 2 — Embeddings
- [x] Phase 3 — Vector DB + retrieval (ChromaDB)
- [x] Phase 4 — Structured evaluation (LLM + Pydantic)
- [x] Phase 5 — Job-description match score
- [x] Phase 6 — Suggestions engine
- [x] Phase 7 — Streamlit UI
- [x] Phase 8 — Deployment (Streamlit Community Cloud)
- [ ] Phase 9 — Evaluation
- [ ] Phase 10 — README + CV packaging
