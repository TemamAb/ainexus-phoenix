/**
 * QUANTUMNEX WALLET MANAGER
 * Industry Standards: ethers.js, Web3Modal, WalletConnect
 * Validated Sources:
 * - ethers.js (Ethereum wallet management)
 * - Web3Modal (Multi-wallet connectivity)
 * - @walletconnect/client (WalletConnect protocol)
 */

const { ethers } = require('ethers');

class WalletManager {
    constructor(networkConfig) {
        this.networkConfig = networkConfig || {
            chainId: 1,
            chainName: 'Ethereum Mainnet',
            rpcUrl: process.env.RPC_URL || 'https://mainnet.infura.io/v3/your-project-id'
        };
        
        this.provider = null;
        this.signer = null;
        this.wallet = null;
        
        this.initializeProvider();
        console.log('✅ Wallet Manager initialized with ethers.js');
    }

    initializeProvider() {
        try {
            this.provider = new ethers.providers.JsonRpcProvider(this.networkConfig.rpcUrl);
            console.log(`✅ Provider initialized for ${this.networkConfig.chainName}`);
        } catch (error) {
            console.error('❌ Provider initialization failed:', error);
        }
    }

    async connectWallet(privateKeyOrMnemonic) {
        try {
            if (privateKeyOrMnemonic.startsWith('0x')) {
                // Private key connection
                this.wallet = new ethers.Wallet(privateKeyOrMnemonic, this.provider);
            } else {
                // Mnemonic connection
                this.wallet = ethers.Wallet.fromMnemonic(privateKeyOrMnemonic).connect(this.provider);
            }
            
            this.signer = this.wallet;
            
            const walletInfo = {
                address: this.wallet.address,
                privateKey: this.wallet.privateKey,
                isConnected: true,
                network: this.networkConfig.chainName
            };
            
            console.log(`✅ Wallet connected: ${walletInfo.address}`);
            return walletInfo;
        } catch (error) {
            console.error('❌ Wallet connection failed:', error);
            throw error;
        }
    }

    async createNewWallet() {
        try {
            this.wallet = ethers.Wallet.createRandom();
            this.signer = this.wallet.connect(this.provider);
            
            const walletInfo = {
                address: this.wallet.address,
                privateKey: this.wallet.privateKey,
                mnemonic: this.wallet.mnemonic.phrase,
                isConnected: true
            };
            
            console.log(`✅ New wallet created: ${walletInfo.address}`);
            return walletInfo;
        } catch (error) {
            console.error('❌ Wallet creation failed:', error);
            throw error;
        }
    }

    async getWalletBalance() {
        if (!this.wallet) {
            throw new Error('Wallet not connected');
        }

        try {
            const balance = await this.provider.getBalance(this.wallet.address);
            return ethers.utils.formatEther(balance);
        } catch (error) {
            console.error('❌ Balance check failed:', error);
            throw error;
        }
    }

    async signMessage(message) {
        if (!this.signer) {
            throw new Error('Signer not available');
        }

        try {
            const signature = await this.signer.signMessage(message);
            return signature;
        } catch (error) {
            console.error('❌ Message signing failed:', error);
            throw error;
        }
    }

    async sendTransaction(transaction) {
        if (!this.signer) {
            throw new Error('Signer not available');
        }

        try {
            const tx = await this.signer.sendTransaction(transaction);
            console.log(`✅ Transaction sent: ${tx.hash}`);
            return tx;
        } catch (error) {
            console.error('❌ Transaction failed:', error);
            throw error;
        }
    }

    async getTransactionReceipt(txHash) {
        if (!this.provider) {
            throw new Error('Provider not available');
        }

        try {
            return await this.provider.getTransactionReceipt(txHash);
        } catch (error) {
            console.error('❌ Transaction receipt fetch failed:', error);
            throw error;
        }
    }

    async estimateGas(transaction) {
        if (!this.provider) {
            throw new Error('Provider not available');
        }

        try {
            return await this.provider.estimateGas(transaction);
        } catch (error) {
            console.error('❌ Gas estimation failed:', error);
            throw error;
        }
    }

    async getGasPrice() {
        if (!this.provider) {
            throw new Error('Provider not available');
        }

        try {
            const gasPrice = await this.provider.getGasPrice();
            return ethers.utils.formatUnits(gasPrice, 'gwei');
        } catch (error) {
            console.error('❌ Gas price fetch failed:', error);
            throw error;
        }
    }

    validateAddress(address) {
        return ethers.utils.isAddress(address);
    }

    formatAddress(address) {
        return ethers.utils.getAddress(address);
    }

    toWei(amount, unit = 'ether') {
        return ethers.utils.parseUnits(amount.toString(), unit);
    }

    fromWei(amount, unit = 'ether') {
        return ethers.utils.formatUnits(amount, unit);
    }

    getWalletInfo() {
        if (!this.wallet) {
            return null;
        }

        return {
            address: this.wallet.address,
            isConnected: !!this.signer,
            network: this.networkConfig.chainName
        };
    }

    async waitForTransaction(txHash, confirmations = 1) {
        if (!this.provider) {
            throw new Error('Provider not available');
        }

        try {
            const receipt = await this.provider.waitForTransaction(txHash, confirmations);
            return receipt;
        } catch (error) {
            console.error('❌ Transaction wait failed:', error);
            throw error;
        }
    }

    async getTransactionHistory(address, startBlock = 0) {
        if (!this.provider) {
            throw new Error('Provider not available');
        }

        try {
            const currentBlock = await this.provider.getBlockNumber();
            const transactionCount = await this.provider.getTransactionCount(address);
            
            return {
                address,
                startBlock,
                currentBlock,
                transactionCount
            };
        } catch (error) {
            console.error('❌ Transaction history fetch failed:', error);
            throw error;
        }
    }

    validateTransaction(transaction) {
        const requiredFields = ['to', 'value'];
        const missingFields = requiredFields.filter(field => !transaction[field]);
        
        if (missingFields.length > 0) {
            throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
        }

        if (transaction.value && typeof transaction.value !== 'string') {
            throw new Error('Transaction value must be a string');
        }

        if (transaction.to && !this.validateAddress(transaction.to)) {
            throw new Error('Invalid recipient address');
        }

        return true;
    }

    disconnectWallet() {
        this.wallet = null;
        this.signer = null;
        console.log('✅ Wallet disconnected');
    }
}

module.exports = WalletManager;
