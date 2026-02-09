"""TOITURELV Cortex API - Main application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import customers, dashboard, estimate, feedback, health, materials, quotes, submissions
from app.services.embeddings import load_embedding_model, unload_embedding_model
from app.services.llm_reasoning import close_llm_client, init_llm_client
from app.services.pinecone_cbr import close_pinecone, init_pinecone, is_pinecone_available
from app.services.predictor import load_models, unload_models
from app.services.supabase_client import close_supabase, init_supabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle.

    Pre-loads embedding model at startup when Pinecone is configured to avoid
    request timeouts. ML price/material models still use lazy loading.
    """
    # Startup
    load_models()           # No-op: models load on first predict()
    init_pinecone()         # Pinecone connection (lightweight client)
    # Pre-load embedding model if Pinecone is configured (avoids request timeout)
    load_embedding_model(eager=is_pinecone_available())
    init_llm_client()       # OpenRouter LLM client (lightweight)
    init_supabase()         # Supabase connection (lightweight)
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
    allow_origin_regex=r"https://toiture-main.*\.vercel\.app",  # Allow Vercel previews
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS for preflight
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(estimate.router)
app.include_router(feedback.router)
app.include_router(quotes.router)
app.include_router(customers.router)
app.include_router(dashboard.router)
app.include_router(materials.router)
app.include_router(submissions.router)
