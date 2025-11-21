#!/usr/bin/env python3
"""
Simple server for wallet connection test
"""
import http.server
import socketserver
import os
import webbrowser

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Ì∫Ä Wallet Connection Test Server running at: http://localhost:{PORT}")
        print("Ì≥± Open this URL in your browser to test MetaMask connection")
        print("Ì¥ç Make sure MetaMask is installed in your browser")
        print("‚èπÔ∏è  Press Ctrl+C to stop the server")
        
        # Try to open browser automatically
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass
            
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n‚èπÔ∏è  Server stopped")

if __name__ == "__main__":
    main()
