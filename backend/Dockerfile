# Multi-stage build for Django backend
FROM python:3.12.7-alpine as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# Create virtual environment
RUN rm -rf /opt/venv && python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12.7-alpine as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN addgroup -g 1001 -S django && \
    adduser -S django -u 1001 -G django

# Install runtime dependencies
RUN apk add --no-cache \
    postgresql-libs \
    curl \
    libpq

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=django:django . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R django:django /app

# Copy startup script
COPY --chown=django:django start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Run startup script
CMD ["sh", "/app/start.sh"] 