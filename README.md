# Resume Review Agent

AI resume review, powered by RAG — upload a resume, get a rubric-based score and actionable feedback in ~30 seconds.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io)
[![LLM](https://img.shields.io/badge/LLM-Groq-orange)](https://groq.com)

A free web app that analyzes resumes (PDF or DOCX) against a rubric and — optionally — a target job description.

## Features

- **Rubric-based scoring** — structured 0–100 scores for formatting, clarity, and impact, plus an overall score.
- **Job-match analysis** — when a job description is provided, get a match percentage, semantic similarity score, and keyword match, with a grounded gap-analysis paragraph.
- **Retrieval-augmented evaluation** — relevant JD sections are retrieved from a vector store and cited in the review, reducing hallucination.
- **Specific, actionable feedback** — targeted improvement suggestions and a strengths list, not generic advice.
- **Fast and free** — ~30-second turnarounds on a hosted Groq LLM; local embeddings need no API key.
- **Validated structured output** — Pydantic-typed LLM output, validated and retried on failure.

## How it works

The app parses the uploaded document into plain text, chunks and embeds it, then (optionally) retrieves only the job-description chunks most relevant to each resume section. The LLM reviews each section against a scoring rubric and emits a structured, validated JSON report.

```
Upload → Parse → Chunk → Embed → Retrieve (JD) → Rubric-Score → Validate → Report
```

## Screenshot

![Demo](docs/screenshot.png)

*Add a screenshot of the results view here.*

## Built with

| Layer | Tech |
|---|---|
| UI | Streamlit |
| Orchestration / LLM | LangChain + Groq (`llama-3.3-70b-versatile`) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, no API key) |
| Retrieval | ChromaDB vector store |
| Document parsing | `pypdf`, `python-docx` |
| Structured output | Pydantic with validation + retry |
| Config / secrets | `python-dotenv`, Streamlit secrets |

## Getting started (local)

```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

1. Copy `.env.example` to `.env` and add your `GROQ_API_KEY`.
2. Launch the app:

```bash
.venv\Scripts\python -m streamlit run app.py
```

The embedding model (`all-MiniLM-L6-v2`) downloads automatically on first run.

## Deployment

1. Push the repo to GitHub.
2. On [Streamlit Community Cloud](https://streamlit.io/cloud), click **New app**, select the repo, and set the main file to `app.py`.
3. Add the `GROQ_API_KEY` secret under **Advanced settings → Secrets**.
4. Deploy. The embedding model is bundled automatically at deploy time.

## Project structure

```
app.py                 Streamlit entry point (UI, session state, orchestration)
resume_parser.py       PDF / DOCX → plain text extraction
embeddings.py          Text chunking + local embedding model
retriever.py           ChromaDB vector store and JD retrieval
evaluation.py          Rubric prompt, structured scoring, output validation
match_score.py         Job-match %, semantic similarity, gap analysis
llm.py                 LangChain + Groq client wrapper
config.py              Settings, model names, and constants
theme.py               UI styling helpers
tests/                 Per-phase pytest-style verification scripts
sample_resumes/        Sample resumes of varying quality for testing
```

## Evaluation

The project ships with sample resumes of varying quality to sanity-check that scoring ranks them in the expected order, and Phase 9 verifies consistency by scoring the same resume repeatedly and confirming the results are stable.

## Roadmap

- **ATS compatibility checker** — flag formatting that confuses applicant tracking systems.
- **Cover-letter generator** — draft a tailored cover letter from the same match analysis.
- **Multi-resume comparison** — compare candidates side by side against one JD.
- **Feedback memory** — let users track score improvements across revisions.
