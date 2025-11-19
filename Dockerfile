# Nextcloud Log Analyzer - Docker Image
# Simple single-container deployment with FastAPI + Alpine.js

FROM python:3.11-slim

LABEL maintainer="xXRoxXeRXx"
LABEL description="Nextcloud Log Analyzer Web Application"

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for log parsing)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    python-multipart==0.0.6 \
    aiofiles==23.2.1 \
    pydantic==2.5.3

# Copy application code
COPY shared/ /app/shared/
COPY backend/ /app/backend/

# Create directories for uploads and results
RUN mkdir -p /app/uploads /app/results

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
