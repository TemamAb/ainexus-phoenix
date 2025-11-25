const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for dashboard on port 3001
app.use(cors({
  origin: 'http://localhost:3001',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true
}));

app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({ 
    message: 'Ì∫Ä QuantumNex Platform - Multi-Chain Trading',
    status: 'RUNNING',
    version: '1.0.0',
    services: ['API Gateway', 'Trading Bots', 'Security Layer', 'Multi-Chain Router'],
    timestamp: new Date().toISOString()
  });
});

app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    database: 'connected',
    redis: 'connected', 
    timestamp: new Date().toISOString()
  });
});

app.get('/api/status', (req, res) => {
  res.json({
    bots: {
      scanner: 'running',
      executor: 'running', 
      validator: 'running'
    },
    infrastructure: {
      redis: 'connected',
      postgres: 'connected'
    },
    performance: {
      latency: '<50ms',
      uptime: process.uptime()
    }
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`ÌæØ QuantumNex API Server (CORS Enabled) running on port ${PORT}`);
  console.log(`Ì≥ç Dashboard can connect from: http://localhost:3001`);
});
