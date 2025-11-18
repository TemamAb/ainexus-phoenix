/**
 * AI-NEXUS v5.0 - CAPITAL REUSE OPTIMIZER MODULE
 * Advanced Capital Recycling and Efficiency Optimization
 * Dynamic capital deployment across multiple strategies with reuse optimization
 */

const { EventEmitter } = require('events');
const { v4: uuidv4 } = require('uuid');

// Enum for Capital Allocation States
const CapitalState = {
    IDLE: 'idle',
    DEPLOYED: 'deployed',
    IN_TRANSIT: 'in_transit',
    RESERVED: 'reserved',
    RISK_BUFFER: 'risk_buffer'
};

// Enum for Reuse Strategies
const ReuseStrategy = {
    AGGRESSIVE_RECYCLING: 'aggressive_recycling',
    CONSERVATIVE_ROTATION: 'conservative_rotation',
    OPPORTUNISTIC_REUSE: 'opportunistic_reuse',
    STRATEGY_SPECIFIC: 'strategy_specific'
};

// Enum for Efficiency Metrics
const EfficiencyMetric = {
    REUSE_RATE: 'reuse_rate',
    IDLE_TIME_RATIO: 'idle_time_ratio',
    TRANSACTION_COST_RATIO: 'transaction_cost_ratio',
    RETURN_ON_DEPLOYED_CAPITAL: 'return_on_deployed_capital',
    VELOCITY_SCORE: 'velocity_score'
};

/**
 * Capital Allocation Record
 */
class CapitalAllocation {
    constructor({
        allocationId,
        strategyId,
        amount,
        timestamp,
        expectedDuration,
        state = CapitalState.DEPLOYED,
        metadata = {}
    }) {
        this.allocationId = allocationId || uuidv4();
        this.strategyId = strategyId;
        this.amount = amount;
        this.timestamp = timestamp || new Date();
        this.expectedDuration = expectedDuration;
        this.state = state;
        this.metadata = metadata;
        this.actualReturns = 0;
        this.utilizationScore = 1.0;
    }
}

/**
 * Capital Movement Record
 */
class CapitalMovement {
    constructor({
        movementId,
        fromStrategyId,
        toStrategyId,
        amount,
        timestamp,
        transactionCost,
        latency,
        metadata = {}
    }) {
        this.movementId = movementId || uuidv4();
        this.fromStrategyId = fromStrategyId;
        this.toStrategyId = toStrategyId;
        this.amount = amount;
        this.timestamp = timestamp || new Date();
        this.transactionCost = transactionCost;
        this.latency = latency;
        this.metadata = metadata;
    }
}

/**
 * Efficiency Snapshot
 */
class EfficiencySnapshot {
    constructor({
        snapshotId,
        timestamp,
        totalCapital,
        deployedCapital,
        efficiencyMetrics,
        reuseOpportunities,
        metadata = {}
    }) {
        this.snapshotId = snapshotId || uuidv4();
        this.timestamp = timestamp || new Date();
        this.totalCapital = totalCapital;
        this.deployedCapital = deployedCapital;
        this.efficiencyMetrics = efficiencyMetrics;
        this.reuseOpportunities = reuseOpportunities;
        this.metadata = metadata;
    }
}

/**
 * Advanced Capital Reuse Optimizer
 */
