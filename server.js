import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import cors from 'cors';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.static(__dirname));
app.use(express.json());

// Serve main dashboard
app.get('/', (req, res) => {
  res.sendFile(join(__dirname, 'frontend-html', 'unified-dashboard.html'));
});

// Serve other pages
app.get('/dashboard', (req, res) => {
  res.sendFile(join(__dirname, 'frontend-html', 'unified-dashboard.html'));
});

app.get('/profit', (req, res) => {
  res.sendFile(join(__dirname, 'profit_dashboard.html'));
});

// API endpoint for health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    platform: 'AINEXUS v3.0.0',
    modules: 96,
    message: 'AI Trading Platform Running' 
  });
});

// Start server
app.listen(port, () => {
  console.log(`íº AINEXUS Platform running on port ${port}`);
  console.log(`í³ Dashboard: http://localhost:${port}`);
  console.log(`í´§ Health: http://localhost:${port}/api/health`);
});
