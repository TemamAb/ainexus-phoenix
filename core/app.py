from flask import Flask, send_file, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def serve_home():
    try:
        return send_file('frontend-html/unified-dashboard.html')
    except Exception as e:
        return f"""
        <html>
            <head><title>AINEXUS v3.0.0</title></head>
            <body>
                <h1>íº€ AINEXUS Platform - 96 Modules</h1>
                <p>Stormkit Deployment Active</p>
                <p>Error: {str(e)}</p>
                <a href="/dashboard">Enter Dashboard</a>
            </body>
        </html>
        """

@app.route('/dashboard')
def dashboard():
    return send_file('frontend-html/unified-dashboard.html')

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "operational",
        "platform": "AINEXUS v3.0.0 - Stormkit",
        "modules": 96,
        "deployment": "twistergem-3rs6ph.stormkit.dev"
    })

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('.', path)
    except:
        return "File not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
