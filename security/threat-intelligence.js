/**
 * THREAT INTELLIGENCE SYSTEM
 * REF: CrowdStrike Falcon + FireEye Mandiant Threat Intelligence
 * Real-time threat detection and intelligence gathering
 */

const { EventEmitter } = require('events');
const { createHash, randomBytes } = require('crypto');

class ThreatIntelligenceSystem extends EventEmitter {
    constructor() {
        super();
        this.threatFeeds = new Map();
        this.iocDatabase = new Set(); // Indicators of Compromise
        this.behavioralBaselines = new Map();
        this.attackPatterns = new Map();
        this.incidentLog = new Map();
        
        // CrowdStrike Falcon-inspired configuration
        this.config = {
            intelligence: {
                feeds: [
                    'malware_indicators',
                    'phishing_campaigns',
                    'vulnerability_data',
                    'attack_patterns',
                    'blockchain_threats'
                ],
                updateInterval: 300000, // 5 minutes
                retentionPeriod: 2592000000 // 30 days
            },
            detection: {
                anomalyThreshold: 0.8,
                correlationWindow: 60000, // 1 minute
                maxFalsePositiveRate: 0.05
            },
            response: {
                autoBlock: true,
                alertChannels: ['slack', 'email', 'pagerduty'],
                escalationThreshold: 3
            }
        };

        // FireEye Mandiant-inspired threat categories
        this.threatCategories = {
            MALWARE: 'malware',
            PHISHING: 'phishing',
            EXPLOIT: 'exploit',
            RECON: 'reconnaissance',
            PERSISTENCE: 'persistence',
            EXFILTRATION: 'exfiltration',
            BLOCKCHAIN_SPECIFIC: 'blockchain_specific'
        };

        // Initialize threat intelligence feeds
        this._initializeThreatFeeds();
    }

    /**
     * CrowdStrike Falcon-inspired threat detection
     */
    async analyzeForThreats(activity, context) {
        const analysisId = this._generateAnalysisId();
        
        try {
            // Multi-layer threat analysis
            const threatAnalyses = await Promise.all([
                this._analyzeBehavioralPatterns(activity, context),
                this._checkIOCDatabase(activity, context),
                this._detectAnomalies(activity, context),
                this._correlateWithAttackPatterns(activity, context),
                this._analyzeBlockchainSpecificThreats(activity, context)
            ]);

            // Aggregate threat indicators
            const threatIndicators = threatAnalyses.flatMap(analysis => analysis.indicators);
            const threatScore = this._calculateThreatScore(threatIndicators);
            
            const threatAssessment = {
                analysisId,
                activity,
                context,
                threatScore,
                threatIndicators,
                severity: this._determineSeverity(threatScore),
                recommendations: this._generateThreatRecommendations(threatIndicators),
                timestamp: new Date().toISOString()
            };

            // Log for incident response
            await this._logThreatAssessment(threatAssessment);

            // Auto-response for high-severity threats
            if (threatAssessment.severity === 'HIGH' || threatAssessment.severity === 'CRITICAL') {
                await this._executeAutoResponse(threatAssessment);
            }

            this.emit('threatAssessed', threatAssessment);
            return threatAssessment;

        } catch (error) {
            this.emit('threatAnalysisFailed', {
                analysisId,
                error: error.message,
                timestamp: new Date().toISOString()
            });
            throw error;
        }
    }

    /**
     * FireEye Mandiant-inspired IOC matching
     */
    async _checkIOCDatabase(activity, context) {
        const indicators = [];
        
        // Check for known malicious addresses
        if (activity.to && this.iocDatabase.has(activity.to)) {
            indicators.push({
                type: 'MALICIOUS_ADDRESS',
                confidence: 0.95,
                details: `Destination address ${activity.to} is in IOC database`,
                ioc: activity.to
            });
        }

        // Check for known attack patterns in transaction data
        const patternMatch = await this._detectKnownAttackPatterns(activity.data);
        if (patternMatch.found) {
            indicators.push({
                type: 'KNOWN_ATTACK_PATTERN',
                confidence: patternMatch.confidence,
                details: patternMatch.description,
                pattern: patternMatch.patternId
            });
        }

        // Check for suspicious smart contract interactions
        const contractAnalysis = await this._analyzeContractInteraction(activity);
        if (contractAnalysis.suspicious) {
            indicators.push({
                type: 'SUSPICIOUS_CONTRACT',
                confidence: contractAnalysis.confidence,
                details: contractAnalysis.reason,
                contract: activity.to
            });
        }

        return {
            indicators,
            iocsChecked: indicators.length,
            matches: indicators.filter(i => i.confidence > 0.7).length
        };
    }

