"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Return health status.

    Simple endpoint for load balancer and monitoring checks.
    """
    return {"status": "ok", "version": "1.0.0"}
