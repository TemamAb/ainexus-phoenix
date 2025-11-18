/**
 * AI-NEXUS Impact Cost Model
 * Advanced market impact forecasting and temporary vs permanent impact analysis
 */

class ImpactCostModel {
    constructor(config = {}) {
        this.config = {
            defaultModel: config.defaultModel || 'almgren_chriss',
            marketDataProvider: config.marketDataProvider,
            ...config
        };

        this.models = {
            square_root: this.squareRootModel.bind(this),
            almgren_chriss: this.almgrenChrissModel.bind(this),
            obizhaeva_wang: this.obizhaevaWangModel.bind(this),
            kyle: this.kyleModel.bind(this)
        };

        this.impactHistory = new Map();
    }

    /**
     * Calculate market impact for a trade
     */
    async calculateImpact(trade, modelType = this.config.defaultModel) {
        const model = this.models[modelType];
        if (!model) {
            throw new Error(`Unknown impact model: ${modelType}`);
        }

        const impact = await model(trade);
        
        // Store impact calculation
        this.impactHistory.set(trade.id, {
            trade,
            impact,
            model: modelType,
            timestamp: new Date()
        });

        return impact;
    }

    /**
     * Square root impact model (simplified)
     */
    async squareRootModel(trade) {
        const { size, dailyVolume, volatility } = trade;
        const participationRate = size / dailyVolume;

        // Base square root model
        const temporaryImpact = 0.1 * volatility * Math.sqrt(participationRate);
        const permanentImpact = 0.05 * volatility * participationRate;

        return {
            temporaryImpact,
            permanentImpact,
            totalImpact: temporaryImpact + permanentImpact,
            participationRate,
            model: 'square_root'
        };
    }

    /**
     * Almgren-Chriss transient impact model
     */
    async almgrenChrissModel(trade) {
        const { size, dailyVolume, volatility, liquidity } = trade;
        const participationRate = size / dailyVolume;

        // Temporary impact (transient)
        const eta = 0.1; // Temporary impact parameter
        const temporaryImpact = eta * volatility * Math.sqrt(size / liquidity);

        // Permanent impact
        const gamma = 0.05; // Permanent impact parameter
        const permanentImpact = gamma * volatility * participationRate;

        // Resilience effect
        const resilience = 0.5; // Market resilience
        const resilienceAdjustment = 1 / (1 + resilience * participationRate);

        const totalImpact = (temporaryImpact + permanentImpact) * resilienceAdjustment;

        return {
            temporaryImpact,
            permanentImpact,
            totalImpact,
            participationRate,
            resilienceAdjustment,
            model: 'almgren_chriss'
        };
    }

    /**
     * Obizhaeva-Wang model with market resilience
     */
    async obizhaevaWangModel(trade) {
        const { size, dailyVolume, volatility, bidAskSpread } = trade;
        const participationRate = size / dailyVolume;

        // Temporary impact (immediate)
        const lambda = 0.15; // Temporary impact coefficient
        const temporaryImpact = lambda * bidAskSpread * Math.sqrt(participationRate);

        // Permanent impact
        const permanentImpact = 0.08 * volatility * participationRate;

        // Resilience decay
        const resilience = 1.0; // Market resilience parameter
        const decayFactor = Math.exp(-resilience * participationRate);

        const totalImpact = temporaryImpact + permanentImpact * decayFactor;

        return {
            temporaryImpact,
            permanentImpact,
            totalImpact,
            decayFactor,
            participationRate,
            model: 'obizhaeva_wang'
        };
    }

    /**
     * Kyle model (informed trading)
     */
    async kyleModel(trade) {
        const { size, dailyVolume, volatility, noiseTrading } = trade;
        const participationRate = size / dailyVolume;

        // Kyle's lambda (illiquidity parameter)
        const sigmaV = volatility; // Fundamental volatility
        const sigmaU = noiseTrading || dailyVolume * 0.1; // Noise trading volume

        const lambda = sigmaV / (2 * sigmaU); // Kyle's lambda
        const temporaryImpact = lambda * size;

        // Permanent impact (information effect)
        const permanentImpact = 0.5 * lambda * size;

        const totalImpact = temporaryImpact + permanentImpact;

        return {
            temporaryImpact,
            permanentImpact,
            totalImpact,
            kyleLambda: lambda,
            participationRate,
            model: 'kyle'
        };
    }

