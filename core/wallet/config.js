module.exports = {
    rpcUrl: process.env.RPC_URL || 'https://mainnet.infura.io/v3/your-project-id',
    supportedNetworks: {
        1: 'Ethereum Mainnet'
    },
    minBalance: 0.01, // Minimum ETH balance required
    autoConnect: true,
    walletTypes: ['metamask', 'walletconnect'] // Phase 1: metamask only
};
