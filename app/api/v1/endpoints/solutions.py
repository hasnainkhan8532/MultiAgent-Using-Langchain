"""
Solution generation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.client import Client
from app.models.solution import Solution, SolutionFeedback, AnalysisSession
from app.services.gemini_service import GeminiService
from app.services.rag_service import RAGService
from app.core.config import settings

router = APIRouter()

# Initialize services
gemini_service = GeminiService(settings.gemini_api_key) if settings.gemini_api_key else None
rag_service = RAGService(persist_directory=settings.chroma_persist_directory)


class SolutionGenerationRequest(BaseModel):
    client_id: int
    requirements: str
    goals: List[str]
    priority_focus: Optional[str] = None


class SolutionFeedbackRequest(BaseModel):
    solution_id: int
    rating: Optional[int] = None
    feedback: Optional[str] = None
    is_helpful: Optional[bool] = None


class AnalysisSessionRequest(BaseModel):
    client_id: int
    session_name: str
    input_data: dict
    requirements: str
    goals: List[str]


@router.post("/generate", response_model=dict)
async def generate_solutions(
    solution_request: SolutionGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate solutions for a client"""
    try:
        if not gemini_service:
            raise HTTPException(status_code=400, detail="Gemini service not configured")
        
        # Check if client exists
        client = db.query(Client).filter(Client.id == solution_request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Start background solution generation
        background_tasks.add_task(
            process_solution_generation,
            solution_request.client_id,
            solution_request.requirements,
            solution_request.goals,
            solution_request.priority_focus
        )
        
        return {
            "message": "Solution generation started",
            "client_id": solution_request.client_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}", response_model=List[dict])
async def get_client_solutions(
    client_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get solutions for a client"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Build query
        query = db.query(Solution).filter(Solution.client_id == client_id)
        
        if status:
            query = query.filter(Solution.status == status)
        
        solutions = query.all()
        
        return [
            {
                "id": solution.id,
                "title": solution.title,
                "description": solution.description,
                "solution_type": solution.solution_type,
                "priority": solution.priority,
                "status": solution.status,
                "confidence_score": solution.confidence_score,
                "created_at": solution.created_at,
                "updated_at": solution.updated_at
            }
            for solution in solutions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/{solution_id}", response_model=dict)
async def get_solution(
    client_id: int,
    solution_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific solution"""
    try:
        solution = db.query(Solution).filter(
            Solution.id == solution_id,
            Solution.client_id == client_id
        ).first()
        
        if not solution:
            raise HTTPException(status_code=404, detail="Solution not found")
        
        # Get feedback for this solution
        feedback = db.query(SolutionFeedback).filter(
            SolutionFeedback.solution_id == solution_id
        ).all()
        
        return {
            "id": solution.id,
            "title": solution.title,
            "description": solution.description,
            "solution_type": solution.solution_type,
            "priority": solution.priority,
            "status": solution.status,
            "content": solution.content,
            "metadata": solution.metadata,
            "confidence_score": solution.confidence_score,
            "created_at": solution.created_at,
            "updated_at": solution.updated_at,
            "feedback": [
                {
                    "id": fb.id,
                    "rating": fb.rating,
                    "feedback": fb.feedback,
                    "is_helpful": fb.is_helpful,
                    "created_at": fb.created_at
                }
                for fb in feedback
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback", response_model=dict)
async def submit_feedback(
    feedback_request: SolutionFeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit feedback for a solution"""
    try:
        # Check if solution exists
        solution = db.query(Solution).filter(Solution.id == feedback_request.solution_id).first()
        if not solution:
            raise HTTPException(status_code=404, detail="Solution not found")
        
        # Create feedback record
        feedback = SolutionFeedback(
            solution_id=feedback_request.solution_id,
            rating=feedback_request.rating,
            feedback=feedback_request.feedback,
            is_helpful=feedback_request.is_helpful
        )
        
        db.add(feedback)
        db.commit()
        
        return {"message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions", response_model=dict)
async def create_analysis_session(
    session_request: AnalysisSessionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new analysis session"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == session_request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create analysis session
        session = AnalysisSession(
            client_id=session_request.client_id,
            session_name=session_request.session_name,
            input_data=session_request.input_data,
            analysis_results={},
            solutions_generated=[],
            status="active"
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Start background analysis
        background_tasks.add_task(
            process_analysis_session,
            session.id,
            session_request.requirements,
            session_request.goals
        )
        
        return {
            "message": "Analysis session created successfully",
            "session_id": session.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{client_id}", response_model=List[dict])
async def get_analysis_sessions(
    client_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get analysis sessions for a client"""
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Build query
        query = db.query(AnalysisSession).filter(AnalysisSession.client_id == client_id)
        
        if status:
            query = query.filter(AnalysisSession.status == status)
        
        sessions = query.all()
        
        return [
            {
                "id": session.id,
                "session_name": session.session_name,
                "status": session.status,
                "created_at": session.created_at,
                "updated_at": session.updated_at
            }
            for session in sessions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_solution_generation(
    client_id: int,
    requirements: str,
    goals: List[str],
    priority_focus: Optional[str]
):
    """Background task to generate solutions"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get client data
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return
        
        # Get RAG context
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
        solutions = gemini_service.generate_solutions(
            analysis={"client_data": client_data, "rag_context": rag_context},
            requirements=requirements,
            client_goals=goals
        )
        
        # Save solutions to database
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
        
        db.commit()
        
    except Exception as e:
        print(f"Error generating solutions for client {client_id}: {str(e)}")
    finally:
        db.close()


async def process_analysis_session(
    session_id: int,
    requirements: str,
    goals: List[str]
):
    """Background task to process analysis session"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if not session:
            return
        
        client = db.query(Client).filter(Client.id == session.client_id).first()
        if not client:
            return
        
        # Get RAG context
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
        analysis_results = gemini_service.analyze_client_data(
            client_data=client_data,
            scraped_data=[],  # Could be populated from scraping results
            rag_context=rag_context
        )
        
        # Generate solutions
        solutions = gemini_service.generate_solutions(
            analysis=analysis_results,
            requirements=requirements,
            client_goals=goals
        )
        
        # Update session
        session.analysis_results = analysis_results
        session.solutions_generated = solutions
        session.status = "completed"
        
        db.commit()
        
    except Exception as e:
        print(f"Error processing analysis session {session_id}: {str(e)}")
    finally:
        db.close()
