// AINEXUS - PHASE 3 MODULE 40: INSTITUTIONAL RISK MANAGER
// Enterprise-Grade Risk Management & Circuit Breaker System

const EventEmitter = require('events');
const { Gauge, Counter, Histogram } = require('prom-client');

class InstitutionalRiskManager extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.riskModels = new Map();
        this.circuitBreakers = new Map();
        this.exposureLimits = new Map();
        this.stressTests = new Map();
        this.riskMetrics = new Map();
        this.incidentLog = [];
    }

    async initialize() {
        console.log('í»¡ï¸ Initializing Institutional Risk Manager...');
        
        await this.initializeRiskModels();
        await this.initializeCircuitBreakers();
        await this.initializeExposureLimits();
        await this.initializeStressTesting();
        await this.startRiskMonitoring();
        
        this.emit('risk_manager_ready', { 
            module: 'InstitutionalRiskManager', 
            status: 'active',
            models: this.riskModels.size,
            circuitBreakers: this.circuitBreakers.size
        });
        
        return { success: true, riskTier: 'INSTITUTIONAL_GRADE' };
    }

    async initializeRiskModels() {
        const riskModels = [
            {
                id: 'VAR_95_1D',
                name: 'Value at Risk (95%, 1 Day)',
                type: 'STATISTICAL_VAR',
                confidence: 0.95,
                timeHorizon: '1D',
                methodology: 'MONTE_CARLO',
                parameters: {
                    historicalPeriod: 252, // 1 year
                    simulations: 10000,
                    correlationMatrix: 'DYNAMIC'
                },
                updateFrequency: 3600000 // 1 hour
            },
            {
                id: 'VAR_99_1D',
                name: 'Value at Risk (99%, 1 Day)',
                type: 'STATISTICAL_VAR',
                confidence: 0.99,
                timeHorizon: '1D',
                methodology: 'PARAMETRIC',
                parameters: {
                    distribution: 'STUDENT_T',
                    degreesOfFreedom: 5,
                    volatilityModel: 'GARCH'
                },
                updateFrequency: 3600000
            },
            {
                id: 'EXPECTED_SHORTFALL',
                name: 'Expected Shortfall (97.5%)',
                type: 'CONDITIONAL_VAR',
                confidence: 0.975,
                timeHorizon: '1D',
                methodology: 'HISTORICAL_SIMULATION',
                parameters: {
                    lookbackPeriod: 1000,
                    weighting: 'EXPONENTIAL'
                },
                updateFrequency: 7200000 // 2 hours
            },
            {
                id: 'LIQUIDITY_RISK',
                name: 'Liquidity Risk Model',
                type: 'LIQUIDITY_ADJUSTED_VAR',
                confidence: 0.95,
                timeHorizon: '1D',
                methodology: 'BID_ASK_SPREAD',
                parameters: {
                    marketImpact: 0.001,
                    liquidationHorizon: 1,
                    stressMultiplier: 3
                },
                updateFrequency: 1800000 // 30 minutes
            },
            {
                id: 'CONCENTRATION_RISK',
                name: 'Concentration Risk Assessment',
                type: 'HERFINDDAHL_INDEX',
                methodology: 'PORTFOLIO_CONCENTRATION',
                parameters: {
                    maxSingleAsset: 0.2, // 20%
                    maxSector: 0.4, // 40%
                    correlationThreshold: 0.7
                },
                updateFrequency: 86400000 // 24 hours
            }
        ];

        riskModels.forEach(model => {
            this.riskModels.set(model.id, {
                ...model,
                active: true,
                lastCalculation: null,
                currentValue: 0,
                historicalValues: []
            });
        });
    }

    async initializeCircuitBreakers() {
        const breakers = [
            {
                id: 'DRAWDOWN_BREAKER',
                name: 'Maximum Drawdown Circuit Breaker',
                type: 'DRAWDOWN_LIMIT',
                threshold: 0.1, // 10%
                timeWindow: 86400000, // 24 hours
                action: 'SUSPEND_TRADING',
                cooldown: 3600000, // 1 hour
                autoReset: true,
                severity: 'CRITICAL'
            },
            {
                id: 'VAR_BREACH_BREAKER',
                name: 'VaR Breach Circuit Breaker',
                type: 'VAR_BREACH',
                threshold: 1.5, // 150% of VaR
                timeWindow: 3600000, // 1 hour
                action: 'REDUCE_EXPOSURE',
                cooldown: 1800000, // 30 minutes
                autoReset: false,
                severity: 'HIGH'
            },
            {
                id: 'LIQUIDITY_BREAKER',
                name: 'Liquidity Crisis Circuit Breaker',
                type: 'LIQUIDITY_SHORTFALL',
                threshold: 0.5, // 50% of required liquidity
                timeWindow: 300000, // 5 minutes
                action: 'HALT_WITHDRAWALS',
                cooldown: 900000, // 15 minutes
                autoReset: true,
                severity: 'HIGH'
            },
            {
                id: 'VOLATILITY_BREAKER',
                name: 'Extreme Volatility Circuit Breaker',
                type: 'VOLATILITY_SPIKE',
                threshold: 0.05, // 5% price movement in 5 minutes
                timeWindow: 300000,
                action: 'PAUSE_NEW_POSITIONS',
                cooldown: 600000, // 10 minutes
                autoReset: true,
                severity: 'MEDIUM'
            },
            {
                id: 'SYSTEMIC_BREAKER',
                name: 'Systemic Risk Circuit Breaker',
                type: 'MARKET_WIDE_STRESS',
                threshold: 0.8, // 80% correlation across assets
                timeWindow: 1800000, // 30 minutes
                action: 'REDUCE_LEVERAGE',
                cooldown: 7200000, // 2 hours
                autoReset: false,
                severity: 'CRITICAL'
            }
        ];

        breakers.forEach(breaker => {
            this.circuitBreakers.set(breaker.id, {
                ...breaker,
                active: true,
                triggered: false,
                lastTrigger: null,
                triggerCount: 0
            });
        });
    }

    async initializeExposureLimits() {
        const limits = [
            {
                id: 'SINGLE_ASSET_LIMIT',
                name: 'Single Asset Exposure Limit',
                type: 'ASSET_CONCENTRATION',
                asset: 'ALL',
                limit: 0.15, // 15% of portfolio
                timeFrame: 'REAL_TIME',
                enforcement: 'HARD_LIMIT'
            },
            {
                id: 'DAILY_LOSS_LIMIT',
                name: 'Daily Maximum Loss Limit',
                type: 'ABSOLUTE_LOSS',
                currency: 'USD',
                limit: 100000, // $100,000
                timeFrame: 'DAILY',
                enforcement: 'HARD_LIMIT'
            },
            {
                id: 'LEVERAGE_LIMIT',
                name: 'Maximum Leverage Ratio',
                type: 'LEVERAGE',
                ratio: 5, // 5x leverage
                timeFrame: 'REAL_TIME',
                enforcement: 'SOFT_LIMIT'
            },
            {
                id: 'COUNTERPARTY_LIMIT',
                name: 'Single Counterparty Exposure',
                type: 'COUNTERPARTY_RISK',
                limit: 0.1, // 10% of portfolio
                timeFrame: 'REAL_TIME',
                enforcement: 'HARD_LIMIT'
            },
            {
                id: 'SECTOR_LIMIT',
                name: 'Sector Concentration Limit',
                type: 'SECTOR_EXPOSURE',
                sector: 'DEFI',
                limit: 0.3, // 30% of portfolio
                timeFrame: 'REAL_TIME',
                enforcement: 'SOFT_LIMIT'
            }
        ];

        limits.forEach(limit => {
            this.exposureLimits.set(limit.id, {
                ...limit,
                active: true,
                currentExposure: 0,
                utilization: 0,
                lastBreach: null
            });
        });
    }

    async initializeStressTesting() {
        const stressScenarios = [
            {
                id: 'FLASH_CRASH_2020',
                name: 'Flash Crash Scenario (March 2020)',
                type: 'HISTORICAL_STRESS',
                parameters: {
                    priceDecline: 0.35, // 35% drop
                    volatilitySpike: 0.8, // 80% volatility
                    liquidityDryUp: 0.6, // 60% liquidity reduction
                    correlationBreakdown: true
                },
                frequency: 'WEEKLY',
                severity: 'EXTREME'
            },
            {
                id: 'LIQUIDITY_CRISIS',
                name: 'Liquidity Crisis Scenario',
                type: 'SYSTEMIC_STRESS',
                parameters: {
                    bidAskSpread: 0.05, // 5% spread
                    marketDepth: 0.2, // 20% of normal
                    fundingCosts: 0.15, // 15% funding rate
                    counterpartyDefaults: 0.1 // 10% default rate
                },
                frequency: 'MONTHLY',
                severity: 'HIGH'
            },
            {
                id: 'REGULATORY_SHOCK',
                name: 'Regulatory Crackdown Scenario',
                type: 'EVENT_DRIVEN_STRESS',
                parameters: {
                    tradingRestrictions: true,
                    assetSeizures: 0.05, // 5% of assets
                    legalCosts: 5000000, // $5M legal costs
                    reputationDamage: 0.3 // 30% AUM outflow
                },
                frequency: 'QUARTERLY',
                severity: 'MEDIUM'
            },
            {
                id: 'TECHNOLOGY_FAILURE',
                name: 'Technology Infrastructure Failure',
                type: 'OPERATIONAL_STRESS',
                parameters: {
                    systemDowntime: 7200, // 2 hours
                    dataLoss: 0.01, // 1% data loss
                    recoveryTime: 14400, // 4 hours
                    customerImpact: 0.8 // 80% of customers affected
                },
                frequency: 'QUARTERLY',
                severity: 'HIGH'
            }
        ];

        stressScenarios.forEach(scenario => {
            this.stressTests.set(scenario.id, {
                ...scenario,
                active: true,
                lastRun: null,
                results: null,
                pass: true
            });
        });
    }

    async startRiskMonitoring() {
        // Start risk calculation intervals
        this.riskModels.forEach((model, modelId) => {
            setInterval(() => this.calculateRiskMetric(modelId), model.updateFrequency);
        });

        // Start circuit breaker monitoring
        setInterval(() => this.monitorCircuitBreakers(), 30000); // Every 30 seconds

        // Start exposure monitoring
        setInterval(() => this.monitorExposureLimits(), 60000); // Every minute

        // Start stress testing scheduler
        setInterval(() => this.runScheduledStressTests(), 3600000); // Every hour

        // Start risk reporting
        setInterval(() => this.generateRiskReport(), 300000); // Every 5 minutes
    }

    async calculateRiskMetric(modelId) {
        const model = this.riskModels.get(modelId);
        if (!model || !model.active) return;

        try {
            const riskValue = await this.executeRiskCalculation(model);
            
            model.currentValue = riskValue;
            model.lastCalculation = Date.now();
            model.historicalValues.push({
                timestamp: Date.now(),
                value: riskValue
            });

            // Keep only last 1000 values
            if (model.historicalValues.length > 1000) {
                model.historicalValues.shift();
            }

            this.emit('risk_metric_updated', {
                model: modelId,
                value: riskValue,
                timestamp: Date.now()
            });

            // Check for circuit breaker conditions
            await this.checkRiskBasedBreakers(modelId, riskValue);

        } catch (error) {
            console.error(`Error calculating risk metric ${modelId}:`, error);
            this.recordIncident('RISK_CALCULATION_FAILURE', {
                model: modelId,
                error: error.message
            });
        }
    }

    async executeRiskCalculation(model) {
        // Simulate complex risk calculations
        switch (model.type) {
            case 'STATISTICAL_VAR':
                return await this.calculateStatisticalVaR(model);
            case 'CONDITIONAL_VAR':
                return await this.calculateExpectedShortfall(model);
            case 'LIQUIDITY_ADJUSTED_VAR':
                return await this.calculateLiquidityVaR(model);
            case 'HERFINDDAHL_INDEX':
                return await this.calculateConcentrationRisk(model);
            default:
                return Math.random() * 1000000; // Random value for simulation
        }
    }

    async calculateStatisticalVaR(model) {
        // Simulate VaR calculation
        const baseVaR = 50000 + (Math.random() * 50000); // $50K-100K
        const stressMultiplier = 1 + (Math.random() * 0.5); // 1-1.5x
        
        return baseVaR * stressMultiplier;
    }

    async calculateExpectedShortfall(model) {
        // Simulate Expected Shortfall calculation
        const baseES = 75000 + (Math.random() * 75000); // $75K-150K
        const stressMultiplier = 1.2 + (Math.random() * 0.3); // 1.2-1.5x
        
        return baseES * stressMultiplier;
    }

    async calculateLiquidityVaR(model) {
        // Simulate Liquidity-adjusted VaR
        const baseVaR = 60000 + (Math.random() * 40000); // $60K-100K
        const liquidityAdjustment = 1.3 + (Math.random() * 0.4); // 1.3-1.7x
        
        return baseVaR * liquidityAdjustment;
    }

    async calculateConcentrationRisk(model) {
        // Simulate concentration risk (Herfindahl Index)
        return Math.random(); // 0-1 concentration index
    }

    async monitorCircuitBreakers() {
        for (const [breakerId, breaker] of this.circuitBreakers) {
            if (!breaker.active || breaker.triggered) continue;

            const shouldTrigger = await this.evaluateBreakerCondition(breaker);
            
            if (shouldTrigger) {
                await this.triggerCircuitBreaker(breakerId);
            }
        }
    }

    async evaluateBreakerCondition(breaker) {
        // Simulate condition evaluation based on breaker type
        switch (breaker.type) {
            case 'DRAWDOWN_LIMIT':
                const drawdown = await this.calculateCurrentDrawdown();
                return drawdown >= breaker.threshold;
                
            case 'VAR_BREACH':
                const currentLoss = await this.getCurrentLoss();
                const varLimit = this.riskModels.get('VAR_95_1D')?.currentValue || 0;
                return currentLoss > (varLimit * breaker.threshold);
                
            case 'LIQUIDITY_SHORTFALL':
                const liquidityRatio = await this.calculateLiquidityRatio();
                return liquidityRatio <= breaker.threshold;
                
            case 'VOLATILITY_SPIKE':
                const volatility = await this.calculateRecentVolatility();
                return volatility >= breaker.threshold;
                
            case 'MARKET_WIDE_STRESS':
                const correlation = await this.calculateMarketCorrelation();
                return correlation >= breaker.threshold;
                
            default:
                return false;
        }
    }

    async triggerCircuitBreaker(breakerId) {
        const breaker = this.circuitBreakers.get(breakerId);
        
        breaker.triggered = true;
        breaker.lastTrigger = Date.now();
        breaker.triggerCount++;

        const incident = {
            id: this.generateIncidentId(),
            breakerId: breakerId,
            name: breaker.name,
            severity: breaker.severity,
            action: breaker.action,
            timestamp: Date.now(),
            autoReset: breaker.autoReset
        };

        // Execute breaker action
        await this.executeBreakerAction(breaker.action);

        // Record incident
        this.recordIncident('CIRCUIT_BREAKER_TRIGGERED', incident);

        // Emit event
        this.emit('circuit_breaker_triggered', incident);

        console.log(`í´´ Circuit Breaker Triggered: ${breaker.name} - Action: ${breaker.action}`);

        // Schedule auto-reset if configured
        if (breaker.autoReset) {
            setTimeout(() => this.resetCircuitBreaker(breakerId), breaker.cooldown);
        }
    }

    async executeBreakerAction(action) {
        // Execute the prescribed action for the circuit breaker
        switch (action) {
            case 'SUSPEND_TRADING':
                await this.suspendAllTrading();
                break;
            case 'REDUCE_EXPOSURE':
                await this.reducePortfolioExposure(0.5); // Reduce by 50%
                break;
            case 'HALT_WITHDRAWALS':
                await this.haltCustomerWithdrawals();
                break;
            case 'PAUSE_NEW_POSITIONS':
                await this.pauseNewPositions();
                break;
            case 'REDUCE_LEVERAGE':
                await this.reduceLeverage(0.3); // Reduce by 30%
                break;
        }
    }

    async resetCircuitBreaker(breakerId) {
        const breaker = this.circuitBreakers.get(breakerId);
        if (breaker && breaker.triggered) {
            breaker.triggered = false;
            
            this.emit('circuit_breaker_reset', {
                breakerId: breakerId,
                name: breaker.name,
                timestamp: Date.now()
            });

            console.log(`í¿¢ Circuit Breaker Reset: ${breaker.name}`);
        }
    }

    async monitorExposureLimits() {
        for (const [limitId, limit] of this.exposureLimits) {
            if (!limit.active) continue;

            const currentExposure = await this.calculateCurrentExposure(limit);
            const utilization = currentExposure / limit.limit;

            limit.currentExposure = currentExposure;
            limit.utilization = utilization;

            // Check for limit breaches
            if (utilization >= 0.9) { // 90% of limit
                this.emit('exposure_warning', {
                    limitId: limitId,
                    name: limit.name,
                    utilization: utilization,
                    currentExposure: currentExposure,
                    limit: limit.limit,
                    timestamp: Date.now()
                });
            }

            if (utilization >= 1.0) { // Limit breached
                await this.handleLimitBreach(limitId);
            }
        }
    }

    async calculateCurrentExposure(limit) {
        // Simulate exposure calculation based on limit type
        switch (limit.type) {
            case 'ASSET_CONCENTRATION':
                return Math.random() * limit.limit * 1.2; // Random exposure
            case 'ABSOLUTE_LOSS':
                return Math.random() * limit.limit * 1.1;
            case 'LEVERAGE':
                return Math.random() * limit.ratio * 1.3;
            case 'COUNTERPARTY_RISK':
                return Math.random() * limit.limit * 1.15;
            case 'SECTOR_EXPOSURE':
                return Math.random() * limit.limit * 1.25;
            default:
                return 0;
        }
    }

    async handleLimitBreach(limitId) {
        const limit = this.exposureLimits.get(limitId);
        
        limit.lastBreach = Date.now();

        const breachEvent = {
            limitId: limitId,
            name: limit.name,
            exposure: limit.currentExposure,
            limit: limit.limit,
            utilization: limit.utilization,
            enforcement: limit.enforcement,
            timestamp: Date.now()
        };

        this.recordIncident('EXPOSURE_LIMIT_BREACH', breachEvent);
        this.emit('exposure_limit_breached', breachEvent);

        // Take enforcement action
        if (limit.enforcement === 'HARD_LIMIT') {
            await this.enforceHardLimit(limit);
        } else {
            await this.enforceSoftLimit(limit);
        }
    }

    async enforceHardLimit(limit) {
        // Immediate action for hard limits
        console.log(`í» Enforcing Hard Limit: ${limit.name}`);
        
        switch (limit.type) {
            case 'ASSET_CONCENTRATION':
                await this.reduceAssetExposure(limit.asset, 0.1); // Reduce by 10%
                break;
            case 'ABSOLUTE_LOSS':
                await this.suspendLossMakingStrategies();
                break;
            case 'LEVERAGE':
                await this.forceLeverageReduction(0.2); // Reduce by 20%
                break;
        }
    }

    async enforceSoftLimit(limit) {
        // Warning and gradual action for soft limits
        console.log(`â ï¸ Soft Limit Warning: ${limit.name}`);
        
        // Notify risk team and schedule review
        this.emit('soft_limit_warning', {
            limit: limit,
            timestamp: Date.now()
        });
    }

    async runScheduledStressTests() {
        const now = new Date();
        
        for (const [scenarioId, scenario] of this.stressTests) {
            if (!scenario.active) continue;

            const shouldRun = this.shouldRunStressTest(scenario, now);
            if (shouldRun) {
                await this.executeStressTest(scenarioId);
            }
        }
    }

    shouldRunStressTest(scenario, currentTime) {
        if (!scenario.lastRun) return true;

        const timeSinceLastRun = currentTime - scenario.lastRun;
        
        switch (scenario.frequency) {
            case 'WEEKLY':
                return timeSinceLastRun >= 7 * 24 * 3600000; // 7 days
            case 'MONTHLY':
                return timeSinceLastRun >= 30 * 24 * 3600000; // 30 days
            case 'QUARTERLY':
                return timeSinceLastRun >= 90 * 24 * 3600000; // 90 days
            default:
                return false;
        }
    }

    async executeStressTest(scenarioId) {
        const scenario = this.stressTests.get(scenarioId);
        
        console.log(`í¼ Running Stress Test: ${scenario.name}`);
        
        try {
            const results = await this.simulateStressScenario(scenario);
            scenario.lastRun = Date.now();
            scenario.results = results;
            scenario.pass = results.overallImpact < 0.5; // Example pass condition

            this.emit('stress_test_completed', {
                scenario: scenarioId,
                name: scenario.name,
                results: results,
                pass: scenario.pass,
                timestamp: Date.now()
            });

            if (!scenario.pass) {
                this.recordIncident('STRESS_TEST_FAILURE', {
                    scenario: scenarioId,
                    results: results
                });
            }

        } catch (error) {
            console.error(`Stress test failed: ${scenarioId}`, error);
            this.recordIncident('STRESS_TEST_ERROR', {
                scenario: scenarioId,
                error: error.message
            });
        }
    }

    async simulateStressScenario(scenario) {
        // Simulate stress test results
        return {
            overallImpact: Math.random(), // 0-1 impact scale
            varImpact: Math.random() * 2, // 0-2x VaR increase
            liquidityImpact: Math.random(),
            capitalAdequacy: 0.1 + (Math.random() * 0.9), // 10-100%
            recoveryTime: Math.floor(Math.random() * 72) + 1, // 1-72 hours
            scenarioParameters: scenario.parameters
        };
    }

    async generateRiskReport() {
        const report = {
            timestamp: Date.now(),
            riskMetrics: {},
            circuitBreakerStatus: {},
            exposureSummary: {},
            stressTestResults: {},
            recommendations: await this.generateRiskRecommendations()
        };

        // Collect risk metrics
        this.riskModels.forEach((model, modelId) => {
            report.riskMetrics[modelId] = {
                value: model.currentValue,
                lastUpdate: model.lastCalculation,
                trend: this.calculateMetricTrend(model.historicalValues)
            };
        });

        // Collect circuit breaker status
        this.circuitBreakers.forEach((breaker, breakerId) => {
            report.circuitBreakerStatus[breakerId] = {
                triggered: breaker.triggered,
                lastTrigger: breaker.lastTrigger,
                triggerCount: breaker.triggerCount
            };
        });

        // Collect exposure summary
        this.exposureLimits.forEach((limit, limitId) => {
            report.exposureSummary[limitId] = {
                utilization: limit.utilization,
                currentExposure: limit.currentExposure,
                limit: limit.limit
            };
        });

        this.emit('risk_report_generated', report);
        return report;
    }

    // Simulation methods for monitoring
    async calculateCurrentDrawdown() {
        return Math.random() * 0.15; // 0-15% drawdown
    }

    async getCurrentLoss() {
        return Math.random() * 50000; // 0-50k loss
    }

    async calculateLiquidityRatio() {
        return 0.3 + (Math.random() * 0.7); // 30-100% liquidity ratio
    }

    async calculateRecentVolatility() {
        return Math.random() * 0.1; // 0-10% volatility
    }

    async calculateMarketCorrelation() {
        return Math.random(); // 0-1 correlation
    }

    // Action simulation methods
    async suspendAllTrading() {
        console.log('â¸ï¸ All trading suspended');
    }

    async reducePortfolioExposure(percentage) {
        console.log(`í³ Reducing portfolio exposure by ${percentage * 100}%`);
    }

    async haltCustomerWithdrawals() {
        console.log('íº« Customer withdrawals halted');
    }

    async pauseNewPositions() {
        console.log('â¸ï¸ New positions paused');
    }

    async reduceLeverage(percentage) {
        console.log(`í³ Reducing leverage by ${percentage * 100}%`);
    }

    async reduceAssetExposure(asset, percentage) {
        console.log(`í³ Reducing ${asset} exposure by ${percentage * 100}%`);
    }

    async suspendLossMakingStrategies() {
        console.log('â¸ï¸ Loss-making strategies suspended');
    }

    async forceLeverageReduction(percentage) {
        console.log(`í³ Forcing leverage reduction by ${percentage * 100}%`);
    }

    // Utility Methods
    calculateMetricTrend(historicalValues) {
        if (historicalValues.length < 2) return 'STABLE';
        
        const recent = historicalValues.slice(-2);
        const change = recent[1].value - recent[0].value;
        const percentageChange = change / recent[0].value;

        if (percentageChange > 0.05) return 'INCREASING';
        if (percentageChange < -0.05) return 'DECREASING';
        return 'STABLE';
    }

    generateIncidentId() {
        return `INCIDENT_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
    }

    recordIncident(type, details) {
        const incident = {
            id: this.generateIncidentId(),
            type: type,
            details: details,
            timestamp: Date.now(),
            resolved: false
        };

        this.incidentLog.push(incident);

        // Keep only last 1000 incidents
        if (this.incidentLog.length > 1000) {
            this.incidentLog.shift();
        }

        this.emit('incident_recorded', incident);
    }

    async generateRiskRecommendations() {
        const recommendations = [];

        // Example recommendations based on current state
        if (await this.calculateCurrentDrawdown() > 0.05) {
            recommendations.push({
                type: 'EXPOSURE_REDUCTION',
                priority: 'HIGH',
                message: 'Consider reducing portfolio exposure due to recent drawdown',
                action: 'REDUCE_LEVERAGE'
            });
        }

        const liquidityRatio = await this.calculateLiquidityRatio();
        if (liquidityRatio < 0.5) {
            recommendations.push({
                type: 'LIQUIDITY_MANAGEMENT',
                priority: 'MEDIUM',
                message: 'Increase liquidity reserves to maintain operational flexibility',
                action: 'INCREASE_RESERVES'
            });
        }

        return recommendations;
    }

    getRiskStatus() {
        return {
            activeModels: Array.from(this.riskModels.values()).filter(m => m.active).length,
            triggeredBreakers: Array.from(this.circuitBreakers.values()).filter(b => b.triggered).length,
            limitUtilizations: Array.from(this.exposureLimits.values()).map(l => l.utilization),
            recentIncidents: this.incidentLog.slice(-10), // Last 10 incidents
            overallRiskLevel: this.calculateOverallRiskLevel()
        };
    }

    calculateOverallRiskLevel() {
        // Simple overall risk level calculation
        let riskScore = 0;
        
        // Add risk from triggered breakers
        const triggeredBreakers = Array.from(this.circuitBreakers.values())
            .filter(b => b.triggered).length;
        riskScore += triggeredBreakers * 25;

        // Add risk from high exposure utilization
        const highUtilization = Array.from(this.exposureLimits.values())
            .filter(l => l.utilization > 0.9).length;
        riskScore += highUtilization * 15;

        // Add risk from recent incidents
        const recentIncidents = this.incidentLog
            .filter(i => Date.now() - i.timestamp < 3600000).length; // Last hour
        riskScore += recentIncidents * 10;

        return Math.min(riskScore, 100);
    }

    stop() {
        console.log('í» Institutional Risk Manager stopped');
    }
}

module.exports = InstitutionalRiskManager;
