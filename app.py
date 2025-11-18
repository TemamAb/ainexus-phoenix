#!/usr/bin/env python3
"""
AI-NEXUS MAIN ENTRY POINT - START ENGINE SYSTEM
Starts the 6-phase transformation automatically
"""

import asyncio
import os
import sys

async def start_ainexus_system():
    """Start the AI-Nexus Start Engine system"""
    print("Ì∫Ä AI-NEXUS QUANTUM ENGINE - STARTING...")
    
    try:
        # Import and run the Start Engine
        from start_engine import main
        await main()
        
    except ImportError as e:
        print(f"‚ùå Start Engine import failed: {e}")
        print("Ì¥Ñ Starting core application instead...")
        
        # Fallback to core app
        try:
            from core.app import app
            port = int(os.environ.get('PORT', 10000))
            app.run(host='0.0.0.0', port=port, debug=False)
        except ImportError:
            print("‚ùå All startup methods failed")
            sys.exit(1)

if __name__ == "__main__":
    # Check if we should start the Start Engine
    if os.environ.get('START_ENGINE', 'true').lower() == 'true':
        asyncio.run(start_ainexus_system())
    else:
        # Start normal web app
        try:
            from core.app import app
            port = int(os.environ.get('PORT', 10000))
            app.run(host='0.0.0.0', port=port, debug=False)
        except ImportError as e:
            print(f"‚ùå Failed to start: {e}")
            sys.exit(1)
