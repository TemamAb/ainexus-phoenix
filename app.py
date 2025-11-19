#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
from aiohttp import web

async def start_engine(request):
    try:
        # Try to read the file with explicit path
        file_path = './start_engine.html'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        else:
            # If file doesn't exist, create a basic one
            basic_html = "<html><body><h1>AI-NEXUS Start Engine</h1><p>System Ready</p></body></html>"
            return web.Response(text=basic_html, content_type='text/html')
    except Exception as e:
        # Return the actual HTML content directly as fallback
        return web.Response(text=open('start_engine.html', 'r').read(), content_type='text/html')

async def monitoring_dashboard(request):
    return web.Response(text="Monitoring Dashboard - Live Trading Active", content_type='text/html')

async def health_check(request):
    return web.json_response({'status': 'ready', 'system': 'AI-NEXUS'})

async def init_app():
    app = web.Application()
    app.router.add_get('/', start_engine)
    app.router.add_get('/start_engine.html', start_engine)
    app.router.add_get('/monitoring_dashboard.html', monitoring_dashboard)
    app.router.add_get('/health', health_check)
    return app

if __name__ == '__main__':
    print("AI-NEXUS DEPLOYMENT ENGINE STARTING...")
    web.run_app(init_app(), host='0.0.0.0', port=8080)
