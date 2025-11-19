FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 30 -r requirements.txt

# Copy app
COPY . .

# Performance env vars
ENV PYTHONUTF8=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=3s --retries=2 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "core/app.py"]
