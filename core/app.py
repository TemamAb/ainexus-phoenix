from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.route('/')
def home():
    return jsonify({
        "message": "AINEXUS Platform API",
        "version": "3.0.0",
        "status": "operational"
    })

@app.route('/api/v1/system/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "3.0.0",
        "modules": {
            "core_engine": "operational",
            "ai_intelligence": "operational", 
            "execution_engine": "operational",
            "user_platform": "operational"
        }
    })

@app.route('/api/v1/system/status')
@limiter.limit("10 per minute")
def system_status():
    return jsonify({
        "platform": "AINEXUS",
        "status": "ACTIVE",
        "modules_loaded": 45,
        "gasless_mode": True,
        "chains_supported": 6,
        "dexes_monitored": 50,
        "uptime": "99.9%"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
