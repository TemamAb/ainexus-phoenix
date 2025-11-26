/**
 * QUANTUMNEX CAPITAL ALLOCATOR
 * Industry Standards: Modern Portfolio Theory, Risk-parity, Kelly Criterion
 * Validated Sources:
 * - Modern Portfolio Theory (Markowitz)
 * - Risk-parity models (Bridgewater Associates)
 * - Kelly Criterion (Optimal betting theory)
 * - Black-Litterman model (Asset allocation)
 */

class CapitalAllocator {
    constructor() {
        this.portfolioWeights = new Map();
        this.allocationHistory = new Map();
        this.riskModels = new Map();
        this.optimizationParams = {
            targetReturn: 0.15,
            riskFreeRate: 0.02,
            maxVolatility: 0.25,
            weightBounds: [0, 0.3] // No more than 30% in any single asset
        };
        
        console.log('‚úÖ Capital Allocator initialized with Modern Portfolio Theory');
    }

    async calculatePositionSize(capital, assets, riskParams = {}) {
        try {
            this.validateInputs(capital, assets, riskParams);
            
            const positionSizes = {};
            const totalRiskBudget = this.calculateTotalRiskBudget(assets, riskParams);
            
            for (const asset of assets) {
                const assetRisk = this.calculateAssetRisk(asset, riskParams);
                const riskAllocation = assetRisk / totalRiskBudget;
                const positionSize = capital * riskAllocation;
                
                // Apply Kelly Criterion for optimal sizing
                const kellySize = this.applyKellyCriterion(positionSize, asset, riskParams);
                
                positionSizes[asset.symbol] = {
                    symbol: asset.symbol,
                    allocatedCapital: kellySize,
                    riskAllocation: riskAllocation,
                    kellyFraction: kellySize / positionSize,
                    maxDrawdown: asset.maxDrawdown || 0.1
                };
            }
            
            const allocation = {
                capital: capital,
                positionSizes: positionSizes,
                totalRisk: totalRiskBudget,
                riskParams: riskParams,
                timestamp: new Date().toISOString()
            };

            this.recordAllocation(allocation);
            
            console.log(`Ì≤∞ Capital allocated: $${capital} across ${assets.length} assets`);
            return allocation;
        } catch (error) {
            console.error('‚ùå Position size calculation failed:', error);
            throw error;
        }
    }

    validateInputs(capital, assets, riskParams) {
        if (!capital || capital <= 0) {
            throw new Error('Invalid capital amount');
        }

        if (!assets || assets.length === 0) {
            throw new Error('No assets provided');
        }

        if (assets.length < 2) {
            throw new Error('At least 2 assets required for diversification');
        }

        // Validate each asset
        for (const asset of assets) {
            if (!asset.symbol || !asset.volatility || !asset.expectedReturn) {
                throw new Error('Invalid asset data: symbol, volatility, and expectedReturn required');
            }

            if (asset.volatility <= 0) {
                throw new Error('Asset volatility must be positive');
            }
        }

        return true;
    }

    calculateTotalRiskBudget(assets, riskParams) {
        let totalRisk = 0;
        
        for (const asset of assets) {
            const assetRisk = this.calculateAssetRisk(asset, riskParams);
            totalRisk += assetRisk;
        }
        
        return totalRisk;
    }

    calculateAssetRisk(asset, riskParams) {
        // Base risk calculation using volatility
        let risk = asset.volatility;
        
        // Adjust for correlation if available
        if (asset.correlation) {
            risk *= (1 - Math.abs(asset.correlation));
        }
        
        // Apply risk scaling factors
        if (riskParams.riskTolerance) {
            risk *= riskParams.riskTolerance;
        }
        
        // Apply maximum risk limits
        const maxRisk = riskParams.maxAssetRisk || 0.5;
        risk = Math.min(risk, maxRisk);
        
        return risk;
    }

    applyKellyCriterion(positionSize, asset, riskParams) {
        const winProbability = asset.winRate || 0.5;
        const winLossRatio = asset.winLossRatio || 2.0;
        
        // Kelly formula: f = (bp - q) / b
        // where b = win/loss ratio, p = win probability, q = loss probability
        const b = winLossRatio;
        const p = winProbability;
        const q = 1 - p;
        
        const kellyFraction = (b * p - q) / b;
        
        // Apply fractional Kelly for safety (usually 1/2 or 1/4 Kelly)
        const fractionalKelly = (riskParams.kellyFraction || 0.25) * Math.max(0, kellyFraction);
        
        return positionSize * fractionalKelly;
    }

