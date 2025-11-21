// AINEXUS - PHASE 1 MODULE 4: BASIC DASHBOARD
// Real-time Monitoring Interface

const EventEmitter = require('events');

class BasicDashboard extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.metrics = {
            wallet: {},
            opportunities: [],
            executions: [],
            performance: {},
            system: {}
        };
        this.updateInterval = null;
        this.isRunning = false;
    }

    // Initialize dashboard
    async initialize(modules) {
        try {
            console.log('��� Initializing Basic Dashboard...');
            
            // Store module references for data access
            this.modules = modules;
            
            // Initialize metrics structure
            this.initializeMetrics();
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
            this.emit('module_ready', { module: 'BasicDashboard', status: 'active' });
            return { success: true, dashboard: 'active' };
        } catch (error) {
            this.emit('module_error', { module: 'BasicDashboard', error: error.message });
            throw error;
        }
    }

    // Initialize metrics structure
    initializeMetrics() {
        this.metrics = {
            wallet: {
                connected: false,
                address: null,
                balance: '0',
                network: null
            },
            opportunities: {
                totalScanned: 0,
                profitableFound: 0,
                currentOpportunities: [],
                lastScan: null
            },
            executions: {
                totalExecuted: 0,
                successful: 0,
                failed: 0,
                totalProfit: 0,
                recentExecutions: []
            },
            performance: {
                uptime: 0,
                scanSpeed: 0,
                executionSpeed: 0,
                successRate: 0
            },
            system: {
                modulesActive: 0,
                modulesTotal: 4, // Phase 1 modules
                lastUpdate: Date.now()
            }
        };
    }

    // Start real-time data updates
    startRealTimeUpdates() {
        this.isRunning = true;
        
        this.updateInterval = setInterval(() => {
            this.updateAllMetrics();
            this.emit('metrics_updated', this.metrics);
        }, this.config.updateInterval || 2000); // Update every 2 seconds

        console.log('��� Real-time dashboard updates started');
    }

    // Update all dashboard metrics
    async updateAllMetrics() {
        try {
            // Update wallet metrics
            await this.updateWalletMetrics();
            
            // Update opportunity metrics
            await this.updateOpportunityMetrics();
            
            // Update execution metrics
            await this.updateExecutionMetrics();
            
            // Update performance metrics
            await this.updatePerformanceMetrics();
            
            // Update system metrics
            await this.updateSystemMetrics();
            
            this.metrics.system.lastUpdate = Date.now();
            
        } catch (error) {
            console.error('Dashboard update error:', error);
        }
    }

    // Update wallet-related metrics
    async updateWalletMetrics() {
        if (this.modules.walletManager) {
            const walletStatus = this.modules.walletManager.getStatus();
            this.metrics.wallet = {
                connected: walletStatus.connected,
                address: walletStatus.walletAddress ? 
                    `${walletStatus.walletAddress.substring(0, 6)}...${walletStatus.walletAddress.substring(38)}` : 
                    'Not connected',
                balance: walletStatus.balance,
                network: this.getNetworkName(walletStatus.networkId)
            };
        }
    }

    // Update opportunity metrics
    async updateOpportunityMetrics() {
        if (this.modules.arbitrageOrchestrator) {
            const orchestratorStatus = this.modules.arbitrageOrchestrator.getStatus();
            
            this.metrics.opportunities.totalScanned += orchestratorStatus.opportunitiesFound || 0;
            this.metrics.opportunities.lastScan = new Date().toLocaleTimeString();
            
            // Simulate current opportunities (would come from actual scan)
            if (Math.random() > 0.7) { // 30% chance of new opportunity
                this.metrics.opportunities.profitableFound++;
                this.metrics.opportunities.currentOpportunities = [{
                    pair: 'ETH/USDC',
                    profit: (Math.random() * 0.5 + 0.1).toFixed(2) + '%',
                    dexes: 'Uniswap ↔ SushiSwap',
                    timestamp: new Date().toLocaleTimeString()
                }];
            }
        }
    }

    // Update execution metrics
    async updateExecutionMetrics() {
        if (this.modules.flashLoanExecutor) {
            const executorStatus = this.modules.flashLoanExecutor.getStatus();
            
            this.metrics.executions.totalExecuted = executorStatus.completedLoans + executorStatus.failedLoans;
            this.metrics.executions.successful = executorStatus.completedLoans;
            this.metrics.executions.failed = executorStatus.failedLoans;
            this.metrics.executions.totalProfit = executorStatus.totalProfit || 0;
            
            // Add to recent executions (keep last 5)
            if (executorStatus.completedLoans > this.metrics.executions.totalExecuted) {
                this.metrics.executions.recentExecutions.unshift({
                    profit: `$${(Math.random() * 50 + 10).toFixed(2)}`,
                    pair: 'ETH/USDC',
                    timestamp: new Date().toLocaleTimeString()
                });
                
                if (this.metrics.executions.recentExecutions.length > 5) {
                    this.metrics.executions.recentExecutions.pop();
                }
            }
        }
    }

    // Update performance metrics
    async updatePerformanceMetrics() {
        const totalExecutions = this.metrics.executions.totalExecuted;
        const successful = this.metrics.executions.successful;
        
        this.metrics.performance = {
            uptime: this.formatUptime(process.uptime()),
            scanSpeed: '2s', // Fixed for Phase 1
            executionSpeed: '5-30s', // Estimated
            successRate: totalExecutions > 0 ? 
                ((successful / totalExecutions) * 100).toFixed(1) + '%' : '0%'
        };
    }

    // Update system metrics
    async updateSystemMetrics() {
        let activeModules = 0;
        
        if (this.modules.walletManager && this.modules.walletManager.getStatus) activeModules++;
        if (this.modules.arbitrageOrchestrator && this.modules.arbitrageOrchestrator.getStatus) activeModules++;
        if (this.modules.flashLoanExecutor && this.modules.flashLoanExecutor.getStatus) activeModules++;
        
        this.metrics.system.modulesActive = activeModules;
    }

    // Get network name from ID
    getNetworkName(networkId) {
        const networks = {
            1: 'Ethereum Mainnet',
            5: 'Goerli Testnet',
            137: 'Polygon Mainnet'
        };
        return networks[networkId] || `Network ${networkId}`;
    }

    // Format uptime
    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }

    // Render dashboard to console (for Phase 1)
    renderToConsole() {
        console.clear();
        console.log('┌' + '─'.repeat(78) + '┐');
        console.log('│' + ' AINEXUS ARBITRAGE DASHBOARD '.padStart(53).padEnd(78) + '│');
        console.log('│' + ' Phase 1 - Basic Monitoring '.padStart(47).padEnd(78) + '│');
        console.log('└' + '─'.repeat(78) + '┘');
        
        // Wallet Section
        console.log('┌─────────────────── WALLET ───────────────────┐');
        console.log(`│ Status:    ${this.metrics.wallet.connected ? '✅ Connected' : '❌ Disconnected'.padEnd(40)}│`);
        console.log(`│ Address:   ${this.metrics.wallet.address.padEnd(40)}│`);
        console.log(`│ Balance:   ${this.metrics.wallet.balance + ' ETH'.padEnd(40)}│`);
        console.log(`│ Network:   ${this.metrics.wallet.network?.padEnd(40) || 'Unknown'.padEnd(40)}│`);
        console.log('└' + '─'.repeat(48) + '┘');
        
        // Opportunities Section
        console.log('┌──────────────── OPPORTUNITIES ───────────────┐');
        console.log(`│ Total Scanned:  ${this.metrics.opportunities.totalScanned.toString().padEnd(30)}│`);
        console.log(`│ Profitable:     ${this.metrics.opportunities.profitableFound.toString().padEnd(30)}│`);
        console.log(`│ Last Scan:      ${(this.metrics.opportunities.lastScan || 'Never').padEnd(30)}│`);
        
        if (this.metrics.opportunities.currentOpportunities.length > 0) {
            console.log('│                                                 │');
            this.metrics.opportunities.currentOpportunities.forEach(opp => {
                console.log(`│ ��� ${opp.pair}: ${opp.profit.padEnd(10)} ${opp.dexes.padEnd(20)}│`);
            });
        }
        console.log('└' + '─'.repeat(49) + '┘');
        
        // Executions Section
        console.log('┌───────────────── EXECUTIONS ─────────────────┐');
        console.log(`│ Total:         ${this.metrics.executions.totalExecuted.toString().padEnd(30)}│`);
        console.log(`│ Successful:    ${this.metrics.executions.successful.toString().padEnd(30)}│`);
        console.log(`│ Failed:        ${this.metrics.executions.failed.toString().padEnd(30)}│`);
        console.log(`│ Total Profit:  $${this.metrics.executions.totalProfit.toFixed(2).padEnd(27)}│`);
        
        if (this.metrics.executions.recentExecutions.length > 0) {
            console.log('│                                                 │');
            console.log('│ Recent Executions:                             │');
            this.metrics.executions.recentExecutions.forEach(exec => {
                console.log(`│ ��� ${exec.profit.padEnd(8)} ${exec.pair.padEnd(12)} ${exec.timestamp.padEnd(15)}│`);
            });
        }
        console.log('└' + '─'.repeat(49) + '┘');
        
        // Performance Section
        console.log('┌──────────────── PERFORMANCE ─────────────────┐');
        console.log(`│ Uptime:        ${this.metrics.performance.uptime.padEnd(30)}│`);
        console.log(`│ Scan Speed:    ${this.metrics.performance.scanSpeed.padEnd(30)}│`);
        console.log(`│ Execution:     ${this.metrics.performance.executionSpeed.padEnd(30)}│`);
        console.log(`│ Success Rate:  ${this.metrics.performance.successRate.padEnd(30)}│`);
        console.log('└' + '─'.repeat(49) + '┘');
        
        // System Section
        console.log('┌────────────────── SYSTEM ────────────────────┐');
        console.log(`│ Modules:       ${this.metrics.system.modulesActive}/${this.metrics.system.modulesTotal} active`.padEnd(40) + '│');
        console.log(`│ Last Update:   ${new Date(this.metrics.system.lastUpdate).toLocaleTimeString().padEnd(30)}│`);
        console.log('└' + '─'.repeat(48) + '┘');
    }

    // Start console dashboard
    startConsoleDashboard() {
        console.log('��� Starting console dashboard...');
        
        this.consoleInterval = setInterval(() => {
            this.renderToConsole();
        }, 3000); // Update every 3 seconds
    }

    // Get current metrics
    getMetrics() {
        return this.metrics;
    }

    // Stop dashboard
    stop() {
        this.isRunning = false;
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.consoleInterval) {
            clearInterval(this.consoleInterval);
        }
        console.log('��� Dashboard stopped');
    }
}

module.exports = BasicDashboard;
