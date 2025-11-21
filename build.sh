#!/bin/bash
echo "Installing Python dependencies..."
pip install -r requirements.txt --target .vercel/python/py3.12/src/_vendor
echo "Build complete!"
