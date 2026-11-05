from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

from app.config import get_settings

Base = declarative_base()


def _utcnow() -> datetime:
    """Return the current UTC time as a naive datetime, matching the columns."""
    return datetime.now(UTC).replace(tzinfo=None)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    text_content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=_utcnow)
    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk = Column(String)
    embedding = Column(Vector(get_settings().embeddings_dimensions))
    created_at = Column(DateTime, default=_utcnow)
    document = relationship("Document", back_populates="chunks")
