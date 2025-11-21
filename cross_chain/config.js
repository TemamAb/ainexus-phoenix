module.exports = {
    minProfit: 0.8, // 0.8% minimum profit for cross-chain (higher due to bridge costs)
    scanIntervals: {
        priceScan: 2000, // 2 seconds
        arbitrageScan: 5000, // 5 seconds
        bridgeMonitor: 30000, // 30 seconds
        gasOptimization: 15000 // 15 seconds
    },
    chains: {
        ethereum: {
            chainId: 1,
            rpcUrl: process.env.ETH_RPC_URL,
            nativeToken: 'ETH'
        },
        arbitrum: {
            chainId: 42161,
            rpcUrl: process.env.ARB_RPC_URL,
            nativeToken: 'ETH'
        },
        polygon: {
            chainId: 137,
            rpcUrl: process.env.POLYGON_RPC_URL,
            nativeToken: 'MATIC'
        },
        optimism: {
            chainId: 10,
            rpcUrl: process.env.OPTIMISM_RPC_URL,
            nativeToken: 'ETH'
        },
        base: {
            chainId: 8453,
            rpcUrl: process.env.BASE_RPC_URL,
            nativeToken: 'ETH'
        }
    },
    bridges: {
        hop: {
            supportedTokens: ['ETH', 'USDC', 'USDT', 'DAI'],
            maxTransfer: 100000, // $100K
            minTransfer: 100 // $100
        },
        connext: {
            supportedTokens: ['ETH', 'USDC', 'USDT', 'DAI'],
            maxTransfer: 50000, // $50K
            minTransfer: 50 // $50
        },
        across: {
            supportedTokens: ['ETH', 'USDC', 'DAI'],
            maxTransfer: 100000, // $100K
            minTransfer: 100 // $100
        }
    },
    riskThresholds: {
        maxBridgeRisk: 0.7,
        maxExecutionTime: 1800, // 30 minutes
        minBridgeSuccessRate: 0.9 // 90%
    }
};
