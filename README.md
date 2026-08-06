# Resume Review Agent

Web app that analyzes resumes and gives actionable feedback.

Upload a resume (PDF or DOCX). Optionally add a job description. The app scores your resume on formatting, clarity, and impact, and returns a list of specific things to improve. Runs in about 30 seconds.

## What it does

- Scores your resume out of 100 (formatting, clarity, impact)
- With a job description: match percentage, semantic similarity, and a gap analysis
- Returns specific, actionable suggestions for each section
- Lists your strengths

## How it works

1. The uploaded file is parsed into plain text.
2. If a job description is given, it is chunked, embedded, and stored in a vector store.
3. The most relevant job-description sections are retrieved for each part of the resume.
4. An LLM scores the resume against a rubric and returns structured JSON, validated with Pydantic.

## Tech stack

- Streamlit - web UI
- LangChain - orchestration and LLM calls
- Groq - LLM provider
- sentence-transformers (all-MiniLM-L6-v2) - local embeddings
- ChromaDB - vector store
- Pydantic - structured output validation
- pypdf / python-docx - file parsing

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your `GROQ_API_KEY`. Then start the app:

```bash
.venv\Scripts\python -m streamlit run app.py
```

The embedding model downloads automatically on the first run.

## Deploy

Push the repo to GitHub, then create a new app on Streamlit Community Cloud using `app.py` as the main file. Add `GROQ_API_KEY` in the app's secrets settings.

## Project layout

```
app.py            Streamlit UI and orchestration
resume_parser.py  PDF / DOCX to plain text
embeddings.py     Text chunking and embeddings
retriever.py      ChromaDB vector store and retrieval
evaluation.py     Scoring prompt and structured output
match_score.py    Job match and gap analysis
llm.py            Groq client
config.py         App settings
theme.py          UI styling
tests/            Test scripts per phase
sample_resumes/   Sample resumes
```

## Roadmap

- ATS compatibility checker
- Cover-letter generator
- Multi-resume comparison
- Score history tracking
