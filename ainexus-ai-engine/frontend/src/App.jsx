import React, { useState, useEffect } from 'react'

function App() {
  const [metrics, setMetrics] = useState({
    totalProfit: 12458.32,
    liveTrades: { active: 12, total: 250 },
    aiConfidence: 87.5,
    portfolioValue: 248750.42
  })

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '0.5rem'
        }}>
          íº€ Ainexus AI Engine
        </h1>
        <p style={{ color: '#a0a0c0', fontSize: '1.2rem' }}>
          Professional Trading Platform
        </p>
      </header>

      {/* Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1.5rem',
        marginBottom: '3rem'
      }}>
        <MetricCard 
          title="Total Profit" 
          value={`$${metrics.totalProfit.toLocaleString()}`} 
          change="+4.3% today"
        />
        <MetricCard 
          title="Live Trades" 
          value={`${metrics.liveTrades.active}/${metrics.liveTrades.total}`} 
          change="12 active"
        />
        <MetricCard 
          title="AI Confidence" 
          value={`${metrics.aiConfidence}%`} 
          change="Optimizing"
        />
        <MetricCard 
          title="Portfolio Value" 
          value={`$${metrics.portfolioValue.toLocaleString()}`} 
          change="+2.1% today"
        />
      </div>

      {/* Wallet Section */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ color: '#e0e0ff', marginBottom: '1rem' }}>Wallet Overview</h2>
        <div style={{
          background: 'linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid #33334d'
        }}>
          <p style={{ marginBottom: '0.5rem' }}>
            Trading Wallet: <strong>${metrics.portfolioValue.toLocaleString()}</strong> 
            <span style={{ color: '#10b981', marginLeft: '1rem' }}>í¿¢ Connected</span>
          </p>
          <p style={{ marginBottom: '1rem' }}>
            Today's P&L: <strong style={{ color: '#10b981' }}>+${metrics.totalProfit.toLocaleString()} (4.3%)</strong>
          </p>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Button primary>Deposit</Button>
            <Button>Withdraw</Button>
            <Button outline>Transfer</Button>
          </div>
        </div>
      </div>

      {/* Engine Status */}
      <div>
        <h2 style={{ color: '#e0e0ff', marginBottom: '1rem' }}>AI Engine Status</h2>
        <div style={{
          background: 'linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid #33334d'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#10b981', fontWeight: 'bold' }}>í¿¢ ENGINE RUNNING</p>
              <p style={{ color: '#a0a0c0' }}>AI Confidence: {metrics.aiConfidence}%</p>
            </div>
            <Button danger>Stop Engine</Button>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, change }) {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%)',
      padding: '1.5rem',
      borderRadius: '12px',
      border: '1px solid #33334d'
    }}>
      <h3 style={{ 
        fontSize: '0.9rem', 
        color: '#a0a0c0', 
        marginBottom: '0.5rem',
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        {title}
      </h3>
      <p style={{ 
        fontSize: '1.8rem', 
        fontWeight: 'bold', 
        marginBottom: '0.5rem' 
      }}>
        {value}
      </p>
      <span style={{ color: '#10b981', fontSize: '0.9rem' }}>
        â†— {change}
      </span>
    </div>
  )
}

function Button({ children, primary, outline, danger }) {
  const style = {
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s'
  }

  if (primary) {
    style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    style.color = 'white'
  } else if (outline) {
    style.background = 'transparent'
    style.border = '1px solid #4b5563'
    style.color = '#d1d5db'
  } else if (danger) {
    style.background = '#dc2626'
    style.color = 'white'
  } else {
    style.background = '#374151'
    style.color = 'white'
  }

  return (
    <button style={style}>
      {children}
    </button>
  )
}

export default App
