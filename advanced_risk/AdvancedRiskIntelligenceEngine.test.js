const AdvancedRiskIntelligenceEngine = require('./AdvancedRiskIntelligenceEngine');

// Mock tensorflow
jest.mock('@tensorflow/tfjs-node', () => ({
    sequential: jest.fn(),
    layers: {
        dense: jest.fn(),
        dropout: jest.fn(),
        batchNormalization: jest.fn()
    },
    tensor2d: jest.fn()
}));

describe('AdvancedRiskIntelligenceEngine', () => {
    let riskEngine;
    const config = {
        riskThresholds: {
            highSeverity: 0.8,
            mediumSeverity: 0.6
        },
        monitoring: {
            riskSignalInterval: 2000,
            regimeDetectionInterval: 10000
        }
    };

    beforeEach(() => {
        riskEngine = new AdvancedRiskIntelligenceEngine(config);
    });

    test('should initialize successfully', async () => {
        const result = await riskEngine.initialize();
        expect(result.success).toBe(true);
        expect(result.models).toBeGreaterThan(0);
    });

    test('should generate risk signals', async () => {
        await riskEngine.initialize();
        const signals = await riskEngine.generateRiskSignals();
        expect(Array.isArray(signals)).toBe(true);
        signals.forEach(signal => {
            expect(signal).toHaveProperty('type');
            expect(signal).toHaveProperty('severity');
            expect(signal).toHaveProperty('recommendation');
        });
    });

    test('should detect market regimes', async () => {
        await riskEngine.initialize();
        await riskEngine.detectMarketRegime();
        const status = riskEngine.getStatus();
        expect(status.marketRegime).not.toBe('UNKNOWN');
    });

    test('should calculate correlations', async () => {
        await riskEngine.initialize();
        await riskEngine.analyzeCorrelations();
        const status = riskEngine.getStatus();
        expect(status).toHaveProperty('lastUpdate');
    });
});
