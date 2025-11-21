# AINEXUS PHASE 1 DOCKER BUILD
FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    curl

# Create non-root user
RUN addgroup -g 1001 -S ainexus && \
    adduser -S ainexus -u 1001

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R ainexus:ainexus /app

# Switch to non-root user
USER ainexus

# Expose application port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node scripts/docker-healthcheck.js

# Start Ainexus Phase 1
CMD ["node", "scripts/start-phase1.js"]
