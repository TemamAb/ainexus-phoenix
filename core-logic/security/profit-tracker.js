// QUANTUMNEX PROFIT TRACKER
// Industry Standards: QuantConnect LEAN, Portfolio performance metrics
// Validated Sources:
// - QuantConnect LEAN (Algorithmic trading engine)
// - Portfolio performance metrics
// - P&L calculation methodologies
// - Performance analytics frameworks

const { v4: uuidv4 } = require('uuid');

class QuantumNexProfitTracker {
    constructor() {
        this.trades = new Map();
        this.portfolios = new Map();
        this.performanceMetrics = new Map();
        this.dailySnapshots = new Map();
        this.setupDefaultPortfolios();
    }

    setupDefaultPortfolios() {
        // Initialize default portfolio structure
        this.portfolios.set('MAIN', {
            id: 'MAIN',
            name: 'Main Trading Portfolio',
            currency: 'USD',
            initialCapital: 100000,
            currentValue: 100000,
            createdAt: new Date(),
            strategies: new Set()
        });
    }

    // Trade Recording
    recordTrade(tradeData) {
        const tradeId = tradeData.id || uuidv4();
        
        const trade = {
            id: tradeId,
            portfolioId: tradeData.portfolioId || 'MAIN',
            symbol: tradeData.symbol,
            type: tradeData.type, // 'BUY' or 'SELL'
            quantity: tradeData.quantity,
            price: tradeData.price,
            currency: tradeData.currency || 'USD',
            timestamp: tradeData.timestamp || new Date(),
            fees: tradeData.fees || 0,
            strategy: tradeData.strategy || 'DEFAULT',
            ...tradeData
        };

        // Calculate trade P&L if it's a sell order
        if (trade.type === 'SELL') {
            trade.realizedPnl = this.calculateRealizedPnl(trade);
        }

        this.trades.set(tradeId, trade);
        
        // Update portfolio performance
        this.updatePortfolioPerformance(trade.portfolioId);
        
        this.logTradeEvent('TRADE_RECORDED', trade);
        
        return trade;
    }

    calculateRealizedPnl(sellTrade) {
        // Find matching buy trades for this symbol
        const buyTrades = Array.from(this.trades.values())
            .filter(t => 
                t.symbol === sellTrade.symbol && 
                t.type === 'BUY' &&
                t.portfolioId === sellTrade.portfolioId
            )
            .sort((a, b) => a.timestamp - b.timestamp);

        let remainingQuantity = sellTrade.quantity;
        let totalCost = 0;
        let realizedPnl = 0;

        for (const buyTrade of buyTrades) {
            if (remainingQuantity <= 0) break;

            const availableQuantity = buyTrade.quantity - (buyTrade.allocatedQuantity || 0);
            const allocatedQuantity = Math.min(remainingQuantity, availableQuantity);

            if (allocatedQuantity > 0) {
                const cost = allocatedQuantity * buyTrade.price;
                const proceeds = allocatedQuantity * sellTrade.price;
                const tradePnl = proceeds - cost - (sellTrade.fees / sellTrade.quantity * allocatedQuantity);

                realizedPnl += tradePnl;
                totalCost += cost;
                remainingQuantity -= allocatedQuantity;

                // Update buy trade allocated quantity
                buyTrade.allocatedQuantity = (buyTrade.allocatedQuantity || 0) + allocatedQuantity;
                this.trades.set(buyTrade.id, buyTrade);
            }
        }

        return realizedPnl;
    }

    // Portfolio Performance Tracking
    updatePortfolioPerformance(portfolioId) {
        const portfolio = this.portfolios.get(portfolioId);
        if (!portfolio) return;

        const trades = Array.from(this.trades.values())
            .filter(t => t.portfolioId === portfolioId);

        const performance = this.calculatePortfolioMetrics(portfolio, trades);
        this.performanceMetrics.set(portfolioId, performance);

        // Take daily snapshot
        this.takeDailySnapshot(portfolioId, performance);
    }

