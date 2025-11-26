// QUANTUMNEX RISK MONITOR
// Industry Standards: OpenGamma Strata, VaR calculators, Risk models
// Validated Sources:
// - OpenGamma Strata (Risk management framework)
// - Value at Risk (VaR) methodologies
// - Risk parity models
// - Circuit breaker patterns

class QuantumNexRiskMonitor {
    constructor() {
        this.positions = new Map();
        this.riskLimits = {
            maxPositionSize: 100000,
            maxPortfolioRisk: 0.05,
            varConfidence: 0.95,
            maxDrawdown: 0.10,
            concentrationLimit: 0.10
        };
        this.marketData = new Map();
        this.circuitBreakers = new Set();
        this.riskMetrics = new Map();
        this.setupDefaultCircuitBreakers();
    }

    setupDefaultCircuitBreakers() {
        this.circuitBreakers.add('PRICE_DISLOCATION');
        this.circuitBreakers.add('VOLUME_SPIKE');
        this.circuitBreakers.add('LIQUIDITY_CRISIS');
        this.circuitBreakers.add('VOLATILITY_SURGE');
    }

    // Value at Risk Calculation
    calculateValueAtRisk(positions, confidenceLevel = 0.95, timeHorizon = 1) {
        const portfolioReturns = this.calculateHistoricalReturns(positions);
        const sortedReturns = portfolioReturns.sort((a, b) => a - b);
        const varIndex = Math.floor((1 - confidenceLevel) * sortedReturns.length);
        
        return Math.abs(sortedReturns[varIndex] || 0);
    }

    calculateHistoricalReturns(positions, periods = 1000) {
        const returns = [];
        
        for (let i = 0; i < periods; i++) {
            let portfolioReturn = 0;
            
            for (const [asset, position] of positions) {
                const historicalVolatility = this.getAssetVolatility(asset);
                const randomReturn = this.generateRandomReturn(historicalVolatility);
                portfolioReturn += position.notional * randomReturn;
            }
            
            returns.push(portfolioReturn);
        }
        
        return returns;
    }

    getAssetVolatility(asset) {
        const volatilityMap = {
            'BTC': 0.025,
            'ETH': 0.030,
            'USDT': 0.001,
            'BNB': 0.028,
            'SOL': 0.035
        };
        return volatilityMap[asset] || 0.020;
    }

    generateRandomReturn(volatility) {
        // Box-Muller transform for normal distribution
        let u = 0, v = 0;
        while(u === 0) u = Math.random();
        while(v === 0) v = Math.random();
        
        const normal = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
        return normal * volatility;
    }

    // Position Risk Assessment
    monitorPositionRisk(position) {
        const riskAssessment = {
            positionId: position.id,
            asset: position.asset,
            notional: position.notional,
            risks: {
                sizeRisk: this.assessSizeRisk(position),
                concentrationRisk: this.assessConcentrationRisk(position),
                liquidityRisk: this.assessLiquidityRisk(position),
                marketRisk: this.assessMarketRisk(position)
            },
            timestamp: new Date()
        };

        riskAssessment.totalRiskScore = this.calculateTotalRiskScore(riskAssessment.risks);
        riskAssessment.breachStatus = this.checkRiskBreaches(riskAssessment);

        this.riskMetrics.set(position.id, riskAssessment);
        
        if (riskAssessment.totalRiskScore > 7.5) {
            this.triggerRiskAlert(riskAssessment);
        }

        return riskAssessment;
    }

    assessSizeRisk(position) {
        const sizeRatio = position.notional / this.riskLimits.maxPositionSize;
        return {
            type: 'SIZE',
            score: Math.min(sizeRatio * 10, 10),
            withinLimit: sizeRatio <= 1,
            ratio: sizeRatio
        };
    }

    assessConcentrationRisk(position) {
        const portfolioValue = this.calculateTotalPortfolioValue();
        const concentration = position.notional / portfolioValue;
        
        return {
            type: 'CONCENTRATION',
            score: Math.min(concentration * 20, 10),
            withinLimit: concentration <= this.riskLimits.concentrationLimit,
            ratio: concentration
        };
    }

    calculateTotalPortfolioValue() {
        let total = 0;
        for (const position of this.positions.values()) {
            total += position.notional;
        }
        return total || 1;
    }

    assessLiquidityRisk(position) {
        const liquidityScores = {
            'BTC': 9, 'ETH': 8, 'USDT': 10, 'BNB': 7, 'SOL': 6
        };
        
        const baseScore = liquidityScores[position.asset] || 5;
        const sizeAdjustedScore = (10 - baseScore) * (position.notional / 50000);
        
        return {
            type: 'LIQUIDITY',
            score: Math.min(sizeAdjustedScore, 10),
            withinLimit: baseScore >= 7,
            liquidityScore: baseScore
        };
    }

