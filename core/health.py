from flask import jsonify
import os
from datetime import datetime

def health_check():
    """Minimal health check for faster deployment verification"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.2.0',
        'service': 'AI-NEXUS Core'
    })
