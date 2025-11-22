#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask, jsonify

app = Flask(__name__)

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

# DASHBOARD ROUTES - SERVING ACTUAL HTML FILES
@app.route("/dashboard")
def production_dashboard():
    try:
        with open("./core/templates/dashboard.html", "r") as f:
            return f.read()
    except:
        return "<h1>PRODUCTION DASHBOARD</h1><p>AINEXUS 96-Module Platform</p>"

@app.route("/trading")
def trading_dashboard():
    try:
        with open("./monitoring_dashboard.html", "r") as f:
            return f.read()
    except:
        return "<h1>TRADING DASHBOARD</h1><p>Quantum Arbitrage Engine</p>"

@app.route("/profit")
def profit_dashboard():
    try:
        with open("./profit_dashboard.html", "r") as f:
            return f.read()
    except:
        return "<h1>PROFIT DASHBOARD</h1><p>Revenue Optimization</p>"

@app.route("/activation")
def activation_dashboard():
    try:
        with open("./src/templates/activation_dashboard.html", "r") as f:
            return f.read()
    except:
        return "<h1>ACTIVATION DASHBOARD</h1><p>Two-Click System</p>"

@app.route("/unified")
def unified_dashboard():
    try:
        with open("./frontend-html/unified-dashboard.html", "r") as f:
            return f.read()
    except:
        return "<h1>UNIFIED DASHBOARD</h1><p>Complete Interface</p>"

@app.route("/grafana")
def grafana_dashboard():
    try:
        with open("./grafana_dashboard.html", "r") as f:
            return f.read()
    except:
        return "<h1>GRAFANA DASHBOARD</h1><p>Analytics</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
