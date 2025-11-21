const FlashLoanExecutor = require('./FlashLoanExecutor');

// Mock Web3
jest.mock('web3', () => {
    return jest.fn().mockImplementation(() => ({
        eth: {
            Contract: jest.fn(),
            getGasPrice: jest.fn().mockResolvedValue('20000000000'),
            getTransactionCount: jest.fn().mockResolvedValue(5),
            accounts: {
                signTransaction: jest.fn().mockResolvedValue({ rawTransaction: '0x123' })
            },
            sendSignedTransaction: jest.fn().mockResolvedValue({
                transactionHash: '0xabc123',
                gasUsed: 100000,
                status: true
            })
        },
        utils: {
            toWei: jest.fn().mockReturnValue('1000000000000000000'),
            fromWei: jest.fn().mockReturnValue(0.01),
            asciiToHex: jest.fn().mockReturnValue('0x123')
        }
    }));
});

describe('FlashLoanExecutor', () => {
    let executor;
    const config = {
        rpcUrl: 'http://localhost:8545',
        aavePoolAddress: '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'
    };

    beforeEach(() => {
        executor = new FlashLoanExecutor(config);
    });

    test('should initialize successfully', async () => {
        const result = await executor.initialize();
        expect(result.success).toBe(true);
    });

    test('should calculate optimal loan amount', async () => {
        const opportunity = {
            pair: 'ETH/USDC',
            profit: { netProfit: 100, percentage: 0.01 }
        };
        
        const loanAmount = await executor.calculateOptimalLoan(opportunity);
        expect(loanAmount).toBeGreaterThan(0);
    });

    test('should generate loan ID', () => {
        const loanId = executor.generateLoanId();
        expect(loanId).toContain('FL_');
    });
});
