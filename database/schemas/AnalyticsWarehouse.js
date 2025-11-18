/**
 * AI-NEXUS Analytics Data Warehouse
 * Large-scale analytics and reporting database
 */

const { Client } = require('pg');

class AnalyticsWarehouse {
    constructor(config) {
        this.config = config;
        this.client = new Client(config);
        this.connected = false;
    }

    /**
     * Initialize data warehouse connection
     */
    async initialize() {
        try {
            await this.client.connect();
            this.connected = true;
            console.log('Analytics warehouse connected successfully');
        } catch (error) {
            console.error('Failed to connect to analytics warehouse:', error);
            throw error;
        }
    }

    /**
     * Store aggregated trading performance data
     */
    async storeTradingPerformance(performanceData) {
        const query = `
            INSERT INTO trading_performance_aggregated (
                date,
                total_trades,
                successful_trades,
                total_profit,
                avg_profit_per_trade,
                success_rate,
                sharpe_ratio,
                max_drawdown,
                volatility
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (date) DO UPDATE SET
                total_trades = EXCLUDED.total_trades,
                successful_trades = EXCLUDED.successful_trades,
                total_profit = EXCLUDED.total_profit,
                avg_profit_per_trade = EXCLUDED.avg_profit_per_trade,
                success_rate = EXCLUDED.success_rate,
                sharpe_ratio = EXCLUDED.sharpe_ratio,
                max_drawdown = EXCLUDED.max_drawdown,
                volatility = EXCLUDED.volatility
        `;

        try {
            await this.client.query(query, [
                performanceData.date,
                performanceData.totalTrades,
                performanceData.successfulTrades,
                performanceData.totalProfit,
                performanceData.avgProfitPerTrade,
                performanceData.successRate,
                performanceData.sharpeRatio,
                performanceData.maxDrawdown,
                performanceData.volatility
            ]);
        } catch (error) {
            console.error('Error storing trading performance:', error);
            throw error;
        }
    }

    /**
     * Generate comprehensive performance report
     */
    async generatePerformanceReport(startDate, endDate) {
        const query = `
            SELECT 
                date,
                total_trades,
                successful_trades,
                total_profit,
                avg_profit_per_trade,
                success_rate,
                sharpe_ratio,
                max_drawdown,
                volatility
            FROM trading_performance_aggregated
            WHERE date BETWEEN $1 AND $2
            ORDER BY date ASC
        `;

        try {
            const result = await this.client.query(query, [startDate, endDate]);
            return result.rows;
        } catch (error) {
            console.error('Error generating performance report:', error);
            throw error;
        }
    }

    /**
     * Calculate risk-adjusted return metrics
     */
    async calculateRiskAdjustedMetrics(period = '30 days') {
        const query = `
            WITH period_data AS (
                SELECT 
                    total_profit,
                    volatility,
                    max_drawdown,
                    sharpe_ratio
                FROM trading_performance_aggregated
                WHERE date >= CURRENT_DATE - $1::interval
            )
            SELECT 
                AVG(total_profit) as avg_daily_profit,
                AVG(volatility) as avg_volatility,
                MAX(max_drawdown) as worst_drawdown,
                AVG(sharpe_ratio) as avg_sharpe_ratio,
                COUNT(*) as trading_days
            FROM period_data
        `;

        try {
            const result = await this.client.query(query, [period]);
            return result.rows[0];
        } catch (error) {
            console.error('Error calculating risk metrics:', error);
            throw error;
        }
    }

    /**
     * Store AI model performance data
     */
    async storeAIModelPerformance(modelData) {
        const query = `
            INSERT INTO ai_model_performance_aggregated (
                timestamp,
                model_name,
                model_version,
                accuracy,
                precision,
                recall,
                f1_score,
                inference_time_ms,
                training_loss,
                validation_loss
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        `;

        try {
            await this.client.query(query, [
                modelData.timestamp,
                modelData.modelName,
                modelData.modelVersion,
                modelData.accuracy,
                modelData.precision,
                modelData.recall,
                modelData.f1Score,
                modelData.inferenceTimeMs,
                modelData.trainingLoss,
                modelData.validationLoss
            ]);
        } catch (error) {
            console.error('Error storing AI model performance:', error);
            throw error;
        }
    }

