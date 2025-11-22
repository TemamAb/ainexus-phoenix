FROM node:18-alpine AS js-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM python:3.11-alpine AS python-builder  
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-alpine
WORKDIR /app

COPY --from=python-builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=python-builder /usr/local/bin/ /usr/local/bin/
COPY --from=js-builder /app/node_modules ./node_modules
COPY . .

# Create start script using proper method
RUN cat > start.sh << 'EOS'
#!/bin/sh
echo "íº€ Starting AINEXUS 96-Module Platform..."
echo "í° Starting Python Flask API..."
python core/app.py &
echo "í´§ Starting JavaScript Modules..."
node scripts/load-modules.js &
echo "âœ… Both runtimes started - AINEXUS is live!"
wait
EOS

RUN chmod +x start.sh

EXPOSE 8080
CMD ["./start.sh"]