class ReuseOptimizer extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.optimizerId = options.optimizerId || `reuse_optimizer_${Date.now()}`;
        
        // Capital tracking
        this.capitalAllocations = new Map();
        this.capitalMovements = [];
        this.efficiencySnapshots = [];
        
        // Optimization parameters
        this.optimizationParams = {
            minReuseThreshold: options.minReuseThreshold || 0.1,      // 10% minimum improvement
            maxTransactionCost: options.maxTransactionCost || 0.002,  // 0.2% max cost
            targetReuseRate: options.targetReuseRate || 0.7,          // 70% target reuse
            maxMovementLatency: options.maxMovementLatency || 300,    // 5 minutes max
            snapshotInterval: options.snapshotInterval || 60000,      // 1 minute
            lookbackWindow: options.lookbackWindow || 24 * 60 * 60 * 1000 // 24 hours
        };
        
        // Strategy configurations
        this.strategyConfigs = new Map();
        
        // Performance tracking
        this.performanceMetrics = {
            totalMovements: 0,
            successfulReuses: 0,
            totalSavings: 0,
            avgEfficiencyGain: 0,
            reuseRate: 0
        };
        
        // Initialize optimization engines
        this.initializeOptimizationEngines();
        
        // Start periodic optimization
        this.startPeriodicOptimization();
        
        console.log(`Capital Reuse Optimizer initialized: ${this.optimizerId}`);
    }
    
    /**
     * Initialize optimization engines and algorithms
     */
    initializeOptimizationEngines() {
        this.optimizationEngines = {
            // Linear programming for optimal allocation
            linearProgramming: new LinearProgrammingEngine(),
            
            // Machine learning for pattern recognition
            patternRecognizer: new PatternRecognitionEngine(),
            
            // Cost-benefit analyzer
            costBenefitAnalyzer: new CostBenefitAnalyzer(),
            
            // Risk-adjusted return calculator
            riskReturnCalculator: new RiskReturnCalculator()
        };
        
        this.reuseStrategies = {
            [ReuseStrategy.AGGRESSIVE_RECYCLING]: {
                description: 'Maximize capital velocity with frequent recycling',
                parameters: {
                    minHoldingPeriod: 300000, // 5 minutes
                    targetReuseRate: 0.8,
                    riskTolerance: 'high'
                },
                optimize: this.aggressiveRecycling.bind(this)
            },
            
            [ReuseStrategy.CONSERVATIVE_ROTATION]: {
                description: 'Conservative rotation with focus on stability',
                parameters: {
                    minHoldingPeriod: 3600000, // 1 hour
                    targetReuseRate: 0.5,
                    riskTolerance: 'low'
                },
                optimize: this.conservativeRotation.bind(this)
            },
            
            [ReuseStrategy.OPPORTUNISTIC_REUSE]: {
                description: 'Opportunistic reuse based on market conditions',
                parameters: {
                    minHoldingPeriod: 900000, // 15 minutes
                    targetReuseRate: 0.6,
                    riskTolerance: 'medium'
                },
                optimize: this.opportunisticReuse.bind(this)
            },
            
            [ReuseStrategy.STRATEGY_SPECIFIC]: {
                description: 'Strategy-specific optimization',
                parameters: {
                    minHoldingPeriod: 600000, // 10 minutes
                    targetReuseRate: 0.7,
                    riskTolerance: 'medium'
                },
                optimize: this.strategySpecificOptimization.bind(this)
            }
        };
        
        this.activeStrategy = ReuseStrategy.OPPORTUNISTIC_REUSE;
    }
    
    /**
     * Register a trading strategy with the optimizer
     */
    registerStrategy(strategyConfig) {
        const { strategyId, capitalRequirements, expectedReturns, riskProfile, metadata = {} } = strategyConfig;
        
        this.strategyConfigs.set(strategyId, {
            strategyId,
            capitalRequirements,
            expectedReturns,
            riskProfile,
            metadata,
            performanceHistory: [],
            currentAllocation: 0,
            utilizationScore: 0
        });
        
        console.log(`Strategy registered: ${strategyId}`);
        this.emit('strategyRegistered', { strategyId, config: strategyConfig });
    }
    
    /**
     * Allocate capital to a strategy
     */
    allocateCapital({ strategyId, amount, expectedDuration, metadata = {} }) {
        if (!this.strategyConfigs.has(strategyId)) {
            throw new Error(`Strategy not registered: ${strategyId}`);
        }
        
        const allocation = new CapitalAllocation({
            strategyId,
            amount,
            expectedDuration,
            metadata
        });
        
        this.capitalAllocations.set(allocation.allocationId, allocation);
        
        // Update strategy allocation
        const strategy = this.strategyConfigs.get(strategyId);
        strategy.currentAllocation += amount;
        
        console.log(`Capital allocated: ${amount} to ${strategyId}`);
        this.emit('capitalAllocated', { allocation });
        
        return allocation.allocationId;
    }
    
    /**
     * Deallocate capital from a strategy
     */
    deallocateCapital(allocationId, returns = 0) {
        const allocation = this.capitalAllocations.get(allocationId);
        if (!allocation) {
            throw new Error(`Allocation not found: ${allocationId}`);
        }
        
        allocation.state = CapitalState.IDLE;
        allocation.actualReturns = returns;
        
        // Update strategy allocation
        const strategy = this.strategyConfigs.get(allocation.strategyId);
        strategy.currentAllocation -= allocation.amount;
        
        // Record performance
        strategy.performanceHistory.push({
            timestamp: new Date(),
            allocationId,
            amount: allocation.amount,
            returns,
            duration: Date.now() - allocation.timestamp.getTime()
        });
        
        console.log(`Capital deallocated: ${allocation.amount} from ${allocation.strategyId}`);
        this.emit('capitalDeallocated', { allocation, returns });
        
        return allocation;
    }
    
    /**
     * Optimize capital reuse across strategies
     */
    async optimizeCapitalReuse() {
        const reuseOpportunities = await this.identifyReuseOpportunities();
        
        if (reuseOpportunities.length === 0) {
            console.log('No capital reuse opportunities identified');
            return [];
        }
        
        const optimizedMovements = await this.optimizeMovementPlan(reuseOpportunities);
        const executedMovements = [];
        
        for (const movement of optimizedMovements) {
            try {
                const result = await this.executeCapitalMovement(movement);
                executedMovements.push(result);
                
                this.performanceMetrics.successfulReuses++;
                this.performanceMetrics.totalSavings += movement.expectedSavings || 0;
                
            } catch (error) {
                console.error(`Failed to execute capital movement: ${error.message}`);
                this.emit('movementFailed', { movement, error });
            }
        }
        
        this.performanceMetrics.totalMovements += executedMovements.length;
        this.updatePerformanceMetrics();
        
        console.log(`Capital reuse optimization completed: ${executedMovements.length} movements executed`);
        this.emit('optimizationCompleted', { executedMovements });
        
        return executedMovements;
    }
    
    /**
     * Identify capital reuse opportunities
     */
    async identifyReuseOpportunities() {
        const opportunities = [];
        const now = new Date();
        
        // Analyze idle capital
        const idleCapital = this.calculateIdleCapital();
        if (idleCapital > 0) {
            opportunities.push(...await this.identifyIdleCapitalOpportunities(idleCapital));
        }
        
        // Analyze underutilized strategies
        opportunities.push(...await this.identifyUnderutilizedOpportunities());
        
        // Analyze strategy performance for reallocation
        opportunities.push(...await this.identifyPerformanceBasedOpportunities());
        
        // Filter opportunities by feasibility
        const feasibleOpportunities = opportunities.filter(opp => 
            this.isOpportunityFeasible(opp) && 
            this.calculateEfficiencyGain(opp) >= this.optimizationParams.minReuseThreshold
        );
        
        return feasibleOpportunities;
    }
    
    /**
     * Identify opportunities for idle capital
     */
    async identifyIdleCapitalOpportunities(idleCapital) {
        const opportunities = [];
        const strategies = Array.from(this.strategyConfigs.values());
        
        for (const strategy of strategies) {
            const requiredCapital = strategy.capitalRequirements.min || 0;
            const availableCapacity = strategy.capitalRequirements.max - strategy.currentAllocation;
            
            if (availableCapacity > 0 && idleCapital >= requiredCapital) {
                const allocationAmount = Math.min(idleCapital, availableCapacity, requiredCapital);
                
                opportunities.push({
                    type: 'idle_deployment',
                    fromStrategyId: null,
                    toStrategyId: strategy.strategyId,
                    amount: allocationAmount,
                    expectedEfficiencyGain: await this.calculateDeploymentEfficiency(strategy, allocationAmount),
                    priority: strategy.expectedReturns * allocationAmount,
                    metadata: {
                        reason: 'idle_capital_deployment',
                        strategyExpectedReturns: strategy.expectedReturns
                    }
                });
            }
        }
        
        return opportunities;
    }
    
    /**
     * Identify underutilized strategy opportunities
     */
    async identifyUnderutilizedOpportunities() {
        const opportunities = [];
        const strategies = Array.from(this.strategyConfigs.values());
        
        // Find over-allocated and under-performing strategies
        const performanceMetrics = await this.calculateStrategyPerformance();
        
        for (const [strategyId, metrics] of performanceMetrics) {
            const strategy = this.strategyConfigs.get(strategyId);
            
            if (metrics.utilizationScore < 0.5 && metrics.returnOnCapital < strategy.expectedReturns * 0.7) {
                // Strategy is underutilized and under-performing
                const reallocatableAmount = strategy.currentAllocation * 0.5; // Consider reallocating 50%
                
                // Find better opportunities
                const betterStrategies = strategies.filter(s => 
                    s.expectedReturns > strategy.expectedReturns * 1.2 && 
                    s.currentAllocation < s.capitalRequirements.max
                );
                
                for (const betterStrategy of betterStrategies) {
                    const allocationAmount = Math.min(
                        reallocatableAmount,
                        betterStrategy.capitalRequirements.max - betterStrategy.currentAllocation
                    );
                    
                    if (allocationAmount > 0) {
                        opportunities.push({
                            type: 'performance_reallocation',
                            fromStrategyId: strategyId,
                            toStrategyId: betterStrategy.strategyId,
                            amount: allocationAmount,
                            expectedEfficiencyGain: await this.calculateReallocationEfficiency(
                                strategy, betterStrategy, allocationAmount
                            ),
                            priority: (betterStrategy.expectedReturns - strategy.expectedReturns) * allocationAmount,
                            metadata: {
                                reason: 'performance_optimization',
                                fromReturns: strategy.expectedReturns,
                                toReturns: betterStrategy.expectedReturns
                            }
                        });
                    }
                }
            }
        }
        
        return opportunities;
    }
    
    /**
     * Calculate strategy performance metrics
     */
    async calculateStrategyPerformance() {
        const performance = new Map();
        
        for (const [strategyId, strategy] of this.strategyConfigs) {
            const utilization = strategy.currentAllocation / strategy.capitalRequirements.max;
            const returns = this.calculateStrategyReturns(strategyId);
            const efficiency = await this.calculateStrategyEfficiency(strategyId);
            
            performance.set(strategyId, {
                utilizationScore: utilization,
                returnOnCapital: returns,
                efficiencyScore: efficiency,
                overallScore: (utilization + returns + efficiency) / 3
            });
        }
        
        return performance;
    }
    
    /**
     * Calculate returns for a strategy
     */
    calculateStrategyReturns(strategyId) {
        const strategy = this.strategyConfigs.get(strategyId);
        if (!strategy || strategy.performanceHistory.length === 0) {
            return strategy?.expectedReturns || 0;
        }
        
        const recentPerformance = strategy.performanceHistory.slice(-10); // Last 10 allocations
        const totalReturns = recentPerformance.reduce((sum, perf) => sum + perf.returns, 0);
        const totalAmount = recentPerformance.reduce((sum, perf) => sum + perf.amount, 0);
        
        return totalAmount > 0 ? totalReturns / totalAmount : strategy.expectedReturns;
    }
    
    /**
     * Calculate strategy efficiency
     */
    async calculateStrategyEfficiency(strategyId) {
        const strategy = this.strategyConfigs.get(strategyId);
        const allocations = Array.from(this.capitalAllocations.values())
            .filter(allocation => allocation.strategyId === strategyId);
        
        if (allocations.length === 0) {
            return 0.5; // Default efficiency
        }
        
        // Calculate utilization efficiency
        const targetAllocation = strategy.capitalRequirements.optimal || strategy.capitalRequirements.max;
        const allocationEfficiency = 1 - Math.abs(strategy.currentAllocation - targetAllocation) / targetAllocation;
        
        // Calculate time efficiency
        const now = new Date();
        const timeEfficiencies = allocations.map(allocation => {
            const expectedEnd = new Date(allocation.timestamp.getTime() + allocation.expectedDuration);
            const actualDuration = now - allocation.timestamp;
            const expectedDuration = allocation.expectedDuration;
            
            return 1 - Math.abs(actualDuration - expectedDuration) / expectedDuration;
        });
        
        const avgTimeEfficiency = timeEfficiencies.reduce((a, b) => a + b, 0) / timeEfficiencies.length;
        
        return (allocationEfficiency + avgTimeEfficiency) / 2;
    }
    
    /**
     * Optimize movement plan using linear programming
     */
    async optimizeMovementPlan(opportunities) {
        const strategy = this.reuseStrategies[this.activeStrategy];
        return await strategy.optimize(opportunities);
    }
    
    /**
     * Aggressive recycling optimization
     */
    async aggressiveRecycling(opportunities) {
        // Sort by efficiency gain and prioritize high-velocity movements
        return opportunities
            .filter(opp => opp.expectedEfficiencyGain > 0.2)
            .sort((a, b) => b.expectedEfficiencyGain - a.expectedEfficiencyGain)
            .slice(0, 5); // Limit to top 5 opportunities
    }
    
    /**
     * Conservative rotation optimization
     */
    async conservativeRotation(opportunities) {
        // Focus on high-confidence, stable opportunities
        return opportunities
            .filter(opp => opp.expectedEfficiencyGain > 0.3 && opp.priority > 1000)
            .sort((a, b) => b.priority - a.priority)
            .slice(0, 3); // Limit to top 3 opportunities
    }
    
    /**
     * Opportunistic reuse optimization
     */
    async opportunisticReuse(opportunities) {
        // Balance between efficiency and opportunity size
        return opportunities
            .filter(opp => opp.expectedEfficiencyGain > 0.15 && opp.amount > 1000)
            .sort((a, b) => (b.expectedEfficiencyGain * b.amount) - (a.expectedEfficiencyGain * a.amount))
            .slice(0, 4); // Limit to top 4 opportunities
    }
    
    /**
     * Strategy-specific optimization
     */
    async strategySpecificOptimization(opportunities) {
        // Custom optimization based on strategy characteristics
        const strategyOpportunities = opportunities.reduce((acc, opp) => {
            const category = opp.metadata?.reason || 'other';
            if (!acc[category]) acc[category] = [];
            acc[category].push(opp);
            return acc;
        }, {});
        
        // Select best opportunity from each category
        const selected = [];
        for (const [category, categoryOpportunities] of Object.entries(strategyOpportunities)) {
            const bestInCategory = categoryOpportunities.sort((a, b) => 
                b.expectedEfficiencyGain - a.expectedEfficiencyGain
            )[0];
            if (bestInCategory) selected.push(bestInCategory);
        }
        
        return selected.slice(0, 3);
    }
    
    /**
     * Execute capital movement
     */
    async executeCapitalMovement(movementPlan) {
        const movement = new CapitalMovement({
            fromStrategyId: movementPlan.fromStrategyId,
            toStrategyId: movementPlan.toStrategyId,
            amount: movementPlan.amount,
            transactionCost: await this.calculateTransactionCost(movementPlan),
            latency: await this.estimateMovementLatency(movementPlan),
            metadata: movementPlan.metadata
        });
        
        this.capitalMovements.push(movement);
        
        // Execute the movement
        if (movement.fromStrategyId) {
            // Reallocation - deallocate from source first
            const sourceAllocations = Array.from(this.capitalAllocations.values())
                .filter(allocation => 
                    allocation.strategyId === movement.fromStrategyId && 
                    allocation.state === CapitalState.DEPLOYED
                );
            
            let remainingAmount = movement.amount;
            for (const allocation of sourceAllocations) {
                if (remainingAmount <= 0) break;
                
                const deallocateAmount = Math.min(remainingAmount, allocation.amount);
                this.deallocateCapital(allocation.allocationId, 0);
                remainingAmount -= deallocateAmount;
            }
        }
        
        // Allocate to target strategy
        this.allocateCapital({
            strategyId: movement.toStrategyId,
            amount: movement.amount,
            expectedDuration: 3600000, // 1 hour default
            metadata: { ...movementPlan.metadata, movementId: movement.movementId }
        });
        
        console.log(`Capital movement executed: ${movement.amount} from ${movement.fromStrategyId || 'idle'} to ${movement.toStrategyId}`);
        this.emit('movementExecuted', { movement });
        
        return movement;
    }
    
    /**
     * Calculate transaction cost for movement
     */
    async calculateTransactionCost(movementPlan) {
        // Base cost + strategy-specific costs
        const baseCost = movementPlan.amount * 0.001; // 0.1% base
        const strategyCost = movementPlan.fromStrategyId ? 0.0005 : 0; // Additional cost for reallocation
        
        return Math.min(baseCost + strategyCost, movementPlan.amount * this.optimizationParams.maxTransactionCost);
    }
    
    /**
     * Estimate movement latency
     */
    async estimateMovementLatency(movementPlan) {
        // Base latency + strategy complexity factors
        const baseLatency = 5000; // 5 seconds base
        const strategyLatency = movementPlan.fromStrategyId ? 10000 : 0; // Additional for reallocation
        
        return Math.min(baseLatency + strategyLatency, this.optimizationParams.maxMovementLatency * 1000);
    }
    
    /**
     * Calculate idle capital
     */
    calculateIdleCapital() {
        const totalCapital = Array.from(this.strategyConfigs.values())
            .reduce((sum, strategy) => sum + strategy.capitalRequirements.max, 0);
        
        const deployedCapital = Array.from(this.strategyConfigs.values())
            .reduce((sum, strategy) => sum + strategy.currentAllocation, 0);
        
        return Math.max(0, totalCapital - deployedCapital);
    }
    
    /**
     * Calculate deployment efficiency
     */
    async calculateDeploymentEfficiency(strategy, amount) {
        const currentUtilization = strategy.currentAllocation / strategy.capitalRequirements.max;
        const newUtilization = (strategy.currentAllocation + amount) / strategy.capitalRequirements.max;
        
        // Efficiency gain from better utilization
        const utilizationGain = Math.max(0, newUtilization - currentUtilization);
        
        // Expected returns contribution
        const returnsGain = strategy.expectedReturns * (amount / strategy.capitalRequirements.max);
        
        return (utilizationGain + returnsGain) / 2;
    }
    
    /**
     * Calculate reallocation efficiency
     */
    async calculateReallocationEfficiency(fromStrategy, toStrategy, amount) {
        const fromEfficiency = await this.calculateStrategyEfficiency(fromStrategy.strategyId);
        const toEfficiency = await this.calculateStrategyEfficiency(toStrategy.strategyId);
        
        const efficiencyDifference = toEfficiency - fromEfficiency;
        const returnsDifference = toStrategy.expectedReturns - fromStrategy.expectedReturns;
        
        return (efficiencyDifference + returnsDifference) / 2;
    }
    
    /**
     * Check if opportunity is feasible
     */
    isOpportunityFeasible(opportunity) {
        if (opportunity.fromStrategyId) {
            const fromStrategy = this.strategyConfigs.get(opportunity.fromStrategyId);
            return fromStrategy && fromStrategy.currentAllocation >= opportunity.amount;
        }
        
        return this.calculateIdleCapital() >= opportunity.amount;
    }
    
    /**
     * Calculate efficiency gain for opportunity
     */
    calculateEfficiencyGain(opportunity) {
        return opportunity.expectedEfficiencyGain || 0;
    }
    
    /**
     * Update performance metrics
     */
    updatePerformanceMetrics() {
        const totalMovements = this.performanceMetrics.totalMovements;
        const successfulReuses = this.performanceMetrics.successfulReuses;
        
        this.performanceMetrics.reuseRate = totalMovements > 0 ? successfulReuses / totalMovements : 0;
        
        // Calculate average efficiency gain from recent movements
        const recentMovements = this.capitalMovements.slice(-10);
        if (recentMovements.length > 0) {
            const totalGain = recentMovements.reduce((sum, movement) => {
                const opportunity = movement.metadata.originalOpportunity;
                return sum + (opportunity?.expectedEfficiencyGain || 0);
            }, 0);
            this.performanceMetrics.avgEfficiencyGain = totalGain / recentMovements.length;
        }
    }
    
    /**
     * Start periodic optimization
     */
    startPeriodicOptimization() {
        this.optimizationInterval = setInterval(async () => {
            try {
                await this.optimizeCapitalReuse();
                await this.captureEfficiencySnapshot();
            } catch (error) {
                console.error('Periodic optimization failed:', error);
            }
        }, this.optimizationParams.snapshotInterval);
    }
    
    /**
     * Capture efficiency snapshot
     */
    async captureEfficiencySnapshot() {
        const efficiencyMetrics = await this.calculateEfficiencyMetrics();
        const reuseOpportunities = await this.identifyReuseOpportunities();
        
        const snapshot = new EfficiencySnapshot({
            totalCapital: this.calculateTotalCapital(),
            deployedCapital: this.calculateDeployedCapital(),
            efficiencyMetrics,
            reuseOpportunities
        });
        
        this.efficiencySnapshots.push(snapshot);
        
        // Keep only recent snapshots
        const cutoffTime = Date.now() - this.optimizationParams.lookbackWindow;
        this.efficiencySnapshots = this.efficiencySnapshots.filter(
            snapshot => snapshot.timestamp.getTime() > cutoffTime
        );
        
        this.emit('efficiencySnapshot', { snapshot });
    }
    
    /**
     * Calculate efficiency metrics
     */
    async calculateEfficiencyMetrics() {
        const totalCapital = this.calculateTotalCapital();
        const deployedCapital = this.calculateDeployedCapital();
        const idleCapital = this.calculateIdleCapital();
        
        return {
            [EfficiencyMetric.REUSE_RATE]: this.performanceMetrics.reuseRate,
            [EfficiencyMetric.IDLE_TIME_RATIO]: totalCapital > 0 ? idleCapital / totalCapital : 0,
            [EfficiencyMetric.TRANSACTION_COST_RATIO]: await this.calculateTransactionCostRatio(),
            [EfficiencyMetric.RETURN_ON_DEPLOYED_CAPITAL]: await this.calculateReturnOnDeployedCapital(),
            [EfficiencyMetric.VELOCITY_SCORE]: await this.calculateVelocityScore()
        };
    }
    
    /**
     * Calculate transaction cost ratio
     */
    async calculateTransactionCostRatio() {
        const recentMovements = this.capitalMovements.slice(-20);
        if (recentMovements.length === 0) return 0;
        
        const totalCost = recentMovements.reduce((sum, movement) => sum + movement.transactionCost, 0);
        const totalAmount = recentMovements.reduce((sum, movement) => sum + movement.amount, 0);
        
        return totalAmount > 0 ? totalCost / totalAmount : 0;
    }
    
    /**
     * Calculate return on deployed capital
     */
    async calculateReturnOnDeployedCapital() {
        const deployedCapital = this.calculateDeployedCapital();
        if (deployedCapital === 0) return 0;
        
        const totalReturns = Array.from(this.strategyConfigs.values())
            .reduce((sum, strategy) => {
                const strategyReturns = this.calculateStrategyReturns(strategy.strategyId);
                return sum + (strategyReturns * strategy.currentAllocation);
            }, 0);
        
        return totalReturns / deployedCapital;
    }
    
    /**
     * Calculate velocity score
     */
    async calculateVelocityScore() {
        const recentMovements = this.capitalMovements
            .filter(movement => movement.timestamp.getTime() > Date.now() - 3600000); // Last hour
        
        if (recentMovements.length === 0) return 0;
        
        const totalAmount = recentMovements.reduce((sum, movement) => sum + movement.amount, 0);
        const totalCapital = this.calculateTotalCapital();
        
        return totalCapital > 0 ? totalAmount / totalCapital : 0;
    }
    
    /**
     * Calculate total capital
     */
    calculateTotalCapital() {
        return Array.from(this.strategyConfigs.values())
            .reduce((sum, strategy) => sum + strategy.capitalRequirements.max, 0);
    }
    
    /**
     * Calculate deployed capital
     */
    calculateDeployedCapital() {
        return Array.from(this.strategyConfigs.values())
            .reduce((sum, strategy) => sum + strategy.currentAllocation, 0);
    }
    
    /**
     * Get optimizer status and performance
     */
    getOptimizerStatus() {
        return {
            optimizerId: this.optimizerId,
            activeStrategy: this.activeStrategy,
            performanceMetrics: { ...this.performanceMetrics },
            capitalUtilization: {
                total: this.calculateTotalCapital(),
                deployed: this.calculateDeployedCapital(),
                idle: this.calculateIdleCapital(),
                utilizationRate: this.calculateDeployedCapital() / this.calculateTotalCapital()
            },
            strategyCount: this.strategyConfigs.size,
            movementCount: this.capitalMovements.length
        };
    }
    
    /**
     * Update optimization strategy
     */
    updateOptimizationStrategy(newStrategy) {
        if (this.reuseStrategies[newStrategy]) {
            this.activeStrategy = newStrategy;
            console.log(`Optimization strategy updated to: ${newStrategy}`);
            this.emit('strategyUpdated', { newStrategy });
        } else {
            throw new Error(`Unknown optimization strategy: ${newStrategy}`);
        }
    }
    
    /**
     * Stop the optimizer
     */
    stop() {
        if (this.optimizationInterval) {
            clearInterval(this.optimizationInterval);
            this.optimizationInterval = null;
        }
        console.log('Capital Reuse Optimizer stopped');
    }
}

