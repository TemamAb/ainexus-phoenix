#!/usr/bin/env python3
import os
import sys

def start_application():
    """Start the AI-Nexus application with fallbacks"""
    try:
        # Try to import and run the Start Engine
        from start_engine import GrafanaStartEngine, main as start_engine_main
        print("Ì∫Ä Starting AI-Nexus Start Engine...")
        
        import asyncio
        asyncio.run(start_engine_main())
        
    except ImportError as e:
        print(f"Start Engine import failed: {e}")
        print("Falling back to web application...")
        
        # Fallback to Flask app
        try:
            from app_backup import app
            port = int(os.environ.get('PORT', 10000))
            print(f"Ìºê Starting web server on port {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
        except ImportError:
            print("All startup methods failed")
            sys.exit(1)

if __name__ == "__main__":
    # Check if we should use Start Engine or web app
    if os.environ.get('START_ENGINE', 'true').lower() == 'true':
        start_application()
    else:
        from app_backup import app
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=False)
