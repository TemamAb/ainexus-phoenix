const ArbitrageOrchestrator = require('./ArbitrageOrchestrator');

// Mock Web3
jest.mock('web3', () => {
    return jest.fn().mockImplementation(() => ({
        eth: {
            getBlockNumber: jest.fn().mockResolvedValue(123456),
            net: {
                getId: jest.fn().mockResolvedValue(1)
            },
            getGasPrice: jest.fn().mockResolvedValue('20000000000')
        },
        utils: {
            fromWei: jest.fn().mockReturnValue(0.01)
        }
    }));
});

describe('ArbitrageOrchestrator', () => {
    let orchestrator;
    const config = {
        rpcUrl: 'http://localhost:8545',
        minProfitThreshold: 0.005,
        maxGasCost: 0.1
    };

    beforeEach(() => {
        orchestrator = new ArbitrageOrchestrator(config);
    });

    test('should initialize successfully', async () => {
        const result = await orchestrator.initialize();
        expect(result.success).toBe(true);
    });

    test('should calculate profit correctly', async () => {
        const opp1 = { price: 1900, pair: 'ETH/USDC', dex: 'UNISWAP' };
        const opp2 = { price: 2000, pair: 'ETH/USDC', dex: 'SUSHISWAP' };
        
        const profit = await orchestrator.calculateArbitrageProfit(opp1, opp2);
        expect(profit.percentage).toBeGreaterThan(0);
        expect(profit.hasOwnProperty('netProfit')).toBe(true);
    });

    test('should stop scanning', () => {
        orchestrator.stop();
        expect(orchestrator.scanning).toBe(false);
    });
});
