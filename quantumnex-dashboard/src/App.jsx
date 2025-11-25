import React, { useState, useEffect } from 'react'

function App() {
  const [theme, setTheme] = useState('dark')
  const [currency, setCurrency] = useState('USD')
  const [refreshRate, setRefreshRate] = useState(3000)
  const [engineMode, setEngineMode] = useState('sim')
  const [isRunning, setIsRunning] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [withdrawalMode, setWithdrawalMode] = useState('manual')
  
  // Mock data - replace with real API calls
  const [dashboardData, setDashboardData] = useState({
    profitPerTrade: '0.85',
    tradesPerHour: '12',
    profitPerHour: '10.20',
    totalProfits: '245.50',
    profitPerDay: '244.80',
    availableBalance: '156.75',
    scannerStatus: 'active',
    executorStatus: 'active',
    validatorStatus: 'active',
    successRate: '92.7',
    avgLatency: '47',
    lastTradeTime: '2 seconds ago',
    uptime: '00:15:32',
    engineVersion: 'v2.1.0',
    nextAutoWithdraw: '23:45:12',
    autoWithdrawThreshold: '100.00'
  })
  
  const [events, setEvents] = useState([
    { timestamp: '12:45:23', chain: 'ETH', type: 'arbitrage', details: 'USDC/DAI +0.85', status: 'success' },
    { timestamp: '12:45:19', chain: 'POLY', type: 'flashloan', details: '1.5M USDC', status: 'pending' },
    { timestamp: '12:45:15', chain: 'BSC', type: 'arbitrage', details: 'BUSD/USDT +1.20', status: 'success' },
    { timestamp: '12:45:08', chain: 'ARB', type: 'flashloan', details: '2.0M USDT', status: 'success' },
    { timestamp: '12:45:01', chain: 'ETH', type: 'arbitrage', details: 'ETH/USDC +2.15', status: 'success' }
  ])

  useEffect(() => {
    document.body.className = `${theme}-theme`
  }, [theme])

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate data updates
      setDashboardData(prev => ({
        ...prev,
        profitPerTrade: (Math.random() * 2).toFixed(2),
        tradesPerHour: Math.floor(Math.random() * 5 + 10),
        profitPerHour: (Math.random() * 20 + 5).toFixed(2),
        availableBalance: (parseFloat(prev.availableBalance) + Math.random() * 0.5).toFixed(2)
      }))
      
      // Add new event
      const newEvent = {
        timestamp: new Date().toLocaleTimeString(),
        chain: ['ETH', 'POLY', 'BSC', 'ARB'][Math.floor(Math.random() * 4)],
        type: Math.random() > 0.3 ? 'arbitrage' : 'flashloan',
        details: Math.random() > 0.3 ? `+${(Math.random() * 3).toFixed(2)}` : `${(Math.random() * 2 + 0.5).toFixed(1)}M USDC`,
        status: Math.random() > 0.1 ? 'success' : 'pending'
      }
      
      setEvents(prev => [newEvent, ...prev.slice(0, 9)])
    }, refreshRate)

    return () => clearInterval(interval)
  }, [refreshRate])

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  const toggleEngine = () => setIsRunning(prev => !prev)
  const connectWallet = () => setIsConnected(prev => !prev)
  
  const withdrawProfits = () => {
    alert(`Withdrawing ${currency}${dashboardData.availableBalance}`)
    setDashboardData(prev => ({ ...prev, availableBalance: '0.00' }))
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <h1>QuantumNex</h1>
        <div className="header-controls">
          <button onClick={toggleTheme}>
            {theme === 'dark' ? '‚òÄÔ∏è Light' : 'Ìºô Dark'}
          </button>
          <select value={currency} onChange={(e) => setCurrency(e.target.value)}>
            <option value="USD">USD</option>
            <option value="ETH">ETH</option>
          </select>
          <select value={refreshRate} onChange={(e) => setRefreshRate(Number(e.target.value))}>
            <option value="1000">1 sec</option>
            <option value="3000">3 sec</option>
            <option value="5000">5 sec</option>
            <option value="10000">10 sec</option>
          </select>
        </div>
      </header>

      {/* First Row - 4 Cards */}
      <div className="cards-grid">
        {/* Card 1: Engine Control */}
        <div className="card engine-control">
          <h3>Ì∫Ä Engine Control</h3>
          <div className="mode-selector">
            <button 
              className={engineMode === 'sim' ? 'active' : ''}
              onClick={() => setEngineMode('sim')}
            >
              SIM MODE
            </button>
            <button 
              className={engineMode === 'live' ? 'active' : ''}
              onClick={() => setEngineMode('live')}
            >
              LIVE MODE
            </button>
          </div>
          <div className="deploy-status">
            <div className="status-indicator">
              {isRunning ? 'Ìø¢ RUNNING' : 'Ì¥¥ STOPPED'}
            </div>
            <button onClick={toggleEngine}>
              {isRunning ? 'STOP ENGINE' : 'START ENGINE'}
            </button>
          </div>
          <div className="engine-info">
            <div>Mode: {engineMode.toUpperCase()}</div>
            <div>Uptime: {dashboardData.uptime}</div>
            <div>Version: {dashboardData.engineVersion}</div>
          </div>
        </div>

        {/* Card 2: Profit Metrics */}
        <div className="card profit-metrics">
          <h3>Ì≥ä Profit Analytics</h3>
          <div className="metrics-grid">
            <div className="metric">
              <div className="label">Profit/Trade</div>
              <div className="value">
                {currency === 'USD' ? '$' : 'Œû'}{dashboardData.profitPerTrade}
              </div>
            </div>
            <div className="metric">
              <div className="label">Trades/Hour</div>
              <div className="value">{dashboardData.tradesPerHour}</div>
            </div>
            <div className="metric">
              <div className="label">Profit/Hour</div>
              <div className="value">
                {currency === 'USD' ? '$' : 'Œû'}{dashboardData.profitPerHour}
              </div>
            </div>
            <div className="metric">
              <div className="label">Total Profits</div>
              <div className="value">
                {currency === 'USD' ? '$' : 'Œû'}{dashboardData.totalProfits}
              </div>
              <div className="subtext">Since deployment</div>
            </div>
            <div className="metric">
              <div className="label">Profit/Day</div>
              <div className="value">
                {currency === 'USD' ? '$' : 'Œû'}{dashboardData.profitPerDay}
              </div>
            </div>
            <div className="metric highlight">
              <div className="label">Available Balance</div>
              <div className="value">
                {currency === 'USD' ? '$' : 'Œû'}{dashboardData.availableBalance}
              </div>
              <div className="subtext">For withdrawal</div>
            </div>
          </div>
        </div>

        {/* Card 3: Wallet Management */}
        <div className="card wallet-management">
          <h3>Ì≤∞ Wallet Management</h3>
          <div className="wallet-connection">
            <div className="wallet-status">
              {isConnected ? 'Ìø¢ CONNECTED' : 'Ì¥¥ DISCONNECTED'}
            </div>
            <button onClick={connectWallet}>
              {isConnected ? 'DISCONNECT' : 'CONNECT WALLET'}
            </button>
          </div>
          <div className="withdrawal-controls">
            <h4>Withdraw Profits</h4>
            <div className="withdrawal-mode">
              <label>
                <input 
                  type="radio" 
                  value="auto" 
                  checked={withdrawalMode === 'auto'}
                  onChange={() => setWithdrawalMode('auto')}
                />
                Auto Withdraw
              </label>
              <label>
                <input 
                  type="radio" 
                  value="manual" 
                  checked={withdrawalMode === 'manual'}
                  onChange={() => setWithdrawalMode('manual')}
                />
                Manual Withdraw
              </label>
            </div>
            {withdrawalMode === 'manual' && (
              <div className="manual-withdraw">
                <div className="available-amount">
                  Available: {currency === 'USD' ? '$' : 'Œû'}{dashboardData.availableBalance}
                </div>
                <button 
                  onClick={withdrawProfits}
                  disabled={parseFloat(dashboardData.availableBalance) <= 0}
                >
                  WITHDRAW {currency === 'USD' ? '$' : 'Œû'}{dashboardData.availableBalance}
                </button>
              </div>
            )}
            {withdrawalMode === 'auto' && (
              <div className="auto-settings">
                <div className="auto-info">
                  Next auto-withdraw: {dashboardData.nextAutoWithdraw}
                </div>
                <div className="threshold">
                  Threshold: {currency === 'USD' ? '$' : 'Œû'}{dashboardData.autoWithdrawThreshold}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Card 4: System Status */}
        <div className="card system-status">
          <h3>‚ö° System Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <div className="label">Scanner Bot</div>
              <div className={`status ${dashboardData.scannerStatus}`}>
                {dashboardData.scannerStatus === 'active' ? 'Ìø¢' : 'Ì¥¥'}
              </div>
            </div>
            <div className="status-item">
              <div className="label">Executor Bot</div>
              <div className={`status ${dashboardData.executorStatus}`}>
                {dashboardData.executorStatus === 'active' ? 'Ìø¢' : 'Ì¥¥'}
              </div>
            </div>
            <div className="status-item">
              <div className="label">Validator Bot</div>
              <div className={`status ${dashboardData.validatorStatus}`}>
                {dashboardData.validatorStatus === 'active' ? 'Ìø¢' : 'Ì¥¥'}
              </div>
            </div>
            <div className="status-item">
              <div className="label">Success Rate</div>
              <div className="value">{dashboardData.successRate}%</div>
            </div>
            <div className="status-item">
              <div className="label">Avg Latency</div>
              <div className="value">{dashboardData.avgLatency}ms</div>
            </div>
            <div className="status-item">
              <div className="label">Last Trade</div>
              <div className="value">{dashboardData.lastTradeTime}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Second Row: Events Stream */}
      <div className="events-stream">
        <h3>Ì¥¥ Live Blockchain Events</h3>
        <div className="events-container">
          {events.map((event, index) => (
            <div 
              key={index}
              className={`event-item ${event.type} ${event.status}`}
            >
              <span className="event-time">{event.timestamp}</span>
              <span className="event-chain">{event.chain}</span>
              <span className="event-type">{event.type}</span>
              <span className="event-details">{event.details}</span>
              <span className={`event-status ${event.status}`}>
                {event.status === 'success' ? '‚úÖ' : 
                 event.status === 'pending' ? 'ÔøΩÔøΩ' : '‚ùå'}
              </span>
            </div>
          ))}
        </div>
        <div className="legend">
          <div className="legend-item success">‚úÖ Success</div>
          <div className="legend-item pending">Ìø° Pending</div>
          <div className="legend-item failed">‚ùå Failed</div>
          <div className="legend-item arbitrage">Ì¥µ Arbitrage</div>
          <div className="legend-item flashloan">Ìø£ Flash Loan</div>
        </div>
      </div>
    </div>
  )
}

export default App
