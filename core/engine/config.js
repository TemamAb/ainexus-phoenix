module.exports = {
    rpcUrl: process.env.RPC_URL || 'https://mainnet.infura.io/v3/your-project-id',
    minProfitThreshold: 0.005, // 0.5% minimum profit
    maxGasCost: 0.1, // 0.1 ETH max gas
    scanInterval: 2000, // 2 seconds
    dexAddresses: {
        uniswapV3: '0xE592427A0AEce92De3Edee1F18E0157C05861564',
        sushiswap: '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
    },
    supportedPairs: ['ETH/USDC', 'ETH/DAI', 'WBTC/ETH']
};
