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

# Install system dependencies including chardet for encoding detection
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install chardet

# Copy application files
COPY . .

# Validate UTF-8 before starting application
RUN python3 validate_deployment.py

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
