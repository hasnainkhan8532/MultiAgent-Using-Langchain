"""
Main API router for v1
"""

from fastapi import APIRouter
from app.api.v1.endpoints import clients, scraping, rag, solutions, analysis

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(scraping.router, prefix="/scraping", tags=["scraping"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(solutions.router, prefix="/solutions", tags=["solutions"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
