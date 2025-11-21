module.exports = {
    drawdownThreshold: 0.10, // 10% maximum drawdown
    consecutiveLosses: 3,     // 3 consecutive losses
    gasPriceThreshold: 200,   // 200 Gwei maximum
    checkInterval: 5000,      // Check every 5 seconds
    autoRecovery: true,       // Auto-reset when conditions improve
    emergencyProtocols: {
        drawdown: 'stop_trading',
        consecutiveLosses: 'stop_trading',
        gasPrice: 'pause_trading',
        systemHealth: 'full_shutdown'
    }
};
