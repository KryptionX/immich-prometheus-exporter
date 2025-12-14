# Multi-stage build for Immich Prometheus Exporter
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy exporter script
COPY exporter.py .

# Make script executable
RUN chmod +x exporter.py

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose metrics port
EXPOSE 9700

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9700').read()" || exit 1

# Run exporter
CMD ["python3", "-u", "exporter.py"]

