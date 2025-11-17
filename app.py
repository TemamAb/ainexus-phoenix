# app.py - Main Render entry point
import os
import sys

# Add project to Python path
sys.path.append(os.path.dirname(__file__))

try:
    # Import main Flask app
    from api.flask_app import app
    print("‚úÖ Successfully imported Flask app from api.flask_app")
except ImportError as e:
    print(f"‚ùå Import error: {e}")
    print("Ì¥ç Attempting to find alternative Flask app...")
    
    # Fallback imports
    try:
        from api.app import app
        print("‚úÖ Imported from api.app")
    except ImportError:
        try:
            from app import app
            print("‚úÖ Imported from app")
        except ImportError:
            # Create minimal Flask app as last resort
            from flask import Flask
            app = Flask(__name__)
            @app.route('/')
            def health_check():
                return 'Ì∫Ä AINexus AI Engine - Deployment Active'
            print("‚ö†Ô∏è  Created minimal Flask app as fallback")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
