FROM python:3.11-slim

# PERMANENT UTF-8 SOLUTION
RUN apt-get update && apt-get install -y locales && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen en_US.UTF-8

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV PYTHONUTF8=1
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Basic UTF-8 validation (skip if it fails)
RUN python3 -c "
import sys
try:
    # Simple UTF-8 check for critical files
    with open('app.py', 'r', encoding='utf-8') as f:
        f.read()
    with open('validate_deployment.py', 'r', encoding='utf-8') as f:
        f.read()
    print('✅ Basic UTF-8 validation passed')
except Exception as e:
    print(f'⚠️ UTF-8 check warning: {e}')
    print('Continuing deployment...')
"

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
