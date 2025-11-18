#!/usr/bin/env python3
import os
import sys

print("Ì¥ç DEPLOYMENT DIAGNOSTICS")
print("=" * 50)

# Check Python path
print(f"Python path: {sys.path}")

# Check current directory
print(f"Current directory: {os.getcwd()}")

# List files
print("\nÌ≥Å Root directory files:")
for item in os.listdir('.'):
    if item.endswith('.py') or item in ['requirements.txt', 'render.yaml']:
        print(f"  - {item}")

# Check for Flask
try:
    from flask import Flask
    print("‚úÖ Flask is available")
except ImportError as e:
    print(f"‚ùå Flask import error: {e}")

# Check app.py import
try:
    from app import app
    print("‚úÖ app.py import successful")
except ImportError as e:
    print(f"‚ùå app.py import failed: {e}")

print("=" * 50)
print("Ì∫Ä DIAGNOSTICS COMPLETE")
