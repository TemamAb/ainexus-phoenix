#!/bin/bash
echo "Ì¥ç Quick AI-NEXUS v5.0 File Verification"
echo "========================================"

# Check main directories
directories=(
    "core_foundation"
    "advanced_ai" 
    "performance"
    "competitive_edge"
    "liquidity"
)

for dir in "${directories[@]}"; do
    if [ -d "ai-nexus-v5.0/ai-nexus-v5.0/$dir" ]; then
        file_count=$(find "ai-nexus-v5.0/ai-nexus-v5.0/$dir" -name "*.py" -o -name "*.js" -o -name "*.sol" | wc -l)
        echo "‚úÖ $dir: $file_count files"
    else
        echo "‚ùå $dir: MISSING"
    fi
done

# Count total files
total_files=$(find ai-nexus-v5.0/ai-nexus-v5.0 -name "*.py" -o -name "*.js" -o -name "*.sol" | wc -l)
echo ""
echo "Ì≥ä TOTAL FILES: $total_files"

# Check critical files
critical_files=(
    "core_foundation/ai_intelligence/RLAgent.py"
    "core_foundation/smart_contracts/FlashLoan.sol"
    "core_foundation/execution_engine/NanosecondExecutor.js"
    "advanced_ai/strategic_ai/PortfolioAI.py"
    "advanced_ai/protocol_integration/DEXRouter.js"
)

echo ""
echo "Ì¥ç Critical Files Check:"
for file in "${critical_files[@]}"; do
    if [ -f "ai-nexus-v5.0/ai-nexus-v5.0/$file" ]; then
        size=$(stat -f%z "ai-nexus-v5.0/ai-nexus-v5.0/$file" 2>/dev/null || stat -c%s "ai-nexus-v5.0/ai-nexus-v5.0/$file" 2>/dev/null || echo "0")
        if [ "$size" -gt 1000 ]; then
            echo "‚úÖ $file"
        else
            echo "‚ö†Ô∏è  $file (small file)"
        fi
    else
        echo "‚ùå $file (MISSING)"
    fi
done
