// AINEXUS - PHASE 1 MODULE 6: PROFIT TRACKER
// Performance Analytics & Profit Monitoring

const EventEmitter = require('events');
const fs = require('fs').promises;
const path = require('path');

class ProfitTracker extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.performanceData = {
            trades: [],
            hourly: [],
            daily: [],
            summary: {
                totalProfit: 0,
                totalTrades: 0,
                profitableTrades: 0,
                largestWin: 0,
                largestLoss: 0,
                avgProfit: 0,
                winRate: 0,
                sharpeRatio: 0,
                maxDrawdown: 0
            }
        };
        this.dataFile = path.join(__dirname, '../../data/performance.json');
        this.isTracking = false;
    }

    // Initialize profit tracker
    async initialize() {
        try {
            console.log('íº€ Initializing Profit Tracker...');
            
            // Create data directory if it doesn't exist
            await this.ensureDataDirectory();
            
            // Load historical data if available
            await this.loadHistoricalData();
            
            // Start periodic saving
            this.startAutoSave();
            
            this.isTracking = true;
            
            this.emit('module_ready', { module: 'ProfitTracker', status: 'active' });
            return { success: true, dataPoints: this.performanceData.trades.length };
        } catch (error) {
            this.emit('module_error', { module: 'ProfitTracker', error: error.message });
            throw error;
        }
    }

    // Ensure data directory exists
    async ensureDataDirectory() {
        const dataDir = path.dirname(this.dataFile);
        try {
            await fs.access(dataDir);
        } catch {
            await fs.mkdir(dataDir, { recursive: true });
        }
    }

    // Load historical performance data
    async loadHistoricalData() {
        try {
            const data = await fs.readFile(this.dataFile, 'utf8');
            this.performanceData = JSON.parse(data);
            console.log(`í³Š Loaded ${this.performanceData.trades.length} historical trades`);
        } catch (error) {
            console.log('No historical data found, starting fresh');
            this.performanceData.trades = [];
        }
    }

    // Start automatic data saving
    startAutoSave() {
        this.autoSaveInterval = setInterval(async () => {
            await this.saveData();
        }, this.config.autoSaveInterval || 30000); // Save every 30 seconds
    }

    // Record a new trade
    recordTrade(tradeData) {
        if (!this.isTracking) {
            throw new Error('Profit tracker not initialized');
        }

        const tradeRecord = {
            id: this.generateTradeId(),
            timestamp: tradeData.timestamp || Date.now(),
            profit: tradeData.profit,
            pair: tradeData.pair,
            type: tradeData.type || 'arbitrage',
            gasCost: tradeData.gasCost || 0,
            netProfit: tradeData.profit - (tradeData.gasCost || 0),
            transactionHash: tradeData.transactionHash,
            status: tradeData.status || 'completed'
        };

        // Add to trades array
        this.performanceData.trades.push(tradeRecord);

        // Update hourly aggregation
        this.updateHourlyAggregation(tradeRecord);

        // Update daily aggregation
        this.updateDailyAggregation(tradeRecord);

        // Update summary statistics
        this.updateSummaryStatistics(tradeRecord);

        // Emit event
        this.emit('trade_recorded', tradeRecord);
        this.emit('performance_updated', this.getPerformanceSummary());

        console.log(`í²° Trade recorded: $${tradeRecord.netProfit.toFixed(2)} (${tradeRecord.pair})`);

        return tradeRecord.id;
    }

    // Update hourly aggregation
    updateHourlyAggregation(tradeRecord) {
        const hour = new Date(tradeRecord.timestamp).toISOString().slice(0, 13) + ':00:00Z';
        
        let hourData = this.performanceData.hourly.find(h => h.hour === hour);
        
        if (!hourData) {
            hourData = {
                hour: hour,
                trades: 0,
                totalProfit: 0,
                netProfit: 0,
                gasCost: 0
            };
            this.performanceData.hourly.push(hourData);
        }

        hourData.trades++;
        hourData.totalProfit += tradeRecord.profit;
        hourData.netProfit += tradeRecord.netProfit;
        hourData.gasCost += tradeRecord.gasCost;
    }

    // Update daily aggregation
    updateDailyAggregation(tradeRecord) {
        const day = new Date(tradeRecord.timestamp).toISOString().slice(0, 10);
        
        let dayData = this.performanceData.daily.find(d => d.day === day);
        
        if (!dayData) {
            dayData = {
                day: day,
                trades: 0,
                totalProfit: 0,
                netProfit: 0,
                gasCost: 0
            };
            this.performanceData.daily.push(dayData);
        }

        dayData.trades++;
        dayData.totalProfit += tradeRecord.profit;
        dayData.netProfit += tradeRecord.netProfit;
        dayData.gasCost += tradeRecord.gasCost;
    }

    // Update summary statistics
    updateSummaryStatistics(tradeRecord) {
        const summary = this.performanceData.summary;
        
        summary.totalTrades++;
        summary.totalProfit += tradeRecord.netProfit;
        
        if (tradeRecord.netProfit > 0) {
            summary.profitableTrades++;
        }

        // Update largest win/loss
        if (tradeRecord.netProfit > summary.largestWin) {
            summary.largestWin = tradeRecord.netProfit;
        }
        if (tradeRecord.netProfit < summary.largestLoss) {
            summary.largestLoss = tradeRecord.netProfit;
        }

        // Update averages
        summary.avgProfit = summary.totalProfit / summary.totalTrades;
        summary.winRate = (summary.profitableTrades / summary.totalTrades) * 100;

        // Calculate Sharpe ratio (simplified)
        summary.sharpeRatio = this.calculateSharpeRatio();

        // Update max drawdown
        summary.maxDrawdown = this.calculateMaxDrawdown();
    }

    // Calculate Sharpe ratio (simplified for Phase 1)
    calculateSharpeRatio() {
        if (this.performanceData.trades.length < 2) return 0;
        
        const returns = this.performanceData.trades.map(t => t.netProfit);
        const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
        const stdDev = Math.sqrt(returns.reduce((a, b) => a + Math.pow(b - avgReturn, 2), 0) / returns.length);
        
        // Assume risk-free rate of 0 for crypto
        return stdDev > 0 ? avgReturn / stdDev : 0;
    }

    // Calculate maximum drawdown
    calculateMaxDrawdown() {
        let maxDrawdown = 0;
        let peak = this.performanceData.trades[0]?.netProfit || 0;
        let runningTotal = 0;

        for (const trade of this.performanceData.trades) {
            runningTotal += trade.netProfit;
            
            if (runningTotal > peak) {
                peak = runningTotal;
            }
            
            const drawdown = (peak - runningTotal) / Math.max(peak, 1);
            if (drawdown > maxDrawdown) {
                maxDrawdown = drawdown;
            }
        }

        return maxDrawdown;
    }

    // Generate unique trade ID
    generateTradeId() {
        return `TRADE_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Get performance summary
    getPerformanceSummary() {
        return {
            ...this.performanceData.summary,
            recentTrades: this.performanceData.trades.slice(-10), // Last 10 trades
            hourlyPerformance: this.performanceData.hourly.slice(-24), // Last 24 hours
            dailyPerformance: this.performanceData.daily.slice(-7) // Last 7 days
        };
    }

    // Get detailed trade history
    getTradeHistory(options = {}) {
        let trades = [...this.performanceData.trades];

        // Apply filters
        if (options.limit) {
            trades = trades.slice(-options.limit);
        }

        if (options.pair) {
            trades = trades.filter(t => t.pair === options.pair);
        }

        if (options.timeframe) {
            const cutoff = Date.now() - (options.timeframe * 1000);
            trades = trades.filter(t => t.timestamp >= cutoff);
        }

        return trades;
    }

    // Get hourly performance report
    getHourlyReport(hours = 24) {
        return this.performanceData.hourly.slice(-hours);
    }

    // Get daily performance report
    getDailyReport(days = 7) {
        return this.performanceData.daily.slice(-days);
    }

    // Calculate performance metrics for a timeframe
    calculateTimeframeMetrics(timeframeHours) {
        const cutoff = Date.now() - (timeframeHours * 60 * 60 * 1000);
        const timeframeTrades = this.performanceData.trades.filter(t => t.timestamp >= cutoff);
        
        if (timeframeTrades.length === 0) {
            return {
                trades: 0,
                totalProfit: 0,
                avgProfit: 0,
                winRate: 0,
                profitPerHour: 0
            };
        }

        const totalProfit = timeframeTrades.reduce((sum, t) => sum + t.netProfit, 0);
        const profitableTrades = timeframeTrades.filter(t => t.netProfit > 0).length;
        const profitPerHour = totalProfit / timeframeHours;

        return {
            trades: timeframeTrades.length,
            totalProfit,
            avgProfit: totalProfit / timeframeTrades.length,
            winRate: (profitableTrades / timeframeTrades.length) * 100,
            profitPerHour
        };
    }

    // Export performance data
    async exportData(format = 'json') {
        const data = {
            summary: this.performanceData.summary,
            trades: this.performanceData.trades,
            hourly: this.performanceData.hourly,
            daily: this.performanceData.daily,
            exportDate: new Date().toISOString()
        };

        if (format === 'json') {
            return JSON.stringify(data, null, 2);
        } else if (format === 'csv') {
            return this.convertToCSV(data);
        }

        throw new Error(`Unsupported format: ${format}`);
    }

    // Convert data to CSV
    convertToCSV(data) {
        let csv = 'Timestamp,Profit,Net Profit,Pair,Type,Gas Cost,Transaction Hash\\n';
        
        data.trades.forEach(trade => {
            csv += `"${new Date(trade.timestamp).toISOString()}",${trade.profit},${trade.netProfit},"${trade.pair}","${trade.type}",${trade.gasCost},"${trade.transactionHash}"\\n`;
        });

        return csv;
    }

    // Save data to file
    async saveData() {
        try {
            await fs.writeFile(this.dataFile, JSON.stringify(this.performanceData, null, 2));
            this.emit('data_saved', { trades: this.performanceData.trades.length });
        } catch (error) {
            console.error('Failed to save performance data:', error);
        }
    }

    // Get tracker status
    getStatus() {
        return {
            isTracking: this.isTracking,
            totalTrades: this.performanceData.trades.length,
            totalProfit: this.performanceData.summary.totalProfit,
            dataFile: this.dataFile,
            lastUpdate: this.performanceData.trades.length > 0 ? 
                new Date(this.performanceData.trades[this.performanceData.trades.length - 1].timestamp).toISOString() : 
                'Never'
        };
    }

    // Stop tracker
    async stop() {
        this.isTracking = false;
        
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }

        // Final save
        await this.saveData();
        
        console.log('í»‘ Profit Tracker stopped');
    }
}

module.exports = ProfitTracker;
