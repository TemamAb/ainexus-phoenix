#!/bin/bash

# ÌæØ AI-NEXUS DASHBOARD DIAGNOSIS TOOL
# Ì≥ç Check if dashboard is live and accessible

echo "Ì¥ç AI-NEXUS DASHBOARD DIAGNOSIS"
echo "================================"

# Default Render URL - replace with your actual URL
RENDER_URL="https://ainexus-quantum-arbitrage.onrender.com"

echo "Ì≥ä Testing dashboard accessibility..."
echo "Ìºê URL: $RENDER_URL"

# Test health endpoint
echo ""
echo "1. Testing Health Endpoint:"
curl -s -f "$RENDER_URL/health" && echo " ‚úÖ HEALTHY" || echo " ‚ùå UNHEALTHY"

# Test confidence endpoint
echo ""
echo "2. Testing Confidence API:"
curl -s "$RENDER_URL/confidence" | python3 -m json.tool 2>/dev/null && echo " ‚úÖ CONFIDENCE API WORKING" || echo " ‚ùå CONFIDENCE API FAILED"

# Test main dashboard
echo ""
echo "3. Testing Main Dashboard:"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$RENDER_URL")
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo " ‚úÖ DASHBOARD ACCESSIBLE (HTTP 200)"
    echo " ÌæØ OPEN YOUR DASHBOARD: $RENDER_URL"
else
    echo " ‚ùå DASHBOARD INACCESSIBLE (HTTP $HTTP_STATUS)"
fi

# Check if service is building
echo ""
echo "4. Deployment Status:"
if curl -s "$RENDER_URL" | grep -q "Application not available"; then
    echo " ‚ö†Ô∏è  APPLICATION STILL DEPLOYING"
    echo " ‚è≥ Wait 2-5 minutes and try again"
else
    echo " ‚úÖ APPLICATION DEPLOYED"
fi

echo ""
echo "Ì≥ã NEXT STEPS:"
echo "   ‚Ä¢ If all checks pass: Open $RENDER_URL"
echo "   ‚Ä¢ If checks fail: Check Render.com logs"
echo "   ‚Ä¢ Wait 2-5 minutes if recently deployed"
echo "   ‚Ä¢ Verify service name in Render dashboard"
