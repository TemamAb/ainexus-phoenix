// File: core_foundation/data_intelligence/WalletDataCollector.js
// 7P-PILLAR: CAPITAL-7P, BOT3-7P
// PURPOSE: Real-time wallet monitoring and capital tracking

const { EventEmitter } = require('events');

class WalletDataCollector extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.wallets = new Map();
        this.transactionHistory = new Map();
        this.balanceHistory = new Map();
        this.isMonitoring = false;
        this.monitoringIntervals = new Map();
        
        // Initialize wallet tracking
        this.initializeWallets();
    }

    // Initialize wallet tracking from config
    initializeWallets() {
        const walletConfigs = this.config.wallets || [];
        
        walletConfigs.forEach(walletConfig => {
            this.addWallet(walletConfig);
        });
        
        console.log(`âœ… Initialized ${this.wallets.size} wallets for monitoring`);
    }

    // Add wallet to monitoring
    addWallet(walletConfig) {
        const wallet = {
            id: walletConfig.id || `wallet_${Date.now()}`,
            address: walletConfig.address,
            chain: walletConfig.chain || 'ethereum',
            type: walletConfig.type || 'hot', // hot, cold, contract
            balance: 0,
            tokens: new Map(),
            lastUpdated: Date.now(),
            health: 1.0
        };
        
        this.wallets.set(wallet.id, wallet);
        this.balanceHistory.set(wallet.id, []);
        
        this.emit('wallet_added', { wallet, timestamp: Date.now() });
        
        return wallet.id;
    }

    // Start continuous wallet monitoring
    startMonitoring() {
        if (this.isMonitoring) {
            console.log('âš ï¸ Wallet monitoring already active');
            return;
        }
        
        this.isMonitoring = true;
        console.log('í´ Starting continuous wallet monitoring...');
        
        // Monitor each wallet on its specified interval
        this.wallets.forEach((wallet, walletId) => {
            const interval = setInterval(async () => {
                try {
                    await this.updateWalletData(walletId);
                } catch (error) {
                    console.error(`Error updating wallet ${walletId}:`, error);
                    this.degradeWalletHealth(walletId);
                }
            }, this.config.updateInterval || 30000); // Default 30 seconds
            
            this.monitoringIntervals.set(walletId, interval);
        });
        
        // Start transaction monitoring
        this.startTransactionMonitoring();
    }

    // Stop wallet monitoring
    stopMonitoring() {
        this.isMonitoring = false;
        
        // Clear all monitoring intervals
        this.monitoringIntervals.forEach((interval, walletId) => {
            clearInterval(interval);
        });
        this.monitoringIntervals.clear();
        
        // Stop transaction monitoring
        this.stopTransactionMonitoring();
        
        console.log('í»‘ Wallet monitoring stopped');
    }

    // Update data for specific wallet
    async updateWalletData(walletId) {
        const wallet = this.wallets.get(walletId);
        if (!wallet) {
            throw new Error(`Wallet ${walletId} not found`);
        }
        
        const startTime = Date.now();
        
        try {
            // Fetch native token balance
            const nativeBalance = await this.fetchNativeBalance(wallet.address, wallet.chain);
            wallet.balance = nativeBalance;
            
            // Fetch token balances
            const tokenBalances = await this.fetchTokenBalances(wallet.address, wallet.chain);
            wallet.tokens = new Map(Object.entries(tokenBalances));
            
            // Update timestamp and health
            wallet.lastUpdated = Date.now();
            wallet.health = 1.0; // Reset health on successful update
            
            // Record balance history
            this.recordBalanceHistory(walletId, nativeBalance, tokenBalances);
            
            this.emit('wallet_updated', {
                walletId,
                nativeBalance,
                tokenBalances,
                updateTime: Date.now() - startTime,
                timestamp: Date.now()
            });
            
            return {
                nativeBalance,
                tokenBalances,
                updateTime: Date.now() - startTime
            };
            
        } catch (error) {
            wallet.health -= 0.1; // Degrade health on error
            throw error;
        }
    }

    // Fetch native token balance (ETH, BNB, etc.)
    async fetchNativeBalance(address, chain) {
        // Mock implementation - would use web3.js or ethers.js
        // Simulate balance fetching with some variation
        
        const baseBalances = {
            ethereum: 10.5,
            bsc: 25.3,
            polygon: 150.8,
            arbitrum: 8.2,
            optimism: 12.7
        };
        
        const baseBalance = baseBalances[chain] || 5.0;
        const variation = (Math.random() - 0.5) * 2; // Â±1 variation
        
        return baseBalance + variation;
    }

    // Fetch ERC-20 token balances
    async fetchTokenBalances(address, chain) {
        // Mock implementation - would use token contracts
        const commonTokens = {
            'USDC': { address: '0xa0b8...', decimals: 6 },
            'USDT': { address: '0xdac0...', decimals: 6 },
            'DAI': { address: '0x6b17...', decimals: 18 },
            'WBTC': { address: '0x2260...', decimals: 8 },
            'WETH': { address: '0xc02a...', decimals: 18 }
        };
        
        const balances = {};
        
        Object.keys(commonTokens).forEach(token => {
            // Simulate token balances with some variation
            const baseBalance = {
                'USDC': 50000,
                'USDT': 75000,
                'DAI': 25000,
                'WBTC': 1.5,
                'WETH': 8.2
            }[token] || 1000;
            
            const variation = (Math.random() - 0.5) * 0.2; // Â±10% variation
            balances[token] = baseBalance * (1 + variation);
        });
        
        return balances;
    }

    // Record balance history for analytics
    recordBalanceHistory(walletId, nativeBalance, tokenBalances) {
        if (!this.balanceHistory.has(walletId)) {
            this.balanceHistory.set(walletId, []);
        }
        
        const history = this.balanceHistory.get(walletId);
        const record = {
            timestamp: Date.now(),
            native: nativeBalance,
            tokens: { ...tokenBalances }
        };
        
        history.push(record);
        
        // Keep only last 1000 records
        if (history.length > 1000) {
            history.shift();
        }
    }

    // Start transaction monitoring
    startTransactionMonitoring() {
        console.log('í´ Starting transaction monitoring...');
        
        // In production, this would use WebSocket connections to blockchain nodes
        // For now, simulate transaction monitoring with intervals
        
        this.transactionMonitoringInterval = setInterval(() => {
            this.simulateTransactionActivity();
        }, 15000); // Check every 15 seconds
    }

    // Stop transaction monitoring
    stopTransactionMonitoring() {
        if (this.transactionMonitoringInterval) {
            clearInterval(this.transactionMonitoringInterval);
            this.transactionMonitoringInterval = null;
        }
    }

    // Simulate transaction activity (for testing)
    simulateTransactionActivity() {
        if (this.wallets.size === 0) return;
        
        // Randomly select a wallet to simulate transaction
        const walletIds = Array.from(this.wallets.keys());
        const randomWalletId = walletIds[Math.floor(Math.random() * walletIds.length)];
        const wallet = this.wallets.get(randomWalletId);
        
        // 20% chance of transaction
        if (Math.random() < 0.2) {
            const transaction = {
                hash: `0x${Math.random().toString(16).substr(2, 64)}`,
                from: wallet.address,
                to: this.generateRandomAddress(),
                value: Math.random() * 0.1, // Small transaction
                token: 'ETH',
                timestamp: Date.now(),
                status: 'confirmed',
                gasUsed: 21000 + Math.floor(Math.random() * 50000)
            };
            
            this.recordTransaction(randomWalletId, transaction);
            this.emit('transaction_detected', { walletId: randomWalletId, transaction });
        }
    }

    // Record transaction in history
    recordTransaction(walletId, transaction) {
        if (!this.transactionHistory.has(walletId)) {
            this.transactionHistory.set(walletId, []);
        }
        
        const history = this.transactionHistory.get(walletId);
        history.push(transaction);
        
        // Keep only last 500 transactions
        if (history.length > 500) {
            history.shift();
        }
    }

    // Generate random Ethereum address
    generateRandomAddress() {
        return `0x${Math.random().toString(16).substr(2, 40)}`;
    }

    // Degrade wallet health on errors
    degradeWalletHealth(walletId) {
        const wallet = this.wallets.get(walletId);
        if (wallet) {
            wallet.health = Math.max(0, wallet.health - 0.1);
            
            if (wallet.health < 0.3) {
                this.emit('wallet_health_warning', {
                    walletId,
                    health: wallet.health,
                    timestamp: Date.now()
                });
            }
        }
    }

    // Get wallet information
    getWallet(walletId) {
        return this.wallets.get(walletId);
    }

    // Get all wallets
    getAllWallets() {
        return Array.from(this.wallets.values());
    }

    // Get wallet balance history
    getBalanceHistory(walletId, timeRange = '24h') {
        const history = this.balanceHistory.get(walletId) || [];
        const now = Date.now();
        let rangeMs;
        
        switch (timeRange) {
            case '1h': rangeMs = 3600000; break;
            case '6h': rangeMs = 21600000; break;
            case '24h': rangeMs = 86400000; break;
            case '7d': rangeMs = 604800000; break;
            default: rangeMs = 86400000; // 24h default
        }
        
        return history.filter(record => record.timestamp > now - rangeMs);
    }

    // Get transaction history
    getTransactionHistory(walletId, limit = 50) {
        const history = this.transactionHistory.get(walletId) || [];
        return history.slice(-limit).reverse(); // Newest first
    }

    // Calculate total capital across all wallets
    getTotalCapital() {
        let total = 0;
        
        this.wallets.forEach(wallet => {
            total += wallet.balance || 0;
            
            wallet.tokens.forEach((balance, token) => {
                // Convert token balances to USD (mock conversion rates)
                const conversionRates = {
                    'USDC': 1.0,
                    'USDT': 1.0,
                    'DAI': 1.0,
                    'WBTC': 45000,
                    'WETH': 2500
                };
                
                const rate = conversionRates[token] || 1.0;
                total += balance * rate;
            });
        });
        
        return total;
    }

    // Get system health status
    getSystemHealth() {
        const wallets = Array.from(this.wallets.values());
        const healthyWallets = wallets.filter(w => w.health > 0.7).length;
        const totalWallets = wallets.length;
        
        return {
            totalWallets,
            healthyWallets,
            healthPercentage: totalWallets > 0 ? (healthyWallets / totalWallets) * 100 : 0,
            totalCapital: this.getTotalCapital(),
            isMonitoring: this.isMonitoring,
            lastUpdate: Math.max(...wallets.map(w => w.lastUpdated))
        };
    }
}

module.exports = WalletDataCollector;
