// AINEXUS - PHASE 1 MODULE 3: SINGLE WALLET MANAGER
// Wallet Integration - MetaMask & WalletConnect

const Web3 = require('web3');
const EventEmitter = require('events');

class SingleWalletManager extends EventEmitter {
    constructor(config) {
        super();
        this.web3 = new Web3(config.rpcUrl);
        this.connected = false;
        this.walletAddress = null;
        this.walletType = null;
        this.balance = '0';
        this.networkId = null;
    }

    // Initialize wallet manager
    async initialize() {
        try {
            console.log('ï¿½ï¿½ Initializing Single Wallet Manager...');
            
            // Check if Web3 is injected (MetaMask)
            if (typeof window !== 'undefined' && window.ethereum) {
                this.web3 = new Web3(window.ethereum);
                this.walletType = 'metamask';
                console.log('âœ… MetaMask detected');
            } else {
                console.log('â„¹ï¸ No injected Web3 detected, using provided RPC');
            }

            this.emit('module_ready', { module: 'SingleWalletManager', status: 'active' });
            return { success: true, walletType: this.walletType };
        } catch (error) {
            this.emit('module_error', { module: 'SingleWalletManager', error: error.message });
            throw error;
        }
    }

    // Connect to wallet (MetaMask)
    async connectWallet() {
        try {
            if (!window.ethereum) {
                throw new Error('MetaMask not installed');
            }

            console.log('í´— Connecting to MetaMask...');
            
            // Request account access
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts'
            });

            this.walletAddress = accounts[0];
            this.connected = true;
            
            // Get network ID
            this.networkId = await window.ethereum.request({
                method: 'net_version'
            });

            // Get initial balance
            await this.updateBalance();

            // Set up event listeners
            this.setupWalletListeners();

            this.emit('wallet_connected', {
                address: this.walletAddress,
                networkId: this.networkId,
                balance: this.balance
            });

            console.log(`âœ… Connected: ${this.walletAddress} (Network: ${this.networkId})`);
            return { success: true, address: this.walletAddress };

        } catch (error) {
            this.emit('connection_failed', { error: error.message });
            throw error;
        }
    }

    // Connect via WalletConnect (alternative)
    async connectWalletConnect() {
        try {
            // WalletConnect would be implemented here
            // For Phase 1, we focus on MetaMask
            throw new Error('WalletConnect not implemented in Phase 1');
        } catch (error) {
            this.emit('connection_failed', { error: error.message });
            throw error;
        }
    }

    // Update wallet balance
    async updateBalance() {
        if (!this.walletAddress) return;

        try {
            const balanceWei = await this.web3.eth.getBalance(this.walletAddress);
            this.balance = this.web3.utils.fromWei(balanceWei, 'ether');
            
            this.emit('balance_updated', {
                address: this.walletAddress,
                balance: this.balance,
                timestamp: Date.now()
            });

            return this.balance;
        } catch (error) {
            console.error('Balance update failed:', error);
            return '0';
        }
    }

    // Sign transaction
    async signTransaction(txObject) {
        if (!this.connected) {
            throw new Error('Wallet not connected');
        }

        try {
            this.emit('transaction_signing', {
                from: this.walletAddress,
                to: txObject.to,
                value: txObject.value
            });

            // For MetaMask, we request signing
            if (this.walletType === 'metamask') {
                const txHash = await window.ethereum.request({
                    method: 'eth_sendTransaction',
                    params: [txObject]
                });

                this.emit('transaction_signed', {
                    hash: txHash,
                    from: this.walletAddress,
                    timestamp: Date.now()
                });

                return txHash;
            } else {
                // For other providers, use web3
                const signedTx = await this.web3.eth.sendTransaction(txObject);
                return signedTx.transactionHash;
            }
        } catch (error) {
            this.emit('transaction_failed', {
                error: error.message,
                from: this.walletAddress,
                timestamp: Date.now()
            });
            throw error;
        }
    }

    // Switch network
    async switchNetwork(networkConfig) {
        try {
            if (this.walletType === 'metamask') {
                await window.ethereum.request({
                    method: 'wallet_switchEthereumChain',
                    params: [{ chainId: networkConfig.chainId }]
                });
                
                this.networkId = networkConfig.chainId;
                this.emit('network_switched', {
                    networkId: this.networkId,
                    networkName: networkConfig.name
                });
                
                return true;
            }
            return false;
        } catch (error) {
            // If chain not added, add it
            if (error.code === 4902) {
                return await this.addNetwork(networkConfig);
            }
            throw error;
        }
    }

    // Add new network
    async addNetwork(networkConfig) {
        try {
            await window.ethereum.request({
                method: 'wallet_addEthereumChain',
                params: [networkConfig]
            });
            
            this.networkId = networkConfig.chainId;
            this.emit('network_added', {
                networkId: this.networkId,
                networkName: networkConfig.name
            });
            
            return true;
        } catch (error) {
            this.emit('network_error', { error: error.message });
            throw error;
        }
    }

    // Set up wallet event listeners
    setupWalletListeners() {
        if (window.ethereum) {
            // Account changed
            window.ethereum.on('accountsChanged', (accounts) => {
                if (accounts.length === 0) {
                    this.disconnectWallet();
                } else {
                    this.walletAddress = accounts[0];
                    this.updateBalance();
                    this.emit('account_changed', { address: this.walletAddress });
                }
            });

            // Network changed
            window.ethereum.on('chainChanged', (chainId) => {
                this.networkId = parseInt(chainId, 16);
                this.updateBalance();
                this.emit('network_changed', { networkId: this.networkId });
            });

            // Disconnect
            window.ethereum.on('disconnect', (error) => {
                this.disconnectWallet();
                this.emit('wallet_disconnected', { error: error?.message });
            });
        }
    }

    // Disconnect wallet
    disconnectWallet() {
        this.connected = false;
        this.walletAddress = null;
        this.balance = '0';
        
        this.emit('wallet_disconnected', {
            timestamp: Date.now(),
            manual: true
        });
        
        console.log('í´Œ Wallet disconnected');
    }

    // Get wallet status
    getStatus() {
        return {
            connected: this.connected,
            walletAddress: this.walletAddress,
            walletType: this.walletType,
            balance: this.balance,
            networkId: this.networkId
        };
    }

    // Validate wallet for arbitrage (minimum balance, etc.)
    async validateForArbitrage() {
        if (!this.connected) {
            return { valid: false, error: 'Wallet not connected' };
        }

        const minBalance = 0.01; // Minimum 0.01 ETH for gas
        const balance = parseFloat(this.balance);

        if (balance < minBalance) {
            return { 
                valid: false, 
                error: `Insufficient balance. Minimum ${minBalance} ETH required` 
            };
        }

        // Check if on mainnet (for Phase 1)
        if (this.networkId !== 1) {
            return { 
                valid: false, 
                error: 'Please switch to Ethereum Mainnet' 
            };
        }

        return { valid: true, balance: this.balance };
    }

    // Get supported networks for Phase 1
    getSupportedNetworks() {
        return {
            1: {
                chainId: '0x1',
                chainName: 'Ethereum Mainnet',
                nativeCurrency: {
                    name: 'Ether',
                    symbol: 'ETH',
                    decimals: 18
                },
                rpcUrls: ['https://mainnet.infura.io/v3/'],
                blockExplorerUrls: ['https://etherscan.io']
            }
        };
    }
}

module.exports = SingleWalletManager;
