#!/bin/bash
echo "ÌæØ INTELLIGENT CLEANUP BASED ON FILE SIZES"

# 1. KEEP LARGEST VERSION OF DUPLICATES
echo "=== RESOLVING DUPLICATES (KEEP LARGEST) ==="
duplicates=(
    "test_multi_dex.py"
    "InfrastructureManager.py" 
    "health_check.py"
    "GasPredictor.py"
    "verify_blueprint_completion.py"
    "TransactionRouter.js"
    "trade_analyzer.py"
    "ThreatMonitor.js"
    "strategy_dashboard.py"
    "strategy_benchmark.py"
    "slippage_simulator.js"
    "server.js"
    "SecurityScanner.py"
    "SandwichDetector.py"
    "rpc_load_balancer.py"
)

for module in "${duplicates[@]}"; do
    echo "Ì¥ç Processing: $module"
    largest_file=""
    largest_size=0
    
    # Find largest file
    while read file; do
        size=$(wc -c < "$file" 2>/dev/null || echo "0")
        if [ $size -gt $largest_size ]; then
            largest_size=$size
            largest_file=$file
        fi
    done < <(find . -name "$module" | grep -v "__pycache__")
    
    # Remove smaller duplicates
    if [ -n "$largest_file" ]; then
        echo "‚úÖ Keeping largest: $largest_file ($largest_size bytes)"
        find . -name "$module" | grep -v "__pycache__" | while read file; do
            if [ "$file" != "$largest_file" ]; then
                size=$(wc -c < "$file" 2>/dev/null || echo "0")
                echo "Ì∫Æ Removing smaller: $file ($size bytes)"
                rm "$file"
            fi
        done
    fi
    echo ""
done

# 2. REMOVE EMPTY/SMALL FILES
echo "=== CLEANING EMPTY/SMALL FILES ==="
find . -name "*.py" -o -name "*.js" -o -name "*.sol" | grep -v "__pycache__" | while read file; do
    size=$(wc -c < "$file" 2>/dev/null || echo "0")
    if [ $size -eq 0 ]; then
        echo "Ì∫Æ Removing empty: $file"
        rm "$file"
    elif [ $size -lt 100 ]; then
        echo "Ì≥Ñ Removing small (<100B): $file ($size bytes)"
        rm "$file"
    fi
done

echo "‚úÖ SIZE-BASED CLEANUP COMPLETE"
