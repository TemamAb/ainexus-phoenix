/**
 * Real-time Infrastructure Monitoring Dashboard
 * Monitors trading infrastructure health, performance, and capacity
 */

const WebSocket = require('ws');
const EventEmitter = require('events');
const { performance } = require('perf_hooks');

class InfrastructureMonitor extends EventEmitter {
    constructor() {
        super();
        this.metrics = new Map();
        this.alertThresholds = this.initializeThresholds();
        this.healthChecks = new Map();
        this.performanceMetrics = new Map();
        this.isMonitoring = false;
        
        this.initializeMetricsCollection();
    }

    initializeThresholds() {
        return {
            latency: {
                critical: 1000,  // ms
                warning: 500     // ms
            },
            cpu: {
                critical: 90,    // %
                warning: 75      // %
            },
            memory: {
                critical: 90,    // %
                warning: 80      // %
            },
            disk: {
                critical: 90,    // %
                warning: 85      // %
            },
            network: {
                critical: 1000,  // ms
                warning: 500     // ms
            }
        };
    }

    initializeMetricsCollection() {
        // Initialize metrics for all monitored components
        const components = [
            'execution_engine', 'data_feeds', 'risk_engine', 
            'compliance_engine', 'api_gateway', 'database',
            'cache_layer', 'message_bus', 'monitoring_system'
        ];

        components.forEach(component => {
            this.metrics.set(component, {
                status: 'healthy',
                lastCheck: Date.now(),
                latency: 0,
                errorRate: 0,
                throughput: 0,
                resourceUsage: {
                    cpu: 0,
                    memory: 0,
                    disk: 0,
                    network: 0
                },
                alerts: []
            });
        });
    }

    startMonitoring() {
        this.isMonitoring = true;
        console.log('🚀 Starting infrastructure monitoring...');

        // Start periodic health checks
        this.healthCheckInterval = setInterval(() => {
            this.performHealthChecks();
        }, 5000); // Every 5 seconds

        // Start performance monitoring
        this.performanceInterval = setInterval(() => {
            this.collectPerformanceMetrics();
        }, 10000); // Every 10 seconds

        // Start alert processing
        this.alertInterval = setInterval(() => {
            this.processAlerts();
        }, 30000); // Every 30 seconds
    }

    stopMonitoring() {
        this.isMonitoring = false;
        clearInterval(this.healthCheckInterval);
        clearInterval(this.performanceInterval);
        clearInterval(this.alertInterval);
        console.log('🛑 Infrastructure monitoring stopped');
    }

    async performHealthChecks() {
        const checkPromises = Array.from(this.metrics.keys()).map(async (component) => {
            try {
                const health = await this.checkComponentHealth(component);
                this.updateComponentMetrics(component, health);
                
                // Check for threshold violations
                this.checkThresholdViolations(component, health);
                
            } catch (error) {
                console.error(`Health check failed for ${component}:`, error);
                this.recordComponentFailure(component, error.message);
            }
        });

        await Promise.allSettled(checkPromises);
    }

    async checkComponentHealth(component) {
        const startTime = performance.now();
        
        // Simulate health check - in real implementation, this would make actual checks
        const health = {
            status: 'healthy',
            latency: Math.random() * 200, // Simulated latency
            timestamp: Date.now(),
            metrics: {
                cpu: Math.random() * 100,
                memory: Math.random() * 100,
                disk: Math.random() * 100,
                network: Math.random() * 1000
            },
            throughput: Math.random() * 1000,
            errorRate: Math.random() * 5
        };

        // Simulate occasional failures
        if (Math.random() < 0.05) { // 5% chance of failure
            health.status = 'degraded';
            health.errorRate = Math.random() * 50 + 10;
        }

        const endTime = performance.now();
        health.latency = endTime - startTime;

        return health;
    }

    updateComponentMetrics(component, health) {
        const currentMetrics = this.metrics.get(component);
        
        this.metrics.set(component, {
            ...currentMetrics,
            status: health.status,
            lastCheck: health.timestamp,
            latency: health.latency,
            errorRate: health.errorRate,
            throughput: health.throughput,
            resourceUsage: health.metrics
        });

        this.emit('metricsUpdate', { component, metrics: this.metrics.get(component) });
    }

