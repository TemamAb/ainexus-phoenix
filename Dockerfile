FROM node:18-alpine AS js-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM python:3.11-alpine AS python-builder  
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-alpine
WORKDIR /app

# Copy Python dependencies
COPY --from=python-builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=python-builder /usr/local/bin/ /usr/local/bin/

# Copy Node.js dependencies
COPY --from=js-builder /app/node_modules ./node_modules

# Copy application code
COPY . .

# Create unified start script
RUN echo '#!/bin/sh\n\
echo "íº€ Starting AINEXUS 96-Module Platform..."\n\
echo "í° Starting Python Flask API..."\n\
python core/app.py &\n\
echo "ï¿½ï¿½ Starting JavaScript Modules..."\n\
node scripts/load-modules.js &\n\
echo "âœ… Both runtimes started - AINEXUS is live!"\n\
wait\n' > start.sh && chmod +x start.sh

EXPOSE 8080
CMD ["./start.sh"]
