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

# DASHBOARD ROUTES WITH EXACT FILE PATHS
@app.route("/activation")
def activation_dashboard():
    try:
        with open("./src/templates/activation_dashboard.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>ACTIVATION DASHBOARD</h1><p>Error: {e}</p>"

@app.route("/dashboard")
def production_dashboard():
    try:
        with open("./core/templates/dashboard.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>PRODUCTION DASHBOARD</h1><p>Error: {e}</p>"

@app.route("/trading")
def trading_dashboard():
    try:
        with open("./monitoring_dashboard.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>TRADING DASHBOARD</h1><p>Error: {e}</p>"

@app.route("/profit")
def profit_dashboard():
    try:
        with open("./profit_dashboard.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>PROFIT DASHBOARD</h1><p>Error: {e}</p>"

@app.route("/unified")
def unified_dashboard():
    try:
        with open("./frontend-html/unified-dashboard.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>UNIFIED DASHBOARD</h1><p>Error: {e}</p>"

@app.route("/grafana")
def grafana_dashboard():
    try:
        with open("./grafana_dashboard.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>GRAFANA DASHBOARD</h1><p>Error: {e}</p>"

@app.route("/live")
def live_dashboard():
    try:
        with open("./frontend-html/ainexus-live.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>LIVE DASHBOARD</h1><p>Error: {e}</p>"

@app.route("/backend")
def backend_dashboard():
    try:
        with open("./frontend-html/ainexus-backend-live.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>BACKEND DASHBOARD</h1><p>Error: {e}</p>"

@app.route("/welcome")
def welcome_dashboard():
    try:
        with open("./src/templates/welcome_screen.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"<h1>WELCOME DASHBOARD</h1><p>Error: {e}</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
