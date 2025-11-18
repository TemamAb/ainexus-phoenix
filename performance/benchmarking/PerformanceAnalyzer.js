/**
 * AI-NEXUS PERFORMANCE ANALYZER
 * Comprehensive performance analysis and optimization recommendations
 */

const { ethers } = require('ethers');

class PerformanceAnalyzer {
    constructor(config) {
        this.config = config;
        this.performanceData = new Map();
        this.analysisHistory = [];
        this.benchmarkThresholds = config.benchmarkThresholds || {
            latency: 1000, // ms
            successRate: 0.95, // 95%
            gasEfficiency: 0.8, // 80% of theoretical max
            profitMargin: 0.01 // 1%
        };
    }

    async analyzeStrategyPerformance(strategyData) {
        /**
         * Comprehensive analysis of strategy performance
         */
        const analysis = {
            timestamp: new Date(),
            strategyId: strategyData.id,
            basicMetrics: this.calculateBasicMetrics(strategyData),
            riskMetrics: this.calculateRiskMetrics(strategyData),
            efficiencyMetrics: this.calculateEfficiencyMetrics(strategyData),
            comparativeAnalysis: await this.performComparativeAnalysis(strategyData),
            recommendations: [],
            overallScore: 0
        };

        // Generate recommendations
        analysis.recommendations = this.generateRecommendations(analysis);

        // Calculate overall performance score
        analysis.overallScore = this.calculateOverallScore(analysis);

        // Store analysis
        this.performanceData.set(strategyData.id, analysis);
        this.analysisHistory.push(analysis);

        return analysis;
    }

    calculateBasicMetrics(strategyData) {
        const trades = strategyData.trades || [];
        const successfulTrades = trades.filter(t => t.profit > 0);
        const failedTrades = trades.filter(t => t.profit <= 0);

        const totalProfit = trades.reduce((sum, trade) => sum + trade.profit, 0);
        const totalVolume = trades.reduce((sum, trade) => sum + Math.abs(trade.volume), 0);

        return {
            totalTrades: trades.length,
            successfulTrades: successfulTrades.length,
            failedTrades: failedTrades.length,
            winRate: trades.length > 0 ? successfulTrades.length / trades.length : 0,
            totalProfit: totalProfit,
            totalVolume: totalVolume,
            avgProfitPerTrade: trades.length > 0 ? totalProfit / trades.length : 0,
            profitPerVolume: totalVolume > 0 ? totalProfit / totalVolume : 0
        };
    }

    calculateRiskMetrics(strategyData) {
        const trades = strategyData.trades || [];
        if (trades.length === 0) {
            return {
                sharpeRatio: 0,
                maxDrawdown: 0,
                volatility: 0,
                var95: 0
            };
        }

        const profits = trades.map(t => t.profit);
        const cumulativeReturns = this.calculateCumulativeReturns(profits);

        return {
            sharpeRatio: this.calculateSharpeRatio(profits),
            maxDrawdown: this.calculateMaxDrawdown(cumulativeReturns),
            volatility: this.calculateVolatility(profits),
            var95: this.calculateValueAtRisk(profits, 0.95),
            profitFactor: this.calculateProfitFactor(trades)
        };
    }

    calculateEfficiencyMetrics(strategyData) {
        const trades = strategyData.trades || [];
        if (trades.length === 0) {
            return {
                gasEfficiency: 0,
                latencyEfficiency: 0,
                capitalEfficiency: 0,
                successRate: 0
            };
        }

        const totalGasCost = trades.reduce((sum, trade) => sum + (trade.gasCost || 0), 0);
        const totalSlippage = trades.reduce((sum, trade) => sum + (trade.slippage || 0), 0);
        const totalExecutionTime = trades.reduce((sum, trade) => sum + (trade.executionTime || 0), 0);

        return {
            gasEfficiency: this.calculateGasEfficiency(trades, totalGasCost),
            latencyEfficiency: this.calculateLatencyEfficiency(trades, totalExecutionTime),
            capitalEfficiency: this.calculateCapitalEfficiency(trades),
            successRate: trades.filter(t => t.success).length / trades.length,
            avgGasPerTrade: totalGasCost / trades.length,
            avgSlippagePerTrade: totalSlippage / trades.length
        };
    }

