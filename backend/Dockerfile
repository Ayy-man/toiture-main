# TOITURELV Cortex API - Dockerfile for Railway deployment
FROM python:3.11-slim

WORKDIR /app

# Python settings for container environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install CPU-only PyTorch FIRST (avoids CUDA bloat, ~2GB smaller)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/

# Run the FastAPI application
CMD ["sh", "-c", "fastapi run app/main.py --host 0.0.0.0 --port ${PORT:-8000}"]
