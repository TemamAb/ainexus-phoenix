// QUANTUMNEX v1.0 - ENVIRONMENT CONFIGURATION
// Quantum-Speed Cross-Chain Arbitrage Engine

require('dotenv').config();

const config = {
  // Blockchain Networks
  networks: {
    ethereum: {
      rpc: process.env.ETH_RPC_URL || 'https://mainnet.infura.io/v3/your-key',
      chainId: 1
    },
    polygon: {
      rpc: process.env.POLYGON_RPC_URL || 'https://polygon-rpc.com',
      chainId: 137
    },
    arbitrum: {
      rpc: process.env.ARBITRUM_RPC_URL || 'https://arb1.arbitrum.io/rpc',
      chainId: 42161
    },
    bsc: {
      rpc: process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org',
      chainId: 56
    }
  },

  // Performance Settings
  performance: {
    targetLatency: 70, // ms
    maxSlippage: 0.002, // 0.2%
    minProfitThreshold: 0.0015, // 0.15%
    scanInterval: 100 // ms
  },

  // Security Settings
  security: {
    multiSigRequired: true,
    timelockDelay: 172800, // 2 days in seconds
    maxDrawdown: 0.15, // 15%
    emergencyStopEnabled: true
  },

  // Exchange Connections
  exchanges: {
    uniswap: {
      v2: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
      v3: '0xE592427A0AEce92De3Edee1F18E0157C05861564'
    },
    sushiswap: {
      router: '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
    }
  },

  // Database & Cache
  database: {
    redis: {
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379,
      password: process.env.REDIS_PASSWORD || ''
    },
    postgres: {
      host: process.env.PG_HOST || 'localhost',
      port: process.env.PG_PORT || 5432,
      database: process.env.PG_DATABASE || 'quantumnex',
      user: process.env.PG_USER || 'postgres',
      password: process.env.PG_PASSWORD || ''
    }
  }
};

module.exports = config;
