module.exports = {
    rpcUrl: process.env.RPC_URL || 'https://mainnet.infura.io/v3/your-project-id',
    aavePoolAddress: '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2', // Aave V3 Mainnet
    maxLoanPercentage: 0.5, // Max 50% of available liquidity
    kellyFraction: 0.1, // Conservative position sizing
    gasBuffer: 1.2, // 20% gas buffer
    supportedAssets: ['USDC', 'DAI', 'WETH']
};
