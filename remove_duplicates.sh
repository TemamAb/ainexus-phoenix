#!/bin/bash

echo "Ì∑π REMOVING EXACT DUPLICATE MODULES"
echo "=========================================="

# Remove exact duplicates - keeping the better located versions
echo "Ì∑ëÔ∏è  Removing ./advanced_ai/security_risk/CompetitiveAnalysis.py (duplicate)"
rm "./advanced_ai/security_risk/CompetitiveAnalysis.py"

echo "Ì∑ëÔ∏è  Removing ./cross_chain/BridgeArbitrageur.py (duplicate)" 
rm "./cross_chain/BridgeArbitrageur.py"

echo "Ì∑ëÔ∏è  Removing ./core_foundation/execution_engine/BackrunningEngine.py (duplicate)"
rm "./core_foundation/execution_engine/BackrunningEngine.py"

echo ""
echo "‚úÖ DUPLICATES REMOVED:"
echo "   - Kept: ./analytics/CompetitiveAnalysis.py (better location)"
echo "   - Kept: ./cross_chain/bridge_integration/BridgeArbitrageur.py (specialized)"
echo "   - Kept: ./performance/mev_warfare/BackrunningEngine.py (enhanced)"

echo ""
echo "Ì¥ç VERIFYING CLEANUP:"
find . -name "CompetitiveAnalysis.py" -type f | grep -v __pycache__
find . -name "BridgeArbitrageur.py" -type f | grep -v __pycache__
find . -name "BackrunningEngine.py" -type f | grep -v __pycache__

