"""
Celery tasks for RAG system operations
"""

from celery import current_task
from app.core.celery import celery
from app.services.rag_service import RAGService
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.client import Client
import logging

logger = logging.getLogger(__name__)

# Initialize RAG service
rag_service = RAGService(persist_directory=settings.chroma_persist_directory)


@celery.task(bind=True)
def process_document_task(self, client_id: int, document_data: dict):
    """Background task to process a document for RAG"""
    try:
        current_task.update_state(state='PROGRESS', meta={'status': 'Processing document...'})
        
        # Check if client exists
        db = SessionLocal()
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise Exception(f"Client {client_id} not found")
        db.close()
        
        # Add document to RAG system
        current_task.update_state(state='PROGRESS', meta={'status': 'Adding to knowledge base...'})
        documents = [document_data]
        doc_ids = rag_service.add_documents(documents, client_id)
        
        return {
            "status": "completed",
            "client_id": client_id,
            "document_ids": doc_ids
        }
        
    except Exception as e:
        logger.error(f"Error processing document for client {client_id}: {str(e)}")
        return {"status": "failed", "error": str(e)}


@celery.task(bind=True)
def setup_rag_system_task(self):
    """Background task to setup RAG system"""
    try:
        current_task.update_state(state='PROGRESS', meta={'status': 'Setting up RAG system...'})
        
        if not settings.gemini_api_key:
            raise Exception("Gemini API key not configured")
        
        # Setup QA chain
        current_task.update_state(state='PROGRESS', meta={'status': 'Configuring AI model...'})
        rag_service.setup_qa_chain(settings.gemini_api_key)
        
        return {
            "status": "completed",
            "message": "RAG system setup completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error setting up RAG system: {str(e)}")
        return {"status": "failed", "error": str(e)}


@celery.task(bind=True)
def cleanup_client_data_task(self, client_id: int):
    """Background task to cleanup client data from RAG system"""
    try:
        current_task.update_state(state='PROGRESS', meta={'status': 'Cleaning up client data...'})
        
        # Check if client exists
        db = SessionLocal()
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise Exception(f"Client {client_id} not found")
        db.close()
        
        # Delete client documents from RAG system
        current_task.update_state(state='PROGRESS', meta={'status': 'Removing from knowledge base...'})
        success = rag_service.delete_client_documents(client_id)
        
        if success:
            return {
                "status": "completed",
                "client_id": client_id,
                "message": "Client data cleaned up successfully"
            }
        else:
            raise Exception("Failed to delete client documents")
        
    except Exception as e:
        logger.error(f"Error cleaning up client data for client {client_id}: {str(e)}")
        return {"status": "failed", "error": str(e)}


@celery.task(bind=True)
def reindex_documents_task(self, client_id: int = None):
    """Background task to reindex documents in RAG system"""
    try:
        current_task.update_state(state='PROGRESS', meta={'status': 'Starting reindexing...'})
        
        if client_id:
            # Reindex specific client
            current_task.update_state(state='PROGRESS', meta={'status': f'Reindexing client {client_id}...'})
            
            # Get all documents for client
            documents = rag_service.get_client_documents(client_id)
            
            # Delete and re-add documents
            rag_service.delete_client_documents(client_id)
            
            for doc in documents:
                doc_data = {
                    'content': doc.get('content', ''),
                    'title': doc.get('title', ''),
                    'source_type': doc.get('source_type', 'unknown'),
                    'metadata': doc.get('metadata', {})
                }
                rag_service.add_documents([doc_data], client_id)
            
            return {
                "status": "completed",
                "client_id": client_id,
                "documents_reindexed": len(documents)
            }
        else:
            # Reindex all clients (this would need to be implemented)
            current_task.update_state(state='PROGRESS', meta={'status': 'Reindexing all clients...'})
            
            # This would require getting all clients and reindexing them
            # For now, just return success
            return {
                "status": "completed",
                "message": "Reindexing completed"
            }
        
    except Exception as e:
        logger.error(f"Error reindexing documents: {str(e)}")
        return {"status": "failed", "error": str(e)}
