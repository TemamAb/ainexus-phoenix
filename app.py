#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AINEXUS MAIN APPLICATION
UTF-8 Compliant Version
"""

from flask import Flask, render_template, jsonify
import datetime
import random

app = Flask(__name__)
app.secret_key = 'ainexus_quantum_ai_2024'

# Force UTF-8 encoding for all responses
@app.after_request
def set_charset(response):
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/')
def activation_dashboard():
    return render_template('activation_master.html')

@app.route('/trading')
def trading_dashboard():
    return render_template('trading_dashboard.html')

@app.route('/production')
def production_dashboard():
    return render_template('production_dashboard.html')

@app.route('/profit')
def profit_dashboard():
    return render_template('profit_dashboard.html')

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "system": "AINEXUS 96-Module Engine",
        "encoding": "utf-8",
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
