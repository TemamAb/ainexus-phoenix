import express from 'express'
import cors from 'cors'
import { WebSocketServer } from 'ws'
import { createServer } from 'http'

const app = express()
const server = createServer(app)
const port = 8080

app.use(cors())
app.use(express.json())

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'Ainexus AI Engine',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  })
})

// API routes
app.get('/api/metrics', (req, res) => {
  res.json({
    totalProfit: 12458.32,
    liveTrades: { active: 12, total: 250 },
    aiConfidence: 87.5,
    portfolioValue: 248750.42,
    todaysPnL: { amount: 12458.32, percentage: 4.3 }
  })
})

// WebSocket server for real-time data
const wss = new WebSocketServer({ server, path: '/ws' })

wss.on('connection', (ws) => {
  console.log('WebSocket client connected')
  
  // Send welcome message
  ws.send(JSON.stringify({
    type: 'welcome',
    message: 'Connected to Ainexus AI Engine',
    timestamp: new Date().toISOString()
  }))

  // Simulate real-time trading data
  const interval = setInterval(() => {
    const mockData = {
      type: 'trading_update',
      data: {
        timestamp: new Date().toISOString(),
        profit: (Math.random() * 1000).toFixed(2),
        activeTrades: Math.floor(Math.random() * 20),
        aiConfidence: (85 + Math.random() * 10).toFixed(1)
      }
    }
    ws.send(JSON.stringify(mockData))
  }, 2000)

  ws.on('close', () => {
    console.log('WebSocket client disconnected')
    clearInterval(interval)
  })
})

// Start server
server.listen(port, () => {
  console.log(`íº€ Ainexus AI Engine server running on port ${port}`)
  console.log(`í³Š WebSocket server available at ws://localhost:${port}/ws`)
  console.log(`í¿¥ Health check: http://localhost:${port}/health`)
})
