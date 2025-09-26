"""
Web scraping data models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class ScrapingJob(Base):
    """Web scraping job model"""
    __tablename__ = "scraping_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    url = Column(String(1000), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    scraping_type = Column(String(50), default="general")  # general, ecommerce, blog, etc.
    config = Column(JSON)  # Scraping configuration
    result = Column(JSON)  # Scraped data
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScrapedData(Base):
    """Scraped website data model"""
    __tablename__ = "scraped_data"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("scraping_jobs.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    page_url = Column(String(1000), nullable=False)
    page_title = Column(String(500))
    content_type = Column(String(50))  # text, html, json, etc.
    content = Column(Text)
    page_metadata = Column(JSON)  # Additional page metadata
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
