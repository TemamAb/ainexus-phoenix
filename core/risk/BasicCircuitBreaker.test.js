const BasicCircuitBreaker = require('./BasicCircuitBreaker');

describe('BasicCircuitBreaker', () => {
    let circuitBreaker;
    const config = {
        drawdownThreshold: 0.10, // 10%
        consecutiveLosses: 3,
        gasPriceThreshold: 200,
        checkInterval: 1000
    };

    beforeEach(() => {
        circuitBreaker = new BasicCircuitBreaker(config);
    });

    test('should initialize successfully', async () => {
        const result = await circuitBreaker.initialize();
        expect(result.success).toBe(true);
    });

    test('should trigger drawdown breaker', async () => {
        await circuitBreaker.initialize();
        
        // Simulate significant losses
        circuitBreaker.metrics.totalProfit = -1000;
        circuitBreaker.metrics.peakValue = 0;
        
        await circuitBreaker.checkDrawdownBreaker();
        expect(circuitBreaker.breakers.drawdown.triggered).toBe(true);
    });

    test('should record trade results', () => {
        circuitBreaker.recordTradeResult(50);
        expect(circuitBreaker.metrics.totalTrades).toBe(1);
        expect(circuitBreaker.metrics.profitableTrades).toBe(1);
    });

    test('should check trading permission', () => {
        expect(circuitBreaker.isTradingAllowed()).toBe(true);
        
        circuitBreaker.tradingEnabled = false;
        expect(circuitBreaker.isTradingAllowed()).toBe(false);
    });
});