// Placeholder classes for optimization engines
class LinearProgrammingEngine {
    optimize() { return []; }
}

class PatternRecognitionEngine {
    recognize() { return []; }
}

class CostBenefitAnalyzer {
    analyze() { return { cost: 0, benefit: 0 }; }
}

class RiskReturnCalculator {
    calculate() { return { risk: 0, return: 0 }; }
}

module.exports = {
    ReuseOptimizer,
    CapitalState,
    ReuseStrategy,
    EfficiencyMetric,
    CapitalAllocation,
    CapitalMovement,
    EfficiencySnapshot
};

// Example usage
if (require.main === module) {
    async function demo() {
        const optimizer = new ReuseOptimizer({
            optimizerId: 'demo_optimizer',
            minReuseThreshold: 0.15,
            targetReuseRate: 0.6
        });
        
        // Register strategies
        optimizer.registerStrategy({
            strategyId: 'momentum_trading',
            capitalRequirements: { min: 1000, max: 10000, optimal: 5000 },
            expectedReturns: 0.12,
            riskProfile: 'medium'
        });
        
        optimizer.registerStrategy({
            strategyId: 'arbitrage',
            capitalRequirements: { min: 5000, max: 20000, optimal: 10000 },
            expectedReturns: 0.08,
            riskProfile: 'low'
        });
        
        optimizer.registerStrategy({
            strategyId: 'market_making',
            capitalRequirements: { min: 2000, max: 15000, optimal: 8000 },
            expectedReturns: 0.15,
            riskProfile: 'high'
        });
        
        // Allocate initial capital
        optimizer.allocateCapital({
            strategyId: 'momentum_trading',
            amount: 3000,
            expectedDuration: 3600000
        });
        
        optimizer.allocateCapital({
            strategyId: 'arbitrage',
            amount: 8000,
            expectedDuration: 1800000
        });
        
        // Set up event listeners
        optimizer.on('optimizationCompleted', ({ executedMovements }) => {
            console.log(`Optimization completed: ${executedMovements.length} movements`);
        });
        
        optimizer.on('efficiencySnapshot', ({ snapshot }) => {
            console.log('Efficiency snapshot captured:', snapshot.efficiencyMetrics);
        });
        
        // Run optimization
        setTimeout(async () => {
            await optimizer.optimizeCapitalReuse();
            
            // Get status
            const status = optimizer.getOptimizerStatus();
            console.log('Optimizer status:', status);
            
            // Stop optimizer
            optimizer.stop();
        }, 10000);
    }
    
    demo().catch(console.error);
}
