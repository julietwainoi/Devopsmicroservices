# Stage 1 — Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies to /install prefix
RUN pip install --no-cache-dir --prefix=/install flask prometheus-flask-exporter

# Stage 2 — Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app.py .

# Create non-root user
RUN adduser --disabled-password --no-create-home appuser

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run the app (exec form for proper signal handling)
CMD ["python", "app.py"]
 