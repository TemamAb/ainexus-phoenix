const express = require('express');
const path = require('path');
const fs = require('fs');
const app = express();
const PORT = process.env.PORT || 3000;

// Check if build directory exists
const buildPath = path.join(__dirname, 'build');
const indexHtmlPath = path.join(buildPath, 'index.html');

// Serve static files from the React build if it exists
if (fs.existsSync(buildPath)) {
  app.use(express.static(buildPath));
  console.log('‚úÖ Serving built React app from /build');
} else {
  console.log('‚ö†Ô∏è  Build directory not found - serving fallback');
  
  // Fallback route for development
  app.get('/', (req, res) => {
    res.send(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>QuantumNex AI Trading Engine</title>
          <style>
            body { 
              font-family: Arial, sans-serif; 
              background: #1e1e1e; 
              color: white; 
              margin: 0; 
              padding: 2rem;
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
            }
            .container { 
              text-align: center; 
              max-width: 600px;
            }
            h1 { 
              color: #00d4ff; 
              margin-bottom: 1rem;
              background: linear-gradient(45deg, #00d4ff, #00ff88);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
            }
            .status { 
              background: #2d2d2d; 
              padding: 2rem; 
              border-radius: 8px; 
              border: 1px solid #444;
              margin: 1rem 0;
            }
            .warning { 
              color: #ffaa00; 
              background: rgba(255,170,0,0.1);
              padding: 1rem;
              border-radius: 6px;
              margin: 1rem 0;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>Ì∫Ä QuantumNex AI Trading Engine</h1>
            <div class="status">
              <h2>Enterprise DeFi Monitoring & Execution</h2>
              <p>Status: <strong style="color: #00ff88">RUNNING</strong></p>
              <p>Version: 1.0.0</p>
              <div class="warning">
                <strong>‚ö†Ô∏è Dashboard Building...</strong>
                <p>The React dashboard is currently being built. Please refresh in a moment.</p>
              </div>
            </div>
            <div style="margin-top: 2rem;">
              <p><a href="/api/status" style="color: #00d4ff;">Check API Status</a></p>
              <p><a href="/health" style="color: #00d4ff;">Health Check</a></p>
            </div>
          </div>
        </body>
      </html>
    `);
  });
}

// API endpoint for status
app.get('/api/status', (req, res) => {
  res.json({
    message: "Ì∫Ä QuantumNex Platform - Multi-Chain Trading",
    status: "RUNNING", 
    version: "1.0.0",
    services: ["API Gateway", "Trading Bots", "Security Layer", "Multi-Chain Router"],
    timestamp: new Date().toISOString(),
    build: fs.existsSync(buildPath) ? "READY" : "BUILDING"
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    build: fs.existsSync(buildPath) ? "READY" : "BUILDING"
  });
});

// All other requests return the React app or fallback
app.get('*', (req, res) => {
  if (fs.existsSync(indexHtmlPath)) {
    res.sendFile(indexHtmlPath);
  } else {
    res.redirect('/');
  }
});

app.listen(PORT, () => {
  console.log(`Ì∫Ä QuantumNex Dashboard running on port ${PORT}`);
  console.log(`Ì≥ä Dashboard: http://localhost:${PORT}`);
  console.log(`Ì¥ß API Status: http://localhost:${PORT}/api/status`);
  console.log(`‚ù§Ô∏è  Health: http://localhost:${PORT}/health`);
  
  if (!fs.existsSync(buildPath)) {
    console.log('‚ö†Ô∏è  Build directory not found - running fallback mode');
    console.log('Ì¥ß Run: npm run build to generate React app');
  }
});

module.exports = app;
