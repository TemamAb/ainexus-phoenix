FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x *.py

# Expose port for web service
EXPOSE 8080

# Start the main arbitrage engine
CMD ["python", "main_arbitrage_engine.py"]
