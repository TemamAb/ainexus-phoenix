module.exports = {
    autoSaveInterval: 30000, // Save every 30 seconds
    dataRetention: {
        trades: 10000, // Keep last 10,000 trades
        hourly: 720,    // Keep last 720 hours (30 days)
        daily: 365      // Keep last 365 days
    },
    metrics: {
        calculateSharpe: true,
        calculateDrawdown: true,
        trackGasCosts: true
    },
    exportFormats: ['json', 'csv'],
    performanceThresholds: {
        minWinRate: 0.6,      // 60% minimum win rate
        maxDrawdown: 0.15,    // 15% maximum drawdown
        minProfitPerHour: 1   // $1 minimum profit per hour
    }
};
