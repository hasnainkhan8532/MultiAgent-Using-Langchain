"""
RAG (Retrieval Augmented Generation) endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.client import Client
from app.services.rag_service import RAGService
from app.core.config import settings

router = APIRouter()

# Initialize RAG service
rag_service = RAGService(persist_directory=settings.chroma_persist_directory)


class QueryRequest(BaseModel):
    client_id: int
    query: str
    k: Optional[int] = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    question: str


class DocumentRequest(BaseModel):
    client_id: int
    content: str
    title: str
    source_type: str = "manual"
    metadata: Optional[dict] = None


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Query the RAG system"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == query_request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Check if Gemini API key is configured
        if not settings.gemini_api_key:
            raise HTTPException(status_code=400, detail="Gemini API key not configured")
        
        # Setup QA chain if not already done
        if not rag_service.qa_chain:
            rag_service.setup_qa_chain(settings.gemini_api_key)
        
        # Query the RAG system
        result = rag_service.query(query_request.query, query_request.client_id)
        
        return QueryResponse(
            answer=result['answer'],
            sources=result['sources'],
            question=result['question']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[dict])
async def search_documents(
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Search for relevant documents without AI generation"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == query_request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Search documents
        results = rag_service.search_documents(
            query_request.query,
            query_request.client_id,
            query_request.k
        )
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents", response_model=dict)
async def add_document(
    document_request: DocumentRequest,
    db: Session = Depends(get_db)
):
    """Add a document to the RAG system"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == document_request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Add document to RAG system
        documents = [{
            'content': document_request.content,
            'title': document_request.title,
            'source_type': document_request.source_type,
            'metadata': document_request.metadata or {}
        }]
        
        doc_ids = rag_service.add_documents(documents, document_request.client_id)
        
        return {
            "message": "Document added successfully",
            "document_ids": doc_ids
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{client_id}", response_model=List[dict])
async def get_client_documents(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get all documents for a client"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get documents from RAG system
        documents = rag_service.get_client_documents(client_id)
        
        return documents
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{client_id}", response_model=dict)
async def delete_client_documents(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Delete all documents for a client"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Delete documents from RAG system
        success = rag_service.delete_client_documents(client_id)
        
        if success:
            return {"message": "Client documents deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete documents")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/setup", response_model=dict)
async def setup_rag_system(db: Session = Depends(get_db)):
    """Setup RAG system with Gemini"""
    try:
        if not settings.gemini_api_key:
            raise HTTPException(status_code=400, detail="Gemini API key not configured")
        
        # Setup QA chain
        rag_service.setup_qa_chain(settings.gemini_api_key)
        
        return {"message": "RAG system setup completed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=dict)
async def get_rag_status():
    """Get RAG system status"""
    try:
        status = {
            "vector_store_initialized": rag_service.vectorstore is not None,
            "qa_chain_initialized": rag_service.qa_chain is not None,
            "gemini_configured": bool(settings.gemini_api_key),
            "persist_directory": settings.chroma_persist_directory
        }
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
