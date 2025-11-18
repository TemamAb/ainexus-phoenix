/**
 * AI-NEXUS Price Manipulation Detector
 * Real-time detection of oracle manipulation attacks
 */

const { EventEmitter } = require('events');

class PriceManipulationDetector extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            deviationThreshold: config.deviationThreshold || 0.05, // 5%
            volumeThreshold: config.volumeThreshold || 0.1, // 10%
            timeWindow: config.timeWindow || 300000, // 5 minutes
            ...config
        };
        
        this.priceHistory = new Map();
        this.volumeHistory = new Map();
        this.attackPatterns = this.initializeAttackPatterns();
    }

    /**
     * Initialize known manipulation attack patterns
     */
    initializeAttackPatterns() {
        return {
            flashLoanAttack: {
                description: 'Flash loan based price manipulation',
                indicators: ['extreme_price_deviation', 'abnormal_volume', 'quick_reversion'],
                threshold: 0.8
            },
            oracleDDoS: {
                description: 'DDoS attack on oracle infrastructure',
                indicators: ['missing_data_sources', 'increased_latency', 'stale_prices'],
                threshold: 0.7
            },
            sybilAttack: {
                description: 'Sybil attack creating fake price sources',
                indicators: ['new_unverified_sources', 'coordinated_price_movement', 'low_reliability_sources'],
                threshold: 0.6
            },
            latencyArbitrage: {
                description: 'Exploiting price update latency',
                indicators: ['consistent_latency_pattern', 'predictable_updates', 'front_running_signals'],
                threshold: 0.5
            }
        };
    }

    /**
     * Analyze price data for manipulation attempts
     */
    analyzePriceData(symbol, currentPrice, sources, volume = null) {
        const analysis = {
            symbol,
            timestamp: Date.now(),
            currentPrice,
            riskScore: 0,
            detectedAttacks: [],
            warnings: [],
            recommendations: []
        };

        // Update history
        this.updatePriceHistory(symbol, currentPrice, sources);
        if (volume !== null) {
            this.updateVolumeHistory(symbol, volume);
        }

        // Run detection algorithms
        const deviations = this.analyzePriceDeviations(symbol, sources);
        const volumeAnomalies = volume !== null ? this.analyzeVolumeAnomalies(symbol, volume) : [];
        const sourceReliability = this.analyzeSourceReliability(sources);
        const temporalPatterns = this.analyzeTemporalPatterns(symbol);

        // Calculate overall risk score
        analysis.riskScore = this.calculateRiskScore(
            deviations,
            volumeAnomalies,
            sourceReliability,
            temporalPatterns
        );

        // Detect specific attack patterns
        analysis.detectedAttacks = this.detectAttackPatterns(
            deviations,
            volumeAnomalies,
            sourceReliability,
            temporalPatterns
        );

        // Generate warnings and recommendations
        analysis.warnings = this.generateWarnings(analysis);
        analysis.recommendations = this.generateRecommendations(analysis);

        // Emit event if high risk detected
        if (analysis.riskScore > 0.7) {
            this.emit('highRiskDetected', analysis);
        }

        return analysis;
    }

    /**
     * Analyze price deviations across sources
     */
    analyzePriceDeviations(symbol, sources) {
        if (sources.length < 2) {
            return { score: 0.8, message: 'Insufficient price sources' };
        }

        const prices = sources.map(s => s.price);
        const medianPrice = this.calculateMedian(prices);
        const deviations = prices.map(p => Math.abs(p - medianPrice) / medianPrice);

        const maxDeviation = Math.max(...deviations);
        const avgDeviation = deviations.reduce((a, b) => a + b, 0) / deviations.length;

        let score = 0;
        if (maxDeviation > this.config.deviationThreshold) {
            score = Math.min(1, maxDeviation / this.config.deviationThreshold);
        }

        return {
            score,
            maxDeviation,
            avgDeviation,
            message: score > 0.5 ? 'Significant price deviations detected' : 'Normal price variations'
        };
    }

    /**
     * Analyze trading volume for anomalies
     */
    analyzeVolumeAnomalies(symbol, currentVolume) {
        const history = this.volumeHistory.get(symbol) || [];
        if (history.length < 5) {
            return { score: 0, message: 'Insufficient volume history' };
        }

        const avgVolume = history.reduce((a, b) => a + b, 0) / history.length;
        const volumeRatio = currentVolume / avgVolume;

        let score = 0;
        if (volumeRatio > 1 + this.config.volumeThreshold) {
            score = Math.min(1, (volumeRatio - 1) / this.config.volumeThreshold);
        }

        return {
            score,
            volumeRatio,
            currentVolume,
            avgVolume,
            message: score > 0.5 ? 'Abnormal trading volume detected' : 'Normal volume levels'
        };
    }

    /**
     * Analyze reliability of price sources
     */
    analyzeSourceReliability(sources) {
        const unreliableSources = sources.filter(s => s.reliability < 0.5);
        const newSources = sources.filter(s => s.age && s.age < 3600000); // Less than 1 hour
        
        let score = 0;
        if (unreliableSources.length > sources.length * 0.3) {
            score += 0.5;
        }
        if (newSources.length > sources.length * 0.2) {
            score += 0.3;
        }

        return {
            score: Math.min(score, 1),
            unreliableCount: unreliableSources.length,
            newSourcesCount: newSources.length,
            message: score > 0.5 ? 'Questionable price sources detected' : 'Reliable price sources'
        };
    }

    /**
     * Analyze temporal patterns for manipulation
     */
    analyzeTemporalPatterns(symbol) {
        const prices = this.priceHistory.get(symbol) || [];
        if (prices.length < 10) {
            return { score: 0, message: 'Insufficient price history' };
        }

        // Check for quick reversion patterns (flash loan indicator)
        const reversions = this.detectQuickReversions(prices);
        // Check for predictable update patterns
        const predictability = this.analyzePredictability(prices);

        const score = (reversions.score * 0.6 + predictability.score * 0.4);

        return {
            score,
            quickReversions: reversions.count,
            predictability: predictability.score,
            message: score > 0.5 ? 'Suspicious temporal patterns detected' : 'Normal price movements'
        };
    }

    /**
     * Detect quick price reversions (flash loan indicator)
     */
    detectQuickReversions(prices) {
        let reversionCount = 0;
        const reversionThreshold = 0.03; // 3%
        const window = 5; // 5 data points

        for (let i = window; i < prices.length - window; i++) {
            const previousAvg = prices.slice(i - window, i).reduce((a, b) => a + b, 0) / window;
            const current = prices[i];
            const futureAvg = prices.slice(i + 1, i + window + 1).reduce((a, b) => a + b, 0) / window;

            const deviation = Math.abs(current - previousAvg) / previousAvg;
            const reversion = Math.abs(futureAvg - previousAvg) / previousAvg;

            if (deviation > reversionThreshold && reversion < deviation * 0.5) {
                reversionCount++;
            }
        }

        const score = Math.min(1, reversionCount / (prices.length / window));
        return { count: reversionCount, score };
    }

    /**
     * Analyze price predictability
     */
    analyzePredictability(prices) {
        if (prices.length < 20) return { score: 0 };

        const returns = [];
        for (let i = 1; i < prices.length; i++) {
            returns.push(prices[i] / prices[i - 1] - 1);
        }

        // Calculate autocorrelation (simplified)
        let autocorrelation = 0;
        const lag = 1;
        for (let i = lag; i < returns.length; i++) {
            autocorrelation += returns[i] * returns[i - lag];
        }
        autocorrelation /= returns.length - lag;

        // High autocorrelation suggests predictability/manipulation
        const score = Math.min(1, Math.abs(autocorrelation) * 10);
        return { score };
    }

    /**
     * Calculate overall risk score
     */
    calculateRiskScore(deviations, volumeAnomalies, sourceReliability, temporalPatterns) {
        const weights = {
            deviations: 0.3,
            volumeAnomalies: 0.25,
            sourceReliability: 0.2,
            temporalPatterns: 0.25
        };

        return (
            deviations.score * weights.deviations +
            volumeAnomalies.score * weights.volumeAnomalies +
            sourceReliability.score * weights.sourceReliability +
            temporalPatterns.score * weights.temporalPatterns
        );
    }

    /**
     * Detect specific attack patterns
     */
    detectAttackPatterns(deviations, volumeAnomalies, sourceReliability, temporalPatterns) {
        const attacks = [];

        // Flash loan attack pattern
        if (deviations.score > 0.7 && volumeAnomalies.score > 0.6 && temporalPatterns.quickReversions > 2) {
            attacks.push({
                type: 'flashLoanAttack',
                confidence: Math.min(1, (deviations.score + volumeAnomalies.score + temporalPatterns.score) / 3),
                indicators: ['extreme_price_deviation', 'abnormal_volume', 'quick_reversion']
            });
        }

        // Oracle DDoS pattern
        if (sourceReliability.score > 0.6 && deviations.score > 0.5) {
            attacks.push({
                type: 'oracleDDoS',
                confidence: Math.min(1, (sourceReliability.score + deviations.score) / 2),
                indicators: ['missing_data_sources', 'increased_latency']
            });
        }

        return attacks;
    }

    /**
     * Generate warnings based on analysis
     */
    generateWarnings(analysis) {
        const warnings = [];

        if (analysis.riskScore > 0.8) {
            warnings.push('CRITICAL: High manipulation risk detected');
        } else if (analysis.riskScore > 0.6) {
            warnings.push('WARNING: Elevated manipulation risk');
        }

        if (analysis.detectedAttacks.length > 0) {
            warnings.push(`Detected potential attacks: ${analysis.detectedAttacks.map(a => a.type).join(', ')}`);
        }

        return warnings;
    }

    /**
     * Generate recommendations based on analysis
     */
    generateRecommendations(analysis) {
        const recommendations = [];

        if (analysis.riskScore > 0.7) {
            recommendations.push('Consider pausing arbitrage operations');
            recommendations.push('Switch to fallback oracle mechanism');
            recommendations.push('Increase price validation thresholds');
        }

        if (analysis.detectedAttacks.some(a => a.type === 'flashLoanAttack')) {
            recommendations.push('Implement flash loan attack protection');
            recommendations.push('Reduce position sizes temporarily');
        }

        return recommendations;
    }

    /**
     * Update price history
     */
    updatePriceHistory(symbol, price, sources) {
        if (!this.priceHistory.has(symbol)) {
            this.priceHistory.set(symbol, []);
        }

        const history = this.priceHistory.get(symbol);
        history.push(price);

        // Keep only recent history
        const maxHistory = 1000;
        if (history.length > maxHistory) {
            history.splice(0, history.length - maxHistory);
        }
    }

    /**
     * Update volume history
     */
    updateVolumeHistory(symbol, volume) {
        if (!this.volumeHistory.has(symbol)) {
            this.volumeHistory.set(symbol, []);
        }

        const history = this.volumeHistory.get(symbol);
        history.push(volume);

        // Keep only recent history
        const maxHistory = 1000;
        if (history.length > maxHistory) {
            history.splice(0, history.length - maxHistory);
        }
    }

    /**
     * Calculate median of array
     */
    calculateMedian(arr) {
        const sorted = [...arr].sort((a, b) => a - b);
        const mid = Math.floor(sorted.length / 2);
        return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    }
}

module.exports = PriceManipulationDetector;