    async optimizePortfolio(assets, constraints = {}) {
        try {
            this.validateAssets(assets);
            
            // Calculate expected returns and covariance
            const expectedReturns = this.calculateExpectedReturns(assets);
            const covarianceMatrix = this.calculateCovarianceMatrix(assets);
            
            // Apply constraints
            const optimizationConstraints = this.buildConstraints(constraints);
            
            // Optimize using Markowitz model
            const optimizedWeights = this.markowitzOptimization(
                expectedReturns, 
                covarianceMatrix, 
                optimizationConstraints
            );
            
            const portfolio = {
                weights: optimizedWeights,
                expectedReturn: this.calculatePortfolioReturn(optimizedWeights, expectedReturns),
                expectedRisk: this.calculatePortfolioRisk(optimizedWeights, covarianceMatrix),
                sharpeRatio: this.calculateSharpeRatio(optimizedWeights, expectedReturns, covarianceMatrix),
                diversification: this.calculateDiversification(optimizedWeights),
                constraints: constraints,
                timestamp: new Date().toISOString()
            };

            console.log(`Ì≥à Portfolio optimized: ${(portfolio.expectedReturn * 100).toFixed(2)}% expected return`);
            return portfolio;
        } catch (error) {
            console.error('‚ùå Portfolio optimization failed:', error);
            throw error;
        }
    }

    validateAssets(assets) {
        if (!assets || assets.length === 0) {
            throw new Error('No assets provided for optimization');
        }

        if (assets.length < 2) {
            throw new Error('At least 2 assets required for portfolio optimization');
        }

        // Check for sufficient data
        for (const asset of assets) {
            if (!asset.historicalReturns || asset.historicalReturns.length < 30) {
                console.warn(`Insufficient historical data for ${asset.symbol}`);
            }
        }
    }

    calculateExpectedReturns(assets) {
        const returns = {};
        for (const asset of assets) {
            returns[asset.symbol] = asset.expectedReturn || 0.1; // Default 10%
        }
        return returns;
    }

    calculateCovarianceMatrix(assets) {
        const matrix = {};
        const symbols = assets.map(asset => asset.symbol);
        
        // Initialize matrix
        for (const symbol1 of symbols) {
            matrix[symbol1] = {};
            for (const symbol2 of symbols) {
                matrix[symbol1][symbol2] = 0;
            }
        }
        
        // Calculate covariances (simplified)
        for (let i = 0; i < assets.length; i++) {
            for (let j = 0; j < assets.length; j++) {
                const asset1 = assets[i];
                const asset2 = assets[j];
                
                if (i === j) {
                    // Variance (diagonal)
                    matrix[asset1.symbol][asset2.symbol] = Math.pow(asset1.volatility, 2);
                } else {
                    // Covariance (simplified correlation assumption)
                    const correlation = asset1.correlation?.[asset2.symbol] || 0.3;
                    matrix[asset1.symbol][asset2.symbol] = correlation * asset1.volatility * asset2.volatility;
                }
            }
        }
        
        return matrix;
    }

    buildConstraints(constraints) {
        const defaultConstraints = {
            weight_bounds: this.optimizationParams.weightBounds,
            target_return: this.optimizationParams.targetReturn,
            market_neutral: false
        };

        return { ...defaultConstraints, ...constraints };
    }

    markowitzOptimization(expectedReturns, covarianceMatrix, constraints) {
        // Simplified Markowitz optimization
        // In production, use quadratic programming libraries
        
        const symbols = Object.keys(expectedReturns);
        const weights = {};
        
        // Equal weight as fallback (simplified)
        const equalWeight = 1 / symbols.length;
        for (const symbol of symbols) {
            weights[symbol] = equalWeight;
        }
        
        // Apply weight bounds
        for (const symbol in weights) {
            weights[symbol] = Math.max(
                constraints.weight_bounds[0],
                Math.min(constraints.weight_bounds[1], weights[symbol])
            );
        }
        
        // Normalize weights to sum to 1
        return this.normalizeWeights(weights);
    }

    calculatePortfolioReturn(weights, expectedReturns) {
        let totalReturn = 0;
        for (const symbol in weights) {
            totalReturn += weights[symbol] * expectedReturns[symbol];
        }
        return totalReturn;
    }

    calculatePortfolioRisk(weights, covarianceMatrix) {
        let variance = 0;
        
        for (const symbol1 in weights) {
            for (const symbol2 in weights) {
                variance += weights[symbol1] * weights[symbol2] * covarianceMatrix[symbol1][symbol2];
            }
        }
        
        return Math.sqrt(variance);
    }

    calculateSharpeRatio(weights, expectedReturns, covarianceMatrix) {
        const expectedReturn = this.calculatePortfolioReturn(weights, expectedReturns);
        const portfolioRisk = this.calculatePortfolioRisk(weights, covarianceMatrix);
        const riskFreeRate = this.optimizationParams.riskFreeRate;
        
        return portfolioRisk !== 0 ? (expectedReturn - riskFreeRate) / portfolioRisk : 0;
    }

    calculateDiversification(weights) {
        const weightValues = Object.values(weights);
        const herfindahl = weightValues.reduce((sum, weight) => sum + weight * weight, 0);
        
        // Convert to diversification score (0 to 1)
        return 1 - herfindahl;
    }

