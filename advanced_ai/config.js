module.exports = {
    minProfit: 0.5, // 0.5% minimum profit
    minConfidence: 0.7, // 70% minimum confidence
    scanIntervals: {
        highFrequency: 1000, // 1 second
        complexScan: 5000, // 5 seconds
        modelRetrain: 300000 // 5 minutes
    },
    dexConfigs: {
        uniswapV3: {
            router: '0xE592427A0AEce92De3Edee1F18E0157C05861564',
            factory: '0x1F98431c8aD98523631AE4a59f267346ea31F984'
        },
        sushiswap: {
            router: '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
            factory: '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'
        },
        curve: {
            router: '0x81C46fECa27B31F3E2B2c8b1d5c38b0B6B6b7a0c',
            registry: '0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5'
        }
    },
    mlConfig: {
        trainingEpochs: 10,
        batchSize: 32,
        learningRate: 0.001
    }
};
