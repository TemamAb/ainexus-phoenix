/**
 * QUANTUMNEX WALLET CONNECTOR
 * Industry Standards: Web3React patterns, MetaMask, WalletConnect
 * Validated Sources:
 * - Web3React patterns (React Web3 integration)
 * - MetaMask (Browser wallet integration)
 * - WalletConnect (Mobile wallet support)
 */

const { ethers } = require('ethers');

class WalletConnector {
    constructor() {
        this.connectors = new Map();
        this.activeConnector = null;
        this.provider = null;
        this.signer = null;
        
        this.initializeConnectors();
        console.log('âœ… Wallet Connector initialized with Web3React patterns');
    }

    initializeConnectors() {
        // Initialize available connectors
        this.connectors.set('metamask', {
            name: 'MetaMask',
            supported: typeof window !== 'undefined' && window.ethereum,
            connector: this.metamaskConnector.bind(this)
        });

        this.connectors.set('walletconnect', {
            name: 'WalletConnect',
            supported: true, // Always supported via external library
            connector: this.walletConnectConnector.bind(this)
        });

        this.connectors.set('coinbase', {
            name: 'Coinbase Wallet',
            supported: typeof window !== 'undefined' && window.ethereum?.isCoinbaseWallet,
            connector: this.coinbaseConnector.bind(this)
        });
    }

    async metamaskConnector() {
        if (!window.ethereum) {
            throw new Error('MetaMask not installed');
        }

        try {
            // Request account access
            await window.ethereum.request({ method: 'eth_requestAccounts' });
            
            this.provider = new ethers.providers.Web3Provider(window.ethereum);
            this.signer = this.provider.getSigner();
            this.activeConnector = 'metamask';
            
            const address = await this.signer.getAddress();
            console.log(`âœ… MetaMask connected: ${address}`);
            
            return {
                connector: 'metamask',
                address: address,
                provider: this.provider,
                signer: this.signer
            };
        } catch (error) {
            console.error('âŒ MetaMask connection failed:', error);
            throw error;
        }
    }

    async walletConnectConnector() {
        try {
            // In production, use @walletconnect/web3-provider
            console.log('í´„ WalletConnect connector - requires external library');
            
            // Simulated connection for demo
            this.activeConnector = 'walletconnect';
            
            return {
                connector: 'walletconnect',
                address: null,
                provider: null,
                signer: null
            };
        } catch (error) {
            console.error('âŒ WalletConnect connection failed:', error);
            throw error;
        }
    }

    async coinbaseConnector() {
        if (!window.ethereum?.isCoinbaseWallet) {
            throw new Error('Coinbase Wallet not detected');
        }

        try {
            await window.ethereum.request({ method: 'eth_requestAccounts' });
            
            this.provider = new ethers.providers.Web3Provider(window.ethereum);
            this.signer = this.provider.getSigner();
            this.activeConnector = 'coinbase';
            
            const address = await this.signer.getAddress();
            console.log(`âœ… Coinbase Wallet connected: ${address}`);
            
            return {
                connector: 'coinbase',
                address: address,
                provider: this.provider,
                signer: this.signer
            };
        } catch (error) {
            console.error('âŒ Coinbase Wallet connection failed:', error);
            throw error;
        }
    }

    async connect(connectorType) {
        try {
            const connector = this.connectors.get(connectorType);
            if (!connector) {
                throw new Error(`Unsupported connector: ${connectorType}`);
            }

            if (!connector.supported) {
                throw new Error(`${connector.name} is not supported in this environment`);
            }

            const connection = await connector.connector();
            return connection;
        } catch (error) {
            console.error(`âŒ ${connectorType} connection failed:`, error);
            throw error;
        }
    }

    async disconnect() {
        if (this.activeConnector === 'walletconnect' && this.provider?.disconnect) {
            await this.provider.disconnect();
        }
        
        this.activeConnector = null;
        this.provider = null;
        this.signer = null;
        
        console.log('âœ… Wallet disconnected');
    }

