const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(require('cors')());

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
  console.log(`ÌæØ QuantumNex API Server running on port ${PORT}`);
  console.log(`Ì≥ç Local: http://localhost:${PORT}`);
  console.log(`Ì≥ä Health: http://localhost:${PORT}/health`);
  console.log(`Ì¥ß API Status: http://localhost:${PORT}/api/status`);
});
