// File: advanced_ai/protocol_integration/ProtocolHealthMonitor.js
// 7P-PILLAR: BOT3-7P
// PURPOSE: Comprehensive DeFi protocol health monitoring

const { EventEmitter } = require('events');

class ProtocolHealthMonitor extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.protocolStatus = new Map();
        this.healthMetrics = new Map();
        this.incidentHistory = [];
        this.isMonitoring = false;
        
        this.initializeProtocols();
    }

    // Initialize supported DeFi protocols
    initializeProtocols() {
        const supportedProtocols = [
            {
                name: 'Aave',
                type: 'lending',
                chains: ['ethereum', 'polygon', 'avalanche'],
                health: 1.0,
                lastChecked: Date.now(),
                criticalMetrics: ['totalValueLocked', 'borrowAPY', 'utilizationRate']
            },
            {
                name: 'UniswapV3',
                type: 'dex',
                chains: ['ethereum', 'polygon', 'arbitrum', 'optimism'],
                health: 1.0,
                lastChecked: Date.now(),
                criticalMetrics: ['totalLiquidity', 'volume24h', 'feeCollection']
            },
            {
                name: 'Compound',
                type: 'lending',
                chains: ['ethereum'],
                health: 1.0,
                lastChecked: Date.now(),
                criticalMetrics: ['totalValueLocked', 'reserveFactor', 'collateralFactor']
            },
            {
                name: 'Curve',
                type: 'dex',
                chains: ['ethereum', 'polygon', 'arbitrum'],
                health: 1.0,
                lastChecked: Date.now(),
                criticalMetrics: ['totalValueLocked', 'volume24h', 'poolBalances']
            },
            {
                name: 'Lido',
                type: 'staking',
                chains: ['ethereum'],
                health: 1.0,
                lastChecked: Date.now(),
                criticalMetrics: ['totalValueLocked', 'stakedETH', 'validatorPerformance']
            },
            {
                name: 'MakerDAO',
                type: 'lending',
                chains: ['ethereum'],
                health: 1.0,
                lastChecked: Date.now(),
                criticalMetrics: ['totalValueLocked', 'debtCeiling', 'collateralizationRatio']
            }
        ];

        supportedProtocols.forEach(protocol => {
            this.protocolStatus.set(protocol.name, protocol);
            this.healthMetrics.set(protocol.name, {
                uptime: 1.0,
                responseTime: 0,
                errorRate: 0,
                lastIncident: null,
                performanceScore: 100
            });
        });

        console.log(`âœ… Initialized ${this.protocolStatus.size} DeFi protocol health monitors`);
    }

    // Start continuous protocol monitoring
    startMonitoring() {
        if (this.isMonitoring) {
            console.log('âš ï¸ Protocol monitoring already active');
            return;
        }

        this.isMonitoring = true;
        console.log('í¿¥ Starting continuous protocol health monitoring...');

        // Monitor each protocol
        this.protocolStatus.forEach((protocol, protocolName) => {
            const interval = setInterval(async () => {
                try {
                    await this.checkProtocolHealth(protocolName);
                } catch (error) {
                    console.error(`Error monitoring protocol ${protocolName}:`, error);
                    this.recordProtocolIncident(protocolName, 'monitoring_error', error.message);
                }
            }, this.config.checkInterval || 120000); // Default 2 minutes

            this.monitoringIntervals = this.monitoringIntervals || new Map();
            this.monitoringIntervals.set(protocolName, interval);
        });

        // Start incident detection
        this.startIncidentDetection();
    }

    // Stop protocol monitoring
    stopMonitoring() {
        this.isMonitoring = false;

        if (this.monitoringIntervals) {
            this.monitoringIntervals.forEach((interval, protocolName) => {
                clearInterval(interval);
            });
            this.monitoringIntervals.clear();
        }

        // Stop incident detection
        this.stopIncidentDetection();

        console.log('í»‘ Protocol health monitoring stopped');
    }

    // Check health of specific protocol
    async checkProtocolHealth(protocolName) {
        const protocol = this.protocolStatus.get(protocolName);
        if (!protocol) {
            throw new Error(`Protocol ${protocolName} not found`);
        }

        const startTime = Date.now();

        try {
            // Perform comprehensive health check
            const healthCheck = await this.performHealthCheck(protocol);

            // Update protocol status
            protocol.health = healthCheck.overallHealth;
            protocol.lastChecked = Date.now();
            protocol.lastMetrics = healthCheck.metrics;

            // Update health metrics
            this.updateHealthMetrics(protocolName, healthCheck, Date.now() - startTime);

            this.emit('protocol_health_updated', {
                protocol: protocolName,
                health: protocol.health,
                metrics: healthCheck.metrics,
                timestamp: Date.now()
            });

            return healthCheck;

        } catch (error) {
            // Record health check failure
            this.recordProtocolIncident(protocolName, 'health_check_failed', error.message);
            throw error;
        }
    }

    // Perform comprehensive health check for a protocol
    async performHealthCheck(protocol) {
        // Simulate protocol health check
        // In production, would check actual protocol metrics via APIs and blockchain

        const healthIndicators = {
            'Aave': { tvl: 5000000000, borrowAPY: 0.025, utilization: 0.65, incidents: 0 },
            'UniswapV3': { tvl: 3000000000, volume24h: 1000000000, fees24h: 5000000, incidents: 0 },
            'Compound': { tvl: 2000000000, reserveFactor: 0.1, collateralFactor: 0.75, incidents: 0 },
            'Curve': { tvl: 4000000000, volume24h: 500000000, poolBalance: 0.98, incidents: 0 },
            'Lido': { tvl: 15000000000, stakedETH: 8000000, apr: 0.042, incidents: 0 },
            'MakerDAO': { tvl: 7000000000, debtCeiling: 1000000000, collateralization: 1.5, incidents: 0 }
        };

        const indicators = healthIndicators[protocol.name] || { 
            tvl: 1000000000, incidents: 0 
        };

        // Add some random variation and occasional incidents
        const incidentChance = 0.05; // 5% chance of incident
        if (Math.random() < incidentChance) {
            indicators.incidents = 1;
        }

        // Calculate overall health score
        const healthScore = this.calculateHealthScore(protocol, indicators);

        return {
            overallHealth: healthScore,
            metrics: indicators,
            timestamp: Date.now(),
            details: this.generateHealthDetails(protocol, indicators)
        };
    }

    // Calculate comprehensive health score
    calculateHealthScore(protocol, metrics) {
        let score = 100;

        // TVL health (30% weight)
        const tvlScore = Math.min(metrics.tvl / 1000000000, 1) * 30; // Normalize to $1B
        score = score * 0.7 + tvlScore;

        // Incident penalty
        if (metrics.incidents > 0) {
            score -= 20 * metrics.incidents;
        }

        // Protocol-specific metrics
        if (protocol.type === 'lending') {
            // Lending protocol specific checks
            if (metrics.utilization !== undefined && metrics.utilization > 0.8) {
                score -= 10; // High utilization penalty
            }
            if (metrics.borrowAPY !== undefined && metrics.borrowAPY > 0.5) {
                score -= 5; // Very high borrow APY
            }
        } else if (protocol.type === 'dex') {
            // DEX specific checks
            if (metrics.volume24h !== undefined && metrics.volume24h < 10000000) {
                score -= 5; // Low volume
            }
        } else if (protocol.type === 'staking') {
            // Staking specific checks
            if (metrics.apr !== undefined && metrics.apr < 0.01) {
                score -= 10; // Very low APR
            }
        }

        return Math.max(0, Math.min(100, score)) / 100; // Normalize to 0-1
    }

    // Generate detailed health analysis
    generateHealthDetails(protocol, metrics) {
        const details = {
            status: 'healthy',
            warnings: [],
            recommendations: []
        };

        if (metrics.incidents > 0) {
            details.status = 'degraded';
            details.warnings.push('Recent incidents detected');
        }

        if (protocol.type === 'lending') {
            if (metrics.utilization > 0.8) {
                details.status = 'warning';
                details.warnings.push('High utilization rate may indicate liquidity issues');
            }
            if (metrics.borrowAPY > 0.2) {
                details.warnings.push('High borrow APY may indicate increased risk');
            }
        }

        if (details.status === 'healthy') {
            details.recommendations.push('Protocol operating normally');
        } else {
            details.recommendations.push('Consider monitoring protocol closely');
            details.recommendations.push('Review recent protocol activity and announcements');
        }

        return details;
    }

    // Update health metrics for a protocol
    updateHealthMetrics(protocolName, healthCheck, responseTime) {
        const metrics = this.healthMetrics.get(protocolName);
        if (!metrics) return;

        // Update response time (moving average)
        metrics.responseTime = (metrics.responseTime * 0.9) + (responseTime * 0.1);

        // Update error rate
        const isError = healthCheck.overallHealth < 0.7;
        if (isError) {
            metrics.errorRate = (metrics.errorRate * 0.95) + 0.05;
        } else {
            metrics.errorRate = metrics.errorRate * 0.99;
        }

        // Update uptime
        if (!isError) {
            metrics.uptime = (metrics.uptime * 0.99) + 0.01;
        } else {
            metrics.uptime = metrics.uptime * 0.95;
        }

        // Update performance score
        metrics.performanceScore = healthCheck.overallHealth * 100;

        // Update last incident
        if (isError) {
            metrics.lastIncident = Date.now();
        }
    }

    // Record protocol incident
    recordProtocolIncident(protocolName, incidentType, description) {
        const incident = {
            protocol: protocolName,
            type: incidentType,
            description: description,
            timestamp: Date.now(),
            severity: this.determineIncidentSeverity(incidentType),
            resolved: false
        };

        this.incidentHistory.push(incident);

        // Keep only recent incidents
        if (this.incidentHistory.length > 500) {
            this.incidentHistory = this.incidentHistory.slice(-500);
        }

        this.emit('protocol_incident_detected', incident);
    }

    // Determine incident severity
    determineIncidentSeverity(incidentType) {
        const severityMap = {
            'health_check_failed': 'medium',
            'monitoring_error': 'low',
            'high_utilization': 'medium',
            'low_liquidity': 'high',
            'security_incident': 'critical'
        };

        return severityMap[incidentType] || 'low';
    }

    // Start incident detection and alerting
    startIncidentDetection() {
        console.log('íº¨ Starting protocol incident detection...');

        this.incidentDetectionInterval = setInterval(() => {
            this.detectIncidentPatterns();
        }, 60000); // Check every minute
    }

    // Stop incident detection
    stopIncidentDetection() {
        if (this.incidentDetectionInterval) {
            clearInterval(this.incidentDetectionInterval);
            this.incidentDetectionInterval = null;
        }
    }

    // Detect incident patterns and trigger alerts
    detectIncidentPatterns() {
        const now = Date.now();
        const oneHourAgo = now - 60 * 60 * 1000;

        // Check for recent incidents
        const recentIncidents = this.incidentHistory.filter(
            incident => incident.timestamp > oneHourAgo && !incident.resolved
        );

        // Group incidents by protocol and type
        const incidentsByProtocol = {};
        recentIncidents.forEach(incident => {
            if (!incidentsByProtocol[incident.protocol]) {
                incidentsByProtocol[incident.protocol] = [];
            }
            incidentsByProtocol[incident.protocol].push(incident);
        });

        // Check for critical patterns
        for (const [protocolName, incidents] of Object.entries(incidentsByProtocol)) {
            const criticalIncidents = incidents.filter(i => i.severity === 'critical');
            const highIncidents = incidents.filter(i => i.severity === 'high');

            if (criticalIncidents.length > 0) {
                // Critical incident - immediate alert
                this.emit('critical_protocol_incident', {
                    protocol: protocolName,
                    incidentCount: criticalIncidents.length,
                    incidents: criticalIncidents,
                    timestamp: now,
                    recommendation: 'Immediate attention required'
                });

                // Mark incidents as resolved for alerting
                criticalIncidents.forEach(incident => incident.resolved = true);
            }

            if (highIncidents.length >= 2) {
                // Multiple high-severity incidents
                this.emit('protocol_incident_warning', {
                    protocol: protocolName,
                    incidentCount: highIncidents.length,
                    incidents: highIncidents,
                    timestamp: now,
                    recommendation: 'Close monitoring recommended'
                });
            }

            // Check for health degradation
            const protocol = this.protocolStatus.get(protocolName);
            if (protocol && protocol.health < 0.5) {
                this.emit('protocol_health_degraded', {
                    protocol: protocolName,
                    health: protocol.health,
                    incidentCount: incidents.length,
                    timestamp: now,
                    recommendation: 'Consider alternative protocols'
                });
            }
        }
    }

    // Get protocol recommendations based on health
    getProtocolRecommendations(operationType, amount, riskTolerance = 'medium') {
        const suitableProtocols = [];

        this.protocolStatus.forEach((protocol, protocolName) => {
            const metrics = this.healthMetrics.get(protocolName);
            
            if (this.isProtocolSuitable(protocol, operationType, amount, riskTolerance)) {
                suitableProtocols.push({
                    protocol: protocolName,
                    type: protocol.type,
                    health: protocol.health,
                    performanceScore: metrics.performanceScore,
                    recommendationScore: this.calculateRecommendationScore(protocol, metrics, operationType, amount)
                });
            }
        });

        if (suitableProtocols.length === 0) {
            throw new Error(`No suitable protocols found for ${operationType} operation`);
        }

        // Sort by recommendation score
        suitableProtocols.sort((a, b) => b.recommendationScore - a.recommendationScore);
        
        return {
            operation: operationType,
            amount: amount,
            riskTolerance: riskTolerance,
            recommendations: suitableProtocols,
            topRecommendation: suitableProtocols[0]
        };
    }

    // Check if protocol is suitable for operation
    isProtocolSuitable(protocol, operationType, amount, riskTolerance) {
        // Basic type matching
        if (operationType === 'flash_loan' && protocol.type !== 'lending') {
            return false;
        }
        if (operationType === 'swap' && protocol.type !== 'dex') {
            return false;
        }

        // Health threshold based on risk tolerance
        const healthThresholds = {
            'low': 0.8,
            'medium': 0.6,
            'high': 0.4
        };

        if (protocol.health < healthThresholds[riskTolerance]) {
            return false;
        }

        // Amount considerations (simplified)
        if (amount > 1000000 && protocol.health < 0.7) {
            return false; // Large amounts require higher health
        }

        return true;
    }

    // Calculate recommendation score
    calculateRecommendationScore(protocol, metrics, operationType, amount) {
        let score = 0;

        // Health score (40% weight)
        score += protocol.health * 40;

        // Performance score (30% weight)
        score += (metrics.performanceScore / 100) * 30;

        // Uptime score (20% weight)
        score += metrics.uptime * 20;

        // Response time score (10% weight)
        const responseScore = Math.max(0, 1 - (metrics.responseTime / 10000)); // Normalize to 10 seconds
        score += responseScore * 10;

        // Operation-specific adjustments
        if (operationType === 'flash_loan' && protocol.type === 'lending') {
            // Prefer protocols with higher TVL for flash loans
            const tvlScore = Math.min((protocol.lastMetrics?.tvl || 0) / 1000000000, 1);
            score += tvlScore * 10;
        }

        return score;
    }

    // Get overall system health summary
    getSystemHealthSummary() {
        const summary = {
            totalProtocols: this.protocolStatus.size,
            healthyProtocols: 0,
            warningProtocols: 0,
            criticalProtocols: 0,
            overallHealth: 0,
            protocols: []
        };

        let totalHealth = 0;

        this.protocolStatus.forEach((protocol, protocolName) => {
            const metrics = this.healthMetrics.get(protocolName);

            let status = 'healthy';
            if (protocol.health < 0.3) status = 'critical';
            else if (protocol.health < 0.7) status = 'warning';

            if (status === 'healthy') summary.healthyProtocols++;
            else if (status === 'warning') summary.warningProtocols++;
            else summary.criticalProtocols++;

            totalHealth += protocol.health;

            summary.protocols.push({
                name: protocolName,
                type: protocol.type,
                status: status,
                health: protocol.health,
                performanceScore: metrics.performanceScore,
                uptime: metrics.uptime,
                lastChecked: protocol.lastChecked
            });
        });

        summary.overallHealth = totalHealth / summary.totalProtocols;

        return summary;
    }

    // Get incident analytics
    getIncidentAnalytics(timeframeHours = 24) {
        const timeframeMs = timeframeHours * 60 * 60 * 1000;
        const cutoffTime = Date.now() - timeframeMs;

        const recentIncidents = this.incidentHistory.filter(
            incident => incident.timestamp > cutoffTime
        );

        const incidentsByProtocol = {};
        const incidentsBySeverity = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        };

        recentIncidents.forEach(incident => {
            if (!incidentsByProtocol[incident.protocol]) {
                incidentsByProtocol[incident.protocol] = 0;
            }
            incidentsByProtocol[incident.protocol]++;

            incidentsBySeverity[incident.severity]++;
        });

        return {
            timeframeHours: timeframeHours,
            totalIncidents: recentIncidents.length,
            incidentsByProtocol: incidentsByProtocol,
            incidentsBySeverity: incidentsBySeverity,
            mttr: this.calculateMTTR(recentIncidents), // Mean Time To Resolution
            incidentTrend: this.calculateIncidentTrend(recentIncidents, timeframeMs)
        };
    }

    // Calculate Mean Time To Resolution
    calculateMTTR(incidents) {
        const resolvedIncidents = incidents.filter(i => i.resolved);
        if (resolvedIncidents.length === 0) return 0;

        const totalResolutionTime = resolvedIncidents.reduce((sum, incident) => {
            // For simulation, assume incidents are resolved after 30 minutes
            return sum + (30 * 60 * 1000); // 30 minutes in milliseconds
        }, 0);

        return totalResolutionTime / resolvedIncidents.length;
    }

    // Calculate incident trend
    calculateIncidentTrend(incidents, timeframeMs) {
        if (incidents.length < 2) return 'stable';

        const halfTime = Date.now() - (timeframeMs / 2);
        const earlyIncidents = incidents.filter(i => i.timestamp < halfTime).length;
        const lateIncidents = incidents.filter(i => i.timestamp >= halfTime).length;

        if (lateIncidents > earlyIncidents * 1.5) return 'increasing';
        if (lateIncidents < earlyIncidents * 0.5) return 'decreasing';
        return 'stable';
    }
}

module.exports = ProtocolHealthMonitor;