    calculatePortfolioMetrics(portfolio, trades) {
        const currentValue = this.calculatePortfolioValue(portfolio.id);
        const realizedPnl = this.calculateRealizedPnlTotal(trades);
        const unrealizedPnl = this.calculateUnrealizedPnl(portfolio.id, trades);
        const totalPnl = realizedPnl + unrealizedPnl;

        return {
            portfolioId: portfolio.id,
            timestamp: new Date(),
            currentValue,
            initialCapital: portfolio.initialCapital,
            realizedPnl,
            unrealizedPnl,
            totalPnl,
            totalReturn: (totalPnl / portfolio.initialCapital) * 100,
            sharpeRatio: this.calculateSharpeRatio(portfolio.id),
            maxDrawdown: this.calculateMaxDrawdown(portfolio.id),
            volatility: this.calculateVolatility(portfolio.id),
            winRate: this.calculateWinRate(trades),
            profitFactor: this.calculateProfitFactor(trades)
        };
    }

    calculatePortfolioValue(portfolioId) {
        // Simplified portfolio value calculation
        // In production, this would use current market prices
        const trades = Array.from(this.trades.values())
            .filter(t => t.portfolioId === portfolioId);

        let value = this.portfolios.get(portfolioId).initialCapital;
        
        for (const trade of trades) {
            if (trade.type === 'BUY') {
                value -= trade.quantity * trade.price + trade.fees;
            } else {
                value += trade.quantity * trade.price - trade.fees;
            }
        }

        return value;
    }

    calculateRealizedPnlTotal(trades) {
        return trades
            .filter(t => t.realizedPnl)
            .reduce((sum, t) => sum + t.realizedPnl, 0);
    }

    calculateUnrealizedPnl(portfolioId, trades) {
        // Simplified unrealized PnL calculation
        // In production, this would use current market prices
        const openPositions = this.getOpenPositions(portfolioId);
        let unrealizedPnl = 0;

        for (const position of openPositions) {
            // Assume current price is 5% higher than average entry price for demo
            const currentPrice = position.averageEntryPrice * 1.05;
            unrealizedPnl += (currentPrice - position.averageEntryPrice) * position.quantity;
        }

        return unrealizedPnl;
    }

    getOpenPositions(portfolioId) {
        const trades = Array.from(this.trades.values())
            .filter(t => t.portfolioId === portfolioId);

        const positions = new Map();

        for (const trade of trades) {
            if (!positions.has(trade.symbol)) {
                positions.set(trade.symbol, {
                    symbol: trade.symbol,
                    quantity: 0,
                    totalCost: 0,
                    averageEntryPrice: 0
                });
            }

            const position = positions.get(trade.symbol);

            if (trade.type === 'BUY') {
                const allocatedQuantity = trade.allocatedQuantity || 0;
                const unallocatedQuantity = trade.quantity - allocatedQuantity;
                
                position.quantity += unallocatedQuantity;
                position.totalCost += unallocatedQuantity * trade.price;
            } else {
                position.quantity -= trade.quantity;
            }

            position.averageEntryPrice = position.quantity > 0 ? 
                position.totalCost / position.quantity : 0;
        }

        return Array.from(positions.values()).filter(p => p.quantity > 0);
    }

    // Advanced Performance Metrics
    calculateSharpeRatio(portfolioId, riskFreeRate = 0.02) {
        const returns = this.getPortfolioReturns(portfolioId);
        if (returns.length < 2) return 0;

        const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
        const stdDev = Math.sqrt(
            returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length
        );

        return stdDev > 0 ? (avgReturn - riskFreeRate) / stdDev : 0;
    }

    calculateMaxDrawdown(portfolioId) {
        const values = this.getPortfolioValueHistory(portfolioId);
        if (values.length === 0) return 0;

        let maxDrawdown = 0;
        let peak = values[0];

        for (const value of values) {
            if (value > peak) peak = value;
            const drawdown = (peak - value) / peak;
            maxDrawdown = Math.max(maxDrawdown, drawdown);
        }

        return maxDrawdown;
    }

    calculateVolatility(portfolioId) {
        const returns = this.getPortfolioReturns(portfolioId);
        if (returns.length < 2) return 0;

        const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
        const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
        
        return Math.sqrt(variance);
    }

