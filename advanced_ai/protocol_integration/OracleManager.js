// File: advanced_ai/protocol_integration/OracleManager.js
// 7P-PILLAR: BOT3-7P
// PURPOSE: Multi-source oracle management and validation

const { EventEmitter } = require('events');

class OracleManager extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.oracleFeeds = new Map();
        this.priceHistory = new Map();
        this.validationResults = new Map();
        this.isMonitoring = false;
        
        this.initializeOracleFeeds();
    }

    // Initialize supported oracle feeds
    initializeOracleFeeds() {
        const supportedOracles = [
            {
                name: 'Chainlink',
                type: 'decentralized',
                assets: ['ETH/USD', 'BTC/USD', 'LINK/USD', 'USDC/USD', 'USDT/USD'],
                updateFrequency: 30000, // 30 seconds
                health: 1.0,
                lastUpdate: Date.now()
            },
            {
                name: 'UniswapV3',
                type: 'dex',
                assets: ['ETH/USDC', 'BTC/ETH', 'USDC/USDT', 'DAI/USDC'],
                updateFrequency: 15000, // 15 seconds
                health: 1.0,
                lastUpdate: Date.now()
            },
            {
                name: 'Binance',
                type: 'cex',
                assets: ['ETH/USDT', 'BTC/USDT', 'BNB/USDT', 'ADA/USDT'],
                updateFrequency: 10000, // 10 seconds
                health: 1.0,
                lastUpdate: Date.now()
            },
            {
                name: 'Coinbase',
                type: 'cex',
                assets: ['ETH/USD', 'BTC/USD', 'LTC/USD', 'BCH/USD'],
                updateFrequency: 10000,
                health: 1.0,
                lastUpdate: Date.now()
            },
            {
                name: 'Kyber',
                type: 'dex',
                assets: ['ETH/USDT', 'BTC/ETH', 'USDC/ETH', 'DAI/ETH'],
                updateFrequency: 20000,
                health: 1.0,
                lastUpdate: Date.now()
            }
        ];

        supportedOracles.forEach(oracle => {
            this.oracleFeeds.set(oracle.name, oracle);
            
            // Initialize price history for each asset
            oracle.assets.forEach(asset => {
                const priceKey = `${oracle.name}_${asset}`;
                if (!this.priceHistory.has(priceKey)) {
                    this.priceHistory.set(priceKey, []);
                }
            });
        });

        console.log(`âœ… Initialized ${this.oracleFeeds.size} oracle feed monitors`);
    }

    // Start continuous oracle monitoring
    startMonitoring() {
        if (this.isMonitoring) {
            console.log('âš ï¸ Oracle monitoring already active');
            return;
        }

        this.isMonitoring = true;
        console.log('í´® Starting continuous oracle monitoring...');

        // Monitor each oracle feed
        this.oracleFeeds.forEach((oracle, oracleName) => {
            const interval = setInterval(async () => {
                try {
                    await this.updateOraclePrices(oracleName);
                } catch (error) {
                    console.error(`Error updating oracle ${oracleName}:`, error);
                    this.degradeOracleHealth(oracleName);
                }
            }, oracle.updateFrequency);

            this.monitoringIntervals = this.monitoringIntervals || new Map();
            this.monitoringIntervals.set(oracleName, interval);
        });

        // Start price validation
        this.startPriceValidation();
    }

    // Stop oracle monitoring
    stopMonitoring() {
        this.isMonitoring = false;

        if (this.monitoringIntervals) {
            this.monitoringIntervals.forEach((interval, oracleName) => {
                clearInterval(interval);
            });
            this.monitoringIntervals.clear();
        }

        // Stop price validation
        this.stopPriceValidation();

        console.log('í»‘ Oracle monitoring stopped');
    }

    // Update prices for specific oracle
    async updateOraclePrices(oracleName) {
        const oracle = this.oracleFeeds.get(oracleName);
        if (!oracle) {
            throw new Error(`Oracle ${oracleName} not found`);
        }

        const updatePromises = oracle.assets.map(async (asset) => {
            try {
                const price = await this.fetchOraclePrice(oracleName, asset);
                await this.recordPrice(oracleName, asset, price);
                
                return { asset, price, success: true };
            } catch (error) {
                console.error(`Error fetching ${asset} price from ${oracleName}:`, error);
                return { asset, error: error.message, success: false };
            }
        });

        const results = await Promise.allSettled(updatePromises);
        
        // Update oracle health based on success rate
        const successfulUpdates = results.filter(r => r.status === 'fulfilled' && r.value.success).length;
        const successRate = successfulUpdates / oracle.assets.length;
        
        oracle.health = successRate;
        oracle.lastUpdate = Date.now();

        this.emit('oracle_prices_updated', {
            oracle: oracleName,
            successRate: successRate,
            timestamp: Date.now()
        });

        return results;
    }

    // Fetch price from specific oracle
    async fetchOraclePrice(oracleName, asset) {
        // Simulate price fetching from different oracle types
        // In production, would use actual API connections
        
        const basePrices = {
            'ETH/USD': 2500 + (Math.random() - 0.5) * 100,
            'BTC/USD': 40000 + (Math.random() - 0.5) * 1000,
            'ETH/USDC': 2500 + (Math.random() - 0.5) * 50,
            'BTC/ETH': 0.08 + (Math.random() - 0.5) * 0.01,
            'USDC/USD': 1.0,
            'USDT/USD': 0.999 + (Math.random() - 0.5) * 0.002,
            'LINK/USD': 15 + (Math.random() - 0.5) * 2,
            'BNB/USDT': 300 + (Math.random() - 0.5) * 10
        };

        const basePrice = basePrices[asset] || 100 + (Math.random() - 0.5) * 20;

        // Add oracle-specific variations
        const oracleVariations = {
            'Chainlink': 0.001, // 0.1% variation
            'UniswapV3': 0.002, // 0.2% variation
            'Binance': 0.0005,  // 0.05% variation
            'Coinbase': 0.0005,
            'Kyber': 0.003      // 0.3% variation
        };

        const variation = oracleVariations[oracleName] || 0.002;
        const price = basePrice * (1 + (Math.random() - 0.5) * variation);

        // Simulate API latency
        await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 400));

        return price;
    }

    // Record price in history
    async recordPrice(oracleName, asset, price) {
        const priceKey = `${oracleName}_${asset}`;
        
        if (!this.priceHistory.has(priceKey)) {
            this.priceHistory.set(priceKey, []);
        }

        const history = this.priceHistory.get(priceKey);
        const priceRecord = {
            price: price,
            timestamp: Date.now(),
            oracle: oracleName,
            asset: asset
        };

        history.push(priceRecord);

        // Keep only recent history (last 1000 records)
        if (history.length > 1000) {
            history.shift();
        }

        this.emit('price_recorded', priceRecord);
    }

    // Start price validation across oracles
    startPriceValidation() {
        console.log('âœ… Starting cross-oracle price validation...');

        this.validationInterval = setInterval(() => {
            this.validateOraclePrices();
        }, 30000); // Validate every 30 seconds
    }

    // Stop price validation
    stopPriceValidation() {
        if (this.validationInterval) {
            clearInterval(this.validationInterval);
            this.validationInterval = null;
        }
    }

    // Validate prices across different oracles
    validateOraclePrices() {
        const assetOracles = {};

        // Group prices by asset
        this.priceHistory.forEach((history, priceKey) => {
            const [oracleName, asset] = priceKey.split('_');
            if (!assetOracles[asset]) {
                assetOracles[asset] = [];
            }

            const latestPrice = history[history.length - 1];
            if (latestPrice && Date.now() - latestPrice.timestamp < 60000) { // Last minute
                assetOracles[asset].push({
                    oracle: oracleName,
                    price: latestPrice.price,
                    timestamp: latestPrice.timestamp
                });
            }
        });

        // Validate each asset
        Object.entries(assetOracles).forEach(([asset, prices]) => {
            if (prices.length < 2) return; // Need at least 2 sources for validation

            const validationResult = this.performPriceValidation(asset, prices);
            this.validationResults.set(asset, validationResult);

            if (!validationResult.consistent) {
                this.emit('price_discrepancy_detected', validationResult);
            }
        });
    }

    // Perform statistical validation of prices
    performPriceValidation(asset, prices) {
        const priceValues = prices.map(p => p.price);
        const meanPrice = priceValues.reduce((a, b) => a + b, 0) / priceValues.length;
        const stdDev = Math.sqrt(
            priceValues.reduce((a, b) => a + Math.pow(b - meanPrice, 2), 0) / priceValues.length
        );

        const coefficientOfVariation = stdDev / meanPrice;
        const consistent = coefficientOfVariation < 0.01; // 1% threshold

        // Identify outliers (2 standard deviations)
        const outliers = prices.filter(p => Math.abs(p.price - meanPrice) > 2 * stdDev);

        return {
            asset: asset,
            meanPrice: meanPrice,
            stdDev: stdDev,
            coefficientOfVariation: coefficientOfVariation,
            consistent: consistent,
            outlierCount: outliers.length,
            outliers: outliers,
            timestamp: Date.now(),
            priceSources: prices.length
        };
    }

    // Degrade oracle health on errors
    degradeOracleHealth(oracleName) {
        const oracle = this.oracleFeeds.get(oracleName);
        if (oracle) {
            oracle.health = Math.max(0, oracle.health - 0.1);

            if (oracle.health < 0.3) {
                this.emit('oracle_health_warning', {
                    oracle: oracleName,
                    health: oracle.health,
                    timestamp: Date.now()
                });
            }
        }
    }

    // Get consensus price for an asset
    getConsensusPrice(asset, confidenceThreshold = 0.95) {
        const recentPrices = [];

        // Collect recent prices from all oracles for this asset
        this.priceHistory.forEach((history, priceKey) => {
            const [oracleName, historyAsset] = priceKey.split('_');
            if (historyAsset === asset && history.length > 0) {
                const latestPrice = history[history.length - 1];
                const oracle = this.oracleFeeds.get(oracleName);

                // Only include prices from healthy oracles
                if (oracle && oracle.health > 0.7 && Date.now() - latestPrice.timestamp < 120000) { // 2 minutes
                    recentPrices.push({
                        oracle: oracleName,
                        price: latestPrice.price,
                        weight: oracle.health, // Weight by oracle health
                        timestamp: latestPrice.timestamp
                    });
                }
            }
        });

        if (recentPrices.length === 0) {
            throw new Error(`No recent prices available for ${asset}`);
        }

        // Calculate weighted average
        const totalWeight = recentPrices.reduce((sum, p) => sum + p.weight, 0);
        const weightedPrice = recentPrices.reduce((sum, p) => sum + p.price * p.weight, 0) / totalWeight;

        // Calculate confidence
        const priceVariance = recentPrices.reduce((sum, p) => {
            return sum + Math.pow(p.price - weightedPrice, 2) * p.weight;
        }, 0) / totalWeight;

        const confidence = Math.max(0, 1 - Math.sqrt(priceVariance) / weightedPrice);

        return {
            asset: asset,
            consensusPrice: weightedPrice,
            confidence: confidence,
            meetsThreshold: confidence >= confidenceThreshold,
            sources: recentPrices.length,
            timestamp: Date.now()
        };
    }

    // Detect price manipulation attempts
    detectPriceManipulation(asset, windowMinutes = 5) {
        const windowMs = windowMinutes * 60 * 1000;
        const cutoffTime = Date.now() - windowMs;

        const assetPrices = [];
        this.priceHistory.forEach((history, priceKey) => {
            const [oracleName, historyAsset] = priceKey.split('_');
            if (historyAsset === asset) {
                const recentPrices = history.filter(p => p.timestamp > cutoffTime);
                assetPrices.push(...recentPrices.map(p => ({
                    ...p,
                    oracle: oracleName
                })));
            }
        });

        if (assetPrices.length < 10) {
            return { detected: false, reason: 'Insufficient data' };
        }

        // Check for abnormal price movements
        const prices = assetPrices.map(p => p.price);
        const returns = prices.slice(1).map((price, i) => (price - prices[i]) / prices[i]);

        const volatility = Math.sqrt(returns.reduce((sum, ret) => sum + ret * ret, 0) / returns.length);
        const abnormalVolatility = volatility > 0.05; // 5% threshold

        // Check for outlier patterns
        const meanPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
        const stdDev = Math.sqrt(prices.reduce((a, b) => a + Math.pow(b - meanPrice, 2), 0) / prices.length);
        const outlierRatio = prices.filter(p => Math.abs(p - meanPrice) > 2 * stdDev).length / prices.length;

        const manipulationDetected = abnormalVolatility || outlierRatio > 0.1;

        return {
            detected: manipulationDetected,
            abnormalVolatility: abnormalVolatility,
            outlierRatio: outlierRatio,
            volatility: volatility,
            confidence: manipulationDetected ? 0.8 : 0.2,
            timestamp: Date.now()
        };
    }

    // Get oracle status summary
    getOracleStatusSummary() {
        const summary = {
            totalOracles: this.oracleFeeds.size,
            healthyOracles: 0,
            degradedOracles: 0,
            oracles: []
        };

        this.oracleFeeds.forEach((oracle, oracleName) => {
            let status = 'healthy';
            if (oracle.health < 0.5) status = 'degraded';

            if (status === 'healthy') summary.healthyOracles++;
            else summary.degradedOracles++;

            summary.oracles.push({
                name: oracleName,
                type: oracle.type,
                status: status,
                health: oracle.health,
                assets: oracle.assets.length,
                lastUpdate: oracle.lastUpdate,
                updateFrequency: oracle.updateFrequency
            });
        });

        return summary;
    }

    // Get price history for analysis
    getPriceHistory(asset, timeframeMinutes = 60) {
        const timeframeMs = timeframeMinutes * 60 * 1000;
        const cutoffTime = Date.now() - timeframeMs;

        const allPrices = [];

        this.priceHistory.forEach((history, priceKey) => {
            const [oracleName, historyAsset] = priceKey.split('_');
            if (historyAsset === asset) {
                const recentPrices = history.filter(p => p.timestamp > cutoffTime);
                allPrices.push(...recentPrices.map(p => ({
                    oracle: oracleName,
                    price: p.price,
                    timestamp: p.timestamp
                })));
            }
        });

        // Sort by timestamp
        allPrices.sort((a, b) => a.timestamp - b.timestamp);

        return {
            asset: asset,
            timeframeMinutes: timeframeMinutes,
            dataPoints: allPrices.length,
            prices: allPrices
        };
    }
}

module.exports = OracleManager;