    assessMarketRisk(position) {
        const volatility = this.getAssetVolatility(position.asset);
        const marketRiskScore = volatility * 100; // Scale volatility to score
        
        return {
            type: 'MARKET',
            score: Math.min(marketRiskScore, 10),
            withinLimit: marketRiskScore <= 5,
            volatility: volatility
        };
    }

    calculateTotalRiskScore(risks) {
        const weights = {
            'SIZE': 0.3,
            'CONCENTRATION': 0.25,
            'LIQUIDITY': 0.2,
            'MARKET': 0.25
        };

        let totalScore = 0;
        for (const [type, risk] of Object.entries(risks)) {
            totalScore += risk.score * weights[type];
        }

        return Math.min(totalScore, 10);
    }

    checkRiskBreaches(riskAssessment) {
        const breaches = [];
        
        for (const [type, risk] of Object.entries(riskAssessment.risks)) {
            if (!risk.withinLimit) {
                breaches.push({
                    type,
                    score: risk.score,
                    limit: this.getRiskLimit(type)
                });
            }
        }

        return breaches;
    }

    getRiskLimit(riskType) {
        const limits = {
            'SIZE': this.riskLimits.maxPositionSize,
            'CONCENTRATION': this.riskLimits.concentrationLimit,
            'LIQUIDITY': 7, // Minimum liquidity score
            'MARKET': 5     // Maximum volatility score
        };
        
        return limits[riskType];
    }

    triggerRiskAlert(riskAssessment) {
        const alert = {
            id: Date.now().toString(),
            type: 'RISK_BREACH',
            positionId: riskAssessment.positionId,
            asset: riskAssessment.asset,
            riskScore: riskAssessment.totalRiskScore,
            breaches: riskAssessment.breachStatus,
            timestamp: new Date(),
            severity: this.determineAlertSeverity(riskAssessment.totalRiskScore)
        };

        console.warn('íº¨ RISK ALERT:', alert);
        
        // Emit alert for other systems
        if (typeof process !== 'undefined' && process.emit) {
            process.emit('riskAlert', alert);
        }

        return alert;
    }

    determineAlertSeverity(riskScore) {
        if (riskScore >= 9) return 'CRITICAL';
        if (riskScore >= 7) return 'HIGH';
        if (riskScore >= 5) return 'MEDIUM';
        return 'LOW';
    }

    // Portfolio-level Risk Monitoring
    monitorPortfolioRisk() {
        const portfolioValue = this.calculateTotalPortfolioValue();
        const positionsArray = Array.from(this.positions.values());
        
        const portfolioVaR = this.calculateValueAtRisk(this.positions);
        const maxDrawdown = this.calculateMaxDrawdown();
        const concentrationMetrics = this.calculateConcentrationMetrics();

        const portfolioRisk = {
            timestamp: new Date(),
            portfolioValue,
            valueAtRisk: portfolioVaR,
            maxDrawdown,
            concentration: concentrationMetrics,
            positionsAtRisk: this.getPositionsAtRisk(),
            overallRiskScore: this.calculatePortfolioRiskScore(portfolioVaR, maxDrawdown, concentrationMetrics)
        };

        return portfolioRisk;
    }

    calculateMaxDrawdown() {
        // Simplified max drawdown calculation
        // In production, this would use historical portfolio values
        const recentReturns = this.getRecentPortfolioReturns();
        let maxDrawdown = 0;
        let peak = recentReturns[0];

        for (const ret of recentReturns) {
            if (ret > peak) peak = ret;
            const drawdown = (peak - ret) / peak;
            maxDrawdown = Math.max(maxDrawdown, drawdown);
        }

        return maxDrawdown;
    }

    getRecentPortfolioReturns() {
        // Simulate recent returns - in production, use actual historical data
        return Array.from({ length: 100 }, () => Math.random() * 0.1 - 0.05);
    }

    calculateConcentrationMetrics() {
        const portfolioValue = this.calculateTotalPortfolioValue();
        const concentrations = {};
        
        for (const position of this.positions.values()) {
            concentrations[position.asset] = position.notional / portfolioValue;
        }

        return {
            topPosition: Math.max(...Object.values(concentrations)),
            herfindahlIndex: this.calculateHerfindahlIndex(concentrations),
            concentrations
        };
    }

    calculateHerfindahlIndex(concentrations) {
        let hhi = 0;
        for (const concentration of Object.values(concentrations)) {
            hhi += Math.pow(concentration, 2);
        }
        return hhi;
    }

