/**
 * QUANTUMNEX LATENCY MONITOR
 * Industry Standards: Performance API, hrtime, Bottleneck detection
 * Validated Sources:
 * - Performance API (Web performance measurement)
 * - process.hrtime (High-resolution timing)
 * - Bottleneck detection algorithms
 */

const { EventEmitter } = require('events');
const { performance } = require('perf_hooks');

class LatencyMonitor extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            sampleSize: config.sampleSize || 100,
            alertThreshold: config.alertThreshold || 100, // ms
            criticalThreshold: config.criticalThreshold || 500, // ms
            checkInterval: config.checkInterval || 5000, // 5 seconds
            ...config
        };
        
        this.latencyData = new Map();
        this.responseTimes = [];
        this.bottlenecks = new Map();
        this.performanceMarks = new Map();
        
        this.initializeMonitoring();
        console.log('‚úÖ Latency Monitor initialized with Performance API patterns');
    }

    initializeMonitoring() {
        // Initialize latency tracking for different operations
        const operations = [
            'api_request',
            'database_query',
            'cache_access',
            'external_service',
            'blockchain_rpc',
            'websocket_message'
        ];
        
        operations.forEach(operation => {
            this.latencyData.set(operation, {
                current: 0,
                average: 0,
                p50: 0,
                p95: 0,
                p99: 0,
                samples: [],
                lastUpdated: new Date()
            });
        });
        
        this.startMonitoring();
    }

    startMonitoring() {
        // Start periodic latency checks
        this.monitoringInterval = setInterval(() => {
            this.performLatencyChecks();
        }, this.config.checkInterval);

        // Start bottleneck analysis
        this.analysisInterval = setInterval(() => {
            this.analyzeBottlenecks();
        }, 30000); // Every 30 seconds
    }

    async measureOperation(operation, asyncFunction) {
        const startTime = performance.now();
        const startHrTime = process.hrtime();
        
        try {
            const result = await asyncFunction();
            const endTime = performance.now();
            const endHrTime = process.hrtime(startHrTime);
            
            const latencyMs = endTime - startTime;
            const latencyNs = endHrTime[0] * 1e9 + endHrTime[1];
            
            this.recordLatency(operation, latencyMs, latencyNs);
            
            return {
                result,
                latency: latencyMs,
                highPrecisionLatency: latencyNs,
                success: true
            };
        } catch (error) {
            const endTime = performance.now();
            const latencyMs = endTime - startTime;
            
            this.recordLatency(operation, latencyMs, 0);
            
            return {
                error,
                latency: latencyMs,
                success: false
            };
        }
    }

    recordLatency(operation, latencyMs, latencyNs) {
        const data = this.latencyData.get(operation);
        if (!data) return;
        
        // Update current latency
        data.current = latencyMs;
        data.lastUpdated = new Date();
        
        // Add to samples
        data.samples.push({
            timestamp: Date.now(),
            latency: latencyMs,
            highPrecision: latencyNs
        });
        
        // Maintain sample size
        if (data.samples.length > this.config.sampleSize) {
            data.samples.shift();
        }
        
        // Calculate percentiles
        this.calculatePercentiles(data);
        
        // Check for alerts
        this.checkLatencyAlerts(operation, latencyMs);
        
        // Emit latency update
        this.emit('latencyUpdate', {
            operation,
            latency: latencyMs,
            highPrecision: latencyNs,
            percentiles: {
                p50: data.p50,
                p95: data.p95,
                p99: data.p99
            },
            timestamp: new Date().toISOString()
        });
    }

    calculatePercentiles(data) {
        if (data.samples.length === 0) return;
        
        const latencies = data.samples.map(s => s.latency).sort((a, b) => a - b);
        
        data.average = latencies.reduce((sum, lat) => sum + lat, 0) / latencies.length;
        data.p50 = this.getPercentile(latencies, 50);
        data.p95 = this.getPercentile(latencies, 95);
        data.p99 = this.getPercentile(latencies, 99);
    }

    getPercentile(sortedArray, percentile) {
        const index = Math.ceil((percentile / 100) * sortedArray.length) - 1;
        return sortedArray[Math.max(0, index)];
    }

    checkLatencyAlerts(operation, latency) {
        if (latency >= this.config.criticalThreshold) {
            this.triggerAlert(operation, latency, 'critical');
        } else if (latency >= this.config.alertThreshold) {
            this.triggerAlert(operation, latency, 'warning');
        }
    }

    triggerAlert(operation, latency, severity) {
        const alert = {
            id: this.generateAlertId(),
            operation,
            latency,
            threshold: severity === 'critical' ? this.config.criticalThreshold : this.config.alertThreshold,
            severity,
            timestamp: new Date().toISOString()
        };
        
        console.log(`Ì∫® LATENCY ALERT: ${operation} - ${latency}ms (${severity})`);
        this.emit('latencyAlert', alert);
    }

    async performLatencyChecks() {
        const checks = [
            this.checkApiLatency(),
            this.checkDatabaseLatency(),
            this.checkCacheLatency(),
            this.checkExternalServiceLatency()
        ];
        
        try {
            await Promise.allSettled(checks);
        } catch (error) {
            console.error('‚ùå Latency checks failed:', error);
        }
    }

    async checkApiLatency() {
        return this.measureOperation('api_request', async () => {
            // Simulate API request
            await this.delay(Math.random() * 200);
            return { status: 'success' };
        });
    }

    async checkDatabaseLatency() {
        return this.measureOperation('database_query', async () => {
            // Simulate database query
            await this.delay(Math.random() * 150);
            return { rows: [] };
        });
    }

    async checkCacheLatency() {
        return this.measureOperation('cache_access', async () => {
            // Simulate cache access
            await this.delay(Math.random() * 50);
            return { data: 'cached' };
        });
    }

    async checkExternalServiceLatency() {
        return this.measureOperation('external_service', async () => {
            // Simulate external service call
            await this.delay(Math.random() * 300);
            return { response: 'ok' };
        });
    }

    analyzeBottlenecks() {
        console.log('Ì¥ç Analyzing performance bottlenecks...');
        
        this.latencyData.forEach((data, operation) => {
            if (data.p95 > this.config.alertThreshold) {
                this.identifyBottleneck(operation, data);
            }
        });
        
        this.emit('bottleneckAnalysis', {
            bottlenecks: Array.from(this.bottlenecks.values()),
            timestamp: new Date().toISOString()
        });
    }

    identifyBottleneck(operation, data) {
        const bottleneck = {
            operation,
            severity: data.p95 >= this.config.criticalThreshold ? 'critical' : 'warning',
            p95Latency: data.p95,
            p99Latency: data.p99,
            sampleSize: data.samples.length,
            trend: this.calculateLatencyTrend(data.samples),
            probableCauses: this.suggestProbableCauses(operation, data),
            recommendations: this.generateBottleneckRecommendations(operation, data)
        };
        
        this.bottlenecks.set(operation, bottleneck);
        
        console.log(`‚ö†Ô∏è Bottleneck identified: ${operation} - P95: ${data.p95}ms`);
    }

    calculateLatencyTrend(samples) {
        if (samples.length < 10) return 'insufficient_data';
        
        const recent = samples.slice(-5).map(s => s.latency);
        const previous = samples.slice(-10, -5).map(s => s.latency);
        
        const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
        const previousAvg = previous.reduce((a, b) => a + b, 0) / previous.length;
        
        const change = ((recentAvg - previousAvg) / previousAvg) * 100;
        
        if (change > 10) return 'increasing';
        if (change < -10) return 'decreasing';
        return 'stable';
    }

    suggestProbableCauses(operation, data) {
        const causes = [];
        
        if (operation === 'database_query' && data.p95 > 100) {
            causes.push('Inefficient database queries');
            causes.push('Missing database indexes');
            causes.push('High database connection pool usage');
        }
        
        if (operation === 'api_request' && data.p95 > 200) {
            causes.push('Heavy request processing');
            causes.push('Inefficient algorithms');
            causes.push('High server load');
        }
        
        if (operation === 'external_service' && data.p95 > 300) {
            causes.push('Slow external API responses');
            causes.push('Network latency issues');
            causes.push('External service degradation');
        }
        
        if (operation === 'cache_access' && data.p95 > 50) {
            causes.push('Cache server overload');
            causes.push('Network latency to cache');
            causes.push('Large cache objects');
        }
        
        return causes.length > 0 ? causes : ['General system load', 'Network congestion'];
    }

    generateBottleneckRecommendations(operation, data) {
        const recommendations = [];
        
        if (operation === 'database_query') {
            recommendations.push('Optimize slow database queries');
            recommendations.push('Add appropriate indexes');
            recommendations.push('Consider database connection pooling');
        }
        
        if (operation === 'api_request') {
            recommendations.push('Implement request caching');
            recommendations.push('Optimize response serialization');
            recommendations.push('Consider request batching');
        }
        
        if (operation === 'external_service') {
            recommendations.push('Implement circuit breaker pattern');
            recommendations.push('Add request timeouts');
            recommendations.push('Cache external service responses');
        }
        
        if (operation === 'cache_access') {
            recommendations.push('Optimize cache key strategy');
            recommendations.push('Consider distributed caching');
            recommendations.push('Monitor cache hit ratios');
        }
        
        recommendations.push('Scale horizontally if pattern persists');
        recommendations.push('Monitor system resources (CPU, Memory, Network)');
        
        return recommendations;
    }

    // Performance marking (similar to Performance API)
    mark(operation) {
        const mark = {
            operation,
            startTime: performance.now(),
            startHrTime: process.hrtime(),
            timestamp: new Date().toISOString()
        };
        
        this.performanceMarks.set(operation, mark);
        return mark;
    }

    measure(operation) {
        const mark = this.performanceMarks.get(operation);
        if (!mark) {
            throw new Error(`No performance mark found for operation: ${operation}`);
        }
        
        const endTime = performance.now();
        const endHrTime = process.hrtime(mark.startHrTime);
        
        const durationMs = endTime - mark.startTime;
        const durationNs = endHrTime[0] * 1e9 + endHrTime[1];
        
        // Record the measurement
        this.recordLatency(operation, durationMs, durationNs);
        
        // Clean up the mark
        this.performanceMarks.delete(operation);
        
        return {
            operation,
            durationMs,
            durationNs,
            timestamp: new Date().toISOString()
        };
    }

    // Advanced latency analysis
    getLatencyReport(timeframe = '1h') {
        const report = {
            timeframe,
            timestamp: new Date().toISOString(),
            operations: {},
            summary: {},
            bottlenecks: Array.from(this.bottlenecks.values())
        };
        
        this.latencyData.forEach((data, operation) => {
            const samples = this.getSamplesInTimeframe(data.samples, timeframe);
            const latencies = samples.map(s => s.latency);
            
            report.operations[operation] = {
                current: data.current,
                average: data.average,
                p50: data.p50,
                p95: data.p95,
                p99: data.p99,
                sampleCount: samples.length,
                trend: this.calculateLatencyTrend(samples),
                status: this.getOperationStatus(data)
            };
        });
        
        report.summary = this.generateLatencySummary(report.operations);
        
        return report;
    }

    getSamplesInTimeframe(samples, timeframe) {
        const now = Date.now();
        let timeLimit;
        
        switch (timeframe) {
            case '5m':
                timeLimit = now - 5 * 60 * 1000;
                break;
            case '1h':
                timeLimit = now - 60 * 60 * 1000;
                break;
            case '6h':
                timeLimit = now - 6 * 60 * 60 * 1000;
                break;
            case '24h':
                timeLimit = now - 24 * 60 * 60 * 1000;
                break;
            default:
                timeLimit = now - 60 * 60 * 1000;
        }
        
        return samples.filter(sample => sample.timestamp >= timeLimit);
    }

    getOperationStatus(data) {
        if (data.p95 >= this.config.criticalThreshold) return 'critical';
        if (data.p95 >= this.config.alertThreshold) return 'degraded';
        return 'healthy';
    }

    generateLatencySummary(operations) {
        let healthyCount = 0;
        let degradedCount = 0;
        let criticalCount = 0;
        let totalOperations = Object.keys(operations).length;
        
        Object.values(operations).forEach(op => {
            switch (op.status) {
                case 'healthy':
                    healthyCount++;
                    break;
                case 'degraded':
                    degradedCount++;
                    break;
                case 'critical':
                    criticalCount++;
                    break;
            }
        });
        
        const healthScore = Math.round((healthyCount / totalOperations) * 100);
        
        return {
            totalOperations,
            healthyCount,
            degradedCount,
            criticalCount,
            healthScore,
            overallStatus: healthScore >= 80 ? 'healthy' : healthScore >= 60 ? 'degraded' : 'critical',
            recommendations: this.generateSystemRecommendations(operations)
        };
    }

    generateSystemRecommendations(operations) {
        const recommendations = [];
        const criticalOps = Object.entries(operations)
            .filter(([_, op]) => op.status === 'critical')
            .map(([name, _]) => name);
        
        if (criticalOps.length > 0) {
            recommendations.push(`Immediate attention required for: ${criticalOps.join(', ')}`);
        }
        
        if (Object.values(operations).some(op => op.trend === 'increasing')) {
            recommendations.push('Monitor increasing latency trends closely');
        }
        
        if (Object.values(operations).filter(op => op.status === 'degraded').length > 2) {
            recommendations.push('Consider system-wide performance review');
        }
        
        return recommendations.length > 0 ? recommendations : ['System performance is stable'];
    }

    // Utility methods
    generateAlertId() {
        return `latency_alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    getOperationLatency(operation) {
        return this.latencyData.get(operation);
    }

    getAllLatencies() {
        return Object.fromEntries(this.latencyData);
    }

    resetOperationData(operation) {
        const data = this.latencyData.get(operation);
        if (data) {
            data.samples = [];
            data.current = 0;
            data.average = 0;
            data.p50 = 0;
            data.p95 = 0;
            data.p99 = 0;
            console.log(`Ì¥Ñ Reset latency data for operation: ${operation}`);
        }
    }

    // Cleanup
    stop() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        if (this.analysisInterval) {
            clearInterval(this.analysisInterval);
        }
        console.log('‚úÖ Latency Monitor stopped');
    }
}

module.exports = LatencyMonitor;
