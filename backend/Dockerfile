# ==============================================
# Base Stage - Common setup for all stages
# ==============================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# ==============================================
# Development Stage
# ==============================================
FROM base as development

# Copy requirements and install dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p staticfiles mediafiles logs && \
    chown -R appuser:appuser staticfiles mediafiles logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Copy and set entrypoint
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command for development (can be overridden)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==============================================
# Production Stage
# ==============================================
FROM base as production

# Copy requirements and install dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p staticfiles mediafiles logs && \
    chown -R appuser:appuser staticfiles mediafiles logs

# Collect static files (run during build for production)
RUN python manage.py collectstatic --noinput || true

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Copy and set entrypoint
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command for production - Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "desideliver_backend.wsgi:application"]
