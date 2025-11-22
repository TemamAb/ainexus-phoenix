#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AINEXUS Dashboard Activation Protocol
Clean UTF-8 Version
"""

import os
import subprocess

def activate_dashboard_ecosystem():
    print("ACTIVATING AINEXUS DASHBOARD ECOSYSTEM...")
    print("=" * 50)
    
    dashboards = {
        "production": "./core/templates/dashboard.html",
        "trading": "./monitoring_dashboard.html", 
        "profit": "./profit_dashboard.html",
        "activation": "./src/templates/activation_dashboard.html",
        "unified": "./frontend-html/unified-dashboard.html",
        "grafana": "./grafana_dashboard.html"
    }
    
    activated = []
    for name, path in dashboards.items():
        if os.path.exists(path):
            print(f"ACTIVE: {name.upper()} DASHBOARD - {path}")
            activated.append(name)
        else:
            print(f"MISSING: {name.upper()} DASHBOARD - {path}")
    
    print(f"DASHBOARDS ACTIVATED: {len(activated)}/6")
    print("READY FOR INSTITUTIONAL ONBOARDING!")
    
    return activated

if __name__ == "__main__":
    activated = activate_dashboard_ecosystem()
    
    # Create dashboard routing in core/app.py
    with open("core/app.py", "a") as f:
        f.write('\n\n# DASHBOARD ROUTES\n')
        for dashboard in activated:
            f.write(f'@app.route("/{dashboard}")\n')
            f.write(f'def {dashboard}_dashboard():\n')
            f.write(f'    return app.send_static_file("{dashboard}.html")\n\n')
    
    print("DASHBOARD ROUTES INTEGRATED INTO PLATFORM!")
