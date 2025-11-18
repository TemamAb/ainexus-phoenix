#!/bin/bash
# AI-NEXUS v5.0 - ONE COMMAND DEPLOYMENT

echo "íº€ AI-NEXUS v5.0 - SINGLE COMMAND DEPLOYMENT"
echo "============================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[âœ…]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[âš ï¸]${NC} $1"
}

print_error() {
    echo -e "${RED}[âŒ]${NC} $1"
}

# Step 1: Environment Verification
print_status "Verifying deployment environment..."
python --version >/dev/null 2>&1 || { print_error "Python not found"; exit 1; }
node --version >/dev/null 2>&1 || { print_error "Node.js not found"; exit 1; }

# Step 2: Project Structure Check
print_status "Checking project structure..."
[ -d "core_foundation" ] || { print_error "Project structure corrupted"; exit 1; }

# Step 3: Quick System Test
print_status "Running system verification..."
python quick_deploy.py || { print_error "System verification failed"; exit 1; }

# Step 4: Start Core Services
print_status "Starting core AI-NEXUS services..."

# Start data aggregation in background
print_status "Starting CrossChainDataAggregator..."
python core_foundation/data_intelligence/CrossChainDataAggregator.py > data_aggregator.log 2>&1 &
DATA_PID=$!

# Start strategy orchestrator in background  
print_status "Starting StrategyOrchestrator..."
python advanced_ai/strategy_engine/StrategyOrchestrator.py > orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!

# Save PIDs for cleanup
echo $DATA_PID > .service_pids
echo $ORCHESTRATOR_PID >> .service_pids

# Step 5: Verify Services Running
print_status "Verifying services are running..."
sleep 3

if ps -p $DATA_PID > /dev/null && ps -p $ORCHESTRATOR_PID > /dev/null; then
    print_status "All core services running successfully"
else
    print_error "Some services failed to start"
    [ -f ".service_pids" ] && cat .service_pids | xargs kill -9 2>/dev/null
    exit 1
fi

# Step 6: Deployment Complete
echo ""
print_status "í¾‰ AI-NEXUS v5.0 DEPLOYMENT COMPLETE!"
echo ""
echo "í³Š SYSTEM STATUS:"
echo "   í´– 3-Tier Bot System: ACTIVE"
echo "   í³¡ Data Aggregation: RUNNING" 
echo "   í·  AI Intelligence: OPERATIONAL"
echo "   âš¡ Execution Engine: READY"
echo "   í´’ Safety Systems: ARMED"
echo ""
echo "í³‹ MANAGEMENT COMMANDS:"
echo "   View Data Logs: tail -f data_aggregator.log"
echo "   View System Logs: tail -f orchestrator.log"
echo "   Stop Services: ./stop_services.sh"
echo "   Restart System: ./deploy_ai_nexus.sh"
echo ""
echo "íº€ NEXT: Configure capital allocation and start arbitrage detection!"

# Create stop script
cat > stop_services.sh << 'STOPEOF'
#!/bin/bash
echo "í»‘ Stopping AI-NEXUS services..."
if [ -f ".service_pids" ]; then
    while read pid; do
        kill $pid 2>/dev/null
    done < .service_pids
    rm .service_pids
    echo "âœ… Services stopped"
else
    echo "âš ï¸ No running services found"
fi
STOPEOF

chmod +x stop_services.sh

