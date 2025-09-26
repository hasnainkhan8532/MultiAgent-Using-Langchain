"""
Analysis endpoints for comprehensive client analysis
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.client import Client
from app.models.scraping import ScrapedData
from app.services.gemini_service import GeminiService
from app.services.rag_service import RAGService
from app.services.google_apis_service import GoogleAPIsService
from app.core.config import settings

router = APIRouter()

# Initialize services
gemini_service = GeminiService(settings.gemini_api_key) if settings.gemini_api_key else None
rag_service = RAGService(persist_directory=settings.chroma_persist_directory)
google_apis_service = GoogleAPIsService(
    api_key=settings.google_api_key,
    places_api_key=settings.google_places_api_key,
    maps_api_key=settings.google_maps_api_key
) if settings.google_api_key else None


class ComprehensiveAnalysisRequest(BaseModel):
    client_id: int
    analysis_type: str = "comprehensive"  # comprehensive, marketing, technical, content
    include_google_data: bool = True
    requirements: Optional[str] = None
    goals: Optional[List[str]] = None


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


@router.post("/comprehensive", response_model=AnalysisResponse)
async def start_comprehensive_analysis(
    analysis_request: ComprehensiveAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start comprehensive client analysis"""
    try:
        if not gemini_service:
            raise HTTPException(status_code=400, detail="Gemini service not configured")
        
        # Check if client exists
        client = db.query(Client).filter(Client.id == analysis_request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate analysis ID
        import uuid
        analysis_id = str(uuid.uuid4())
        
        # Start background analysis
        background_tasks.add_task(
            process_comprehensive_analysis,
            analysis_id,
            analysis_request.client_id,
            analysis_request.analysis_type,
            analysis_request.include_google_data,
            analysis_request.requirements,
            analysis_request.goals
        )
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="started",
            message="Comprehensive analysis started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketing/{client_id}", response_model=dict)
async def get_marketing_analysis(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get marketing strategy analysis for a client"""
    try:
        if not gemini_service:
            raise HTTPException(status_code=400, detail="Gemini service not configured")
        
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get RAG context
        rag_context = rag_service.search_documents("marketing strategy", client_id, k=10)
        
        # Prepare client data
        client_data = {
            "name": client.name,
            "company": client.company,
            "website": client.website,
            "industry": client.industry,
            "description": client.description,
            "notes": client.notes
        }
        
        # Get scraped website data
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
        
        # Generate marketing strategy
        marketing_strategy = gemini_service.generate_marketing_strategy(
            client_data=client_data,
            analysis={"rag_context": rag_context, "website_data": website_data}
        )
        
        return marketing_strategy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/technical/{client_id}", response_model=dict)
async def get_technical_analysis(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get technical analysis for a client's website"""
    try:
        if not gemini_service:
            raise HTTPException(status_code=400, detail="Gemini service not configured")
        
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get scraped website data
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
        
        # Get RAG context
        rag_context = rag_service.search_documents("technical analysis", client_id, k=10)
        
        # Generate technical recommendations
        technical_recommendations = gemini_service.generate_technical_recommendations(
            scraped_data=website_data,
            analysis={"rag_context": rag_context}
        )
        
        return technical_recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/{client_id}", response_model=List[dict])
async def get_content_suggestions(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get content suggestions for a client"""
    try:
        if not gemini_service:
            raise HTTPException(status_code=400, detail="Gemini service not configured")
        
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get RAG context
        rag_context = rag_service.search_documents("content marketing", client_id, k=10)
        
        # Prepare client data
        client_data = {
            "name": client.name,
            "company": client.company,
            "website": client.website,
            "industry": client.industry,
            "description": client.description,
            "notes": client.notes
        }
        
        # Generate content suggestions
        content_suggestions = gemini_service.generate_content_suggestions(
            client_data=client_data,
            analysis={"rag_context": rag_context}
        )
        
        return content_suggestions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location/{client_id}", response_model=dict)
async def get_location_analysis(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get location analysis for a client using Google APIs"""
    try:
        if not google_apis_service:
            raise HTTPException(status_code=400, detail="Google APIs service not configured")
        
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        if not client.address:
            raise HTTPException(status_code=400, detail="Client address not provided")
        
        # Analyze business location
        location_analysis = google_apis_service.analyze_business_location(client.address)
        
        return location_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{client_id}", response_model=dict)
async def get_analysis_summary(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get a summary of all analyses for a client"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get basic client info
        client_info = {
            "id": client.id,
            "name": client.name,
            "company": client.company,
            "website": client.website,
            "industry": client.industry,
            "description": client.description
        }
        
        # Get data counts
        scraped_data_count = db.query(ScrapedData).filter(ScrapedData.client_id == client_id).count()
        rag_documents = rag_service.get_client_documents(client_id)
        
        # Get recent analyses (if stored)
        summary = {
            "client": client_info,
            "data_summary": {
                "scraped_pages": scraped_data_count,
                "rag_documents": len(rag_documents),
                "knowledge_sources": list(set([doc.get("source_type", "unknown") for doc in rag_documents]))
            },
            "available_analyses": {
                "marketing": True,
                "technical": scraped_data_count > 0,
                "content": True,
                "location": bool(client.address and google_apis_service)
            }
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_comprehensive_analysis(
    analysis_id: str,
    client_id: int,
    analysis_type: str,
    include_google_data: bool,
    requirements: Optional[str],
    goals: Optional[List[str]]
):
    """Background task to process comprehensive analysis"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return
        
        # Get all available data
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
            google_data = google_apis_service.analyze_business_location(client.address)
        
        # Perform comprehensive analysis
        analysis_results = gemini_service.analyze_client_data(
            client_data=client_data,
            scraped_data=website_data,
            rag_context=rag_context
        )
        
        # Generate additional analyses based on type
        additional_analyses = {}
        
        if analysis_type in ["comprehensive", "marketing"]:
            additional_analyses["marketing_strategy"] = gemini_service.generate_marketing_strategy(
                client_data=client_data,
                analysis=analysis_results
            )
        
        if analysis_type in ["comprehensive", "technical"] and website_data:
            additional_analyses["technical_recommendations"] = gemini_service.generate_technical_recommendations(
                scraped_data=website_data,
                analysis=analysis_results
            )
        
        if analysis_type in ["comprehensive", "content"]:
            additional_analyses["content_suggestions"] = gemini_service.generate_content_suggestions(
                client_data=client_data,
                analysis=analysis_results
            )
        
        # Store results (you might want to create a table for this)
        print(f"Analysis {analysis_id} completed for client {client_id}")
        print(f"Results: {analysis_results}")
        print(f"Additional analyses: {additional_analyses}")
        print(f"Google data: {google_data}")
        
    except Exception as e:
        print(f"Error processing comprehensive analysis {analysis_id}: {str(e)}")
    finally:
        db.close()
