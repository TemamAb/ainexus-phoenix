#!/bin/bash
cd core
python -c "import sys; print('Python path:', sys.path)"
python -c "import flask, flask_cors, web3; print('✅ All critical imports successful')"
exec gunicorn --bind 0.0.0.0:$PORT app:app
