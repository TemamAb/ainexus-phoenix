import http.server
import socketserver
import webbrowser
import os

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

PORT = 3000

def main():
    # Change to the directory containing our files
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"íº MetaMask Test Server running at: http://localhost:{PORT}")
        print("í³± Open your browser and navigate to the above URL")
        print("í´§ Make sure MetaMask is installed in your browser")
        print("â¹ï¸  Press Ctrl+C to stop the server")
        
        # Try to open browser automatically
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except Exception as e:
            print(f"Note: Could not open browser automatically: {e}")
            print("Please manually open: http://localhost:3000")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nâ Server stopped successfully")

if __name__ == "__main__":
    main()
