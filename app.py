from flask import Flask, render_template, jsonify, session
import datetime
import random
import os

app = Flask(__name__)
app.secret_key = 'ainexus_quantum_ai_2024'

# Simple UTF-8 compatibility without locale
import sys
if sys.stdout.encoding != 'UTF-8':
    sys.stdout.reconfigure(encoding='utf-8')

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
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/module-status')
def module_status():
    return jsonify({
        "total_modules": 96,
        "active_modules": 96,
        "system_status": "operational"
    })

@app.route('/api/arbitrage-opportunities')
def arbitrage_opportunities():
    opportunities = []
    for i in range(6):
        opportunities.append({
            "id": i,
            "pair": f"ETH/USDC",
            "profit_percent": round(random.uniform(0.15, 2.5), 2),
            "exchanges": ["Uniswap V3", "Binance"],
            "confidence": random.randint(75, 95)
        })
    return jsonify({"opportunities": opportunities})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
