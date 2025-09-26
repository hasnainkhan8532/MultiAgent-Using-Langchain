"""
RAG (Retrieval Augmented Generation) data models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from app.core.database import Base


class DocumentChunk(Base):
    """Document chunk for vector storage"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    source_id = Column(Integer, nullable=False)  # ID of source document/data
    source_type = Column(String(50), nullable=False)  # 'scraped', 'uploaded', 'notes'
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_metadata = Column(JSON)
    embedding_id = Column(String(255))  # Reference to vector database
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RAGQuery(Base):
    """RAG query history"""
    __tablename__ = "rag_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    query = Column(Text, nullable=False)
    context_chunks = Column(JSON)  # Retrieved context chunks
    response = Column(Text)
    query_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeBase(Base):
    """Knowledge base configuration"""
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    config = Column(JSON)  # Vector DB configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
