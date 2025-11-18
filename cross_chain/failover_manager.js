/**
 * AI-NEXUS FAILOVER MANAGER
 * Enterprise-grade failover management for cross-chain operations
 */

class FailoverManager {
    constructor(config, providers) {
        this.config = config;
        this.providers = providers; // Multiple providers per chain
        this.failoverHistory = new Map();
        this.healthChecks = new Map();
        this.currentPrimary = new Map(); // chain -> primary provider
        this.failoverThreshold = config.failoverThreshold || 3; // Consecutive failures
    }

    async initialize() {
        /**
         * Initialize failover manager and health checks
         */
        for (const [chain, providers] of Object.entries(this.providers)) {
            this.currentPrimary.set(chain, providers[0]); // First provider is primary
            await this.initializeHealthChecks(chain, providers);
        }

        // Start continuous health monitoring
        this.startHealthMonitoring();
    }

    async initializeHealthChecks(chain, providers) {
        for (const provider of providers) {
            this.healthChecks.set(this.getProviderKey(chain, provider), {
                provider,
                chain,
                consecutiveFailures: 0,
                lastCheck: Date.now(),
                isHealthy: true,
                responseTime: 0
            });
        }
    }

    getProviderKey(chain, provider) {
        return `${chain}_${provider.connection.url}`;
    }

    async executeWithFailover(chain, operation, operationArgs, retries = 3) {
        /**
         * Execute operation with automatic failover
         */
        let lastError;
        
        for (let attempt = 0; attempt < retries; attempt++) {
            const provider = this.getOptimalProvider(chain);
            
            try {
                const result = await operation(provider, ...operationArgs);
                
                // Record success
                this.recordSuccess(chain, provider);
                return result;
                
            } catch (error) {
                lastError = error;
                
                // Record failure and trigger failover if needed
                const shouldFailover = await this.recordFailure(chain, provider, error);
                
                if (shouldFailover) {
                    console.warn(`Failover triggered for ${chain} after ${attempt + 1} attempts`);
                    await this.triggerFailover(chain, provider, error);
                }
                
                // Exponential backoff
                await this.delay(Math.pow(2, attempt) * 1000);
            }
        }

        throw new Error(`All providers failed for ${chain}: ${lastError.message}`);
    }

    getOptimalProvider(chain) {
        /**
         * Get optimal provider considering health and performance
         */
        const primary = this.currentPrimary.get(chain);
        if (primary && this.isProviderHealthy(chain, primary)) {
            return primary;
        }

        // Fall back to healthy secondary provider
        const secondaryProviders = this.providers[chain].slice(1);
        for (const provider of secondaryProviders) {
            if (this.isProviderHealthy(chain, provider)) {
                return provider;
            }
        }

        // If no healthy providers, return primary anyway
        return primary || this.providers[chain][0];
    }

    isProviderHealthy(chain, provider) {
        const healthKey = this.getProviderKey(chain, provider);
        const health = this.healthChecks.get(healthKey);
        return health && health.isHealthy;
    }

    async recordSuccess(chain, provider) {
        const healthKey = this.getProviderKey(chain, provider);
        const health = this.healthChecks.get(healthKey);
        
        if (health) {
            health.consecutiveFailures = 0;
            health.isHealthy = true;
            health.lastCheck = Date.now();
        }
    }

    async recordFailure(chain, provider, error) {
        const healthKey = this.getProviderKey(chain, provider);
        const health = this.healthChecks.get(healthKey);
        
        if (health) {
            health.consecutiveFailures++;
            health.lastError = error;
            health.lastCheck = Date.now();

            // Check if we should trigger failover
            if (health.consecutiveFailures >= this.failoverThreshold) {
                health.isHealthy = false;
                return true;
            }
        }

        return false;
    }

    async triggerFailover(chain, failedProvider, error) {
        /**
         * Trigger failover to secondary provider
         */
        const secondaryProviders = this.providers[chain].slice(1);
        let newPrimary = null;

        // Find first healthy secondary provider
        for (const provider of secondaryProviders) {
            if (this.isProviderHealthy(chain, provider)) {
                newPrimary = provider;
                break;
            }
        }

        // If no healthy secondary, try to revive primary after cooldown
        if (!newPrimary) {
            console.warn(`No healthy providers for ${chain}, attempting to revive primary`);
            await this.attemptProviderRevival(chain, failedProvider);
            return;
        }

        // Update primary provider
        this.currentPrimary.set(chain, newPrimary);

        // Record failover event
        this.recordFailoverEvent(chain, failedProvider, newPrimary, error);

        console.log(`Failover completed for ${chain}: ${failedProvider.connection.url} -> ${newPrimary.connection.url}`);
    }

    async attemptProviderRevival(chain, provider) {
        /**
         * Attempt to revive a failed provider
         */
        const healthKey = this.getProviderKey(chain, provider);
        const health = this.healthChecks.get(healthKey);

        if (!health) return;

        // Wait for cooldown period
        const cooldown = 5 * 60 * 1000; // 5 minutes
        if (Date.now() - health.lastCheck < cooldown) {
            return;
        }

        try {
            // Test provider health
            await this.testProviderHealth(chain, provider);
            
            // If successful, mark as healthy
            health.consecutiveFailures = 0;
            health.isHealthy = true;
            health.lastCheck = Date.now();

            console.log(`Provider revived for ${chain}: ${provider.connection.url}`);

            // Optionally switch back to revived provider
            this.currentPrimary.set(chain, provider);

        } catch (error) {
            // Provider still unhealthy, extend cooldown
            health.lastCheck = Date.now();
        }
    }

