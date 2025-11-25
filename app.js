const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the React build
app.use(express.static(path.join(__dirname, 'build')));

// API endpoint for status
app.get('/api/status', (req, res) => {
  res.json({
    message: "ÔøΩÔøΩ QuantumNex Platform - Multi-Chain Trading",
    status: "RUNNING", 
    version: "1.0.0",
    services: ["API Gateway", "Trading Bots", "Security Layer", "Multi-Chain Router"],
    timestamp: new Date().toISOString()
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// All other requests return the React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Ì∫Ä QuantumNex Dashboard running on port ${PORT}`);
  console.log(`Ì≥ä Dashboard: http://localhost:${PORT}`);
  console.log(`Ì¥ß API Status: http://localhost:${PORT}/api/status`);
  console.log(`‚ù§Ô∏è  Health: http://localhost:${PORT}/health`);
});

module.exports = app;
