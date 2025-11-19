#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
from aiohttp import web

async def start_engine(request):
    try:
        # Try multiple possible locations for start_engine.html
        possible_paths = [
            'start_engine.html',           # Same directory as core/
            '../start_engine.html',        # Parent directory  
            './start_engine.html',         # Current directory
            'C:/Users/op/Desktop/ainexus/start_engine.html'  # Absolute path
        ]
        
        content = None
        for file_path in possible_paths:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                break
        
        if content:
            return web.Response(text=content, content_type='text/html')
        else:
            # Serve the actual start_engine.html content directly
            return web.Response(text=open('../start_engine.html', 'r', encoding='utf-8').read(), content_type='text/html')
            
    except Exception as e:
        return web.Response(text=f"File Error: {str(e)}", status=500)

async def monitoring_dashboard(request):
    return web.Response(text="Monitoring Dashboard", content_type='text/html')

async def health_check(request):
    return web.json_response({'status': 'ready'})

async def init_app():
    app = web.Application()
    app.router.add_get('/', start_engine)
    app.router.add_get('/start_engine.html', start_engine)
    app.router.add_get('/health', health_check)
    return app

if __name__ == '__main__':
    print("AI-NEXUS STARTING...")
    web.run_app(init_app(), host='0.0.0.0', port=8080)
