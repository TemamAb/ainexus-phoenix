FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set UTF-8 encoding for Python
ENV PYTHONUTF8=1
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

# Copy requirements FIRST
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --timeout 60 -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Entry point
CMD ["python", "core/app.py"]
