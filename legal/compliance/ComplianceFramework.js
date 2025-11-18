/**
 * AI-NEXUS Global Compliance Framework
 * Multi-jurisdiction regulatory compliance automation
 */

const { EventEmitter } = require('events');

class ComplianceFramework extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            enabledJurisdictions: config.enabledJurisdictions || ['US', 'EU', 'UK', 'SG'],
            reportingRequirements: config.reportingRequirements || {},
            taxTreaties: config.taxTreaties || {},
            ...config
        };
        
        this.regulatoryRules = this.initializeRegulatoryRules();
        this.complianceChecks = new Map();
        this.violationHistory = [];
    }

    /**
     * Initialize regulatory rules for different jurisdictions
     */
    initializeRegulatoryRules() {
        return {
            // US Regulations
            US: {
                sec: {
                    patternDayTrader: {
                        description: 'Pattern Day Trader Rule',
                        condition: (activity) => activity.dayTrades > 3 && activity.accountValue < 25000,
                        action: 'restrict_trading',
                        gracePeriod: 5
                    },
                    shortSelling: {
                        description: 'Short Sale Rule',
                        condition: (trade) => trade.side === 'sell' && !trade.hasPosition,
                        action: 'require_borrow',
                        immediate: true
                    }
                },
                finra: {
                    suitability: {
                        description: 'Suitability Rule',
                        condition: (client, investment) => this.checkSuitability(client, investment),
                        action: 'require_approval'
                    }
                }
            },

            // EU Regulations
            EU: {
                mifid: {
                    bestExecution: {
                        description: 'MiFID II Best Execution',
                        condition: (order) => this.checkBestExecution(order),
                        action: 'require_justification',
                        timeframe: 'pre_trade'
                    },
                    transactionReporting: {
                        description: 'Transaction Reporting',
                        condition: (trade) => true, // All trades must be reported
                        action: 'report_transaction',
                        timeframe: 'post_trade'
                    }
                },
                gdpr: {
                    dataProtection: {
                        description: 'GDPR Data Protection',
                        condition: (data) => this.checkDataProtection(data),
                        action: 'anonymize_data',
                        immediate: true
                    }
                }
            },

            // UK Regulations
            UK: {
                fca: {
                    conductRules: {
                        description: 'FCA Conduct Rules',
                        condition: (activity) => this.checkMarketConduct(activity),
                        action: 'review_activity'
                    }
                }
            },

            // Singapore Regulations
            SG: {
                mas: {
                    licensing: {
                        description: 'MAS Licensing Requirements',
                        condition: (activity) => activity.volume > 1000000, // SGD 1M
                        action: 'require_license'
                    }
                }
            }
        };
    }

    /**
     * Check compliance for a specific activity
     */
    async checkCompliance(activity, jurisdiction = 'US') {
        const jurisdictionRules = this.regulatoryRules[jurisdiction];
        if (!jurisdictionRules) {
            throw new Error(`No regulatory rules found for jurisdiction: ${jurisdiction}`);
        }

        const violations = [];
        const requirements = [];

        // Check all rules in the jurisdiction
        for (const [regulator, rules] of Object.entries(jurisdictionRules)) {
            for (const [ruleName, rule] of Object.entries(rules)) {
                try {
                    const isViolated = await this.evaluateRule(rule, activity);
                    
                    if (isViolated) {
                        violations.push({
                            jurisdiction,
                            regulator,
                            rule: ruleName,
                            description: rule.description,
                            activity,
                            timestamp: new Date(),
                            requiredAction: rule.action
                        });

                        // Emit violation event
                        this.emit('compliance_violation', {
                            jurisdiction,
                            regulator,
                            rule: ruleName,
                            activity,
                            requiredAction: rule.action
                        });
                    }

                    // Track requirement regardless of violation
                    requirements.push({
                        jurisdiction,
                        regulator,
                        rule: ruleName,
                        description: rule.description,
                        condition: rule.condition.toString(),
                        action: rule.action
                    });

                } catch (error) {
                    console.error(`Error evaluating rule ${ruleName}:`, error);
                }
            }
        }

        // Store compliance check results
        this.complianceChecks.set(activity.id, {
            activity,
            jurisdiction,
            timestamp: new Date(),
            violations,
            requirements
        });

        return {
            compliant: violations.length === 0,
            violations,
            requirements
        };
    }

    /**
     * Evaluate a single compliance rule
     */
    async evaluateRule(rule, activity) {
        try {
            // Execute rule condition
            const conditionResult = await rule.condition(activity);
            
            // Check if rule has grace period
            if (rule.gracePeriod && conditionResult) {
                const graceKey = `${rule.description}-${activity.id}`;
                const graceStart = this.complianceChecks.get(graceKey);
                
                if (!graceStart) {
                    // First violation - start grace period
                    this.complianceChecks.set(graceKey, new Date());
                    return false; // No violation during grace period
                } else {
                    const graceEnd = new Date(graceStart);
                    graceEnd.setDate(graceEnd.getDate() + rule.gracePeriod);
                    
                    if (new Date() > graceEnd) {
                        // Grace period expired - violation
                        this.complianceChecks.delete(graceKey);
                        return true;
                    } else {
                        // Still in grace period
                        return false;
                    }
                }
            }

            return conditionResult;

        } catch (error) {
            console.error('Error evaluating rule condition:', error);
            return false; // Default to non-violation on error
        }
    }

    /**
     * Check investment suitability (FINRA Rule 2111)
     */
    checkSuitability(client, investment) {
        const { riskTolerance, investmentObjectives, financialStatus } = client;
        const { riskLevel, complexity } = investment;

        // Basic suitability checks
        if (riskLevel > riskTolerance) {
            return true; // Violation - investment too risky
        }

        if (complexity === 'high' && financialStatus.experience < 5) {
            return true; // Violation - complex product for inexperienced investor
        }

        // Check if investment aligns with objectives
        const objectiveMatch = investmentObjectives.some(obj => 
            investment.objectives.includes(obj)
        );

        if (!objectiveMatch) {
            return true; // Violation - doesn't match investment objectives
        }

        return false; // Suitable
    }

    /**
     * Check best execution (MiFID II)
     */
    checkBestExecution(order) {
        const { venues, prices, executionQuality } = order;

        // Check if order was routed to venue providing best execution
        const bestPrice = Math.max(...prices.map(p => p.price));
        const executedPrice = order.executionPrice;

        // Allow small deviation for speed/execution quality
        const priceTolerance = 0.001; // 0.1%
        const priceDifference = Math.abs(executedPrice - bestPrice) / bestPrice;

        if (priceDifference > priceTolerance && executionQuality < 0.8) {
            return true; // Violation - poor execution quality
        }

        return false; // Compliant
    }

    /**
     * Check data protection compliance (GDPR)
     */
    checkDataProtection(data) {
        const { personalData, consent, purpose, retentionPeriod } = data;

        // Check if personal data is being processed without consent
        if (personalData && !consent) {
            return true; // Violation - no consent for personal data
        }

        // Check if data retention exceeds permitted period
        const maxRetention = 365 * 3; // 3 years maximum
        if (retentionPeriod > maxRetention) {
            return true; // Violation - excessive data retention
        }

        // Check if purpose is specified and limited
        if (!purpose || purpose === 'undefined') {
            return true; // Violation - no specified purpose
        }

        return false; // Compliant
    }

    /**
     * Check market conduct (FCA)
     */
    checkMarketConduct(activity) {
        const { trades, volume, frequency } = activity;

        // Check for potential market manipulation
        if (frequency > 1000 && volume > 1000000) { // High frequency, large volume
            // Look for patterns that might indicate manipulation
            const suspiciousPatterns = this.detectSuspiciousPatterns(trades);
            return suspiciousPatterns.length > 0;
        }

        return false; // Compliant
    }

    /**
     * Detect suspicious trading patterns
     */
    detectSuspiciousPatterns(trades) {
        const patterns = [];

        // Check for wash trading (buy and sell same asset rapidly)
        const washTrades = this.detectWashTrades(trades);
        if (washTrades.length > 0) {
            patterns.push({ type: 'wash_trading', trades: washTrades });
        }

        // Check for spoofing (large orders that are cancelled)
        const spoofingOrders = this.detectSpoofing(trades);
        if (spoofingOrders.length > 0) {
            patterns.push({ type: 'spoofing', orders: spoofingOrders });
        }

        // Check for layering
        const layeringPatterns = this.detectLayering(trades);
        if (layeringPatterns.length > 0) {
            patterns.push({ type: 'layering', patterns: layeringPatterns });
        }

        return patterns;
    }

    /**
     * Generate compliance reports
     */
    async generateComplianceReport(timeframe = 'monthly') {
        const report = {
            timeframe,
            generationDate: new Date(),
            jurisdictions: this.config.enabledJurisdictions,
            summary: {},
            detailedFindings: [],
            recommendations: []
        };

        // Aggregate compliance data for the timeframe
        for (const jurisdiction of this.config.enabledJurisdictions) {
            const jurisdictionData = await this.aggregateJurisdictionData(jurisdiction, timeframe);
            report.summary[jurisdiction] = jurisdictionData;
        }

        // Add detailed findings
        report.detailedFindings = await this.getDetailedFindings(timeframe);

        // Generate recommendations
        report.recommendations = await this.generateRecommendations(report);

        return report;
    }

    /**
     * Aggregate jurisdiction-specific compliance data
     */
    async aggregateJurisdictionData(jurisdiction, timeframe) {
        const startDate = this.getTimeframeStartDate(timeframe);
        const jurisdictionChecks = Array.from(this.complianceChecks.values())
            .filter(check => 
                check.jurisdiction === jurisdiction && 
                check.timestamp >= startDate
            );

        const totalChecks = jurisdictionChecks.length;
        const violations = jurisdictionChecks.flatMap(check => check.violations);
        const violationRate = totalChecks > 0 ? violations.length / totalChecks : 0;

        return {
            totalChecks,
            violations: violations.length,
            violationRate,
            topViolations: this.getTopViolations(violations),
            riskLevel: this.calculateRiskLevel(violationRate)
        };
    }

    /**
     * Get detailed compliance findings
     */
    async getDetailedFindings(timeframe) {
        const startDate = this.getTimeframeStartDate(timeframe);
        const recentChecks = Array.from(this.complianceChecks.values())
            .filter(check => check.timestamp >= startDate);

        return recentChecks.flatMap(check => 
            check.violations.map(violation => ({
                activity: check.activity,
                violation,
                checkTimestamp: check.timestamp
            }))
        );
    }

    /**
     * Generate compliance recommendations
     */
    async generateRecommendations(report) {
        const recommendations = [];

        // Analyze violation patterns
        for (const [jurisdiction, data] of Object.entries(report.summary)) {
            if (data.violationRate > 0.05) { // 5% violation rate threshold
                recommendations.push({
                    jurisdiction,
                    priority: 'high',
                    action: `Review and update compliance procedures for ${jurisdiction}`,
                    reason: `High violation rate: ${(data.violationRate * 100).toFixed(1)}%`
                });
            }

            // Specific rule recommendations
            data.topViolations.forEach(violation => {
                recommendations.push({
                    jurisdiction,
                    priority: 'medium',
                    action: `Provide additional training on ${violation.rule}`,
                    reason: `Frequent violations of ${violation.rule}`
                });
            });
        }

        return recommendations;
    }

    /**
     * Calculate compliance risk level
     */
    calculateRiskLevel(violationRate) {
        if (violationRate === 0) return 'low';
        if (violationRate < 0.02) return 'medium';
        if (violationRate < 0.05) return 'high';
        return 'critical';
    }

    /**
     * Get top violations by frequency
     */
    getTopViolations(violations, limit = 5) {
        const violationCounts = violations.reduce((acc, violation) => {
            const key = `${violation.regulator}.${violation.rule}`;
            acc[key] = (acc[key] || 0) + 1;
            return acc;
        }, {});

        return Object.entries(violationCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, limit)
            .map(([key, count]) => ({
                rule: key,
                count,
                description: violations.find(v => `${v.regulator}.${v.rule}` === key)?.description
            }));
    }

    /**
     * Get start date for timeframe
     */
    getTimeframeStartDate(timeframe) {
        const now = new Date();
        switch (timeframe) {
            case 'daily':
                return new Date(now.setDate(now.getDate() - 1));
            case 'weekly':
                return new Date(now.setDate(now.getDate() - 7));
            case 'monthly':
                return new Date(now.setMonth(now.getMonth() - 1));
            case 'quarterly':
                return new Date(now.setMonth(now.getMonth() - 3));
            default:
                return new Date(now.setDate(now.getDate() - 1));
        }
    }

    // Placeholder methods for pattern detection
    detectWashTrades(trades) {
        // Implementation would analyze trades for wash trading patterns
        return [];
    }

    detectSpoofing(trades) {
        // Implementation would analyze order book for spoofing patterns
        return [];
    }

    detectLayering(trades) {
        // Implementation would detect layering manipulation patterns
        return [];
    }
}

module.exports = ComplianceFramework;
