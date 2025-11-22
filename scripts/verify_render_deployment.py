#!/usr/bin/env python3
"""
AINEXUS Render Deployment Verification
"""

import requests
import sys

def verify_render_deployment():
    base_url = "https://ainexus-platform.onrender.com"
    
    endpoints = [
        "/",
        "/api/v1/system/health",
        "/api/v1/ai/health",
        "/api/v1/execution/health", 
        "/api/v1/security/health",
        "/api/v1/infrastructure/health",
        "/api/v1/platform/health",
        "/api/v1/deployment/status"
    ]
    
    print("Ì¥ç Verifying AINEXUS Render Deployment...")
    
    all_success = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"‚úÖ {endpoint} - ONLINE")
            else:
                print(f"‚ùå {endpoint} - OFFLINE (Status: {response.status_code})")
                all_success = False
        except Exception as e:
            print(f"‚ùå {endpoint} - ERROR: {e}")
            all_success = False
    
    if all_success:
        print("\nÌæâ AINEXUS 96-Module Platform successfully deployed on Render!")
        print("Ìºê Platform URL: https://ainexus-platform.onrender.com")
        print("Ì∫Ä Two-click activation ready for institutional clients")
    else:
        print("\n‚ùå Deployment verification failed")
        sys.exit(1)

if __name__ == "__main__":
    verify_render_deployment()
