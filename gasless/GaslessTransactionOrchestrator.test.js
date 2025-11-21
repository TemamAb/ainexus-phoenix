const GaslessTransactionOrchestrator = require('./GaslessTransactionOrchestrator');

// Mock Web3
jest.mock('web3', () => {
    return jest.fn().mockImplementation(() => ({
        eth: {
            getGasPrice: jest.fn().mockResolvedValue('30000000000')
        }
    }));
});

describe('GaslessTransactionOrchestrator', () => {
    let gaslessOrchestrator;
    const config = {
        rpcUrl: 'https://mainnet.infura.io/v3/test',
        relayers: {
            gelato: { supportedChains: [1, 137] }
        }
    };

    beforeEach(() => {
        gaslessOrchestrator = new GaslessTransactionOrchestrator(config);
    });

    test('should initialize successfully', async () => {
        const result = await gaslessOrchestrator.initialize();
        expect(result.success).toBe(true);
        expect(result.relayers).toBeGreaterThan(0);
    });

    test('should validate transactions', async () => {
        await gaslessOrchestrator.initialize();
        
        const transaction = {
            chainId: 1,
            contractAddress: '0x742d35Cc6634C0532925a3b8Df59B9e5C8D7F5a8',
            userAddress: '0x1234567890123456789012345678901234567890',
            encodedData: '0x123456',
            gasToken: 'ETH'
        };
        
        const validation = await gaslessOrchestrator.validateTransaction(transaction);
        expect(validation.valid).toBe(true);
    });

    test('should generate transaction ID', () => {
        const txId = gaslessOrchestrator.generateTransactionId();
        expect(txId).toContain('GASLESS_');
        expect(txId.length).toBeGreaterThan(20);
    });

    test('should get pool status', async () => {
        await gaslessOrchestrator.initialize();
        const poolStatus = gaslessOrchestrator.getPoolStatus();
        expect(typeof poolStatus).toBe('object');
    });
});
