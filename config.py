"""Central config: model names and tunable settings for the agent."""

# Embedding model used for semantic comparison (Phase 2).
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# LLM provider + model used for evaluation (Phase 4).
# Providers live here so a backup (e.g. Gemini) can be added later in one spot.
LLM_PROVIDER = "groq"
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.2

# Retrieval settings (Phase 3).
RETRIEVAL_TOP_K = 5

# Text chunking settings (Phases 2-3).
CHUNK_MAX_CHARS = 600
CHUNK_OVERLAP = 80
