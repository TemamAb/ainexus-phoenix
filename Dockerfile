FROM python:3.11-slim

WORKDIR /app

# Install adaptive profit engine dependencies
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    pandas==2.0.3 \
    websockets==12.0 \
    aiohttp==3.9.1

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x *.py

# Expose port
EXPOSE 8080

# Start adaptive profit engine
CMD ["python", "adaptive_profit_engine.py"]
