#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, jsonify, render_template

# Configure Flask with correct template and static folders
app = Flask(__name__, 
    template_folder='../src/templates',
    static_folder='../static'
)

@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "AINEXUS v3.0.0 - 96 Module Quantum AI Platform",
        "version": "3.0.0",
        "modules": 96,
        "environment": "Docker",
        "two_click_mode": "ACTIVE"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "platform": "AINEXUS"})

# DASHBOARD ROUTES - USING render_template WITH CORRECT PATHS
@app.route("/activation")
def activation_dashboard():
    return render_template('activation_dashboard.html')

@app.route("/dashboard")
def production_dashboard():
    try:
        with open("./core/templates/dashboard.html", "r") as f:
            return f.read()
    except:
        return "<h1>PRODUCTION DASHBOARD</h1><p>AINEXUS Platform</p>"

@app.route("/trading")
def trading_dashboard():
    try:
        with open("./monitoring_dashboard.html", "r") as f:
            return f.read()
    except:
        return "<h1>TRADING DASHBOARD</h1><p>Quantum Arbitrage</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
