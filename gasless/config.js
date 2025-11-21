module.exports = {
    rpcUrl: process.env.RPC_URL || 'https://mainnet.infura.io/v3/your-project-id',
    relayers: {
        gelato: {
            apiKey: process.env.GELATO_API_KEY,
            supportedChains: [1, 137, 42161, 10, 8453]
        },
        openzeppelin: {
            apiKey: process.env.OZ_API_KEY,
            supportedChains: [1, 137, 42161]
        },
        biconomy: {
            apiKey: process.env.BICONOMY_API_KEY,
            supportedChains: [1, 137, 42161, 56]
        }
    },
    sponsorship: {
        pools: {
            ethereum: {
                chainId: 1,
                token: 'USDC',
                totalFunds: 10000,
                maxPerUser: 100,
                maxPerTx: 50,
                refillThreshold: 1000
            },
            arbitrum: {
                chainId: 42161,
                token: 'ETH',
                totalFunds: 5,
                maxPerUser: 0.1,
                maxPerTx: 0.05,
                refillThreshold: 1
            },
            polygon: {
                chainId: 137,
                token: 'MATIC',
                totalFunds: 5000,
                maxPerUser: 50,
                maxPerTx: 20,
                refillThreshold: 500
            }
        },
        autoRefill: true,
        refillAmounts: {
            ethereum: 5000,
            arbitrum: 2,
            polygon: 2000
        }
    },
    gasOptimization: {
        monitoringInterval: 15000,
        maxGasPriceMultiplier: 1.5,
        minGasPriceMultiplier: 0.8,
        congestionThreshold: 0.7
    },
    transactionProcessing: {
        queueCheckInterval: 2000,
        maxQueueSize: 100,
        timeout: 300000, // 5 minutes
        retryAttempts: 3
    },
    security: {
        maxUserAllocationPeriod: 86400, // 24 hours
        sessionTimeout: 3600, // 1 hour
        permitDeadline: 3600 // 1 hour
    }
};
