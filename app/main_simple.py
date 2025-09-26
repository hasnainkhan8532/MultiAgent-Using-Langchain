"""
MultiToolAPI - Simple Main FastAPI Application (No Docker/Redis)
Intelligent Client Analysis and Solution Generation System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    yield
    # Shutdown
    pass


app = FastAPI(
    title="MultiToolAPI",
    description="Intelligent Client Analysis and Solution Generation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MultiToolAPI - Intelligent Client Analysis System",
        "version": "1.0.0",
        "docs": "/docs",
        "setup": "Simple mode - No Docker required"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "MultiToolAPI",
        "database": "SQLite",
        "mode": "Simple"
    }


@app.get("/setup-status")
async def setup_status():
    """Check setup status"""
    status = {
        "database_configured": bool(settings.database_url),
        "gemini_configured": bool(settings.gemini_api_key),
        "google_apis_configured": bool(settings.google_api_key),
        "directories": {
            "chroma_db": os.path.exists("./data/chroma_db"),
            "uploads": os.path.exists("./uploads"),
            "sqlite": os.path.exists("./data/sqlite")
        }
    }
    
    return status


if __name__ == "__main__":
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
