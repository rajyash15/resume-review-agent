# Resume Review Agent

A simple web app that reviews resumes. Upload a PDF or DOCX, optionally paste a job description, and it gives you scores (formatting, clarity, impact, keyword match) plus specific suggestions on what to improve. Runs in about 30 seconds.

Built with Streamlit, LangChain, Groq, and ChromaDB.

## How it works

1. The resume is parsed into plain text (PDF or DOCX).
2. If you provide a job description, its content is embedded and the most relevant sections are retrieved.
3. The LLM scores each part of your resume against a rubric and returns a structured report (validated with Pydantic).

```
Upload → Parse → Embed → Retrieve (JD) → Score → Report
```

## Features

- Score your resume 0-100 on formatting, clarity, and impact
- Optional job-description matching: match percentage, semantic similarity, and a gap analysis
- Specific, actionable suggestions (not generic advice)
- All free — Groq for the LLM, local embeddings, no API key needed for the model

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your `GROQ_API_KEY`, then run:

```bash
.venv\Scripts\python -m streamlit run app.py
```

The embedding model (`all-MiniLM-L6-v2`) downloads automatically on first run.

## Deploy

Push to GitHub, then create a new app on [Streamlit Community Cloud](https://streamlit.io/cloud) pointing at `app.py`. Add `GROQ_API_KEY` under **Advanced settings → Secrets**.

## Project structure

```
app.py            Streamlit UI + orchestration
resume_parser.py  PDF/DOCX → text
embeddings.py     Text chunking + embeddings
retriever.py      ChromaDB vector store
evaluation.py     Scoring prompt + structured output
match_score.py    JD match % + gap analysis
llm.py            Groq client
config.py         Settings
theme.py          UI styling
tests/            Per-phase test scripts
sample_resumes/   Sample resumes for testing
```

## Roadmap

- ATS compatibility checker
- Cover-letter generator
- Multi-resume comparison
- Track score improvements across revisions
