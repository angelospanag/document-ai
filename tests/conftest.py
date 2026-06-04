import os

os.environ.setdefault("GENERATION_MODEL_NAME", "test-model")
os.environ.setdefault("EMBEDDINGS_MODEL_NAME", "test-embed")
os.environ.setdefault("EMBEDDINGS_DIMENSIONS", "768")
os.environ.setdefault("DATABASE_USER", "postgres")
os.environ.setdefault("DATABASE_PASSWORD", "postgres")
os.environ.setdefault("DATABASE_NAME", "test")
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_PORT", "5432")
