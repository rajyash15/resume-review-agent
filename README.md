# Resume Review Agent

A free web app that reviews resumes and returns rubric-based scores, strengths, and specific, actionable improvement suggestions.

## What it does

Upload a resume (PDF or DOCX) and optionally paste a job description. The app scores the resume out of 100 on formatting, clarity, and impact, shows an overall score, lists what the resume does well, and gives specific things to fix. When a job description is provided it also returns a keyword match score, a match percentage, a semantic similarity value, and a short gap analysis naming what the resume is missing for that role. A full review takes about 30 seconds.

## How it works

1. The uploaded file is parsed into clean plain text. PDF and DOCX are both supported. Common resume sections (summary, experience, education, skills, projects, certifications, languages) are detected with heading patterns; content before the first heading is treated as the header.
2. If a job description is pasted, it is split into overlapping text chunks, embedded locally with sentence-transformers, and stored in a persistent ChromaDB vector store under `.chroma/`.
3. Each resume chunk is used as a query; the most relevant JD chunks (similarity above 0.30) are retrieved and given to the LLM as context. This is the retrieval step in the RAG pipeline.
4. The LLM (Groq, llama-3.3-70b-versatile) scores the resume against a fixed rubric and must reply with a single JSON object. The reply is validated against a Pydantic schema; malformed replies are fed back with the parse error and the model retries, up to three attempts.
5. With a JD, the whole-resume and whole-JD embeddings are compared with cosine similarity and rescaled into a 0-100 match percentage, and a second LLM call writes a grounded gap analysis.

## Features

- Scores out of 100 for formatting, clarity, and impact, plus an overall score
- Keyword match score when a job description is provided (omitted otherwise)
- 2-4 strengths and 3-5 improvement suggestions, each grounded in the actual resume text
- Match percentage and semantic similarity against a job description
- Gap analysis paragraph naming missing or understated requirements
- PDF and DOCX parsing with bullet, whitespace, and line-wrap normalization
- Persistent local ChromaDB index; no separate vector database server
- Embeddings run locally, so only the LLM calls need an API key
- Dark, wemakedevs-style theme (custom CSS in `theme.py`, plus `.streamlit/config.toml`)

## Tech stack

- Streamlit - web UI
- LangChain + langchain-groq - LLM orchestration
- Groq - LLM provider, model `llama-3.3-70b-versatile`
- sentence-transformers - embeddings, model `all-MiniLM-L6-v2` (384-dim)
- ChromaDB - persistent vector store
- Pydantic - structured output validation
- pypdf, python-docx - file parsing
- python-dotenv - local environment loading

## Run locally

Windows:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `GROQ_API_KEY` (a free key from the Groq console). The `.env` file is gitignored and should never be committed.

Then start the app:

```bash
.venv\Scripts\python -m streamlit run app.py
```

The embedding model downloads automatically on first run. The local venv in this repo was built with Python 3.14.

## Deployment

The app is ready for Streamlit Community Cloud: push the repo to GitHub, create a new app pointing at `app.py`, and add `GROQ_API_KEY` in the app's Secrets settings. `llm.py` checks Streamlit secrets first and falls back to environment variables, so the same code works locally and in the cloud. `.streamlit/config.toml` already sets `headless = true` and disables usage stats.

## Project structure

```
app.py            Streamlit UI and orchestration
resume_parser.py  PDF/DOCX to clean text plus section detection
embeddings.py     Chunking, embeddings, cosine similarity
retriever.py      ChromaDB persistent index and top-k retrieval
evaluation.py     Rubric prompt, Pydantic validation, JSON retry loop
match_score.py    Match percentage and LLM gap analysis
llm.py            API key resolution and Groq client factory
config.py         Model names and tunable settings
theme.py          Dark theme CSS and HTML helpers
tests/            Phase-by-phase test scripts
sample_resumes/   Sample PDF/DOCX resume for testing
```

## Testing

The tests are plain Python scripts with `test_` functions (pytest is not required). Run each phase directly:

```bash
.venv\Scripts\python tests\test_parser.py        # Phase 1: parsing and section detection
.venv\Scripts\python tests\test_embeddings.py    # Phase 2: embeddings and chunking
.venv\Scripts\python tests\test_retriever.py     # Phase 3: ChromaDB index and retrieval
.venv\Scripts\python tests\test_evaluation.py    # Phase 4: live LLM review (needs GROQ_API_KEY)
.venv\Scripts\python tests\test_match_score.py   # Phase 5-6: match % and gap analysis (needs GROQ_API_KEY)
```

The first three phases are offline. Phases 4 and 5-6 make live Groq API calls, so they require `GROQ_API_KEY` in `.env`. Note that `test_retriever.py` writes to the local `.chroma/` index. `tests/make_sample_resumes.py` regenerates the sample resume files and needs `reportlab`, which is deliberately not in `requirements.txt`.

## Roadmap

- ATS compatibility checker
- Cover-letter generator
- Multi-resume comparison
- Score history tracking
