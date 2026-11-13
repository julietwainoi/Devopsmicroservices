# Builder stage - install dependencies
FROM python:3.11-slim AS builder

WORKDIR /install

# Install packages to a custom location
RUN pip install --no-cache-dir --prefix=/install \
    flask \
    requests \
    prometheus-flask-exporter

# Runtime stage - minimal final image
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app.py .

# Run as non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Use exec form for proper signal handling
CMD ["python", "app.py"]
