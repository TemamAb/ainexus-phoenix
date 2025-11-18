#!/bin/bash
echo "Ì∫Ä Starting Ainexus AI Engine..."
echo "================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "‚ùå Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "Ì≥¶ Building and starting services..."
docker-compose up -d --build

echo "‚è≥ Waiting for services to start..."
sleep 15

echo "‚úÖ Services started:"
echo "   Frontend:    http://localhost:3000"
echo "   API:         http://localhost:8080"
echo "   WebSocket:   ws://localhost:8081"
echo "   PostgreSQL:  localhost:5432"
echo "   Redis:       localhost:6379"
echo "   Prometheus:  http://localhost:9090"
echo "   Grafana:     http://localhost:3001 (admin/admin)"

echo ""
echo "Ìø• Checking service health..."
curl -s http://localhost:8080/health | grep -o '"status":"[^"]*"' || echo "API starting..."

echo ""
echo "ÌæØ Ainexus AI Engine is ready!"
echo "   Open http://localhost:3000 to view the dashboard"