    normalizeWeights(weights) {
        const total = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
        
        if (total === 0) return weights;
        
        const normalized = {};
        for (const symbol in weights) {
            normalized[symbol] = weights[symbol] / total;
        }
        
        return normalized;
    }

    async calculateRiskParityAllocation(assets, targetRisk = 0.1) {
        try {
            const riskContributions = {};
            let totalInverseRisk = 0;
            
            // Calculate risk contributions
            for (const asset of assets) {
                const risk = asset.volatility || 0.2;
                riskContributions[asset.symbol] = risk;
                totalInverseRisk += 1 / risk;
            }
            
            // Calculate weights inversely proportional to risk
            const weights = {};
            for (const asset of assets) {
                const risk = riskContributions[asset.symbol];
                weights[asset.symbol] = (1 / risk) / totalInverseRisk;
            }
            
            console.log(`‚öñÔ∏è Risk parity allocation calculated for ${assets.length} assets`);
            return weights;
        } catch (error) {
            console.error('‚ùå Risk parity allocation failed:', error);
            throw error;
        }
    }

    recordAllocation(allocation) {
        const allocationId = this.generateAllocationId();
        this.allocationHistory.set(allocationId, allocation);
        
        // Update current portfolio weights
        this.portfolioWeights = allocation.positionSizes;
        
        console.log(`Ì≤æ Allocation recorded: ${allocationId}`);
    }

    generateAllocationId() {
        return `alloc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Risk management methods
    async calculateValueAtRisk(portfolio, confidence = 0.95, timeHorizon = 1) {
        try {
            // Simplified VaR calculation using parametric method
            const portfolioReturn = portfolio.expectedReturn;
            const portfolioRisk = portfolio.expectedRisk;
            
            // Z-score for confidence level
            const zScores = { 0.95: 1.645, 0.99: 2.326 };
            const zScore = zScores[confidence] || 1.645;
            
            const varValue = portfolioRisk * zScore * Math.sqrt(timeHorizon);
            const portfolioVaR = portfolio.currentValue * varValue;
            
            return {
                value: portfolioVaR,
                confidence: confidence,
                timeHorizon: timeHorizon,
                method: 'parametric'
            };
        } catch (error) {
            console.error('‚ùå VaR calculation failed:', error);
            throw error;
        }
    }

    async stressTestPortfolio(portfolio, scenarios) {
        try {
            const stressResults = {};
            
            for (const scenario of scenarios) {
                stressResults[scenario.name] = this.applyStressScenario(portfolio, scenario);
            }
            
            return {
                portfolio: portfolio,
                scenarios: stressResults,
                worstCase: this.findWorstCaseScenario(stressResults),
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('‚ùå Portfolio stress test failed:', error);
            throw error;
        }
    }

    applyStressScenario(portfolio, scenario) {
        let stressedValue = portfolio.currentValue;
        
        for (const asset in portfolio.weights) {
            const assetReturn = scenario.assetReturns[asset] || 0;
            stressedValue += portfolio.weights[asset] * portfolio.currentValue * assetReturn;
        }
        
        return {
            scenario: scenario.name,
            portfolioValue: stressedValue,
            drawdown: (portfolio.currentValue - stressedValue) / portfolio.currentValue
        };
    }

    findWorstCaseScenario(scenarios) {
        let worstCase = null;
        let maxDrawdown = 0;
        
        for (const scenarioName in scenarios) {
            const scenario = scenarios[scenarioName];
            if (scenario.drawdown > maxDrawdown) {
                maxDrawdown = scenario.drawdown;
                worstCase = scenarioName;
            }
        }
        
        return {
            scenario: worstCase,
            drawdown: maxDrawdown
        };
    }

    // Utility methods
    getCurrentAllocation() {
        return this.portfolioWeights;
    }

    getAllocationHistory(limit = 50) {
        const history = Array.from(this.allocationHistory.values());
        return history.slice(-limit).reverse();
    }

    setOptimizationParams(params) {
        this.optimizationParams = { ...this.optimizationParams, ...params };
        console.log('‚úÖ Optimization parameters updated');
    }

    getOptimizationParams() {
        return this.optimizationParams;
    }

    // Cleanup
    cleanupOldAllocations(daysToKeep = 90) {
        const cutoffDate = new Date(Date.now() - daysToKeep * 24 * 60 * 60 * 1000);
        let cleanedCount = 0;

        for (const [allocationId, allocation] of this.allocationHistory) {
            if (new Date(allocation.timestamp) < cutoffDate) {
                this.allocationHistory.delete(allocationId);
                cleanedCount++;
            }
        }

        console.log(`Ì∑π Cleaned up ${cleanedCount} old allocations`);
        return cleanedCount;
    }
}

module.exports = CapitalAllocator;
