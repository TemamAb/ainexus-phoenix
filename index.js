const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({ 
    message: 'QuantumNex Platform Running',
    status: 'OK',
    version: '1.0.0'
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`ï¿½ï¿½ QuantumNex running on port ${PORT}`);
  console.log(`í³Š Health check: http://localhost:${PORT}/health`);
});
