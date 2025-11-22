from flask import Flask, render_template, jsonify
import datetime

app = Flask(__name__)
app.secret_key = 'ainexus_quantum_ai_2024'

@app.route('/')
def activation_dashboard():
    try:
        return render_template('activation_master.html')
    except Exception as e:
        return f"Error loading template: {str(e)}", 500

@app.route('/trading')
def trading_dashboard():
    return "Trading Dashboard - Coming Soon"

@app.route('/production')
def production_dashboard():
    return "Production Dashboard - Coming Soon"

@app.route('/profit')
def profit_dashboard():
    return "Profit Dashboard - Coming Soon"

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "system": "AINEXUS",
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