    async switchChain(chainId) {
        if (!window.ethereum) {
            throw new Error('No Ethereum provider available');
        }

        try {
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: `0x${chainId.toString(16)}` }],
            });
            console.log(`âœ… Switched to chain: ${chainId}`);
        } catch (error) {
            console.error('âŒ Chain switch failed:', error);
            throw error;
        }
    }

    async addTokenToWallet(tokenInfo) {
        if (!window.ethereum) {
            throw new Error('No Ethereum provider available');
        }

        try {
            await window.ethereum.request({
                method: 'wallet_watchAsset',
                params: {
                    type: 'ERC20',
                    options: tokenInfo
                }
            });
            console.log('âœ… Token added to wallet');
        } catch (error) {
            console.error('âŒ Token addition failed:', error);
            throw error;
        }
    }

    getActiveConnection() {
        if (!this.activeConnector) {
            return null;
        }

        return {
            connector: this.activeConnector,
            address: this.signer ? this.signer.address : null,
            isConnected: !!this.signer,
            provider: this.provider,
            signer: this.signer
        };
    }

    getSupportedConnectors() {
        const supported = [];
        for (const [type, connector] of this.connectors) {
            if (connector.supported) {
                supported.push({
                    type: type,
                    name: connector.name
                });
            }
        }
        return supported;
    }

    isConnected() {
        return !!this.activeConnector && !!this.signer;
    }

    async getBalance() {
        if (!this.signer) {
            throw new Error('No active connection');
        }

        try {
            const address = await this.signer.getAddress();
            const balance = await this.provider.getBalance(address);
            return ethers.utils.formatEther(balance);
        } catch (error) {
            console.error('âŒ Balance check failed:', error);
            throw error;
        }
    }

    async signMessage(message) {
        if (!this.signer) {
            throw new Error('No active signer');
        }

        try {
            const signature = await this.signer.signMessage(message);
            return signature;
        } catch (error) {
            console.error('âŒ Message signing failed:', error);
            throw error;
        }
    }

    async sendTransaction(transaction) {
        if (!this.signer) {
            throw new Error('No active signer');
        }

        try {
            this.validateTransaction(transaction);
            const tx = await this.signer.sendTransaction(transaction);
            console.log(`âœ… Transaction sent: ${tx.hash}`);
            return tx;
        } catch (error) {
            console.error('âŒ Transaction failed:', error);
            throw error;
        }
    }

    validateTransaction(transaction) {
        const requiredFields = ['to', 'value'];
        const missingFields = requiredFields.filter(field => !transaction[field]);
        
        if (missingFields.length > 0) {
            throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
        }

        if (!ethers.utils.isAddress(transaction.to)) {
            throw new Error('Invalid recipient address');
        }

        return true;
    }

    setupEventListeners() {
        if (!window.ethereum) return;

        // Account changed
        window.ethereum.on('accountsChanged', (accounts) => {
            console.log('í´„ Accounts changed:', accounts);
            this.handleAccountsChanged(accounts);
        });

        // Chain changed
        window.ethereum.on('chainChanged', (chainId) => {
            console.log('í´„ Chain changed:', chainId);
            this.handleChainChanged(chainId);
        });

        // Disconnect
        window.ethereum.on('disconnect', (error) => {
            console.log('í´Œ Wallet disconnected:', error);
            this.handleDisconnect(error);
        });
    }

    handleAccountsChanged(accounts) {
        if (accounts.length === 0) {
            console.log('í´Œ Wallet disconnected');
            this.disconnect();
        } else {
            console.log(`í´„ Account changed to: ${accounts[0]}`);
        }
    }

    handleChainChanged(chainId) {
        console.log(`í´„ Network changed to: ${parseInt(chainId)}`);
        // Reload page or update network info
        window.location.reload();
    }

    handleDisconnect(error) {
        console.error('í´Œ Wallet disconnected:', error);
        this.disconnect();
    }

    removeEventListeners() {
        if (!window.ethereum) return;

        window.ethereum.removeAllListeners('accountsChanged');
        window.ethereum.removeAllListeners('chainChanged');
        window.ethereum.removeAllListeners('disconnect');
    }

    // Utility methods
    getShortAddress(address) {
        if (!address) return '';
        return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    }

    validateAddress(address) {
        return ethers.utils.isAddress(address);
    }

    formatAddress(address) {
        return ethers.utils.getAddress(address);
    }
}

module.exports = WalletConnector;