    async testProviderHealth(chain, provider) {
        /**
         * Test provider health with basic operations
         */
        const tests = [
            () => provider.getBlockNumber(),
            () => provider.getGasPrice(),
            () => provider.getNetwork()
        ];

        for (const test of tests) {
            await test();
            await this.delay(100); // Small delay between tests
        }
    }

    recordFailoverEvent(chain, fromProvider, toProvider, error) {
        const event = {
            timestamp: new Date(),
            chain,
            fromProvider: fromProvider.connection.url,
            toProvider: toProvider.connection.url,
            error: error.message,
            healthStats: this.getHealthStats(chain)
        };

        const historyKey = `${chain}_${Date.now()}`;
        this.failoverHistory.set(historyKey, event);

        // Keep only recent history
        this.cleanupHistory();
    }

    getHealthStats(chain) {
        const stats = {};
        
        for (const provider of this.providers[chain]) {
            const healthKey = this.getProviderKey(chain, provider);
            const health = this.healthChecks.get(healthKey);
            
            if (health) {
                stats[provider.connection.url] = {
                    isHealthy: health.isHealthy,
                    consecutiveFailures: health.consecutiveFailures,
                    lastCheck: health.lastCheck,
                    responseTime: health.responseTime
                };
            }
        }

        return stats;
    }

    startHealthMonitoring() {
        /**
         * Start continuous health monitoring
         */
        setInterval(() => {
            this.performHealthChecks();
        }, 30000); // Check every 30 seconds
    }

    async performHealthChecks() {
        /**
         * Perform health checks on all providers
         */
        for (const [chain, providers] of Object.entries(this.providers)) {
            for (const provider of providers) {
                await this.checkProviderHealth(chain, provider);
            }
        }
    }

    async checkProviderHealth(chain, provider) {
        const healthKey = this.getProviderKey(chain, provider);
        const health = this.healthChecks.get(healthKey);

        if (!health) return;

        try {
            const startTime = Date.now();
            await provider.getBlockNumber(); // Simple health check
            const responseTime = Date.now() - startTime;

            health.responseTime = responseTime;
            health.lastCheck = Date.now();
            
            // If provider was marked unhealthy but now passes health check, revive it
            if (!health.isHealthy && health.consecutiveFailures > 0) {
                health.consecutiveFailures = Math.max(0, health.consecutiveFailures - 1);
                
                if (health.consecutiveFailures === 0) {
                    health.isHealthy = true;
                    console.log(`Provider health restored for ${chain}: ${provider.connection.url}`);
                }
            }

        } catch (error) {
            health.consecutiveFailures++;
            health.lastError = error;
            health.lastCheck = Date.now();

            if (health.consecutiveFailures >= this.failoverThreshold) {
                health.isHealthy = false;
                
                // If this is the current primary, trigger failover
                const currentPrimary = this.currentPrimary.get(chain);
                if (currentPrimary === provider) {
                    this.triggerFailover(chain, provider, error);
                }
            }
        }
    }

    cleanupHistory() {
        const oneHourAgo = Date.now() - (60 * 60 * 1000);
        
        for (const [key, event] of this.failoverHistory.entries()) {
            if (event.timestamp.getTime() < oneHourAgo) {
                this.failoverHistory.delete(key);
            }
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    getFailoverStats() {
        const stats = {
            totalFailovers: this.failoverHistory.size,
            recentFailovers: Array.from(this.failoverHistory.values())
                .filter(event => event.timestamp > new Date(Date.now() - 24 * 60 * 60 * 1000))
                .length,
            currentPrimaries: Object.fromEntries(this.currentPrimary.entries()),
            healthStatus: {}
        };

        for (const [chain, providers] of Object.entries(this.providers)) {
            stats.healthStatus[chain] = this.getHealthStats(chain);
        }

        return stats;
    }

    getProviderRecommendations() {
        const recommendations = [];

        for (const [chain, providers] of Object.entries(this.providers)) {
            const healthStats = this.getHealthStats(chain);
            const unhealthyProviders = Object.entries(healthStats)
                .filter(([url, stats]) => !stats.isHealthy)
                .map(([url]) => url);

            if (unhealthyProviders.length > 0) {
                recommendations.push({
                    chain,
                    message: `Unhealthy providers: ${unhealthyProviders.join(', ')}`,
                    severity: 'HIGH'
                });
            }

            // Check for performance issues
            const slowProviders = Object.entries(healthStats)
                .filter(([url, stats]) => stats.responseTime > 1000) // > 1 second
                .map(([url]) => url);

            if (slowProviders.length > 0) {
                recommendations.push({
                    chain,
                    message: `Slow providers: ${slowProviders.join(', ')}`,
                    severity: 'MEDIUM'
                });
            }
        }

        return recommendations;
    }
}

module.exports = FailoverManager;
