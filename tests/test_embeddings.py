"""Phase 2 tests: embeddings capture meaning, not just exact words."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from embeddings import chunk_text, cosine_similarity, embed_text, embed_texts


def test_similar_pair_closer_than_unrelated() -> None:
    resume_style = "Led a team of 5 engineers to ship a new product"
    jd_style = "Managed a small engineering team to release software"
    unrelated = "I cooked pasta with tomato sauce for dinner"
    s_similar = cosine_similarity(embed_text(resume_style), embed_text(jd_style))
    s_unrelated = cosine_similarity(embed_text(resume_style), embed_text(unrelated))
    print(f"  similar pair:   {s_similar:.4f}")
    print(f"  unrelated pair: {s_unrelated:.4f}")
    assert s_similar > s_unrelated
    assert s_similar > 0.3
    assert s_unrelated < 0.4


def test_same_text_is_almost_identical() -> None:
    text = "Analyzed customer churn and improved retention by 12%"
    s = cosine_similarity(embed_text(text), embed_text(text))
    print(f"  self-similarity: {s:.4f}")
    assert s > 0.99


def test_embed_texts_batches() -> None:
    vectors = embed_texts(["one", "two", "three"])
    assert len(vectors) == 3
    assert all(len(v) == 384 for v in vectors)


def test_chunk_text_splits_and_overlaps() -> None:
    lines = [f"bullet line {i} about SQL and Tableau dashboards" for i in range(30)]
    text = "\n".join(lines)
    chunks = chunk_text(text, max_chars=400, overlap=60)
    print(f"  {len(chunks)} chunks from {len(text)} chars")
    assert len(chunks) > 1
    assert all(len(c) <= 500 for c in chunks)
    assert all(c.strip() for c in chunks)


if __name__ == "__main__":
    test_similar_pair_closer_than_unrelated()
    test_same_text_is_almost_identical()
    test_embed_texts_batches()
    test_chunk_text_splits_and_overlaps()
    print("All Phase 2 tests passed.")
