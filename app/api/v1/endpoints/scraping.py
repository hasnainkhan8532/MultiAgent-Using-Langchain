"""
Web scraping endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.scraping import ScrapingJob, ScrapedData
from app.models.client import Client
from app.services.web_scraper import WebScraper
from app.services.rag_service import RAGService
from app.core.config import settings

router = APIRouter()

# Initialize services
web_scraper = WebScraper()
rag_service = RAGService(persist_directory=settings.chroma_persist_directory)


class ScrapingRequest(BaseModel):
    client_id: int
    url: str
    scraping_type: str = "general"
    strategy: str = "auto"
    config: Optional[dict] = None


class ScrapingResponse(BaseModel):
    job_id: int
    status: str
    message: str


@router.post("/start", response_model=ScrapingResponse)
async def start_scraping(
    scraping_request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a web scraping job"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == scraping_request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create scraping job
        scraping_job = ScrapingJob(
            client_id=scraping_request.client_id,
            url=scraping_request.url,
            scraping_type=scraping_request.scraping_type,
            config=scraping_request.config or {}
        )
        
        db.add(scraping_job)
        db.commit()
        db.refresh(scraping_job)
        
        # Start background scraping task
        background_tasks.add_task(
            process_scraping_job,
            scraping_job.id,
            scraping_request.url,
            scraping_request.strategy,
            scraping_request.config or {}
        )
        
        return ScrapingResponse(
            job_id=scraping_job.id,
            status="started",
            message="Scraping job started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{client_id}", response_model=List[dict])
async def get_scraping_jobs(client_id: int, db: Session = Depends(get_db)):
    """Get all scraping jobs for a client"""
    try:
        jobs = db.query(ScrapingJob).filter(ScrapingJob.client_id == client_id).all()
        
        return [
            {
                "id": job.id,
                "url": job.url,
                "status": job.status,
                "scraping_type": job.scraping_type,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "error_message": job.error_message
            }
            for job in jobs
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{client_id}/{job_id}", response_model=dict)
async def get_scraping_job(client_id: int, job_id: int, db: Session = Depends(get_db)):
    """Get a specific scraping job"""
    try:
        job = db.query(ScrapingJob).filter(
            ScrapingJob.id == job_id,
            ScrapingJob.client_id == client_id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Scraping job not found")
        
        # Get scraped data
        scraped_data = db.query(ScrapedData).filter(ScrapedData.job_id == job_id).all()
        
        return {
            "job": {
                "id": job.id,
                "url": job.url,
                "status": job.status,
                "scraping_type": job.scraping_type,
                "config": job.config,
                "result": job.result,
                "error_message": job.error_message,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "created_at": job.created_at
            },
            "scraped_data": [
                {
                    "id": data.id,
                    "page_url": data.page_url,
                    "page_title": data.page_title,
                    "content_type": data.content_type,
                    "is_processed": data.is_processed,
                    "created_at": data.created_at
                }
                for data in scraped_data
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/{client_id}", response_model=List[dict])
async def get_scraped_data(client_id: int, db: Session = Depends(get_db)):
    """Get all scraped data for a client"""
    try:
        scraped_data = db.query(ScrapedData).filter(ScrapedData.client_id == client_id).all()
        
        return [
            {
                "id": data.id,
                "job_id": data.job_id,
                "page_url": data.page_url,
                "page_title": data.page_title,
                "content_type": data.content_type,
                "is_processed": data.is_processed,
                "created_at": data.created_at
            }
            for data in scraped_data
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reprocess/{job_id}", response_model=dict)
async def reprocess_scraped_data(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reprocess scraped data for RAG system"""
    try:
        job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Scraping job not found")
        
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        # Start background reprocessing task
        background_tasks.add_task(reprocess_job_data, job_id)
        
        return {"message": "Reprocessing started successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_scraping_job(job_id: int, url: str, strategy: str, config: dict):
    """Background task to process scraping job"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Update job status
        job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
        if not job:
            return
        
        job.status = "running"
        job.started_at = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first().created_at
        db.commit()
        
        # Perform scraping
        scraped_data = await web_scraper.scrape_website(url, strategy)
        
        if "error" in scraped_data:
            job.status = "failed"
            job.error_message = scraped_data["error"]
            db.commit()
            return
        
        # Save scraped data
        scraped_record = ScrapedData(
            job_id=job_id,
            client_id=job.client_id,
            page_url=url,
            page_title=scraped_data.get("title", ""),
            content_type="html",
            content=scraped_data.get("raw_html", ""),
            metadata=scraped_data
        )
        
        db.add(scraped_record)
        db.commit()
        
        # Add to RAG system
        documents = [{
            'content': scraped_data.get("text_content", ""),
            'title': scraped_data.get("title", url),
            'source_id': scraped_record.id,
            'source_type': 'scraped'
        }]
        
        rag_service.add_documents(documents, job.client_id)
        
        # Mark as processed
        scraped_record.is_processed = True
        job.status = "completed"
        job.completed_at = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first().created_at
        job.result = scraped_data
        
        db.commit()
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
    finally:
        db.close()


async def reprocess_job_data(job_id: int):
    """Background task to reprocess scraped data"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
        if not job:
            return
        
        # Get all scraped data for this job
        scraped_data = db.query(ScrapedData).filter(ScrapedData.job_id == job_id).all()
        
        # Process each scraped page
        for data in scraped_data:
            if not data.is_processed:
                # Add to RAG system
                documents = [{
                    'content': data.content,
                    'title': data.page_title or data.page_url,
                    'source_id': data.id,
                    'source_type': 'scraped'
                }]
                
                rag_service.add_documents(documents, job.client_id)
                
                # Mark as processed
                data.is_processed = True
                db.commit()
        
    except Exception as e:
        print(f"Error reprocessing job {job_id}: {str(e)}")
    finally:
        db.close()
