#!/bin/bash
echo "ÌæØ FINAL DUPLICATION CLEANUP"

remaining_duplicates=(
    "RollupOptimizer.js"
    "ROI_Predictor.py" 
    "RiskEngine.js"
    "RiskDashboard.js"
    "RelayerHealthMonitor.py"
    "real_time_metrics.py"
    "quick_deploy.py"
    "PrivatePoolManager.py"
    "PriorityFeeCalculator.js"
    "PredictiveDataEngine.py"
)

for module in "${remaining_duplicates[@]}"; do
    echo "Ì¥ç Processing: $module"
    
    # Find both copies
    files=($(find . -name "$module" | grep -v "__pycache__"))
    
    if [ ${#files[@]} -eq 2 ]; then
        size1=$(wc -c < "${files[0]}")
        size2=$(wc -c < "${files[1]}")
        
        # Keep the larger file
        if [ $size1 -gt $size2 ]; then
            keep="${files[0]}"
            remove="${files[1]}"
        else
            keep="${files[1]}"
            remove="${files[0]}"
        fi
        
        echo "‚úÖ Keeping: $keep ($(wc -c < "$keep") bytes)"
        echo "Ì∫Æ Removing: $remove ($(wc -c < "$remove") bytes)"
        rm "$remove"
    fi
    echo ""
done

echo "‚úÖ FINAL DUPLICATION CLEANUP COMPLETE"