    /**
     * Generate strategy performance comparison
     */
    async compareStrategyPerformance(strategies, period) {
        const query = `
            SELECT 
                strategy_name,
                COUNT(*) as trade_count,
                AVG(net_profit) as avg_profit,
                STDDEV(net_profit) as profit_volatility,
                SUM(net_profit) as total_profit,
                MIN(net_profit) as min_profit,
                MAX(net_profit) as max_profit,
                COUNT(CASE WHEN net_profit > 0 THEN 1 END) as profitable_trades,
                COUNT(CASE WHEN net_profit <= 0 THEN 1 END) as losing_trades
            FROM trade_executions
            WHERE strategy_name = ANY($1)
            AND created_at >= $2
            GROUP BY strategy_name
            ORDER BY total_profit DESC
        `;

        try {
            const result = await this.client.query(query, [strategies, period]);
            return result.rows;
        } catch (error) {
            console.error('Error comparing strategy performance:', error);
            throw error;
        }
    }

    /**
     * Generate market regime analysis
     */
    async analyzeMarketRegimes(startDate, endDate) {
        const query = `
            WITH market_data AS (
                SELECT 
                    time,
                    last_price,
                    LAG(last_price) OVER (PARTITION BY pair_id ORDER BY time) as prev_price
                FROM market_prices
                WHERE time BETWEEN $1 AND $2
            ),
            returns AS (
                SELECT 
                    time,
                    (last_price - prev_price) / prev_price as return
                FROM market_data
                WHERE prev_price IS NOT NULL
            ),
            regimes AS (
                SELECT 
                    time,
                    return,
                    CASE 
                        WHEN ABS(return) > 0.01 THEN 'high_volatility'
                        WHEN return > 0 THEN 'bullish'
                        WHEN return < 0 THEN 'bearish'
                        ELSE 'stable'
                    END as regime
                FROM returns
            )
            SELECT 
                regime,
                COUNT(*) as period_count,
                AVG(return) as avg_return,
                STDDEV(return) as regime_volatility
            FROM regimes
            GROUP BY regime
            ORDER BY period_count DESC
        `;

        try {
            const result = await this.client.query(query, [startDate, endDate]);
            return result.rows;
        } catch (error) {
            console.error('Error analyzing market regimes:', error);
            throw error;
        }
    }

    /**
     * Generate arbitrage opportunity analysis
     */
    async analyzeArbitrageOpportunities(days = 7) {
        const query = `
            SELECT 
                DATE(detected_at) as opportunity_date,
                COUNT(*) as total_opportunities,
                AVG(spread) as avg_spread,
                AVG(estimated_profit) as avg_estimated_profit,
                COUNT(CASE WHEN spread > 0.01 THEN 1 END) as high_spread_opportunities,
                COUNT(CASE WHEN risk_score < 0.3 THEN 1 END) as low_risk_opportunities
            FROM arbitrage_opportunities
            WHERE detected_at >= CURRENT_DATE - $1::integer
            GROUP BY DATE(detected_at)
            ORDER BY opportunity_date DESC
        `;

        try {
            const result = await this.client.query(query, [days]);
            return result.rows;
        } catch (error) {
            console.error('Error analyzing arbitrage opportunities:', error);
            throw error;
        }
    }

    /**
     * Generate executive dashboard data
     */
    async getExecutiveDashboardData(period = '30 days') {
        const dashboardData = {};

        try {
            // Get performance metrics
            dashboardData.performance = await this.calculateRiskAdjustedMetrics(period);

            // Get opportunity analysis
            dashboardData.opportunities = await this.analyzeArbitrageOpportunities(30);

            // Get strategy performance
            dashboardData.strategies = await this.compareStrategyPerformance(
                ['triangular_arb', 'flash_loan_arb', 'cross_chain_arb'],
                period
            );

            // Get market regime analysis
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 30);
            dashboardData.marketRegimes = await this.analyzeMarketRegimes(startDate, endDate);

            return dashboardData;

        } catch (error) {
            console.error('Error generating executive dashboard data:', error);
            throw error;
        }
    }

    /**
     * Close data warehouse connection
     */
    async close() {
        if (this.connected) {
            await this.client.end();
            this.connected = false;
            console.log('Analytics warehouse connection closed');
        }
    }
}

module.exports = AnalyticsWarehouse;
