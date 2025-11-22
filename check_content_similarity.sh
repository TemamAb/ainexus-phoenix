#!/bin/bash

echo "Ì¥ç CHECKING CONTENT SIMILARITY IN CRITICAL MODULES"
echo "=========================================="

# Compare similar modules
compare_modules() {
    module1=$1
    module2=$2
    echo "--- Comparing: $(basename $module1) vs $(basename $module2) ---"
    
    if [ -f "$module1" ] && [ -f "$module2" ]; then
        size1=$(stat -f%z "$module1" 2>/dev/null || stat -c%s "$module1" 2>/dev/null)
        size2=$(stat -f%z "$module2" 2>/dev/null || stat -c%s "$module2" 2>/dev/null)
        
        if [ "$size1" -eq "$size2" ]; then
            echo "Ì∫® IDENTICAL FILE SIZES: $size1 bytes"
            diff "$module1" "$module2" > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                echo "Ì∫®Ì∫® EXACT DUPLICATE CONTENT!"
            else
                echo "‚ö†Ô∏è  Same size but different content"
            fi
        else
            echo "‚úÖ Different sizes: $size1 vs $size2 bytes"
        fi
    else
        echo "‚ùå One or both files missing"
    fi
    echo ""
}

# Check critical duplicates
echo "Ì¥ç CRITICAL MODULE COMPARISONS:"

# MultiAgentOrchestrator
compare_modules "./ai/multi_agent/MultiAgentOrchestrator.py" "./multi_agent_advanced/multi_agent_system/MultiAgentOrchestrator.py"

# CompetitiveAnalysis  
compare_modules "./advanced_ai/security_risk/CompetitiveAnalysis.py" "./analytics/CompetitiveAnalysis.py"

# BridgeArbitrageur
compare_modules "./cross_chain/BridgeArbitrageur.py" "./cross_chain/bridge_integration/BridgeArbitrageur.py"

# InsuranceManager
compare_modules "./advanced_ai/security_risk/InsuranceManager.js" "./advanced_ai/security_risk/InsuranceManager.py"

# BackrunningEngine
compare_modules "./core_foundation/execution_engine/BackrunningEngine.py" "./performance/mev_warfare/BackrunningEngine.py"

# Check for similar dashboard modules
echo "Ì≥ä DASHBOARD MODULES:"
find . -name "*Dashboard*" -type f | grep -v __pycache__

# Check for similar monitoring modules  
echo ""
echo "Ì±Ä MONITORING MODULES:"
find . -name "*Monitor*" -type f | grep -v __pycache__ | head -10

