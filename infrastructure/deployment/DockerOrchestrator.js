// AINEXUS - PHASE 1 MODULE 7: DOCKER ORCHESTRATOR
// Containerized Deployment & Management

const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');
const EventEmitter = require('events');

const execAsync = promisify(exec);

class DockerOrchestrator extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.containers = {};
        this.services = {};
        this.healthStatus = {};
        this.isRunning = false;
    }

    // Initialize Docker orchestrator
    async initialize() {
        try {
            console.log('Ì∫Ä Initializing Docker Orchestrator...');
            
            // Verify Docker is available
            await this.verifyDocker();
            
            // Create necessary directories
            await this.createDirectories();
            
            // Generate Docker configurations
            await this.generateDockerConfigs();
            
            // Start health monitoring
            this.startHealthMonitoring();
            
            this.isRunning = true;
            
            this.emit('module_ready', { module: 'DockerOrchestrator', status: 'active' });
            return { success: true, dockerAvailable: true };
        } catch (error) {
            this.emit('module_error', { module: 'DockerOrchestrator', error: error.message });
            throw error;
        }
    }

    // Verify Docker installation
    async verifyDocker() {
        try {
            const { stdout } = await execAsync('docker --version');
            console.log('‚úÖ Docker available:', stdout.trim());
            return true;
        } catch (error) {
            throw new Error('Docker not available. Please install Docker.');
        }
    }

    // Create necessary directories
    async createDirectories() {
        const directories = [
            './docker',
            './docker/configs',
            './docker/logs',
            './docker/data',
            './docker/scripts'
        ];

        for (const dir of directories) {
            try {
                await fs.mkdir(dir, { recursive: true });
            } catch (error) {
                // Directory might already exist
            }
        }
    }

    // Generate Docker configurations
    async generateDockerConfigs() {
        // Generate Dockerfile for Ainexus Core
        const dockerfileContent = `
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S ainexus && \\
    adduser -S ainexus -u 1001

# Change ownership
RUN chown -R ainexus:ainexus /app

USER ainexus

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD node scripts/health-check.js

# Start application
CMD ["node", "scripts/start-phase1.js"]
`;

        await fs.writeFile('./docker/Dockerfile', dockerfileContent);

        // Generate docker-compose.yml
        const dockerComposeContent = `
version: '3.8'

services:
  ainexus-core:
    build:
      context: .
      dockerfile: ./docker/Dockerfile
    container_name: ainexus-phase1
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - RPC_URL=${process.env.RPC_URL || 'https://mainnet.infura.io/v3/your-project-id'}
      - LOG_LEVEL=info
    volumes:
      - ./docker/logs:/app/logs
      - ./docker/data:/app/data
    healthcheck:
      test: ["CMD", "node", "scripts/health-check.js"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    container_name: ainexus-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data

volumes:
  redis-data:
`;

        await fs.writeFile('./docker/docker-compose.yml', dockerComposeContent);

        // Generate health check script
        const healthCheckContent = `
const http = require('http');

const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/health',
    method: 'GET',
    timeout: 2000
};

const req = http.request(options, (res) => {
    if (res.statusCode === 200) {
        process.exit(0);
    } else {
        process.exit(1);
    }
});

req.on('error', () => {
    process.exit(1);
});

req.on('timeout', () => {
    process.exit(1);
});

req.end();
`;

        await fs.writeFile('./docker/scripts/health-check.js', healthCheckContent);

        // Generate start script
        const startScriptContent = `
#!/usr/bin/env node
// Ainexus Phase 1 Start Script
const ArbitrageOrchestrator = require('../core/engine/ArbitrageOrchestrator');
const FlashLoanExecutor = require('../core/execution/FlashLoanExecutor');
const SingleWalletManager = require('../core/wallet/SingleWalletManager');
const BasicDashboard = require('../ui/dashboard/BasicDashboard');
const BasicCircuitBreaker = require('../core/risk/BasicCircuitBreaker');
const ProfitTracker = require('../core/analytics/ProfitTracker');

async function startPhase1() {
    console.log('Ì∫Ä Starting Ainexus Phase 1 in Docker...');
    
    try {
        // Initialize all modules
        const modules = {};
        
        modules.arbitrageOrchestrator = new ArbitrageOrchestrator(require('../core/engine/config'));
        modules.flashLoanExecutor = new FlashLoanExecutor(require('../core/execution/config'));
        modules.walletManager = new SingleWalletManager(require('../core/wallet/config'));
        modules.circuitBreaker = new BasicCircuitBreaker(require('../core/risk/config'));
        modules.profitTracker = new ProfitTracker(require('../core/analytics/config'));
        modules.dashboard = new BasicDashboard(require('../ui/dashboard/config'));
        
        // Initialize modules
        await modules.arbitrageOrchestrator.initialize();
        await modules.flashLoanExecutor.initialize();
        await modules.walletManager.initialize();
        await modules.circuitBreaker.initialize();
        await modules.profitTracker.initialize();
        await modules.dashboard.initialize(modules);
        
        console.log('‚úÖ All Phase 1 modules initialized successfully');
        
        // Start dashboard
        modules.dashboard.startConsoleDashboard();
        
        // Keep the process running
        process.on('SIGINT', async () => {
            console.log('\\nÌªë Shutting down Ainexus...');
            await modules.dashboard.stop();
            await modules.arbitrageOrchestrator.stop();
            await modules.circuitBreaker.stop();
            await modules.profitTracker.stop();
            process.exit(0);
        });
        
    } catch (error) {
        console.error('‚ùå Failed to start Ainexus:', error);
        process.exit(1);
    }
}

// Simple HTTP health check endpoint
const http = require('http');
const server = http.createServer((req, res) => {
    if (req.url === '/health') {
        res.writeHead(200);
        res.end('OK');
    } else {
        res.writeHead(404);
        res.end('Not Found');
    }
});

server.listen(3000, () => {
    console.log('Ìºê Health check server listening on port 3000');
    startPhase1();
});
`;

        await fs.writeFile('./docker/scripts/start-phase1.js', startScriptContent);
        await fs.chmod('./docker/scripts/start-phase1.js', 0o755);

        console.log('‚úÖ Docker configurations generated');
    }

    // Build Docker image
    async buildImage() {
        try {
            console.log('ÌøóÔ∏è Building Docker image...');
            
            const { stdout } = await execAsync(
                'docker build -t ainexus-phase1:latest -f ./docker/Dockerfile .',
                { cwd: process.cwd() }
            );
            
            console.log('‚úÖ Docker image built successfully');
            this.emit('image_built', { image: 'ainexus-phase1:latest' });
            
            return { success: true, output: stdout };
        } catch (error) {
            throw new Error(`Docker build failed: ${error.message}`);
        }
    }

    // Start containers using docker-compose
    async startContainers() {
        try {
            console.log('Ì∫Ä Starting Ainexus containers...');
            
            const { stdout } = await execAsync(
                'docker-compose -f ./docker/docker-compose.yml up -d',
                { cwd: process.cwd() }
            );
            
            // Wait for services to be ready
            await this.waitForServices();
            
            console.log('‚úÖ Ainexus containers started successfully');
            this.emit('containers_started', { services: ['ainexus-core', 'redis'] });
            
            return { success: true, output: stdout };
        } catch (error) {
            throw new Error(`Failed to start containers: ${error.message}`);
        }
    }

    // Wait for services to be ready
    async waitForServices() {
        const maxAttempts = 30;
        const delay = 2000; // 2 seconds
        
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                const { stdout } = await execAsync(
                    'docker-compose -f ./docker/docker-compose.yml ps --services --filter "status=running"'
                );
                
                const runningServices = stdout.trim().split('\\n').filter(s => s);
                
                if (runningServices.length >= 1) { // At least core service
                    console.log(`‚úÖ Services running: ${runningServices.join(', ')}`);
                    return true;
                }
                
                if (attempt < maxAttempts) {
                    console.log(`‚è≥ Waiting for services... (${attempt}/${maxAttempts})`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            } catch (error) {
                console.log(`‚ö†Ô∏è Health check attempt ${attempt} failed: ${error.message}`);
                if (attempt < maxAttempts) {
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        
        throw new Error('Services failed to start within expected time');
    }

    // Stop containers
    async stopContainers() {
        try {
            console.log('Ìªë Stopping Ainexus containers...');
            
            const { stdout } = await execAsync(
                'docker-compose -f ./docker/docker-compose.yml down',
                { cwd: process.cwd() }
            );
            
            console.log('‚úÖ Ainexus containers stopped successfully');
            this.emit('containers_stopped');
            
            return { success: true, output: stdout };
        } catch (error) {
            throw new Error(`Failed to stop containers: ${error.message}`);
        }
    }

    // Get container status
    async getContainerStatus() {
        try {
            const { stdout } = await execAsync(
                'docker-compose -f ./docker/docker-compose.yml ps --format json'
            );
            
            const containers = JSON.parse(stdout);
            this.containers = {};
            
            containers.forEach(container => {
                this.containers[container.Service] = {
                    service: container.Service,
                    state: container.State,
                    status: container.Status,
                    ports: container.Ports
                };
            });
            
            return this.containers;
        } catch (error) {
            console.error('Failed to get container status:', error);
            return {};
        }
    }

    // Get container logs
    async getContainerLogs(service = 'ainexus-core', lines = 50) {
        try {
            const { stdout } = await execAsync(
                `docker-compose -f ./docker/docker-compose.yml logs --tail=${lines} ${service}`
            );
            
            return { success: true, logs: stdout };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // Start health monitoring
    startHealthMonitoring() {
        this.healthInterval = setInterval(async () => {
            try {
                const status = await this.getContainerStatus();
                const healthStatus = await this.checkHealth();
                
                this.healthStatus = {
                    timestamp: Date.now(),
                    containers: status,
                    health: healthStatus
                };
                
                this.emit('health_update', this.healthStatus);
                
                // Check if any container is unhealthy
                const unhealthy = Object.values(status).filter(c => c.state !== 'running');
                if (unhealthy.length > 0) {
                    this.emit('health_alert', { unhealthy, status });
                }
                
            } catch (error) {
                console.error('Health monitoring error:', error);
            }
        }, this.config.healthCheckInterval || 30000); // Check every 30 seconds
    }

    // Check health of services
    async checkHealth() {
        try {
            // Check if core service is responding
            const { stdout: coreStatus } = await execAsync(
                'docker exec ainexus-phase1 node scripts/health-check.js || echo "FAILED"'
            );
            
            return {
                core: coreStatus.includes('FAILED') ? 'unhealthy' : 'healthy',
                redis: this.containers.redis?.state === 'running' ? 'healthy' : 'unhealthy',
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                core: 'unhealthy',
                redis: 'unknown',
                error: error.message
            };
        }
    }

    // Deploy full stack
    async deployFullStack() {
        try {
            console.log('ÌæØ Deploying Ainexus Phase 1 Full Stack...');
            
            // Build image
            await this.buildImage();
            
            // Start containers
            await this.startContainers();
            
            // Verify deployment
            const status = await this.getContainerStatus();
            const health = await this.checkHealth();
            
            console.log('‚úÖ Ainexus Phase 1 deployed successfully!');
            console.log('Ì≥ä Deployment Status:');
            Object.entries(status).forEach(([service, info]) => {
                console.log(`   ${service}: ${info.state} - ${info.status}`);
            });
            
            this.emit('deployment_complete', { status, health });
            
            return { success: true, status, health };
            
        } catch (error) {
            this.emit('deployment_failed', { error: error.message });
            throw error;
        }
    }

    // Get orchestrator status
    getStatus() {
        return {
            isRunning: this.isRunning,
            containers: Object.keys(this.containers).length,
            healthStatus: this.healthStatus,
            configGenerated: true
        };
    }

    // Stop orchestrator
    stop() {
        this.isRunning = false;
        
        if (this.healthInterval) {
            clearInterval(this.healthInterval);
        }
        
        console.log('Ìªë Docker Orchestrator stopped');
    }
}

module.exports = DockerOrchestrator;
