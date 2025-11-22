#!/bin/bash
<<<<<<< HEAD
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
=======
echo "Installing Python dependencies..."
pip install -r requirements.txt --target .vercel/python/py3.12/src/_vendor
echo "Build complete!"
>>>>>>> e14d347ed7e3a3289a0fd77e0038360221240f17
