const BasicDashboard = require('./BasicDashboard');

// Mock modules
const mockModules = {
    walletManager: {
        getStatus: jest.fn().mockReturnValue({
            connected: true,
            walletAddress: '0x742d35Cc6634C0532925a3b8Df59B9e5C8D7F5a8',
            balance: '1.5',
            networkId: 1
        })
    },
    arbitrageOrchestrator: {
        getStatus: jest.fn().mockReturnValue({
            opportunitiesFound: 10,
            scanning: true
        })
    },
    flashLoanExecutor: {
        getStatus: jest.fn().mockReturnValue({
            completedLoans: 5,
            failedLoans: 1,
            totalProfit: 250.50
        })
    }
};

describe('BasicDashboard', () => {
    let dashboard;
    const config = {
        updateInterval: 1000
    };

    beforeEach(() => {
        dashboard = new BasicDashboard(config);
    });

    test('should initialize successfully', async () => {
        const result = await dashboard.initialize(mockModules);
        expect(result.success).toBe(true);
    });

    test('should update metrics', async () => {
        await dashboard.initialize(mockModules);
        await dashboard.updateAllMetrics();
        
        const metrics = dashboard.getMetrics();
        expect(metrics.wallet.connected).toBe(true);
        expect(metrics.executions.totalExecuted).toBe(6); // 5 + 1
    });

    test('should format uptime correctly', () => {
        const uptime = dashboard.formatUptime(3665); // 1 hour, 1 minute, 5 seconds
        expect(uptime).toBe('1h 1m');
    });
});
