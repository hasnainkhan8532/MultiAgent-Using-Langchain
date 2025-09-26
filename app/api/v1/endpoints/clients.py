"""
Client management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.client import Client, ClientData
from app.services.rag_service import RAGService
from app.core.config import settings

router = APIRouter()

# Initialize RAG service
rag_service = RAGService(persist_directory=settings.chroma_persist_directory)


class ClientCreate(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientDataCreate(BaseModel):
    data_type: str
    title: str
    content: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/", response_model=dict)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    try:
        # Check if client already exists
        existing_client = db.query(Client).filter(Client.email == client.email).first()
        if existing_client:
            raise HTTPException(status_code=400, detail="Client with this email already exists")
        
        # Create new client
        db_client = Client(**client.dict())
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        
        return {
            "message": "Client created successfully",
            "client_id": db_client.id,
            "client": {
                "id": db_client.id,
                "name": db_client.name,
                "email": db_client.email,
                "company": db_client.company,
                "website": db_client.website
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[dict])
async def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all clients"""
    try:
        clients = db.query(Client).filter(Client.is_active == True).offset(skip).limit(limit).all()
        
        return [
            {
                "id": client.id,
                "name": client.name,
                "email": client.email,
                "company": client.company,
                "website": client.website,
                "industry": client.industry,
                "created_at": client.created_at
            }
            for client in clients
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}", response_model=dict)
async def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a specific client"""
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return {
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "company": client.company,
            "website": client.website,
            "phone": client.phone,
            "address": client.address,
            "industry": client.industry,
            "description": client.description,
            "notes": client.notes,
            "metadata": client.metadata,
            "is_active": client.is_active,
            "created_at": client.created_at,
            "updated_at": client.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{client_id}", response_model=dict)
async def update_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    """Update a client"""
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Update fields
        update_data = client_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        db.commit()
        db.refresh(client)
        
        return {
            "message": "Client updated successfully",
            "client": {
                "id": client.id,
                "name": client.name,
                "email": client.email,
                "company": client.company,
                "website": client.website
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{client_id}", response_model=dict)
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client (soft delete)"""
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Soft delete
        client.is_active = False
        db.commit()
        
        # Delete client data from RAG system
        rag_service.delete_client_documents(client_id)
        
        return {"message": "Client deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/data", response_model=dict)
async def upload_client_data(
    client_id: int,
    data_type: str,
    title: str,
    content: Optional[str] = None,
    file: Optional[UploadFile] = File(None),
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Upload client data (text or file)"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Handle file upload
        file_path = None
        file_size = 0
        file_content = content
        
        if file:
            # Save file
            import os
            os.makedirs(settings.upload_directory, exist_ok=True)
            file_path = os.path.join(settings.upload_directory, f"{client_id}_{file.filename}")
            
            with open(file_path, "wb") as buffer:
                content_data = await file.read()
                buffer.write(content_data)
                file_size = len(content_data)
            
            # Extract text content from file
            file_content = await extract_file_content(file_path, file.content_type)
        
        # Create client data record
        client_data = ClientData(
            client_id=client_id,
            data_type=data_type,
            title=title,
            content=file_content,
            file_path=file_path,
            file_type=file.content_type if file else None,
            file_size=file_size,
            metadata=metadata or {}
        )
        
        db.add(client_data)
        db.commit()
        db.refresh(client_data)
        
        # Add to RAG system
        if file_content:
            documents = [{
                'content': file_content,
                'title': title,
                'source_id': client_data.id,
                'source_type': data_type
            }]
            rag_service.add_documents(documents, client_id)
            
            # Mark as processed
            client_data.is_processed = True
            db.commit()
        
        return {
            "message": "Client data uploaded successfully",
            "data_id": client_data.id,
            "processed": client_data.is_processed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/data", response_model=List[dict])
async def get_client_data(client_id: int, db: Session = Depends(get_db)):
    """Get all data for a client"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client_data = db.query(ClientData).filter(ClientData.client_id == client_id).all()
        
        return [
            {
                "id": data.id,
                "data_type": data.data_type,
                "title": data.title,
                "file_type": data.file_type,
                "file_size": data.file_size,
                "is_processed": data.is_processed,
                "created_at": data.created_at
            }
            for data in client_data
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def extract_file_content(file_path: str, content_type: str) -> str:
    """Extract text content from various file types"""
    try:
        if content_type == "text/plain":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        elif content_type == "application/pdf":
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            from docx import Document
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        elif content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_string()
        
        else:
            # Try to read as text
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
                
    except Exception as e:
        return f"Error extracting content: {str(e)}"
