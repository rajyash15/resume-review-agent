"""Vector database & retrieval: index text chunks in ChromaDB and search by meaning.

Phase 3 of the Resume Review Agent. This is the "R" in RAG — before the LLM
reasons about a resume, we retrieve only the most relevant job-description
chunks and give those to it as context.

ChromaDB runs locally as a Python library (no separate server). Indexed data
persists on disk under `.chroma/`, which is gitignored.
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.config import Settings

from embeddings import chunk_text, embed_texts

DB_DIR = Path(__file__).resolve().parent / ".chroma"
COLLECTION_NAME = "jd_chunks"


def _client() -> "chromadb.ClientAPI":
    return chromadb.PersistentClient(
        path=str(DB_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def _collection(client: "chromadb.ClientAPI | None" = None):
    client = client or _client()
    return client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def index_text(text: str) -> list[str]:
    """Replace the stored index with chunks of `text`, embedding them by meaning.

    Returns the chunks that were stored (useful for debugging and for the
    caller to know what got indexed).
    """
    chunks = chunk_text(text)
    if not chunks:
        return []

    ids = [f"jd-{i}" for i in range(len(chunks))]
    vectors = embed_texts(chunks)

    client = _client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # collection didn't exist yet
    collection = _collection(client)
    collection.add(ids=ids, embeddings=vectors, documents=chunks)
    return chunks


def has_index() -> bool:
    """True if the database holds at least one stored chunk."""
    return _collection().count() > 0


def retrieve_top_k(query_text: str, k: int = 5) -> list[tuple[str, float]]:
    """Return the k most semantically similar stored chunks to `query_text`.

    Returns a list of (chunk, similarity) pairs, best first. Similarity is
    cosine similarity in 0..1 (roughly); higher is more similar.
    """
    collection = _collection()
    count = collection.count()
    if count == 0:
        return []

    vector = embed_texts([query_text])
    results = collection.query(
        query_embeddings=vector,
        n_results=min(k, count),
    )

    docs = results["documents"][0]
    distances = results["distances"][0]  # cosine distance = 1 - similarity
    return [
        (doc, round(1.0 - dist, 4))
        for doc, dist in zip(docs, distances)
    ]
