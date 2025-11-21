from flask import Flask, send_file, jsonify, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return send_file('frontend-html/unified-dashboard.html')
    except Exception as e:
        return f"""
        <html>
            <head><title>AINEXUS v3.0.0 - Stormkit</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #0f0f23; color: #00ff00; }
                h1 { color: #00ffff; }
                a { color: #ffff00; text-decoration: none; }
                .status { background: #1a1a2e; padding: 20px; border-radius: 10px; }
            </style>
            </head>
            <body>
                <div class="status">
                    <h1>íº€ AINEXUS v3.0.0 - 96 Modules</h1>
                    <p><strong>Platform:</strong> Stormkit Python Deployment</p>
                    <p><strong>Status:</strong> Flask App Running</p>
                    <p><strong>Dashboard:</strong> <a href="/dashboard">Enter AINEXUS</a></p>
                    <p><strong>Health Check:</strong> <a href="/api/health">API Status</a></p>
                </div>
            </body>
        </html>
        """

@app.route('/dashboard')
def dashboard():
    return send_file('frontend-html/unified-dashboard.html')

@app.route('/api/health')
def health():
    return jsonify({
        "status": "operational",
        "platform": "AINEXUS v3.0.0",
        "modules": 96,
        "deployment": "stormkit-python",
        "environment": "twistergem-3rs6ph.stormkit.dev"
    })

@app.route('/<path:path>')
def serve_file(path):
    try:
        return send_from_directory('.', path)
    except:
        return jsonify({"error": "File not found", "path": path}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"íº€ AINEXUS starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
