#!/bin/bash

echo "Ì∫Ä AI-NEXUS DEPENDENCY SETUP"

# Check if we're on Render
if [ ! -z "$RENDER" ]; then
    echo "Ì≥¶ Render environment detected"
    echo "Ì¥ß Installing system dependencies..."
    
    # Install system dependencies for TA-Lib alternatives
    apt-get update
    apt-get install -y build-essential python3-dev
fi

echo "Ì≥• Installing Python dependencies..."
pip install -r requirements.txt

# Check if pandas-ta works as TA-Lib replacement
python3 -c "
try:
    import pandas_ta as ta
    print('‚úÖ pandas-ta installed successfully (TA-Lib replacement)')
except ImportError as e:
    print(f'‚ùå pandas-ta import failed: {e}')
"

echo "‚úÖ Setup completed"
