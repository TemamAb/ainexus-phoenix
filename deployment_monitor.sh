#!/bin/bash

# ÌæØ AI-NEXUS DEPLOYMENT MONITOR
# Ì≥ç Monitor deployment progress in real-time

echo "Ì∫Ä AI-NEXUS DEPLOYMENT MONITOR"
echo "=============================="

SERVICE_URL="https://ainexus-quantum-arbitrage.onrender.com"

echo "‚è≥ Monitoring deployment status..."
echo "Ìºê Service: $SERVICE_URL"

for i in {1..30}; do
    echo ""
    echo "Ìµí Check #$i - $(date)"
    
    # Test if service is responding
    if curl -s -f "$SERVICE_URL/health" > /dev/null; then
        echo "‚úÖ SERVICE IS LIVE!"
        echo "ÌæØ DASHBOARD READY: $SERVICE_URL"
        
        # Get confidence level
        CONFIDENCE=$(curl -s "$SERVICE_URL/confidence" | grep -o '"system_confidence":[0-9.]*' | cut -d: -f2)
        if [ ! -z "$CONFIDENCE" ]; then
            echo "Ì≥ä System Confidence: ${CONFIDENCE}%"
        fi
        
        break
    else
        echo "‚è≥ Service not ready... (Attempt $i/30)"
        echo "Ì≤° Check Render.com dashboard for build status"
        sleep 10
    fi
done

echo ""
echo "Ì≥ã FINAL STATUS:"
if curl -s -f "$SERVICE_URL/health" > /dev/null; then
    echo "Ìæâ DEPLOYMENT SUCCESSFUL!"
    echo "Ìºê OPEN YOUR DASHBOARD: $SERVICE_URL"
else
    echo "‚ùå SERVICE NOT ACCESSIBLE AFTER 5 MINUTES"
    echo "Ì¥ç Check Render.com for build errors"
    echo "Ì≥ß Contact Render support if needed"
fi