    calculateWinRate(trades) {
        const profitableTrades = trades.filter(t => t.realizedPnl > 0);
        return trades.length > 0 ? (profitableTrades.length / trades.length) * 100 : 0;
    }

    calculateProfitFactor(trades) {
        const grossProfit = trades
            .filter(t => t.realizedPnl > 0)
            .reduce((sum, t) => sum + t.realizedPnl, 0);

        const grossLoss = Math.abs(trades
            .filter(t => t.realizedPnl < 0)
            .reduce((sum, t) => sum + t.realizedPnl, 0));

        return grossLoss > 0 ? grossProfit / grossLoss : grossProfit > 0 ? Infinity : 0;
    }

    // Data Management
    getPortfolioReturns(portfolioId) {
        const snapshots = this.dailySnapshots.get(portfolioId) || [];
        const returns = [];

        for (let i = 1; i < snapshots.length; i++) {
            const prevValue = snapshots[i - 1].currentValue;
            const currentValue = snapshots[i].currentValue;
            const dailyReturn = (currentValue - prevValue) / prevValue;
            returns.push(dailyReturn);
        }

        return returns;
    }

    getPortfolioValueHistory(portfolioId) {
        const snapshots = this.dailySnapshots.get(portfolioId) || [];
        return snapshots.map(s => s.currentValue);
    }

    takeDailySnapshot(portfolioId, performance) {
        const today = new Date().toDateString();
        
        if (!this.dailySnapshots.has(portfolioId)) {
            this.dailySnapshots.set(portfolioId, []);
        }

        const snapshots = this.dailySnapshots.get(portfolioId);
        
        // Check if we already have a snapshot for today
        const existingIndex = snapshots.findIndex(s => 
            new Date(s.timestamp).toDateString() === today
        );

        if (existingIndex >= 0) {
            snapshots[existingIndex] = performance;
        } else {
            snapshots.push(performance);
        }
    }

    // Reporting and Analytics
    generatePerformanceReport(portfolioId, timeframe = 'ALL') {
        const performance = this.performanceMetrics.get(portfolioId);
        const snapshots = this.dailySnapshots.get(portfolioId) || [];
        
        let filteredSnapshots = snapshots;
        if (timeframe !== 'ALL') {
            const cutoffDate = this.getCutoffDate(timeframe);
            filteredSnapshots = snapshots.filter(s => new Date(s.timestamp) >= cutoffDate);
        }

        return {
            portfolioId,
            timeframe,
            generatedAt: new Date(),
            currentPerformance: performance,
            historicalSnapshots: filteredSnapshots,
            summary: this.generateSummary(performance, filteredSnapshots)
        };
    }

