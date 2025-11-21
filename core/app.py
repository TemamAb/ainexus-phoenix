from flask import Flask, send_file, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "AINEXUS v3.0.0 - 96 Modules",
        "message": "AI Trading Platform Running",
        "deployment": "vercel-python"
    })

@app.route('/dashboard')
def dashboard():
    try:
        return send_file('frontend-html/unified-dashboard.html')
    except:
        return "Dashboard loading..."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