    checkThresholdViolations(component, health) {
        const thresholds = this.alertThresholds;
        const alerts = [];

        // Check latency
        if (health.latency > thresholds.latency.critical) {
            alerts.push({
                severity: 'CRITICAL',
                type: 'LATENCY',
                message: `Critical latency detected: ${health.latency.toFixed(2)}ms`,
                timestamp: Date.now()
            });
        } else if (health.latency > thresholds.latency.warning) {
            alerts.push({
                severity: 'WARNING',
                type: 'LATENCY',
                message: `High latency detected: ${health.latency.toFixed(2)}ms`,
                timestamp: Date.now()
            });
        }

        // Check CPU usage
        if (health.metrics.cpu > thresholds.cpu.critical) {
            alerts.push({
                severity: 'CRITICAL',
                type: 'CPU',
                message: `Critical CPU usage: ${health.metrics.cpu.toFixed(2)}%`,
                timestamp: Date.now()
            });
        }

        // Check memory usage
        if (health.metrics.memory > thresholds.memory.critical) {
            alerts.push({
                severity: 'CRITICAL',
                type: 'MEMORY',
                message: `Critical memory usage: ${health.metrics.memory.toFixed(2)}%`,
                timestamp: Date.now()
            });
        }

        // Check error rate
        if (health.errorRate > 10) {
            alerts.push({
                severity: 'CRITICAL',
                type: 'ERROR_RATE',
                message: `High error rate: ${health.errorRate.toFixed(2)}%`,
                timestamp: Date.now()
            });
        }

        // Add alerts to component
        if (alerts.length > 0) {
            const currentMetrics = this.metrics.get(component);
            currentMetrics.alerts.push(...alerts);
            this.metrics.set(component, currentMetrics);

            // Emit alert events
            alerts.forEach(alert => {
                this.emit('alert', { component, alert });
            });
        }
    }

    recordComponentFailure(component, error) {
        const currentMetrics = this.metrics.get(component);
        currentMetrics.status = 'failed';
        currentMetrics.alerts.push({
            severity: 'CRITICAL',
            type: 'FAILURE',
            message: `Component failure: ${error}`,
            timestamp: Date.now()
        });

        this.metrics.set(component, currentMetrics);
        this.emit('componentFailure', { component, error });
    }

    async collectPerformanceMetrics() {
        const performanceData = {
            timestamp: Date.now(),
            components: {},
            systemWide: {
                totalThroughput: 0,
                averageLatency: 0,
                overallHealth: 100
            }
        };

        let totalLatency = 0;
        let healthyComponents = 0;

        this.metrics.forEach((metrics, component) => {
            performanceData.components[component] = {
                status: metrics.status,
                latency: metrics.latency,
                throughput: metrics.throughput,
                errorRate: metrics.errorRate,
                resourceUsage: metrics.resourceUsage
            };

            totalLatency += metrics.latency;
            performanceData.systemWide.totalThroughput += metrics.throughput;

            if (metrics.status === 'healthy') {
                healthyComponents++;
            }
        });

        performanceData.systemWide.averageLatency = totalLatency / this.metrics.size;
        performanceData.systemWide.overallHealth = (healthyComponents / this.metrics.size) * 100;

        this.performanceMetrics.set(performanceData.timestamp, performanceData);
        this.emit('performanceUpdate', performanceData);
    }

    processAlerts() {
        const criticalAlerts = [];
        
        this.metrics.forEach((metrics, component) => {
            const recentAlerts = metrics.alerts.filter(alert => 
                Date.now() - alert.timestamp < 300000 // Last 5 minutes
            );

            criticalAlerts.push(...recentAlerts.filter(alert => 
                alert.severity === 'CRITICAL'
            ));
        });

        if (criticalAlerts.length > 0) {
            this.emit('criticalAlerts', criticalAlerts);
        }
    }

    getInfrastructureStatus() {
        const status = {
            timestamp: Date.now(),
            overallHealth: this.calculateOverallHealth(),
            componentStatus: {},
            criticalAlerts: 0,
            warningAlerts: 0
        };

        this.metrics.forEach((metrics, component) => {
            status.componentStatus[component] = {
                status: metrics.status,
                lastCheck: metrics.lastCheck,
                latency: metrics.latency,
                alerts: metrics.alerts.length
            };

            status.criticalAlerts += metrics.alerts.filter(a => a.severity === 'CRITICAL').length;
            status.warningAlerts += metrics.alerts.filter(a => a.severity === 'WARNING').length;
        });

        return status;
    }

