#!/bin/bash
cd core
echo "íº€ Starting AINexus Production Server..."
exec gunicorn --bind 0.0.0.0:$PORT --worker-class eventlet --workers 1 app_production:app
