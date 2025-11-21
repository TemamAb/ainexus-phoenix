const ProfitTracker = require('./ProfitTracker');
const fs = require('fs').promises;

jest.mock('fs', () => ({
    promises: {
        access: jest.fn(),
        mkdir: jest.fn(),
        readFile: jest.fn(),
        writeFile: jest.fn()
    }
}));

describe('ProfitTracker', () => {
    let profitTracker;
    const config = {
        autoSaveInterval: 10000
    };

    beforeEach(() => {
        profitTracker = new ProfitTracker(config);
        jest.clearAllMocks();
    });

    test('should initialize successfully', async () => {
        fs.readFile.mockRejectedValue(new Error('File not found')); // No historical data
        
        const result = await profitTracker.initialize();
        expect(result.success).toBe(true);
    });

    test('should record trade', async () => {
        await profitTracker.initialize();
        
        const tradeData = {
            profit: 50,
            pair: 'ETH/USDC',
            gasCost: 5,
            transactionHash: '0x123'
        };
        
        const tradeId = profitTracker.recordTrade(tradeData);
        expect(tradeId).toContain('TRADE_');
        expect(profitTracker.performanceData.trades).toHaveLength(1);
    });

    test('should calculate performance metrics', async () => {
        await profitTracker.initialize();
        
        // Record multiple trades
        profitTracker.recordTrade({ profit: 100, pair: 'ETH/USDC', gasCost: 10 });
        profitTracker.recordTrade({ profit: -50, pair: 'ETH/DAI', gasCost: 8 });
        profitTracker.recordTrade({ profit: 75, pair: 'ETH/USDC', gasCost: 12 });
        
        const summary = profitTracker.getPerformanceSummary();
        expect(summary.totalTrades).toBe(3);
        expect(summary.winRate).toBeGreaterThan(0);
    });

    test('should export data', async () => {
        await profitTracker.initialize();
        profitTracker.recordTrade({ profit: 100, pair: 'ETH/USDC', gasCost: 10 });
        
        const jsonExport = await profitTracker.exportData('json');
        expect(jsonExport).toContain('ETH/USDC');
        
        const csvExport = await profitTracker.exportData('csv');
        expect(csvExport).toContain('Timestamp,Profit');
    });
});
