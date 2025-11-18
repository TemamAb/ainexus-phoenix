#!/bin/bash
# AI-NEXUS v5.0 EMERGENCY STOP

echo "í»‘ EMERGENCY STOP ACTIVATED"
echo "==========================="

# Kill all Python processes related to AI-NEXUS
pkill -f "python.*ai-nexus" || true
pkill -f "python.*StrategyOrchestrator" || true  
pkill -f "python.*CrossChainDataAggregator" || true
pkill -f "python.*MarketScanner" || true

# Kill any Node.js processes
pkill -f "node.*ai-nexus" || true

# Remove service PID files
rm -f .service_pids

echo "âœ… ALL AI-NEXUS PROCESSES TERMINATED"
echo "í´’ SYSTEM SAFELY SHUTDOWN"
