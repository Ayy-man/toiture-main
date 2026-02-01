"""TOITURELV Cortex API - Main application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import customers, dashboard, estimate, feedback, health, quotes
from app.services.embeddings import load_embedding_model, unload_embedding_model
from app.services.llm_reasoning import close_llm_client, init_llm_client
from app.services.pinecone_cbr import close_pinecone, init_pinecone
from app.services.predictor import load_models, unload_models
from app.services.supabase_client import close_supabase, init_supabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle.

    ML models use lazy loading (load on first request) to reduce startup memory.
    Only lightweight API clients are initialized at startup.
    """
    # Startup - ML models load lazily on first request to reduce memory
    load_models()           # No-op: models load on first predict()
    load_embedding_model()  # No-op: model loads on first embed()
    init_pinecone()         # Pinecone connection (lightweight client)
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
