# Resume Review Agent

A free web app that reviews resumes. Upload a resume (PDF or DOCX), optionally paste a job description, and get rubric-based scores, strengths, and specific improvement suggestions — in about 30 seconds.

## Features

- Scores out of 100 for **formatting**, **clarity**, and **impact**, plus an **overall** score
- 2-4 strengths and 3-5 specific, actionable suggestions, grounded in the resume text
- With a job description: **keyword match** score, **match percentage**, **semantic similarity**, and a **gap analysis** paragraph

## How it works

1. **Parse** — the uploaded file is converted to clean plain text (pypdf for PDF, python-docx for DOCX), with bullets, whitespace, and line-wraps normalized and resume sections detected.
2. **Embed** — if a job description is pasted, it is split into 600-character chunks (80-char overlap) and embedded locally with `sentence-transformers/all-MiniLM-L6-v2`.
3. **Retrieve** — chunks are stored in a persistent ChromaDB index (`.chroma/`). The most relevant JD chunks (similarity >= 0.30) are retrieved for each resume chunk and added as LLM context. This is the retrieval step in the RAG pipeline.
4. **Score** — the LLM (Groq, `llama-3.3-70b-versatile`) evaluates the resume against a fixed rubric and must reply with a single JSON object, validated against a Pydantic schema. Invalid replies are fed back with the error and retried (up to 3 attempts).
5. **Match** — with a JD, whole-document cosine similarity is rescaled from the 0.30-0.75 band into a 0-100 match percentage, and a second LLM call writes a grounded gap analysis.

```
Upload -> Parse -> Embed -> Retrieve (JD) -> Score -> Report
```

## Tech stack

| Component | Tech |
|---|---|
| Web UI | Streamlit |
| LLM orchestration | LangChain + langchain-groq |
| LLM | Groq (`llama-3.3-70b-versatile`, temperature 0.2) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, local, no API key) |
| Vector store | ChromaDB (persistent, `.chroma/`) |
| Structured output | Pydantic |
| Document parsing | pypdf, python-docx |
| Environment | python-dotenv |

Python 3.10+ required.

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your `GROQ_API_KEY` (free from the [Groq console](https://console.groq.com)). The `.env` file is gitignored.

Start the app:

```bash
.venv\Scripts\python -m streamlit run app.py
```

The embedding model downloads automatically on first run. Only the LLM calls need an API key — embeddings run locally.

## Deploy

The app is ready for Streamlit Community Cloud:

1. Push the repo to GitHub.
2. Create a new app on [Streamlit Community Cloud](https://streamlit.io/cloud), pointing at `app.py`.
3. Add `GROQ_API_KEY` in **App Settings -> Secrets**.

`llm.py` checks Streamlit secrets first, then environment variables, so the same code works locally and in the cloud.

## Testing

Tests are plain Python scripts (pytest not required). Run each phase:

```bash
.venv\Scripts\python tests\test_parser.py        # parsing + section detection (offline)
.venv\Scripts\python tests\test_embeddings.py    # embeddings + chunking (offline)
.venv\Scripts\python tests\test_retriever.py     # ChromaDB index + retrieval (offline)
.venv\Scripts\python tests\test_evaluation.py    # live LLM review (needs GROQ_API_KEY)
.venv\Scripts\python tests\test_match_score.py   # match % + gap analysis (needs GROQ_API_KEY)
```

`tests/make_sample_resumes.py` regenerates the sample resume files and requires `reportlab` (dev-only, not in `requirements.txt`).

## Project structure

```
app.py            Streamlit UI + orchestration
resume_parser.py  PDF/DOCX -> clean text + section detection
embeddings.py     Chunking, embeddings, cosine similarity
retriever.py      ChromaDB persistent index + top-k retrieval
evaluation.py     Rubric prompt, Pydantic validation, retry loop
match_score.py    Match percentage + gap analysis
llm.py            API key resolution + Groq client
config.py         Model names + settings (chunk size, top-k, ...)
theme.py          Dark UI theme + HTML helpers
tests/            Phase-by-phase test scripts
sample_resumes/   Sample PDF/DOCX resume
```

## Roadmap

- ATS compatibility checker
- Cover-letter generator
- Multi-resume comparison
- Score history tracking
