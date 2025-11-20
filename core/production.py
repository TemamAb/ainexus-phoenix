"""
AINEXUS Production Server Configuration
Chief Architect - Production Deployment Fix
"""
import os
from app import app, socketio

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    # Production server configuration
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=False,
        allow_unsafe_werkzeug=True,  # Required for Render.com deployment
        log_output=True
    )
