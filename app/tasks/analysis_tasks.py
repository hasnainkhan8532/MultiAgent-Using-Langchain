"""
Celery tasks for analysis and solution generation
"""

from celery import current_task
from app.core.celery import celery
from app.services.gemini_service import GeminiService
from app.services.rag_service import RAGService
from app.services.google_apis_service import GoogleAPIsService
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.client import Client
from app.models.solution import Solution
from app.models.scraping import ScrapedData
import logging

logger = logging.getLogger(__name__)

# Initialize services
gemini_service = GeminiService(settings.gemini_api_key) if settings.gemini_api_key else None
rag_service = RAGService(persist_directory=settings.chroma_persist_directory)
google_apis_service = GoogleAPIsService(
    api_key=settings.google_api_key,
    places_api_key=settings.google_places_api_key,
    maps_api_key=settings.google_maps_api_key
) if settings.google_api_key else None


@celery.task(bind=True)
def generate_solutions_task(self, client_id: int, requirements: str, goals: list, priority_focus: str = None):
    """Background task to generate solutions for a client"""
    db = SessionLocal()
    try:
        current_task.update_state(state='PROGRESS', meta={'status': 'Gathering client data...'})
        
        # Get client data
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise Exception(f"Client {client_id} not found")
        
        # Get RAG context
        current_task.update_state(state='PROGRESS', meta={'status': 'Searching knowledge base...'})
        rag_context = rag_service.search_documents(requirements, client_id, k=10)
        
        # Prepare client data for analysis
        client_data = {
            "name": client.name,
            "company": client.company,
            "website": client.website,
            "industry": client.industry,
            "description": client.description,
            "notes": client.notes
        }
        
        # Generate solutions using Gemini
        current_task.update_state(state='PROGRESS', meta={'status': 'Generating solutions with AI...'})
        if not gemini_service:
            raise Exception("Gemini service not configured")
        
        solutions = gemini_service.generate_solutions(
            analysis={"client_data": client_data, "rag_context": rag_context},
            requirements=requirements,
            client_goals=goals
        )
        
        # Save solutions to database
        current_task.update_state(state='PROGRESS', meta={'status': 'Saving solutions...'})
        solution_records = []
        for i, solution_data in enumerate(solutions):
            solution = Solution(
                client_id=client_id,
                title=solution_data.get("title", f"Solution {i+1}"),
                description=solution_data.get("description", ""),
                solution_type=solution_data.get("solution_type", "recommendation"),
                priority=solution_data.get("priority_level", "medium"),
                content=solution_data.get("implementation_steps", ""),
                metadata=solution_data,
                confidence_score=0.8  # Default confidence
            )
            
            db.add(solution)
            solution_records.append(solution)
        
        db.commit()
        
        return {
            "status": "completed", 
            "client_id": client_id,
            "solutions_generated": len(solution_records)
        }
        
    except Exception as e:
        logger.error(f"Error in solution generation task for client {client_id}: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery.task(bind=True)
def comprehensive_analysis_task(self, analysis_id: str, client_id: int, analysis_type: str, 
                              include_google_data: bool, requirements: str = None, goals: list = None):
    """Background task for comprehensive client analysis"""
    db = SessionLocal()
    try:
        current_task.update_state(state='PROGRESS', meta={'status': 'Starting comprehensive analysis...'})
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise Exception(f"Client {client_id} not found")
        
        if not gemini_service:
            raise Exception("Gemini service not configured")
        
        # Get all available data
        current_task.update_state(state='PROGRESS', meta={'status': 'Gathering data sources...'})
        rag_context = rag_service.search_documents(requirements or "comprehensive analysis", client_id, k=20)
        
        scraped_data = db.query(ScrapedData).filter(ScrapedData.client_id == client_id).all()
        website_data = []
        for data in scraped_data:
            if data.metadata:
                website_data.append({
                    "url": data.page_url,
                    "title": data.page_title,
                    "content": data.content,
                    "metadata": data.metadata
                })
        
        # Prepare client data
        client_data = {
            "name": client.name,
            "company": client.company,
            "website": client.website,
            "industry": client.industry,
            "description": client.description,
            "notes": client.notes,
            "address": client.address
        }
        
        # Get Google location data if requested
        google_data = {}
        if include_google_data and client.address and google_apis_service:
            current_task.update_state(state='PROGRESS', meta={'status': 'Analyzing location data...'})
            google_data = google_apis_service.analyze_business_location(client.address)
        
        # Perform comprehensive analysis
        current_task.update_state(state='PROGRESS', meta={'status': 'Running AI analysis...'})
        analysis_results = gemini_service.analyze_client_data(
            client_data=client_data,
            scraped_data=website_data,
            rag_context=rag_context
        )
        
        # Generate additional analyses based on type
        additional_analyses = {}
        
        if analysis_type in ["comprehensive", "marketing"]:
            current_task.update_state(state='PROGRESS', meta={'status': 'Generating marketing strategy...'})
            additional_analyses["marketing_strategy"] = gemini_service.generate_marketing_strategy(
                client_data=client_data,
                analysis=analysis_results
            )
        
        if analysis_type in ["comprehensive", "technical"] and website_data:
            current_task.update_state(state='PROGRESS', meta={'status': 'Generating technical recommendations...'})
            additional_analyses["technical_recommendations"] = gemini_service.generate_technical_recommendations(
                scraped_data=website_data,
                analysis=analysis_results
            )
        
        if analysis_type in ["comprehensive", "content"]:
            current_task.update_state(state='PROGRESS', meta={'status': 'Generating content suggestions...'})
            additional_analyses["content_suggestions"] = gemini_service.generate_content_suggestions(
                client_data=client_data,
                analysis=analysis_results
            )
        
        # Store results (you might want to create a table for this)
        current_task.update_state(state='PROGRESS', meta={'status': 'Saving analysis results...'})
        
        # Here you could save the analysis results to a database table
        # For now, we'll just log them
        logger.info(f"Analysis {analysis_id} completed for client {client_id}")
        logger.info(f"Analysis results: {analysis_results}")
        logger.info(f"Additional analyses: {additional_analyses}")
        logger.info(f"Google data: {google_data}")
        
        return {
            "status": "completed",
            "analysis_id": analysis_id,
            "client_id": client_id,
            "analysis_results": analysis_results,
            "additional_analyses": additional_analyses,
            "google_data": google_data
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis task {analysis_id}: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery.task(bind=True)
def process_analysis_session_task(self, session_id: int, requirements: str, goals: list):
    """Background task to process analysis session"""
    db = SessionLocal()
    try:
        from app.models.solution import AnalysisSession
        
        current_task.update_state(state='PROGRESS', meta={'status': 'Processing analysis session...'})
        
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if not session:
            raise Exception(f"Analysis session {session_id} not found")
        
        client = db.query(Client).filter(Client.id == session.client_id).first()
        if not client:
            raise Exception(f"Client {session.client_id} not found")
        
        # Get RAG context
        current_task.update_state(state='PROGRESS', meta={'status': 'Searching knowledge base...'})
        rag_context = rag_service.search_documents(requirements, session.client_id, k=10)
        
        # Prepare client data
        client_data = {
            "name": client.name,
            "company": client.company,
            "website": client.website,
            "industry": client.industry,
            "description": client.description,
            "notes": client.notes
        }
        
        # Perform analysis
        current_task.update_state(state='PROGRESS', meta={'status': 'Running AI analysis...'})
        if not gemini_service:
            raise Exception("Gemini service not configured")
        
        analysis_results = gemini_service.analyze_client_data(
            client_data=client_data,
            scraped_data=[],  # Could be populated from scraping results
            rag_context=rag_context
        )
        
        # Generate solutions
        current_task.update_state(state='PROGRESS', meta={'status': 'Generating solutions...'})
        solutions = gemini_service.generate_solutions(
            analysis=analysis_results,
            requirements=requirements,
            client_goals=goals
        )
        
        # Update session
        current_task.update_state(state='PROGRESS', meta={'status': 'Saving results...'})
        session.analysis_results = analysis_results
        session.solutions_generated = solutions
        session.status = "completed"
        
        db.commit()
        
        return {
            "status": "completed",
            "session_id": session_id,
            "analysis_results": analysis_results,
            "solutions_generated": len(solutions)
        }
        
    except Exception as e:
        logger.error(f"Error processing analysis session {session_id}: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
