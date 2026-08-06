"""Embeddings: turn text chunks into meaning-vectors and compare them.

Phase 2 of the Resume Review Agent.

Uses the free, local sentence-transformers model `all-MiniLM-L6-v2` — no API
key, no internet call once the model is downloaded. The model is loaded once
per process (a module-level lazy singleton) because loading is the slow part.
"""

from __future__ import annotations

from typing import Optional

from sentence_transformers import SentenceTransformer, util

# A small, fast embedding model. Outputs 384-dimension vectors. See the model
# card at https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
MODEL_NAME = "all-MiniLM-L6-v2"

_model: Optional[SentenceTransformer] = None


def get_model() -> SentenceTransformer:
    """Return the loaded model, downloading it on first use."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return an embedding vector for each text."""
    if not texts:
        return []
    model = get_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).tolist()


def embed_text(text: str) -> list[float]:
    """Return the embedding vector for a single text."""
    return embed_texts([text])[0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors (0 = unrelated, 1 = identical).

    Embeddings from `embed_texts` are already length-normalized, so this is a
    simple dot product. Range is roughly -1..1 in general, but for semantic
    similarity we expect mostly positive values.
    """
    return float(util.cos_sim(a, b)[0][0])


def chunk_text(text: str, max_chars: int = 600, overlap: int = 80) -> list[str]:
    """Split text into overlapping chunks of roughly `max_chars` characters.

    Splits on line boundaries first, then fills chunks to the limit. Keeps
    related lines (bullets, sentences) together where possible. The small
    overlap gives the retrieval step context across chunk boundaries.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    lines = text.split("\n")
    chunks: list[str] = []
    current = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if current and len(current) + len(line) + 1 > max_chars:
            chunks.append(current)
            # Overlap: carry over the tail of the finished chunk.
            tail = current[-overlap:].split("\n", 1)[-1].lstrip()
            current = tail + " " if tail else ""
        current = f"{current} {line}".strip()

    if current:
        chunks.append(current)
    return chunks