    calculateSharpeRatio(returns, riskFreeRate = 0.02) {
        if (returns.length < 2) return 0;

        const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
        const stdDev = Math.sqrt(returns.reduce((a, b) => a + Math.pow(b - avgReturn, 2), 0) / returns.length);
        
        if (stdDev === 0) return 0;

        const dailyRiskFree = riskFreeRate / 365;
        return (avgReturn - dailyRiskFree) / stdDev;
    }

    calculateMaxDrawdown(cumulativeReturns) {
        let maxDrawdown = 0;
        let peak = cumulativeReturns[0];

        for (let i = 1; i < cumulativeReturns.length; i++) {
            if (cumulativeReturns[i] > peak) {
                peak = cumulativeReturns[i];
            } else {
                const drawdown = (peak - cumulativeReturns[i]) / peak;
                maxDrawdown = Math.max(maxDrawdown, drawdown);
            }
        }

        return maxDrawdown;
    }

    calculateCumulativeReturns(returns) {
        const cumulative = [];
        let sum = 0;

        for (const ret of returns) {
            sum += ret;
            cumulative.push(sum);
        }

        return cumulative;
    }

    calculateVolatility(returns) {
        if (returns.length < 2) return 0;

        const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
        const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length;
        
        return Math.sqrt(variance);
    }

    calculateValueAtRisk(returns, confidenceLevel) {
        if (returns.length === 0) return 0;

        const sortedReturns = [...returns].sort((a, b) => a - b);
        const index = Math.floor((1 - confidenceLevel) * sortedReturns.length);
        
        return Math.abs(sortedReturns[Math.max(0, index - 1)]);
    }

    calculateProfitFactor(trades) {
        const grossProfit = trades.filter(t => t.profit > 0).reduce((sum, t) => sum + t.profit, 0);
        const grossLoss = Math.abs(trades.filter(t => t.profit < 0).reduce((sum, t) => sum + t.profit, 0));

        return grossLoss > 0 ? grossProfit / grossLoss : grossProfit > 0 ? Infinity : 0;
    }

    calculateGasEfficiency(trades, totalGasCost) {
        const totalProfit = trades.reduce((sum, t) => sum + t.profit, 0);
        return totalGasCost > 0 ? totalProfit / totalGasCost : 0;
    }

    calculateLatencyEfficiency(trades, totalExecutionTime) {
        if (trades.length === 0 || totalExecutionTime === 0) return 0;

        const avgProfitPerSecond = trades.reduce((sum, t) => sum + t.profit, 0) / totalExecutionTime;
        return Math.min(avgProfitPerSecond * 1000, 1); // Normalize
    }

    calculateCapitalEfficiency(trades) {
        const totalCapitalDeployed = trades.reduce((sum, t) => sum + (t.capitalUsed || 0), 0);
        const totalProfit = trades.reduce((sum, t) => sum + t.profit, 0);

        return totalCapitalDeployed > 0 ? totalProfit / totalCapitalDeployed : 0;
    }

    async performComparativeAnalysis(strategyData) {
        const similarStrategies = await this.findSimilarStrategies(strategyData);
        const comparison = {};

        if (similarStrategies.length > 0) {
            const currentMetrics = this.calculateBasicMetrics(strategyData);
            const peerMetrics = similarStrategies.map(s => this.calculateBasicMetrics(s));

            comparison.winRatePercentile = this.calculatePercentile(
                currentMetrics.winRate,
                peerMetrics.map(m => m.winRate)
            );

            comparison.profitPercentile = this.calculatePercentile(
                currentMetrics.avgProfitPerTrade,
                peerMetrics.map(m => m.avgProfitPerTrade)
            );

            comparison.ranking = this.calculateStrategyRanking(strategyData, similarStrategies);
        }

        return comparison;
    }

    async findSimilarStrategies(strategyData) {
        // Implementation would search for strategies with similar characteristics
        // For now, return empty array
        return [];
    }

