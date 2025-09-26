"""
Celery tasks for web scraping
"""

from celery import current_task
from app.core.celery import celery
from app.services.web_scraper import WebScraper
from app.services.rag_service import RAGService
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.scraping import ScrapingJob, ScrapedData
import logging

logger = logging.getLogger(__name__)

# Initialize services
web_scraper = WebScraper()
rag_service = RAGService(persist_directory=settings.chroma_persist_directory)


@celery.task(bind=True)
def scrape_website_task(self, job_id: int, url: str, strategy: str = "auto", config: dict = None):
    """Background task to scrape a website"""
    db = SessionLocal()
    try:
        # Update task status
        current_task.update_state(state='PROGRESS', meta={'status': 'Starting scraping...'})
        
        # Get job from database
        job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
        if not job:
            raise Exception(f"Scraping job {job_id} not found")
        
        # Update job status
        job.status = "running"
        db.commit()
        
        # Perform scraping
        current_task.update_state(state='PROGRESS', meta={'status': 'Scraping website...'})
        scraped_data = web_scraper.scrape_website(url, strategy)
        
        if "error" in scraped_data:
            job.status = "failed"
            job.error_message = scraped_data["error"]
            db.commit()
            return {"status": "failed", "error": scraped_data["error"]}
        
        # Save scraped data
        current_task.update_state(state='PROGRESS', meta={'status': 'Saving scraped data...'})
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
        current_task.update_state(state='PROGRESS', meta={'status': 'Adding to knowledge base...'})
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
        job.result = scraped_data
        
        db.commit()
        
        return {"status": "completed", "job_id": job_id}
        
    except Exception as e:
        logger.error(f"Error in scraping task {job_id}: {str(e)}")
        if 'job' in locals():
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery.task(bind=True)
def reprocess_scraped_data_task(self, job_id: int):
    """Background task to reprocess scraped data for RAG"""
    db = SessionLocal()
    try:
        current_task.update_state(state='PROGRESS', meta={'status': 'Reprocessing data...'})
        
        job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
        if not job:
            raise Exception(f"Scraping job {job_id} not found")
        
        # Get all scraped data for this job
        scraped_data = db.query(ScrapedData).filter(ScrapedData.job_id == job_id).all()
        
        # Process each scraped page
        for i, data in enumerate(scraped_data):
            if not data.is_processed:
                current_task.update_state(
                    state='PROGRESS', 
                    meta={'status': f'Processing page {i+1}/{len(scraped_data)}...'}
                )
                
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
        
        return {"status": "completed", "job_id": job_id}
        
    except Exception as e:
        logger.error(f"Error in reprocessing task {job_id}: {str(e)}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
