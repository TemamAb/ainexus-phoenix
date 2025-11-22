#!/bin/bash
echo "íº€ Building AINEXUS 96-Module Platform on Render..."

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p data
mkdir -p config

# Set proper permissions
chmod +x core/app.py

echo "âœ… AINEXUS build completed successfully"