    calculatePercentile(value, values) {
        if (values.length === 0) return 0;

        const sorted = [...values].sort((a, b) => a - b);
        const count = sorted.filter(v => v <= value).length;
        
        return count / sorted.length;
    }

    calculateStrategyRanking(targetStrategy, peerStrategies) {
        if (peerStrategies.length === 0) return 1;

        const targetScore = this.calculateOverallScore({ basicMetrics: this.calculateBasicMetrics(targetStrategy) });
        const peerScores = peerStrategies.map(s => 
            this.calculateOverallScore({ basicMetrics: this.calculateBasicMetrics(s) })
        );

        const betterStrategies = peerScores.filter(score => score > targetScore).length;
        return betterStrategies + 1; // Rank (1 is best)
    }

    generateRecommendations(analysis) {
        const recommendations = [];
        const { basicMetrics, riskMetrics, efficiencyMetrics } = analysis;

        // Profitability recommendations
        if (basicMetrics.winRate < 0.6) {
            recommendations.push({
                type: 'PROFITABILITY',
                priority: 'HIGH',
                message: `Improve win rate (current: ${(basicMetrics.winRate * 100).toFixed(1)}%)`,
                suggestion: 'Review entry/exit criteria and risk management'
            });
        }

        if (basicMetrics.avgProfitPerTrade < this.benchmarkThresholds.profitMargin) {
            recommendations.push({
                type: 'PROFITABILITY',
                priority: 'MEDIUM',
                message: `Increase average profit per trade (current: ${basicMetrics.avgProfitPerTrade.toFixed(4)} ETH)`,
                suggestion: 'Optimize position sizing and execution timing'
            });
        }

        // Risk management recommendations
        if (riskMetrics.maxDrawdown > 0.1) {
            recommendations.push({
                type: 'RISK_MANAGEMENT',
                priority: 'HIGH',
                message: `Reduce maximum drawdown (current: ${(riskMetrics.maxDrawdown * 100).toFixed(1)}%)`,
                suggestion: 'Implement stricter stop-loss and position limits'
            });
        }

        if (riskMetrics.sharpeRatio < 1.0) {
            recommendations.push({
                type: 'RISK_MANAGEMENT',
                priority: 'MEDIUM',
                message: `Improve risk-adjusted returns (Sharpe ratio: ${riskMetrics.sharpeRatio.toFixed(2)})`,
                suggestion: 'Diversify strategies and reduce volatility'
            });
        }

        // Efficiency recommendations
        if (efficiencyMetrics.gasEfficiency < this.benchmarkThresholds.gasEfficiency) {
            recommendations.push({
                type: 'EFFICIENCY',
                priority: 'MEDIUM',
                message: 'Optimize gas usage for better cost efficiency',
                suggestion: 'Batch transactions and use gas optimization techniques'
            });
        }

        if (efficiencyMetrics.successRate < this.benchmarkThresholds.successRate) {
            recommendations.push({
                type: 'RELIABILITY',
                priority: 'HIGH',
                message: `Improve transaction success rate (current: ${(efficiencyMetrics.successRate * 100).toFixed(1)}%)`,
                suggestion: 'Review RPC endpoints and transaction parameters'
            });
        }

        return recommendations;
    }

    calculateOverallScore(analysis) {
        const weights = {
            profitability: 0.35,
            risk: 0.30,
            efficiency: 0.20,
            reliability: 0.15
        };

        let score = 0;

        // Profitability score (win rate and profit factor)
        const profitabilityScore = Math.min(
            analysis.basicMetrics.winRate * 2, // Double weight for win rate
            analysis.riskMetrics.profitFactor / 5 // Normalize profit factor
        );
        score += profitabilityScore * weights.profitability;

        // Risk score (inverse of drawdown and volatility)
        const riskScore = Math.max(0, 1 - (analysis.riskMetrics.maxDrawdown * 10)); // Penalize drawdown
        score += riskScore * weights.risk;

        // Efficiency score (gas and capital efficiency)
        const efficiencyScore = Math.min(
            analysis.efficiencyMetrics.gasEfficiency * 2,
            analysis.efficiencyMetrics.capitalEfficiency * 2
        );
        score += efficiencyScore * weights.efficiency;

        // Reliability score (success rate)
        const reliabilityScore = analysis.efficiencyMetrics.successRate;
        score += reliabilityScore * weights.reliability;

        return Math.min(1, Math.max(0, score));
    }