    getPositionsAtRisk() {
        const atRisk = [];
        
        for (const [positionId, riskMetric] of this.riskMetrics) {
            if (riskMetric.totalRiskScore > 5) {
                atRisk.push({
                    positionId,
                    asset: riskMetric.asset,
                    riskScore: riskMetric.totalRiskScore,
                    breaches: riskMetric.breachStatus.length
                });
            }
        }

        return atRisk;
    }

    calculatePortfolioRiskScore(varValue, drawdown, concentration) {
        const varScore = Math.min(varValue / 1000, 1) * 4; // Scale VaR to 0-4
        const drawdownScore = Math.min(drawdown / 0.2, 1) * 3; // Scale drawdown to 0-3
        const concentrationScore = Math.min(concentration.herfindahlIndex / 0.5, 1) * 3; // Scale HHI to 0-3
        
        return varScore + drawdownScore + concentrationScore;
    }

    // Circuit Breaker Management
    checkCircuitBreakers(marketConditions) {
        const triggeredBreakers = [];
        
        for (const breaker of this.circuitBreakers) {
            if (this.shouldTriggerCircuitBreaker(breaker, marketConditions)) {
                triggeredBreakers.push(breaker);
                this.triggerCircuitBreaker(breaker, marketConditions);
            }
        }

        return triggeredBreakers;
    }

    shouldTriggerCircuitBreaker(breaker, conditions) {
        switch (breaker) {
            case 'PRICE_DISLOCATION':
                return conditions.priceChange > 0.15; // 15% price move
            case 'VOLUME_SPIKE':
                return conditions.volumeRatio > 5; // 5x normal volume
            case 'VOLATILITY_SURGE':
                return conditions.volatility > 0.05; // 5% volatility
            default:
                return false;
        }
    }

    triggerCircuitBreaker(breaker, conditions) {
        console.warn(`âš¡ CIRCUIT BREAKER TRIGGERED: ${breaker}`, conditions);
        
        // Implement breaker-specific actions
        switch (breaker) {
            case 'PRICE_DISLOCATION':
                this.haltTradingTemporarily(300); // 5 minutes
                break;
            case 'VOLUME_SPIKE':
                this.reducePositionLimits(0.5); // Reduce limits by 50%
                break;
            case 'VOLATILITY_SURGE':
                this.increaseMarginRequirements(1.5); // Increase margin by 50%
                break;
        }
    }

    haltTradingTemporarily(seconds) {
        console.log(`â¸ï¸ Trading halted for ${seconds} seconds`);
        // Implement trading halt logic
    }

    reducePositionLimits(factor) {
        this.riskLimits.maxPositionSize *= factor;
        console.log(`ï¿½ï¿½ Position limits reduced by factor ${factor}`);
    }

    increaseMarginRequirements(factor) {
        console.log(`í²° Margin requirements increased by factor ${factor}`);
        // Implement margin adjustment logic
    }

    // Risk Reporting
    generateRiskReport() {
        const portfolioRisk = this.monitorPortfolioRisk();
        const positionsAtRisk = this.getPositionsAtRisk();
        
        return {
            reportId: `risk_report_${Date.now()}`,
            timestamp: new Date(),
            summary: {
                portfolioValue: portfolioRisk.portfolioValue,
                overallRiskScore: portfolioRisk.overallRiskScore,
                valueAtRisk: portfolioRisk.valueAtRisk,
                maxDrawdown: portfolioRisk.maxDrawdown
            },
            positions: {
                total: this.positions.size,
                atRisk: positionsAtRisk.length,
                details: positionsAtRisk
            },
            limits: this.riskLimits,
            recommendations: this.generateRiskRecommendations(portfolioRisk, positionsAtRisk)
        };
    }

    generateRiskRecommendations(portfolioRisk, positionsAtRisk) {
        const recommendations = [];
        
        if (portfolioRisk.overallRiskScore > 7) {
            recommendations.push({
                type: 'PORTFOLIO',
                priority: 'HIGH',
                action: 'Reduce overall portfolio risk',
                details: 'Consider reducing position sizes or adding hedges'
            });
        }

        if (portfolioRisk.concentration.topPosition > 0.15) {
            recommendations.push({
                type: 'CONCENTRATION',
                priority: 'MEDIUM',
                action: 'Diversify portfolio',
                details: 'Top position concentration exceeds 15%'
            });
        }

        for (const position of positionsAtRisk) {
            if (position.riskScore > 8) {
                recommendations.push({
                    type: 'POSITION',
                    priority: 'HIGH',
                    action: `Review position ${position.positionId}`,
                    details: `High risk score: ${position.riskScore}`
                });
            }
        }

        return recommendations;
    }
}

module.exports = QuantumNexRiskMonitor;
