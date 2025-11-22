#!/bin/bash

echo "Ì¥Ñ MAPPING REAL FILES TO BLUEPRINT REQUIREMENTS"
echo "=========================================="

# Discover ALL real files
find . -type f \( -name "*.js" -o -name "*.py" -o -name "*.sol" \) | grep -v __pycache__ > actual_files.txt

echo "Ì≥ã ACTUAL FILES FOUND:"
cat actual_files.txt

echo ""
echo "ÌæØ CRITICAL REALITY CHECKS:"

# Check if we have the core functionality regardless of paths
declare -a critical_modules=(
    "AdvancedOpportunityDetector"
    "QuantumOptimizer" 
    "ArbitrageOrchestrator"
    "FlashLoanExecutor"
    "MEVShield"
    "FlashLoan"
    "EnterpriseDashboard"
    "ProfitTracker"
)

echo ""
echo "Ì¥ç CHECKING CORE FUNCTIONALITY:"
for module in "${critical_modules[@]}"; do
    if grep -q "$module" actual_files.txt; then
        echo "‚úÖ CORE MODULE EXISTS: $module"
    else
        echo "‚ùå MISSING CORE MODULE: $module"
    fi
done

# Check what execution engines actually exist
echo ""
echo "‚ö° ACTUAL EXECUTION ENGINES:"
grep -E "(execution|engine|arbitrage)" actual_files.txt | grep -i -E "(\.js|\.py)" | sort

# Check what AI modules actually exist  
echo ""
echo "Ì∑† ACTUAL AI MODULES:"
grep -E "(ai|intelligence|predict|learning)" actual_files.txt | grep -i -E "(\.js|\.py)" | sort

# Check what smart contracts actually exist
echo ""
echo "Ì≥ú ACTUAL SMART CONTRACTS:"
grep "\.sol" actual_files.txt | sort
