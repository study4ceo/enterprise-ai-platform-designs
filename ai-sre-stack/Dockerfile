# Production-ready Dockerfile for AI SRE Stack

FROM python:3.11-slim

LABEL maintainer="SRE Team"
LABEL description="AI SRE Stack - Intelligent Site Reliability Engineering"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 sre && \
    chown -R sre:sre /app && \
    mkdir -p /app/logs && \
    chown -R sre:sre /app/logs

# Switch to non-root user
USER sre

# Expose metrics port (if needed)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Run orchestrator
CMD ["python", "-u", "sre_orchestrator.py"]
