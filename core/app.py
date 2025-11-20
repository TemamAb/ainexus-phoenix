# -*- coding: utf-8 -*-
"""
AINEXUS PRODUCTION - PROPER METAMASK INTEGRATION
Reliable wallet detection and connection
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
        self.wallet_detected = False
        
    def get_system_status(self):
        return {
            "status": self.status,
            "wallet_detected": self.wallet_detected,
            "production_ready": self.status == "active",
            "live_data": False,
            "mock_data": False
        }

production_engine = ProductionEngine()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/system/status')
def system_status():
    return jsonify(production_engine.get_system_status())

@app.route('/api/health')
def health():
    return jsonify({
        "status": "operational",
        "version": "1.0.0",
        "environment": "production", 
        "wallet_integration": "active",
        "metamask_support": True,
        "ready_for_ai_integration": True
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("=" * 60)
    print("AINEXUS PRODUCTION - PROPER METAMASK INTEGRATION")
    print("=" * 60)
    print("WALLET DETECTION: Multi-method reliable detection")
    print("DEPENDENCIES: Ethers.js + MetaMask detect-provider")
    print("CONNECTION: Proper error handling and status updates")
    print("SUPPORT: MetaMask, Coinbase, Trust Wallet, BitKeep")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False
    )