    getPerformanceTrend(strategyId, period = '30d') {
        const historicalData = this.analysisHistory.filter(
            analysis => analysis.strategyId === strategyId &&
                       analysis.timestamp > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        );

        if (historicalData.length < 2) {
            return { trend: 'insufficient_data', confidence: 0 };
        }

        const scores = historicalData.map(d => d.overallScore);
        const dates = historicalData.map(d => d.timestamp.getTime());

        // Simple linear regression for trend
        const n = scores.length;
        const sumX = dates.reduce((a, b) => a + b, 0);
        const sumY = scores.reduce((a, b) => a + b, 0);
        const sumXY = dates.reduce((a, date, i) => a + date * scores[i], 0);
        const sumX2 = dates.reduce((a, b) => a + b * b, 0);

        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const avgScore = sumY / n;

        let trend;
        if (slope > 0.000001) trend = 'improving';
        else if (slope < -0.000001) trend = 'declining';
        else trend = 'stable';

        return {
            trend,
            slope,
            currentScore: scores[scores.length - 1],
            averageScore: avgScore,
            confidence: Math.abs(slope) * 1000000 // Simple confidence measure
        };
    }

    generatePerformanceReport(strategyId) {
        const analysis = this.performanceData.get(strategyId);
        if (!analysis) {
            return { error: 'No performance data available for strategy' };
        }

        const trend = this.getPerformanceTrend(strategyId);

        return {
            strategyId,
            timestamp: new Date(),
            overallScore: analysis.overallScore,
            performanceGrade: this.scoreToGrade(analysis.overallScore),
            trend: trend.trend,
            trendConfidence: trend.confidence,
            keyMetrics: {
                profitability: analysis.basicMetrics,
                risk: analysis.riskMetrics,
                efficiency: analysis.efficiencyMetrics
            },
            recommendations: analysis.recommendations,
            comparativeAnalysis: analysis.comparativeAnalysis
        };
    }

    scoreToGrade(score) {
        if (score >= 0.9) return 'A+';
        if (score >= 0.8) return 'A';
        if (score >= 0.7) return 'B';
        if (score >= 0.6) return 'C';
        if (score >= 0.5) return 'D';
        return 'F';
    }

    getTopPerformers(limit = 5) {
        const allAnalyses = Array.from(this.performanceData.values());
        return allAnalyses
            .sort((a, b) => b.overallScore - a.overallScore)
            .slice(0, limit)
            .map(analysis => ({
                strategyId: analysis.strategyId,
                score: analysis.overallScore,
                grade: this.scoreToGrade(analysis.overallScore),
                winRate: analysis.basicMetrics.winRate,
                totalProfit: analysis.basicMetrics.totalProfit
            }));
    }

    getPerformanceSummary() {
        const allAnalyses = Array.from(this.performanceData.values());
        if (allAnalyses.length === 0) {
            return { error: 'No performance data available' };
        }

        const scores = allAnalyses.map(a => a.overallScore);
        const winRates = allAnalyses.map(a => a.basicMetrics.winRate);
        const profits = allAnalyses.map(a => a.basicMetrics.totalProfit);

        return {
            totalStrategies: allAnalyses.length,
            averageScore: scores.reduce((a, b) => a + b, 0) / scores.length,
            averageWinRate: winRates.reduce((a, b) => a + b, 0) / winRates.length,
            totalProfit: profits.reduce((a, b) => a + b, 0),
            topPerformer: this.getTopPerformers(1)[0],
            strategiesByGrade: this.getStrategiesByGrade(allAnalyses)
        };
    }

    getStrategiesByGrade(analyses) {
        const grades = {
            'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0
        };

        analyses.forEach(analysis => {
            const grade = this.scoreToGrade(analysis.overallScore);
            grades[grade]++;
        });

        return grades;
    }
}

module.exports = PerformanceAnalyzer;
