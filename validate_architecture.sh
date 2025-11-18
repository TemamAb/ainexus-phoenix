#!/bin/bash

echo "ÔøΩÔøΩ Validating 45-Module Transformation"

# Check module directories
required_dirs=(
    "competitive_edge/predictive_slippage"
    "competitive_edge/cross_asset_arbitrage" 
    "institutional_gateway/white_label"
    "research_automation/continuous_innovation"
    "multi_agent_advanced/orchestration"
    "enterprise_features/compliance_global"
    "advanced_ai/quantum_research"
    "capital_optimization/nested_flashloans"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "‚úÖ $dir"
    else
        echo "‚ùå $dir - MISSING"
    fi
done

# Check critical files
critical_files=(
    "core_foundation/execution_engine/ExecutionOrchestrator.js"
    "core_foundation/ai_intelligence/MarketPredictor.py"
    "advanced_ai/security_risk/ComplianceEngine.js"
    "competitive_edge/cross_asset_arbitrage/VolSurfaceArb.py"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "‚úÖ $file"
    else
        echo "‚ùå $file - MISSING"
    fi
done

echo "Ì≥ä Validation complete"
