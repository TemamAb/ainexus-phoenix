# -*- coding: utf-8 -*-
"""
AINEXUS PRODUCTION - DIRECT METAMASK CONNECTION
Simple, reliable MetaMask integration
"""
import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'ainexus-production-2024')
CORS(app)

class ProductionEngine:
    def __init__(self):
        self.status = "awaiting_wallet"
        
    def get_system_status(self):
        return {
            "status": self.status,
            "production_ready": self.status == "active",
            "direct_metamask": True,
            "simple_connection": True
        }

production_engine = ProductionEngine()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/system/status')
def system_status():
    return jsonify(production_engine.get_system_status())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("=" * 60)
    print("AINEXUS - DIRECT METAMASK CONNECTION")
    print("=" * 60)
    print("CONNECTION: Direct to MetaMask extension")
    print("METHOD: window.ethereum.request()")
    print("SIMPLE: No external dependencies")
    print("RELIABLE: Direct Chrome extension API")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False
    )
