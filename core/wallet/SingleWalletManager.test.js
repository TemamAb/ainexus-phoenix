const SingleWalletManager = require('./SingleWalletManager');

// Mock window.ethereum for MetaMask
global.window = {
    ethereum: {
        request: jest.fn(),
        on: jest.fn(),
        removeListener: jest.fn()
    }
};

describe('SingleWalletManager', () => {
    let walletManager;
    const config = {
        rpcUrl: 'https://mainnet.infura.io/v3/test'
    };

    beforeEach(() => {
        walletManager = new SingleWalletManager(config);
        jest.clearAllMocks();
    });

    test('should initialize without MetaMask', async () => {
        delete global.window.ethereum;
        const result = await walletManager.initialize();
        expect(result.success).toBe(true);
    });

    test('should detect MetaMask', async () => {
        const result = await walletManager.initialize();
        expect(result.walletType).toBe('metamask');
    });

    test('should validate wallet for arbitrage', async () => {
        walletManager.connected = true;
        walletManager.balance = '0.5';
        walletManager.networkId = 1;
        
        const validation = await walletManager.validateForArbitrage();
        expect(validation.valid).toBe(true);
    });
});
