"""TOITURELV Cortex API - Main application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.routers import estimate, health
from backend.app.services.embeddings import load_embedding_model, unload_embedding_model
from backend.app.services.pinecone_cbr import close_pinecone, init_pinecone
from backend.app.services.predictor import load_models, unload_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle.

    Load ML models and CBR services at startup, clean up at shutdown.
    """
    # Startup
    load_models()           # ML prediction models
    load_embedding_model()  # sentence-transformers model
    init_pinecone()         # Pinecone connection
    yield
    # Shutdown
    close_pinecone()
    unload_embedding_model()
    unload_models()


app = FastAPI(
    title="TOITURELV Cortex API",
    description="ML-powered roofing estimate API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware FIRST before any other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(estimate.router)
