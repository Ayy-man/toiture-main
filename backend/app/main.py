"""TOITURELV Cortex API - Main application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.services.predictor import load_models, unload_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle.

    Load ML models at startup, clean up at shutdown.
    """
    load_models()
    yield
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
