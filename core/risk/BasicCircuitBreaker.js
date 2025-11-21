// AINEXUS - PHASE 1 MODULE 5: BASIC CIRCUIT BREAKER
// Risk Management - Emergency Stop & Protection

const EventEmitter = require('events');

class BasicCircuitBreaker extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.breakers = {
            drawdown: { triggered: false, threshold: config.drawdownThreshold || 0.10 }, // 10%
            consecutiveLosses: { triggered: false, threshold: config.consecutiveLosses || 3 },
            gasPrice: { triggered: false, threshold: config.gasPriceThreshold || 200 }, // 200 Gwei
            systemHealth: { triggered: false }
        };
        this.tradingEnabled = true;
        this.emergencyStop = false;
        this.metrics = {
            totalTrades: 0,
            profitableTrades: 0,
            totalProfit: 0,
            maxDrawdown: 0,
            currentDrawdown: 0
        };
    }

    // Initialize circuit breaker
    async initialize() {
        try {
            console.log('íº€ Initializing Basic Circuit Breaker...');
            
            // Start monitoring
            this.startMonitoring();
            
            this.emit('module_ready', { module: 'BasicCircuitBreaker', status: 'active' });
            return { success: true, breakers: Object.keys(this.breakers) };
        } catch (error) {
            this.emit('module_error', { module: 'BasicCircuitBreaker', error: error.message });
            throw error;
        }
    }

    // Start monitoring for risk conditions
    startMonitoring() {
        this.monitoringInterval = setInterval(() => {
            this.checkAllBreakers();
        }, this.config.checkInterval || 5000); // Check every 5 seconds
    }

    // Check all circuit breakers
    async checkAllBreakers() {
        if (this.emergencyStop) return;

        try {
            await this.checkDrawdownBreaker();
            await this.checkConsecutiveLossesBreaker();
            await this.checkGasPriceBreaker();
            await this.checkSystemHealthBreaker();
            
            this.emit('breakers_checked', {
                timestamp: Date.now(),
                triggered: this.getTriggeredBreakers(),
                tradingEnabled: this.tradingEnabled
            });
        } catch (error) {
            console.error('Circuit breaker check failed:', error);
        }
    }

    // Check drawdown breaker
    async checkDrawdownBreaker() {
        const drawdown = this.calculateCurrentDrawdown();
        this.metrics.currentDrawdown = drawdown;
        
        if (drawdown > this.breakers.drawdown.threshold) {
            await this.triggerBreaker('drawdown', 
                `Drawdown exceeded: ${(drawdown * 100).toFixed(1)}% > ${(this.breakers.drawdown.threshold * 100).toFixed(1)}%`
            );
        } else if (this.breakers.drawdown.triggered && drawdown < (this.breakers.drawdown.threshold * 0.5)) {
            await this.resetBreaker('drawdown');
        }
    }

    // Check consecutive losses breaker
    async checkConsecutiveLossesBreaker() {
        if (this.metrics.consecutiveLosses >= this.breakers.consecutiveLosses.threshold) {
            await this.triggerBreaker('consecutiveLosses',
                `${this.metrics.consecutiveLosses} consecutive losses detected`
            );
        }
    }

    // Check gas price breaker
    async checkGasPriceBreaker() {
        // In production, this would fetch current gas price
        const currentGasPrice = await this.getCurrentGasPrice();
        
        if (currentGasPrice > this.breakers.gasPrice.threshold) {
            await this.triggerBreaker('gasPrice',
                `Gas price too high: ${currentGasPrice} Gwei > ${this.breakers.gasPrice.threshold} Gwei`
            );
        } else if (this.breakers.gasPrice.triggered && currentGasPrice < (this.breakers.gasPrice.threshold * 0.7)) {
            await this.resetBreaker('gasPrice');
        }
    }

    // Check system health breaker
    async checkSystemHealthBreaker() {
        // This would check system metrics like memory, CPU, etc.
        const systemHealth = await this.checkSystemHealth();
        
        if (!systemHealth.healthy) {
            await this.triggerBreaker('systemHealth', systemHealth.message);
        }
    }

    // Trigger a circuit breaker
    async triggerBreaker(breakerName, reason) {
        if (this.breakers[breakerName].triggered) return; // Already triggered
        
        this.breakers[breakerName].triggered = true;
        this.tradingEnabled = false;
        
        console.log(`í´´ CIRCUIT BREAKER TRIGGERED: ${breakerName}`);
        console.log(`   Reason: ${reason}`);
        
        this.emit('breaker_triggered', {
            breaker: breakerName,
            reason: reason,
            timestamp: Date.now(),
            tradingEnabled: this.tradingEnabled
        });

        // Execute emergency actions
        await this.executeEmergencyActions(breakerName);
    }

    // Reset a circuit breaker
    async resetBreaker(breakerName) {
        this.breakers[breakerName].triggered = false;
        
        // Check if all breakers are reset
        const allReset = Object.values(this.breakers).every(breaker => !breaker.triggered);
        if (allReset) {
            this.tradingEnabled = true;
        }
        
        console.log(`í¿¢ CIRCUIT BREAKER RESET: ${breakerName}`);
        
        this.emit('breaker_reset', {
            breaker: breakerName,
            timestamp: Date.now(),
            tradingEnabled: this.tradingEnabled
        });
    }

    // Execute emergency actions when breaker triggers
    async executeEmergencyActions(breakerName) {
        switch (breakerName) {
            case 'drawdown':
                await this.handleDrawdownEmergency();
                break;
            case 'consecutiveLosses':
                await this.handleConsecutiveLossesEmergency();
                break;
            case 'gasPrice':
                await this.handleGasPriceEmergency();
                break;
            case 'systemHealth':
                await this.handleSystemHealthEmergency();
                break;
        }
    }

    // Handle drawdown emergency
    async handleDrawdownEmergency() {
        console.log('í´„ Executing drawdown emergency protocol...');
        
        // Stop all active trading
        this.emit('emergency_stop', {
            type: 'drawdown',
            message: 'Trading stopped due to excessive drawdown',
            timestamp: Date.now()
        });

        // Would interface with ArbitrageOrchestrator to stop scanning
        // and with FlashLoanExecutor to cancel pending executions
    }

    // Handle consecutive losses emergency
    async handleConsecutiveLossesEmergency() {
        console.log('í´„ Executing consecutive losses protocol...');
        
        this.emit('emergency_stop', {
            type: 'consecutive_losses',
            message: 'Trading stopped after consecutive losses',
            timestamp: Date.now()
        });
    }

    // Handle gas price emergency
    async handleGasPriceEmergency() {
        console.log('í´„ Executing gas price emergency protocol...');
        
        this.emit('emergency_stop', {
            type: 'gas_price',
            message: 'Trading paused due to high gas prices',
            timestamp: Date.now()
        });
    }

    // Handle system health emergency
    async handleSystemHealthEmergency() {
        console.log('í´„ Executing system health emergency protocol...');
        
        this.emit('emergency_stop', {
            type: 'system_health',
            message: 'Trading stopped due to system health issues',
            timestamp: Date.now()
        });
    }

    // Manual emergency stop
    async emergencyStop(reason = 'Manual emergency stop') {
        this.emergencyStop = true;
        this.tradingEnabled = false;
        
        console.log('í»‘ MANUAL EMERGENCY STOP ACTIVATED');
        console.log(`   Reason: ${reason}`);
        
        this.emit('manual_emergency_stop', {
            reason: reason,
            timestamp: Date.now(),
            tradingEnabled: this.tradingEnabled
        });
    }

    // Manual resume
    async resumeTrading() {
        if (!this.emergencyStop) {
            throw new Error('No emergency stop active');
        }
        
        this.emergencyStop = false;
        
        // Reset all breakers
        Object.keys(this.breakers).forEach(breaker => {
            this.breakers[breaker].triggered = false;
        });
        
        this.tradingEnabled = true;
        
        console.log('í¿¢ MANUAL RESUME ACTIVATED');
        
        this.emit('manual_resume', {
            timestamp: Date.now(),
            tradingEnabled: this.tradingEnabled
        });
    }

    // Record trade result for metrics
    recordTradeResult(profit, tradeDetails = {}) {
        this.metrics.totalTrades++;
        
        if (profit > 0) {
            this.metrics.profitableTrades++;
            this.metrics.consecutiveLosses = 0;
        } else {
            this.metrics.consecutiveLosses = (this.metrics.consecutiveLosses || 0) + 1;
        }
        
        this.metrics.totalProfit += profit;
        
        // Update max drawdown
        const currentDrawdown = this.calculateCurrentDrawdown();
        if (currentDrawdown > this.metrics.maxDrawdown) {
            this.metrics.maxDrawdown = currentDrawdown;
        }
        
        this.emit('trade_recorded', {
            profit: profit,
            totalTrades: this.metrics.totalTrades,
            profitableTrades: this.metrics.profitableTrades,
            consecutiveLosses: this.metrics.consecutiveLosses,
            totalProfit: this.metrics.totalProfit
        });
    }

    // Calculate current drawdown
    calculateCurrentDrawdown() {
        if (this.metrics.peakValue === undefined) {
            this.metrics.peakValue = this.metrics.totalProfit;
            return 0;
        }
        
        if (this.metrics.totalProfit > this.metrics.peakValue) {
            this.metrics.peakValue = this.metrics.totalProfit;
            return 0;
        }
        
        const drawdown = (this.metrics.peakValue - this.metrics.totalProfit) / Math.max(this.metrics.peakValue, 1);
        return Math.max(0, drawdown);
    }

    // Get current gas price (mock for Phase 1)
    async getCurrentGasPrice() {
        // In production, this would fetch from web3
        return Math.random() * 100 + 50; // 50-150 Gwei for simulation
    }

    // Check system health (mock for Phase 1)
    async checkSystemHealth() {
        return {
            healthy: Math.random() > 0.1, // 90% healthy
            message: Math.random() > 0.1 ? 'System healthy' : 'Simulated system issue'
        };
    }

    // Check if trading is allowed
    isTradingAllowed() {
        return this.tradingEnabled && !this.emergencyStop;
    }

    // Get triggered breakers
    getTriggeredBreakers() {
        return Object.entries(this.breakers)
            .filter(([_, breaker]) => breaker.triggered)
            .map(([name, _]) => name);
    }

    // Get circuit breaker status
    getStatus() {
        return {
            tradingEnabled: this.tradingEnabled,
            emergencyStop: this.emergencyStop,
            triggeredBreakers: this.getTriggeredBreakers(),
            metrics: this.metrics,
            breakers: this.breakers
        };
    }

    // Stop circuit breaker
    stop() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        console.log('í»‘ Circuit Breaker stopped');
    }
}

module.exports = BasicCircuitBreaker;