    /**
     * Compare multiple impact models
     */
    async compareImpactModels(trade, modelTypes = ['square_root', 'almgren_chriss', 'obizhaeva_wang']) {
        const comparisons = [];

        for (const modelType of modelTypes) {
            try {
                const impact = await this.calculateImpact(trade, modelType);
                comparisons.push({
                    model: modelType,
                    ...impact
                });
            } catch (error) {
                console.error(`Error in model ${modelType}:`, error);
            }
        }

        // Calculate consensus impact
        const validComparisons = comparisons.filter(c => c.totalImpact !== undefined);
        const consensusImpact = validComparisons.length > 0 
            ? validComparisons.reduce((sum, c) => sum + c.totalImpact, 0) / validComparisons.length
            : 0;

        return {
            trade,
            comparisons,
            consensusImpact,
            recommendedModel: this.recommendBestModel(comparisons)
        };
    }

    /**
     * Recommend best impact model based on market conditions
     */
    recommendBestModel(comparisons) {
        if (comparisons.length === 0) return 'square_root';

        // Simple heuristic based on volatility and trade size
        const trade = comparisons[0].trade; // All comparisons have same trade

        if (trade.volatility > 0.05) {
            // High volatility: prefer Almgren-Chriss
            return 'almgren_chriss';
        } else if (trade.size > trade.dailyVolume * 0.01) {
            // Large trade: prefer Obizhaeva-Wang
            return 'obizhaeva_wang';
        } else {
            // Normal conditions: square root is sufficient
            return 'square_root';
        }
    }

    /**
     * Calculate optimal execution schedule
     */
    async calculateOptimalSchedule(trade, modelType = 'almgren_chriss') {
        const impact = await this.calculateImpact(trade, modelType);
        const { size, urgency, volatility } = trade;

        // Almgren-Chriss optimal execution theory
        const riskAversion = 0.1; // Risk aversion parameter
        const temporaryImpact = impact.temporaryImpact;
        const permanentImpact = impact.permanentImpact;

        // Optimal trading rate (simplified)
        const kappa = Math.sqrt(riskAversion * volatility * volatility / temporaryImpact);
        const optimalRate = size * kappa / (1 + kappa * permanentImpact);

        // Schedule over time
        const timeHorizon = Math.min(urgency || 300, 3600); // Max 1 hour
        const timeSteps = Math.ceil(timeHorizon / 60); // 1-minute steps

        const schedule = [];
        let remainingSize = size;
        const timeStep = timeHorizon / timeSteps;

        for (let i = 0; i < timeSteps && remainingSize > 0; i++) {
            const time = i * timeStep;
            const tradeSize = Math.min(optimalRate * timeStep, remainingSize);
            
            schedule.push({
                time: time,
                size: tradeSize,
                cumulativeSize: size - remainingSize + tradeSize
            });

            remainingSize -= tradeSize;
        }

        return {
            impact,
            schedule,
            totalTime: schedule[schedule.length - 1]?.time || 0,
            riskAversion,
            optimalRate
        };
    }

    /**
     * Estimate price impact trajectory
     */
    async estimateImpactTrajectory(trade, modelType = 'almgren_chriss') {
        const impact = await this.calculateImpact(trade, modelType);
        const schedule = await this.calculateOptimalSchedule(trade, modelType);

        const trajectory = [];
        let cumulativeImpact = 0;

        for (const step of schedule.schedule) {
            // Impact increases with cumulative trading
            const stepImpact = impact.totalImpact * (step.cumulativeSize / trade.size);
            cumulativeImpact += stepImpact;

            trajectory.push({
                time: step.time,
                cumulativeSize: step.cumulativeSize,
                stepImpact: stepImpact,
                cumulativeImpact: cumulativeImpact,
                price: trade.price * (1 + cumulativeImpact)
            });
        }

        return {
            initialPrice: trade.price,
            finalPrice: trade.price * (1 + cumulativeImpact),
            totalImpact: cumulativeImpact,
            trajectory
        };
    }

