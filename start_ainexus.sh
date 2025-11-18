#!/bin/bash

echo "Ì∫Ä AI-NEXUS START ENGINE - 6-PHASE TRANSFORMATION"
echo "=================================================="

# Check if Python is available
python3 --version

# Run the Start Engine directly
python3 start_engine.py

# If Start Engine completes, show status
if [ $? -eq 0 ]; then
    echo ""
    echo "Ìæâ AI-NEXUS TRANSFORMATION COMPLETE"
    echo "ÔøΩÔøΩ Live arbitrage trading is ACTIVE"
    echo "Ì≥ä Monitoring dashboard is RUNNING"
else
    echo ""
    echo "‚ùå Start Engine encountered an issue"
    echo "Ì¥Ñ Check the logs above for details"
fi
