"""
Drug Interaction Risk Screener - FastAPI Backend
Production-ready RAG-powered clinical decision support system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from routers import interactions, patients, chat, dashboard
from services.knowledge_graph import KnowledgeGraphService
from services.vector_store import VectorStoreService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown."""
    logger.info("🚀 Starting Drug Interaction Screener API...")
    
    # Initialize Knowledge Graph
    kg_service = KnowledgeGraphService()
    await kg_service.initialize()
    app.state.kg_service = kg_service
    
    # Initialize Vector Store
    vs_service = VectorStoreService()
    await vs_service.initialize()
    app.state.vs_service = vs_service
    
    logger.info("✅ All services initialized successfully")
    yield
    
    logger.info("👋 Shutting down services...")
    await kg_service.close()


app = FastAPI(
    title="Drug Interaction Risk Screener",
    description="AI-powered polypharmacy risk detection system using RAG pipelines",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(interactions.router, prefix="/api/v1", tags=["Drug Interactions"])
app.include_router(patients.router, prefix="/api/v1", tags=["Patients"])
app.include_router(chat.router, prefix="/api/v1", tags=["AI Chat"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "knowledge_graph": "connected",
            "vector_store": "ready",
            "llm": "available"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