    /**
     * Analyze impact cost for portfolio of trades
     */
    async analyzePortfolioImpact(trades, modelType = 'almgren_chriss') {
        const portfolioAnalysis = {
            totalSize: 0,
            totalImpact: 0,
            trades: [],
            correlations: []
        };

        for (const trade of trades) {
            const impact = await this.calculateImpact(trade, modelType);
            const impactCost = impact.totalImpact * trade.size;

            portfolioAnalysis.totalSize += trade.size;
            portfolioAnalysis.totalImpact += impactCost;

            portfolioAnalysis.trades.push({
                ...trade,
                impact,
                impactCost
            });
        }

        // Calculate cross-impact correlations (simplified)
        portfolioAnalysis.correlations = this.estimateCrossImpact(trades);

        return portfolioAnalysis;
    }

    /**
     * Estimate cross-impact between correlated assets
     */
    estimateCrossImpact(trades) {
        const correlations = [];

        for (let i = 0; i < trades.length; i++) {
            for (let j = i + 1; j < trades.length; j++) {
                const trade1 = trades[i];
                const trade2 = trades[j];

                // Simplified correlation estimation
                const correlation = this.estimateAssetCorrelation(trade1.asset, trade2.asset);
                const crossImpact = 0.1 * correlation; // Cross-impact coefficient

                correlations.push({
                    asset1: trade1.asset,
                    asset2: trade2.asset,
                    correlation,
                    crossImpact
                });
            }
        }

        return correlations;
    }

    /**
     * Estimate correlation between two assets (simplified)
     */
    estimateAssetCorrelation(asset1, asset2) {
        // This would use historical data in production
        const correlationMap = {
            'ETH/USD-BTC/USD': 0.8,
            'ETH/USD-ADA/USD': 0.6,
            'BTC/USD-ADA/USD': 0.5
        };

        const key = `${asset1}-${asset2}`;
        const reverseKey = `${asset2}-${asset1}`;

        return correlationMap[key] || correlationMap[reverseKey] || 0.3;
    }

    /**
     * Generate impact analysis report
     */
    async generateImpactReport(trade, modelTypes = ['square_root', 'almgren_chriss', 'obizhaeva_wang']) {
        const modelComparison = await this.compareImpactModels(trade, modelTypes);
        const optimalSchedule = await this.calculateOptimalSchedule(trade);
        const impactTrajectory = await this.estimateImpactTrajectory(trade);

        return {
            trade,
            modelComparison,
            optimalSchedule,
            impactTrajectory,
            recommendations: this.generateImpactRecommendations(modelComparison, optimalSchedule)
        };
    }

    /**
     * Generate impact minimization recommendations
     */
    generateImpactRecommendations(modelComparison, optimalSchedule) {
        const recommendations = [];
        const consensusImpact = modelComparison.consensusImpact;

        if (consensusImpact > 0.01) {
            recommendations.push({
                priority: 'high',
                action: 'Split trade into smaller chunks',
                reason: `High expected impact: ${(consensusImpact * 100).toFixed(2)}%`
            });
        }

        if (optimalSchedule.totalTime > 300) {
            recommendations.push({
                priority: 'medium',
                action: 'Consider longer execution horizon',
                reason: `Optimal schedule requires ${optimalSchedule.totalTime} seconds`
            });
        }

        const avgStepSize = optimalSchedule.schedule.reduce((sum, step) => sum + step.size, 0) 
            / optimalSchedule.schedule.length;

        if (avgStepSize > 10000) {
            recommendations.push({
                priority: 'medium',
                action: 'Reduce individual trade sizes',
                reason: 'Large step sizes may cause significant impact'
            });
        }

        return recommendations;
    }
}

module.exports = ImpactCostModel;