    getCutoffDate(timeframe) {
        const now = new Date();
        switch (timeframe) {
            case 'WEEK':
                return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            case 'MONTH':
                return new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
            case 'QUARTER':
                return new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());
            case 'YEAR':
                return new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
            default:
                return new Date(0);
        }
    }

    generateSummary(performance, snapshots) {
        if (snapshots.length === 0) return {};

        const firstSnapshot = snapshots[0];
        const lastSnapshot = snapshots[snapshots.length - 1];

        return {
            totalReturn: ((lastSnapshot.currentValue - firstSnapshot.initialCapital) / firstSnapshot.initialCapital) * 100,
            bestDay: Math.max(...snapshots.map(s => s.totalPnl)),
            worstDay: Math.min(...snapshots.map(s => s.totalPnl)),
            averageDailyReturn: snapshots.reduce((sum, s) => sum + s.totalPnl, 0) / snapshots.length,
            tradingDays: snapshots.length
        };
    }

    // Strategy Performance Analysis
    analyzeStrategyPerformance(portfolioId) {
        const trades = Array.from(this.trades.values())
            .filter(t => t.portfolioId === portfolioId);

        const strategies = new Map();

        for (const trade of trades) {
            if (!strategies.has(trade.strategy)) {
                strategies.set(trade.strategy, {
                    strategy: trade.strategy,
                    trades: [],
                    totalPnl: 0,
                    winRate: 0
                });
            }

            const strategy = strategies.get(trade.strategy);
            strategy.trades.push(trade);
            
            if (trade.realizedPnl) {
                strategy.totalPnl += trade.realizedPnl;
            }
        }

        // Calculate additional metrics for each strategy
        for (const strategy of strategies.values()) {
            const profitableTrades = strategy.trades.filter(t => t.realizedPnl > 0);
            strategy.winRate = strategy.trades.length > 0 ? 
                (profitableTrades.length / strategy.trades.length) * 100 : 0;
            
            strategy.averageWin = profitableTrades.length > 0 ?
                profitableTrades.reduce((sum, t) => sum + t.realizedPnl, 0) / profitableTrades.length : 0;
            
            const losingTrades = strategy.trades.filter(t => t.realizedPnl < 0);
            strategy.averageLoss = losingTrades.length > 0 ?
                losingTrades.reduce((sum, t) => sum + t.realizedPnl, 0) / losingTrades.length : 0;
        }

        return Array.from(strategies.values());
    }

    // Risk-Adjusted Performance
    calculateRiskAdjustedMetrics(portfolioId) {
        const performance = this.performanceMetrics.get(portfolioId);
        if (!performance) return null;

        return {
            sharpeRatio: performance.sharpeRatio,
            sortinoRatio: this.calculateSortinoRatio(portfolioId),
            calmarRatio: this.calculateCalmarRatio(portfolioId),
            treynorRatio: this.calculateTreynorRatio(portfolioId)
        };
    }

    calculateSortinoRatio(portfolioId, riskFreeRate = 0.02) {
        const returns = this.getPortfolioReturns(portfolioId);
        const negativeReturns = returns.filter(r => r < 0);
        
        if (negativeReturns.length === 0) return 0;

        const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
        const downsideDeviation = Math.sqrt(
            negativeReturns.reduce((sum, ret) => sum + Math.pow(ret, 2), 0) / negativeReturns.length
        );

        return downsideDeviation > 0 ? (avgReturn - riskFreeRate) / downsideDeviation : 0;
    }

    calculateCalmarRatio(portfolioId) {
        const performance = this.performanceMetrics.get(portfolioId);
        if (!performance || performance.maxDrawdown === 0) return 0;

        const annualReturn = performance.totalReturn / (this.getPortfolioAgeInYears(portfolioId) || 1);
        return annualReturn / performance.maxDrawdown;
    }

    calculateTreynorRatio(portfolioId, riskFreeRate = 0.02) {
        // Simplified Treynor ratio (would need beta in production)
        const performance = this.performanceMetrics.get(portfolioId);
        if (!performance) return 0;

        const beta = 1.0; // Assume market beta of 1.0 for demo
        const annualReturn = performance.totalReturn / (this.getPortfolioAgeInYears(portfolioId) || 1);
        
        return beta > 0 ? (annualReturn - riskFreeRate) / beta : 0;
    }

    getPortfolioAgeInYears(portfolioId) {
        const portfolio = this.portfolios.get(portfolioId);
        if (!portfolio) return 0;

        const ageInMs = Date.now() - portfolio.createdAt.getTime();
        return ageInMs / (365 * 24 * 60 * 60 * 1000);
    }

    // Event Logging
    logTradeEvent(eventType, data) {
        const event = {
            id: uuidv4(),
            type: eventType,
            timestamp: new Date(),
            data
        };

        console.log('í³Š TRADE EVENT:', event);
        return event;
    }

    // Data Export
    exportTradeHistory(portfolioId, format = 'JSON') {
        const trades = Array.from(this.trades.values())
            .filter(t => t.portfolioId === portfolioId)
            .sort((a, b) => a.timestamp - b.timestamp);

        switch (format) {
            case 'JSON':
                return JSON.stringify(trades, null, 2);
            case 'CSV':
                return this.convertToCSV(trades);
            default:
                return trades;
        }
    }

    convertToCSV(trades) {
        if (trades.length === 0) return '';
        
        const headers = Object.keys(trades[0]).join(',');
        const rows = trades.map(trade => 
            Object.values(trade).map(value => 
                typeof value === 'string' ? `"${value}"` : value
            ).join(',')
        );
        
        return [headers, ...rows].join('\n');
    }
}

module.exports = QuantumNexProfitTracker;
