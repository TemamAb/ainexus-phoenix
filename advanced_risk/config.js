module.exports = {
    riskThresholds: {
        highSeverity: 0.8,
        mediumSeverity: 0.6,
        lowSeverity: 0.4,
        blackSwanThreshold: 0.3
    },
    monitoring: {
        riskSignalInterval: 2000,
        regimeDetectionInterval: 10000,
        correlationAnalysisInterval: 30000,
        forecastingInterval: 15000,
        stressTestingInterval: 60000,
        modelRetrainingInterval: 600000
    },
    models: {
        volatility: {
            confidenceThreshold: 0.7,
            retrainSamples: 1000
        },
        liquidity: {
            confidenceThreshold: 0.75,
            retrainSamples: 800
        },
        correlation: {
            confidenceThreshold: 0.8,
            retrainSamples: 1500
        },
        blackSwan: {
            confidenceThreshold: 0.65,
            retrainSamples: 500
        }
    },
    forecasting: {
        horizons: [1, 6, 24], // hours
        confidenceLevels: {
            short: 0.7,
            medium: 0.6,
            long: 0.5
        }
    },
    stressTesting: {
        scenarios: ['FLASH_CRASH', 'LIQUIDITY_CRISIS', 'CORRELATION_BREAKDOWN', 'VOLATILITY_SPIKE'],
        severityLevels: ['LOW', 'MEDIUM', 'HIGH', 'EXTREME'],
        impactThreshold: 0.7
    }
};
