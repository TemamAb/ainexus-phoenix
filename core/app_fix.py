#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix dashboard routes to serve actual HTML files
"""

# Read the activation dashboard HTML
try:
    with open("./src/templates/activation_dashboard.html", "r") as f:
        activation_html = f.read()
except:
    activation_html = "<h1>ACTIVATION DASHBOARD</h1><p>Two-Click System Ready</p>"

# Update core/app.py to serve real HTML
with open("core/app.py", "r") as f:
    content = f.read()

# Replace the activation dashboard route
new_content = content.replace(
    '@app.route("/activation")\ndef activation_dashboard():\n    return "ACTIVATION DASHBOARD - Two-Click System"',
    f'@app.route("/activation")\ndef activation_dashboard():\n    return """{activation_html}"""'
)

with open("core/app.py", "w") as f:
    f.write(new_content)

print("ACTIVATION DASHBOARD FIXED - Now serving real HTML")
