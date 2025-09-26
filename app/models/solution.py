"""
Solution generation data models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from app.core.database import Base


class Solution(Base):
    """Generated solution model"""
    __tablename__ = "solutions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    solution_type = Column(String(50), nullable=False)  # 'recommendation', 'strategy', 'implementation'
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="draft")  # draft, reviewed, approved, implemented
    content = Column(Text, nullable=False)
    solution_metadata = Column(JSON)
    confidence_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SolutionFeedback(Base):
    """Solution feedback and ratings"""
    __tablename__ = "solution_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    solution_id = Column(Integer, ForeignKey("solutions.id"), nullable=False)
    rating = Column(Integer)  # 1-5 scale
    feedback = Column(Text)
    is_helpful = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisSession(Base):
    """Client analysis session"""
    __tablename__ = "analysis_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    session_name = Column(String(255), nullable=False)
    input_data = Column(JSON)  # Client input and requirements
    analysis_results = Column(JSON)  # Analysis results
    solutions_generated = Column(JSON)  # Generated solutions
    status = Column(String(20), default="active")  # active, completed, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
