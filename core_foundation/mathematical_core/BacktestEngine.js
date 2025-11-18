/**
 * AI-NEXUS v5.0 - Backtesting Engine
 * 7P-PILLAR: BOT5-MATH
 * PURPOSE: Comprehensive strategy backtesting with simulations
 */

class BacktestEngine {
    constructor(config) {
        this.config = config;
        this.backtestResults = new Map();
        this.performanceMetrics = {};
    }

    async runBacktest(strategy, historicalData, parameters = {}) {
        const backtestId = this.generateBacktestId();
        
        try {
            // Initialize backtest state
            const initialState = this.initializeBacktestState(parameters);
            
            // Execute strategy on historical data
            const results = await this.executeStrategyBacktest(strategy, historicalData, initialState);
            
            // Calculate performance metrics
            const metrics = this.calculatePerformanceMetrics(results);
            
            // Store results
            const backtestResult = {
                id: backtestId,
                strategy: strategy.name,
                parameters,
                results,
                metrics,
                timestamp: new Date().toISOString()
            };
            
            this.backtestResults.set(backtestId, backtestResult);
            return backtestResult;
            
        } catch (error) {
            throw new Error(`Backtest failed: ${error.message}`);
        }
    }

    initializeBacktestState(parameters) {
        return {
            capital: parameters.initialCapital || 100000,
            position: 0,
            cash: parameters.initialCapital || 100000,
            trades: [],
            portfolioValue: [],
            currentStep: 0,
            transactionCost: parameters.transactionCost || 0.002 // 0.2%
        };
    }

    async executeStrategyBacktest(strategy, historicalData, state) {
        const results = {
            trades: [],
            portfolioValues: [],
            returns: [],
            timestamps: []
        };

        // Initialize strategy
        let strategyState = strategy.initialize(historicalData);
        
        for (let i = 0; i < historicalData.length; i++) {
            const currentData = historicalData[i];
            const currentPrice = currentData.price;
            
            // Get strategy signal
            const signal = await strategy.generateSignal(currentData, strategyState);
            
            // Execute trade based on signal
            if (signal.action !== 'hold') {
                const tradeResult = this.executeTrade(signal, state, currentPrice, currentData.timestamp);
                if (tradeResult) {
                    results.trades.push(tradeResult);
                }
            }
            
            // Update portfolio value
            const portfolioValue = this.calculatePortfolioValue(state, currentPrice);
            results.portfolioValues.push(portfolioValue);
            results.timestamps.push(currentData.timestamp);
            
            // Update strategy state
            strategyState = strategy.updateState(strategyState, currentData, signal);
            state.currentStep = i;
        }

        return results;
    }

    executeTrade(signal, state, currentPrice, timestamp) {
        const tradeSize = this.calculateTradeSize(signal, state, currentPrice);
        
        if (tradeSize === 0) return null;

        const trade = {
            timestamp,
            action: signal.action,
            size: tradeSize,
            price: currentPrice,
            value: tradeSize * currentPrice,
            fee: this.calculateTransactionFee(tradeSize * currentPrice, state.transactionCost)
        };

        // Update state
        if (signal.action === 'buy') {
            state.position += tradeSize;
            state.cash -= (trade.value + trade.fee);
        } else if (signal.action === 'sell') {
            state.position -= tradeSize;
            state.cash += (trade.value - trade.fee);
        }

        state.trades.push(trade);
        return trade;
    }

    calculateTradeSize(signal, state, currentPrice) {
        const maxPosition = state.capital / currentPrice;
        const positionSize = signal.confidence * maxPosition * 0.1; // 10% of capital per trade
        
        if (signal.action === 'buy') {
            const affordableSize = state.cash / currentPrice;
            return Math.min(positionSize, affordableSize);
        } else if (signal.action === 'sell') {
            return Math.min(positionSize, state.position);
        }
        
        return 0;
    }

    calculateTransactionFee(tradeValue, feeRate) {
        return tradeValue * feeRate;
    }

    calculatePortfolioValue(state, currentPrice) {
        return state.cash + (state.position * currentPrice);
    }

    calculatePerformanceMetrics(results) {
        const portfolioValues = results.portfolioValues;
        const initialValue = portfolioValues[0];
        const finalValue = portfolioValues[portfolioValues.length - 1];
        
        // Calculate returns
        const returns = this.calculateReturns(portfolioValues);
        
        return {
            totalReturn: (finalValue - initialValue) / initialValue,
            sharpeRatio: this.calculateSharpeRatio(returns),
            maxDrawdown: this.calculateMaxDrawdown(portfolioValues),
            volatility: this.calculateVolatility(returns),
            totalTrades: results.trades.length,
            winRate: this.calculateWinRate(results.trades),
            profitFactor: this.calculateProfitFactor(results.trades)
        };
    }

    calculateReturns(portfolioValues) {
        const returns = [];
        for (let i = 1; i < portfolioValues.length; i++) {
            returns.push((portfolioValues[i] - portfolioValues[i-1]) / portfolioValues[i-1]);
        }
        return returns;
    }

    calculateSharpeRatio(returns, riskFreeRate = 0.02) {
        const excessReturns = returns.map(r => r - riskFreeRate / 252); // Daily risk-free
        const meanReturn = excessReturns.reduce((a, b) => a + b, 0) / excessReturns.length;
        const stdDev = Math.sqrt(excessReturns.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / excessReturns.length);
        
        return stdDev > 0 ? (meanReturn * Math.sqrt(252)) / stdDev : 0;
    }

    calculateMaxDrawdown(portfolioValues) {
        let peak = portfolioValues[0];
        let maxDrawdown = 0;
        
        for (const value of portfolioValues) {
            if (value > peak) {
                peak = value;
            }
            const drawdown = (peak - value) / peak;
            maxDrawdown = Math.max(maxDrawdown, drawdown);
        }
        
        return maxDrawdown;
    }

    calculateVolatility(returns) {
        const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
        const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length;
        return Math.sqrt(variance) * Math.sqrt(252); // Annualized
    }

    calculateWinRate(trades) {
        if (trades.length === 0) return 0;
        const profitableTrades = trades.filter(trade => trade.value > 0);
        return profitableTrades.length / trades.length;
    }

    calculateProfitFactor(trades) {
        const grossProfit = trades.filter(t => t.value > 0).reduce((sum, t) => sum + t.value, 0);
        const grossLoss = trades.filter(t => t.value < 0).reduce((sum, t) => sum + Math.abs(t.value), 0);
        return grossLoss > 0 ? grossProfit / grossLoss : Infinity;
    }

    generateBacktestId() {
        return `backtest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getBacktestHistory() {
        return Array.from(this.backtestResults.values());
    }
}

module.exports = BacktestEngine;
