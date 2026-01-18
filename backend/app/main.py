"""TOITURELV Cortex API - Main application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import estimate, feedback, health
from app.services.embeddings import load_embedding_model, unload_embedding_model
from app.services.llm_reasoning import close_llm_client, init_llm_client
from app.services.pinecone_cbr import close_pinecone, init_pinecone
from app.services.predictor import load_models, unload_models
from app.services.supabase_client import close_supabase, init_supabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle.

    Load ML models and CBR services at startup, clean up at shutdown.
    """
    # Startup
    load_models()           # ML prediction models
    load_embedding_model()  # sentence-transformers model
    init_pinecone()         # Pinecone connection
    init_llm_client()       # OpenRouter LLM client
    init_supabase()         # Supabase connection (feedback system)
    yield
    # Shutdown
    close_supabase()
    close_llm_client()
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
app.include_router(feedback.router)
