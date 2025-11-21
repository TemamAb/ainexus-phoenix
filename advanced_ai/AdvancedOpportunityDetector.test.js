const AdvancedOpportunityDetector = require('./AdvancedOpportunityDetector');

// Mock tensorflow
jest.mock('@tensorflow/tfjs-node', () => ({
    sequential: jest.fn(),
    layers: {
        dense: jest.fn(),
        dropout: jest.fn()
    },
    tensor2d: jest.fn(),
    randomNormal: jest.fn(),
    randomUniform: jest.fn()
}));

describe('AdvancedOpportunityDetector', () => {
    let detector;
    const config = {
        minProfit: 0.5,
        minConfidence: 0.7,
        scanIntervals: {
            highFrequency: 1000,
            complexScan: 5000
        }
    };

    beforeEach(() => {
        detector = new AdvancedOpportunityDetector(config);
    });

    test('should initialize successfully', async () => {
        const result = await detector.initialize();
        expect(result.success).toBe(true);
        expect(result.dexCount).toBeGreaterThan(0);
    });

    test('should find simple arbitrage opportunities', async () => {
        await detector.initialize();
        const opportunities = await detector.findSimpleArbitrage();
        expect(Array.isArray(opportunities)).toBe(true);
    });

    test('should calculate route profit', async () => {
        await detector.initialize();
        const route = ['ETH/USDC', 'USDC/DAI', 'DAI/ETH'];
        const result = await detector.calculateRouteProfit(route);
        expect(result).toHaveProperty('profit');
        expect(result).toHaveProperty('steps');
    });

    test('should extract features from opportunity', () => {
        const opportunity = {
            profit: 1.5,
            confidence: 0.8,
            buyFrom: 'UNISWAP_V3',
            sellTo: 'SUSHISWAP',
            pair: 'ETH/USDC'
        };
        
        const features = detector.extractFeatures(opportunity);
        expect(features).toHaveLength(10);
        expect(features.every(f => typeof f === 'number')).toBe(true);
    });
});
