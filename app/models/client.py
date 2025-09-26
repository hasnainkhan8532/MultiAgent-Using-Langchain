"""
Client data models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Client(Base):
    """Client information model"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    company = Column(String(255))
    website = Column(String(500))
    phone = Column(String(50))
    address = Column(Text)
    industry = Column(String(100))
    description = Column(Text)
    notes = Column(Text)
    client_metadata = Column(JSON)  # Additional client data
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClientData(Base):
    """Client uploaded data model"""
    __tablename__ = "client_data"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    data_type = Column(String(50), nullable=False)  # 'document', 'website', 'notes', 'api_data'
    title = Column(String(255), nullable=False)
    content = Column(Text)
    file_path = Column(String(500))
    file_type = Column(String(50))
    file_size = Column(Integer)
    data_metadata = Column(JSON)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