    /**
     * Behavioral anomaly detection (CrowdStrike patterns)
     */
    async _analyzeBehavioralPatterns(activity, context) {
        const indicators = [];
        const userBehavior = this.behavioralBaselines.get(context.userId) || 
                           this._createBehavioralBaseline(context);

        // Transaction amount anomalies
        const amountAnomaly = await this._detectAmountAnomaly(activity.amount, userBehavior);
        if (amountAnomaly.isAnomaly) {
            indicators.push({
                type: 'AMOUNT_ANOMALY',
                confidence: amountAnomaly.confidence,
                details: `Transaction amount ${activity.amount} is anomalous`,
                deviation: amountAnomaly.deviation
            });
        }

        // Transaction frequency anomalies
        const frequencyAnomaly = await this._detectFrequencyAnomaly(activity, userBehavior);
        if (frequencyAnomaly.isAnomaly) {
            indicators.push({
                type: 'FREQUENCY_ANOMALY',
                confidence: frequencyAnomaly.confidence,
                details: `Transaction frequency is anomalous`,
                currentRate: frequencyAnomaly.currentRate,
                baselineRate: frequencyAnomaly.baselineRate
            });
        }

        // Time-of-day anomalies
        const timeAnomaly = await this._detectTimeAnomaly(activity, userBehavior);
        if (timeAnomaly.isAnomaly) {
            indicators.push({
                type: 'TIME_ANOMALY',
                confidence: timeAnomaly.confidence,
                details: `Transaction time ${new Date(activity.timestamp).toISOString()} is anomalous`,
                usualHours: timeAnomaly.usualHours
            });
        }

        // Update behavioral baseline
        this._updateBehavioralBaseline(context.userId, activity);

        return {
            indicators,
            baselineUsed: userBehavior,
            anomaliesDetected: indicators.length
        };
    }

    /**
     * Blockchain-specific threat detection
     */
    async _analyzeBlockchainSpecificThreats(activity, context) {
        const indicators = [];
        
        // MEV attack detection
        const mevAnalysis = await this._detectMEVAttack(activity);
        if (mevAnalysis.suspicious) {
            indicators.push({
                type: 'POTENTIAL_MEV_ATTACK',
                confidence: mevAnalysis.confidence,
                details: mevAnalysis.description,
                attackType: mevAnalysis.attackType
            });
        }

        // Flash loan attack detection
        const flashLoanAnalysis = await this._detectFlashLoanAttack(activity);
        if (flashLoanAnalysis.suspicious) {
            indicators.push({
                type: 'POTENTIAL_FLASH_LOAN_ATTACK',
                confidence: flashLoanAnalysis.confidence,
                details: flashLoanAnalysis.description,
                patterns: flashLoanAnalysis.patterns
            });
        }

        // Smart contract exploit detection
        const exploitAnalysis = await this._detectContractExploit(activity);
        if (exploitAnalysis.suspicious) {
            indicators.push({
                type: 'POTENTIAL_CONTRACT_EXPLOIT',
                confidence: exploitAnalysis.confidence,
                details: exploitAnalysis.description,
                vulnerability: exploitAnalysis.vulnerability
            });
        }

        // Front-running detection
        const frontRunAnalysis = await this._detectFrontRunning(activity);
        if (frontRunAnalysis.suspicious) {
            indicators.push({
                type: 'POTENTIAL_FRONT_RUNNING',
                confidence: frontRunAnalysis.confidence,
                details: frontRunAnalysis.description,
                evidence: frontRunAnalysis.evidence
            });
        }

        return {
            indicators,
            blockchainSpecific: true,
            threatsDetected: indicators.length
        };
    }

    /**
     * Attack pattern correlation (FireEye Mandiant patterns)
     */
    async _correlateWithAttackPatterns(activity, context) {
        const indicators = [];
        
        for (const [patternId, pattern] of this.attackPatterns) {
            const correlation = await this._correlateActivityWithPattern(activity, pattern);
            
            if (correlation.score > pattern.threshold) {
                indicators.push({
                    type: 'ATTACK_PATTERN_CORRELATION',
                    confidence: correlation.score,
                    details: `Matches attack pattern: ${pattern.description}`,
                    patternId,
                    tactics: pattern.tactics,
                    techniques: pattern.techniques
                });
            }
        }

        return {
            indicators,
            patternsChecked: this.attackPatterns.size,
            correlations: indicators.length
        };
    }

