import React, { useState, useEffect } from 'react'

const QuantumNexDashboard = () => {
  const [systemStatus, setSystemStatus] = useState({
    aiEngine: 'ACTIVE',
    apiGateway: 'RUNNING', 
    securityLayer: 'SECURE',
    multiChain: 'SYNCED',
    tradingBots: 'EXECUTING'
  })

  const [tradingBots, setTradingBots] = useState([
    { id: 1, name: 'Arbitrage Hunter', tier: 'TIER_1', status: 'LIVE', pnl: 1245.50, chains: ['ETH', 'BSC', 'POLY'] },
    { id: 2, name: 'Market Maker Pro', tier: 'TIER_2', status: 'LIVE', pnl: 3240.25, chains: ['ETH', 'ARB'] },
    { id: 3, name: 'Flash Loan Sniper', tier: 'TIER_3', status: 'SIMULATION', pnl: 0, chains: ['ETH', 'AVAX'] },
    { id: 4, name: 'Cross-Chain Arb', tier: 'TIER_1', status: 'LIVE', pnl: 867.30, chains: ['ETH', 'BSC', 'FTM'] }
  ])

  const [chainMetrics, setChainMetrics] = useState({
    ethereum: { tps: 15.2, gas: 32.1, volume: 2450000 },
    binance: { tps: 24.7, gas: 8.5, volume: 1870000 },
    polygon: { tps: 45.8, gas: 1.2, volume: 956000 },
    arbitrum: { tps: 12.3, gas: 0.8, volume: 1234000 }
  })

  const [executions, setExecutions] = useState([
    { id: 1, type: 'FLASH_LOAN', chain: 'ETH', amount: 45000, profit: 1245, status: 'COMPLETED' },
    { id: 2, type: 'ARBITRAGE', chain: 'BSC', amount: 23000, profit: 867, status: 'COMPLETED' },
    { id: 3, type: 'LIQUIDATION', chain: 'POLY', amount: 15000, profit: 542, status: 'EXECUTING' },
    { id: 4, type: 'CROSS_CHAIN', chain: 'ARB', amount: 67000, profit: 2103, status: 'PENDING' }
  ])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setExecutions(prev => {
        const newExecutions = [...prev]
        if (Math.random() > 0.7) {
          newExecutions.unshift({
            id: Date.now(),
            type: ['FLASH_LOAN', 'ARBITRAGE', 'LIQUIDATION'][Math.floor(Math.random() * 3)],
            chain: ['ETH', 'BSC', 'POLY', 'ARB'][Math.floor(Math.random() * 4)],
            amount: Math.floor(Math.random() * 100000) + 10000,
            profit: Math.floor(Math.random() * 2000) + 200,
            status: 'COMPLETED'
          })
        }
        return newExecutions.slice(0, 10)
      })
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="quantumnex-dashboard">
      {/* Header */}
      <header className="qn-header">
        <div className="qn-brand">
          <h1>íº€ QuantumNex AI Trading Engine</h1>
          <span className="qn-subtitle">Enterprise Multi-Chain DeFi Execution</span>
        </div>
        <div className="qn-system-status">
          <div className={`status-indicator ${systemStatus.aiEngine.toLowerCase()}`}>
            AI Engine: {systemStatus.aiEngine}
          </div>
          <div className={`status-indicator ${systemStatus.securityLayer.toLowerCase()}`}>
            Security: {systemStatus.securityLayer}
          </div>
        </div>
      </header>

      {/* Main Dashboard Grid */}
      <div className="qn-grid">
        
        {/* System Overview */}
        <div className="qn-card system-overview">
          <h2>í»  System Overview</h2>
          <div className="system-metrics">
            <div className="metric">
              <span className="metric-label">API Gateway</span>
              <span className="metric-value running">{systemStatus.apiGateway}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Multi-Chain Router</span>
              <span className="metric-value synced">{systemStatus.multiChain}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Active Bots</span>
              <span className="metric-value executing">{tradingBots.filter(b => b.status === 'LIVE').length}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Total PnL</span>
              <span className="metric-value profit">
                ${tradingBots.reduce((sum, bot) => sum + bot.pnl, 0).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Trading Bots Management */}
        <div className="qn-card bots-management">
          <h2>í´– Three-Tier Bot System</h2>
          <div className="bots-grid">
            {tradingBots.map(bot => (
              <div key={bot.id} className={`bot-card ${bot.tier.toLowerCase()} ${bot.status.toLowerCase()}`}>
                <div className="bot-header">
                  <span className="bot-name">{bot.name}</span>
                  <span className={`bot-status ${bot.status.toLowerCase()}`}>{bot.status}</span>
                </div>
                <div className="bot-tier">{bot.tier.replace('_', ' ')}</div>
                <div className="bot-chains">
                  {bot.chains.map(chain => (
                    <span key={chain} className="chain-tag">{chain}</span>
                  ))}
                </div>
                <div className="bot-pnl">PnL: ${bot.pnl.toLocaleString()}</div>
                <div className="bot-actions">
                  <button className="btn-small">Details</button>
                  {bot.status === 'SIMULATION' && (
                    <button className="btn-small primary">Deploy</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Multi-Chain Monitoring */}
        <div className="qn-card chain-monitoring">
          <h2>â›“ Multi-Chain Metrics</h2>
          <div className="chains-grid">
            {Object.entries(chainMetrics).map(([chain, metrics]) => (
              <div key={chain} className="chain-card">
                <h3>{chain.toUpperCase()}</h3>
                <div className="chain-metrics">
                  <div className="chain-metric">
                    <span>TPS</span>
                    <strong>{metrics.tps}</strong>
                  </div>
                  <div className="chain-metric">
                    <span>Gas</span>
                    <strong>{metrics.gas} Gwei</strong>
                  </div>
                  <div className="chain-metric">
                    <span>Volume</span>
                    <strong>${(metrics.volume / 1000).toFixed(0)}K</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Executions */}
        <div className="qn-card live-executions">
          <h2>âš¡ Live Executions</h2>
          <div className="executions-list">
            {executions.map(exec => (
              <div key={exec.id} className={`execution-item ${exec.status.toLowerCase()}`}>
                <div className="exec-type">{exec.type.replace('_', ' ')}</div>
                <div className="exec-chain">{exec.chain}</div>
                <div className="exec-amount">${exec.amount.toLocaleString()}</div>
                <div className="exec-profit">+${exec.profit}</div>
                <div className={`exec-status ${exec.status.toLowerCase()}`}>{exec.status}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="qn-card quick-actions">
          <h2>í¾¯ Quick Actions</h2>
          <div className="action-buttons">
            <button className="qn-btn primary">Start Zero-Sim</button>
            <button className="qn-btn secondary">Gasless Trade</button>
            <button className="qn-btn outline">Flash Loan Setup</button>
            <button className="qn-btn outline">Bot Factory</button>
            <button className="qn-btn danger">Emergency Stop</button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default QuantumNexDashboard
