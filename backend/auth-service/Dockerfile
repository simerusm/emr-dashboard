# Use Python 3.10 slim as base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    FLASK_ENV=production

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system app && adduser --system --group app

# Create necessary directories with correct permissions
RUN mkdir -p /app/logs /app/dbs \
    && chown -R app:app /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application code (using .dockerignore to exclude unnecessary files)
COPY . .

# Set version information
RUN echo "$(date +%Y%m%d)-$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" > version.txt

# Set proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Create volume for logs and database
VOLUME ["/app/logs", "/app/dbs"]

# Expose port
EXPOSE 5001

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "src.app:app"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1