    calculateOverallHealth() {
        let healthyComponents = 0;
        this.metrics.forEach(metrics => {
            if (metrics.status === 'healthy') {
                healthyComponents++;
            }
        });

        return (healthyComponents / this.metrics.size) * 100;
    }

    getPerformanceReport(timeRange = '1h') {
        const now = Date.now();
        let startTime;

        switch (timeRange) {
            case '1h':
                startTime = now - 3600000;
                break;
            case '6h':
                startTime = now - 21600000;
                break;
            case '24h':
                startTime = now - 86400000;
                break;
            default:
                startTime = now - 3600000;
        }

        const relevantMetrics = Array.from(this.performanceMetrics.entries())
            .filter(([timestamp]) => timestamp >= startTime)
            .map(([, data]) => data);

        return {
            timeRange,
            dataPoints: relevantMetrics.length,
            averageLatency: this.calculateAverage(relevantMetrics, 'systemWide.averageLatency'),
            maxLatency: this.calculateMax(relevantMetrics, 'systemWide.averageLatency'),
            totalThroughput: this.calculateAverage(relevantMetrics, 'systemWide.totalThroughput'),
            healthScore: this.calculateAverage(relevantMetrics, 'systemWide.overallHealth')
        };
    }

    calculateAverage(data, path) {
        const values = data.map(item => this.getNestedValue(item, path));
        return values.reduce((sum, val) => sum + val, 0) / values.length;
    }

    calculateMax(data, path) {
        const values = data.map(item => this.getNestedValue(item, path));
        return Math.max(...values);
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current[key], obj);
    }
}

// WebSocket server for real-time dashboard updates
class InfrastructureWebSocket {
    constructor(port = 8080) {
        this.monitor = new InfrastructureMonitor();
        this.wss = new WebSocket.Server({ port });
        this.clients = new Set();

        this.setupWebSocket();
        this.setupMonitorEvents();
    }

    setupWebSocket() {
        this.wss.on('connection', (ws) => {
            console.log('New client connected to infrastructure monitor');
            this.clients.add(ws);

            // Send current status on connection
            ws.send(JSON.stringify({
                type: 'INITIAL_STATUS',
                data: this.monitor.getInfrastructureStatus()
            }));

            ws.on('close', () => {
                this.clients.delete(ws);
                console.log('Client disconnected from infrastructure monitor');
            });

            ws.on('error', (error) => {
                console.error('WebSocket error:', error);
                this.clients.delete(ws);
            });
        });
    }

    setupMonitorEvents() {
        this.monitor.on('metricsUpdate', (data) => {
            this.broadcast({
                type: 'METRICS_UPDATE',
                data
            });
        });

        this.monitor.on('alert', (data) => {
            this.broadcast({
                type: 'ALERT',
                data
            });
        });

        this.monitor.on('performanceUpdate', (data) => {
            this.broadcast({
                type: 'PERFORMANCE_UPDATE',
                data
            });
        });

        this.monitor.on('criticalAlerts', (alerts) => {
            this.broadcast({
                type: 'CRITICAL_ALERTS',
                data: { alerts, timestamp: Date.now() }
            });
        });
    }

    broadcast(message) {
        const messageString = JSON.stringify(message);
        this.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(messageString);
            }
        });
    }

    start() {
        this.monitor.startMonitoring();
        console.log(`Infrastructure WebSocket server running on port ${this.wss.address().port}`);
    }

    stop() {
        this.monitor.stopMonitoring();
        this.wss.close();
        console.log('Infrastructure WebSocket server stopped');
    }
}

module.exports = { InfrastructureMonitor, InfrastructureWebSocket };

// Example usage
if (require.main === module) {
    const wsServer = new InfrastructureWebSocket(8080);
    wsServer.start();

    // Graceful shutdown
    process.on('SIGINT', () => {
        console.log('Shutting down infrastructure monitor...');
        wsServer.stop();
        process.exit(0);
    });
}