    /**
     * Real-time threat intelligence feed processing
     */
    async _processThreatIntelligenceFeeds() {
        for (const [feedName, feedConfig] of this.threatFeeds) {
            try {
                const newIndicators = await this._fetchThreatFeed(feedConfig);
                
                // Process new indicators
                for (const indicator of newIndicators) {
                    await this._processThreatIndicator(indicator, feedName);
                }
                
                this.emit('threatFeedProcessed', {
                    feed: feedName,
                    indicators: newIndicators.length,
                    timestamp: new Date().toISOString()
                });
                
            } catch (error) {
                this.emit('threatFeedError', {
                    feed: feedName,
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        }
    }

    /**
     * MEV attack detection
     */
    async _detectMEVAttack(activity) {
        // Analyze transaction for MEV attack patterns
        const patterns = [
            this._analyzeForSandwichAttack(activity),
            this._analyzeForArbitrageManipulation(activity),
            this._analyzeForLiquidityAttack(activity)
        ];

        const results = await Promise.all(patterns);
        const suspiciousResult = results.find(r => r.suspicious);
        
        return suspiciousResult || {
            suspicious: false,
            confidence: 0.0,
            description: 'No MEV attack patterns detected'
        };
    }

    /**
     * Flash loan attack detection
     */
    async _detectFlashLoanAttack(activity) {
        // Check for flash loan attack patterns
        // Large borrows followed by market manipulation
        const flashLoanPatterns = [
            'large_instant_borrow',
            'price_manipulation',
            'rapid_liquidation'
        ];

        // Implementation would analyze transaction sequence
        const attackProbability = await this._calculateFlashLoanProbability(activity);
        
        return {
            suspicious: attackProbability > 0.7,
            confidence: attackProbability,
            description: attackProbability > 0.7 ? 
                'Potential flash loan attack detected' :
                'No flash loan attack patterns',
            patterns: flashLoanPatterns
        };
    }

    /**
     * Automated threat response
     */
    async _executeAutoResponse(threatAssessment) {
        const responseActions = [];
        
        // Block transaction if auto-block enabled
        if (this.config.response.autoBlock && threatAssessment.severity === 'CRITICAL') {
            await this._blockMaliciousActivity(threatAssessment.activity);
            responseActions.push('BLOCKED_TRANSACTION');
        }

        // Alert security team
        await this._alertSecurityTeam(threatAssessment);
        responseActions.push('ALERTED_SECURITY_TEAM');

        // Isolate affected systems if necessary
        if (threatAssessment.threatIndicators.some(i => i.type === 'MALICIOUS_ADDRESS')) {
            await this._quarantineAddress(threatAssessment.activity.to);
            responseActions.push('QUARANTINED_ADDRESS');
        }

        this.emit('threatResponseExecuted', {
            threatAssessment,
            responseActions,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Threat scoring and severity determination
     */
    _calculateThreatScore(threatIndicators) {
        if (threatIndicators.length === 0) return 0;
        
        const weightedSum = threatIndicators.reduce((sum, indicator) => {
            return sum + (indicator.confidence * this._getThreatWeight(indicator.type));
        }, 0);

        const totalWeight = threatIndicators.reduce((sum, indicator) => {
            return sum + this._getThreatWeight(indicator.type);
        }, 0);

        return weightedSum / totalWeight;
    }

    _determineSeverity(threatScore) {
        if (threatScore >= 0.9) return 'CRITICAL';
        if (threatScore >= 0.7) return 'HIGH';
        if (threatScore >= 0.5) return 'MEDIUM';
        if (threatScore >= 0.3) return 'LOW';
        return 'INFO';
    }

    _getThreatWeight(threatType) {
        const weights = {
            'MALICIOUS_ADDRESS': 1.0,
            'KNOWN_ATTACK_PATTERN': 0.9,
            'POTENTIAL_MEV_ATTACK': 0.8,
            'POTENTIAL_FLASH_LOAN_ATTACK': 0.9,
            'AMOUNT_ANOMALY': 0.6,
            'FREQUENCY_ANOMALY': 0.5,
            'TIME_ANOMALY': 0.4
        };

        return weights[threatType] || 0.5;
    }

    _generateThreatRecommendations(threatIndicators) {
        const recommendations = [];
        
        if (threatIndicators.some(i => i.type === 'MALICIOUS_ADDRESS')) {
            recommendations.push('Immediately block transaction to malicious address');
        }
        
        if (threatIndicators.some(i => i.type.includes('MEV_ATTACK'))) {
            recommendations.push('Use Flashbots protection for transaction execution');
        }
        
        if (threatIndicators.some(i => i.type.includes('ANOMALY'))) {
            recommendations.push('Require additional authentication for this transaction');
        }

        return recommendations;
    }

    _generateAnalysisId() {
        return `threat_${Date.now()}_${randomBytes(8).toString('hex')}`;
    }

    _initializeThreatFeeds() {
        // Initialize threat intelligence feeds
        this.threatFeeds.set('malware_indicators', {
            url: 'https://threat-intel.example.com/malware-iocs',
            format: 'json',
            updateInterval: 3600000 // 1 hour
        });

        this.threatFeeds.set('blockchain_threats', {
            url: 'https://blockchain-threats.example.com/feed',
            format: 'json',
            updateInterval: 300000 // 5 minutes
        });

        // Start feed processing
        setInterval(() => {
            this._processThreatIntelligenceFeeds();
        }, this.config.intelligence.updateInterval);
    }

    _createBehavioralBaseline(context) {
        return {
            typicalAmounts: [],
            transactionTimes: [],
            frequency: 0,
            devices: new Set(),
            locations: new Set()
        };
    }

    _updateBehavioralBaseline(userId, activity) {
        const baseline = this.behavioralBaselines.get(userId);
        if (baseline) {
            baseline.typicalAmounts.push(activity.amount);
            baseline.transactionTimes.push(activity.timestamp);
            // Keep only recent data (sliding window)
            if (baseline.typicalAmounts.length > 100) {
                baseline.typicalAmounts.shift();
                baseline.transactionTimes.shift();
            }
        }
    }
}

module.exports = ThreatIntelligenceSystem;
