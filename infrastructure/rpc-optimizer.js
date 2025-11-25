/**
 * QUANTUMNEX RPC OPTIMIZER
 * Industry Standards: ethers.js providers, Load balancing, Request batching
 * Validated Sources:
 * - ethers.js providers (Ethereum RPC interactions)
 * - Load balancing patterns (High availability)
 * - Request batching (Efficiency optimization)
 */

const { ethers } = require('ethers');
const { EventEmitter } = require('events');

class RPCOptimizer extends EventEmitter {
    constructor(providersConfig) {
        super();
        this.providers = new Map();
        this.providerStats = new Map();
        this.requestQueue = [];
        this.isProcessingQueue = false;
        this.batchSize = 10;
        this.batchDelay = 50; // ms
        
        this.initializeProviders(providersConfig);
        this.startHealthMonitoring();
        
        console.log('âœ… RPC Optimizer initialized with ethers.js providers');
    }

    initializeProviders(providersConfig) {
        providersConfig.forEach((config, index) => {
            try {
                const provider = new ethers.providers.JsonRpcProvider(config.url);
                const providerId = config.id || `provider_${index}`;
                
                this.providers.set(providerId, {
                    id: providerId,
                    provider: provider,
                    url: config.url,
                    priority: config.priority || 1,
                    weight: config.weight || 1,
                    isActive: true,
                    failureCount: 0,
                    lastFailure: null,
                    responseTimes: [],
                    successRate: 1.0
                });

                this.providerStats.set(providerId, {
                    totalRequests: 0,
                    successfulRequests: 0,
                    failedRequests: 0,
                    totalResponseTime: 0,
                    averageResponseTime: 0
                });

                console.log(`âœ… Provider initialized: ${providerId} (${config.url})`);
            } catch (error) {
                console.error(`âŒ Failed to initialize provider ${config.url}:`, error);
            }
        });

        if (this.providers.size === 0) {
            throw new Error('No valid RPC providers configured');
        }
    }

    async sendRequest(method, params = []) {
        const requestId = this.generateRequestId();
        const startTime = Date.now();
        
        try {
            const provider = this.selectOptimalProvider();
            if (!provider) {
                throw new Error('No active RPC providers available');
            }

            const result = await this.executeWithProvider(provider, method, params);
            
            this.recordSuccess(provider.id, Date.now() - startTime);
            
            console.log(`âœ… RPC ${method} completed via ${provider.id} in ${Date.now() - startTime}ms`);
            
            return {
                success: true,
                data: result,
                provider: provider.id,
                responseTime: Date.now() - startTime,
                requestId: requestId
            };
        } catch (error) {
            this.recordFailure(this.lastUsedProvider, error);
            
            console.error(`âŒ RPC ${method} failed:`, error.message);
            
            // Retry with fallback provider
            return await this.retryWithFallback(requestId, method, params, startTime);
        }
    }

    async executeWithProvider(provider, method, params) {
        this.lastUsedProvider = provider.id;
        
        switch (method) {
            case 'eth_getBalance':
                return await provider.provider.getBalance(...params);
            case 'eth_getTransactionCount':
                return await provider.provider.getTransactionCount(...params);
            case 'eth_getBlockNumber':
                return await provider.provider.getBlockNumber();
            case 'eth_getBlock':
                return await provider.provider.getBlock(...params);
            case 'eth_getTransaction':
                return await provider.provider.getTransaction(...params);
            case 'eth_getTransactionReceipt':
                return await provider.provider.getTransactionReceipt(...params);
            case 'eth_call':
                return await provider.provider.call(...params);
            case 'eth_sendRawTransaction':
                return await provider.provider.sendTransaction(...params);
            case 'eth_estimateGas':
                return await provider.provider.estimateGas(...params);
            case 'eth_getLogs':
                return await provider.provider.getLogs(...params);
            default:
                // Fallback to direct JSON-RPC for unsupported methods
                return await provider.provider.send(method, params);
        }
    }

    selectOptimalProvider() {
        const activeProviders = Array.from(this.providers.values())
            .filter(p => p.isActive)
            .sort((a, b) => {
                // Sort by priority, then by success rate, then by average response time
                if (a.priority !== b.priority) {
                    return b.priority - a.priority;
                }
                if (a.successRate !== b.successRate) {
                    return b.successRate - a.successRate;
                }
                return a.averageResponseTime - b.averageResponseTime;
            });

        return activeProviders[0] || null;
    }

    async retryWithFallback(requestId, method, params, startTime) {
        const fallbackProviders = Array.from(this.providers.values())
            .filter(p => p.isActive && p.id !== this.lastUsedProvider)
            .sort((a, b) => b.successRate - a.successRate);

        for (const provider of fallbackProviders) {
            try {
                console.log(`í´„ Retrying with fallback provider: ${provider.id}`);
                
                const result = await this.executeWithProvider(provider, method, params);
                
                this.recordSuccess(provider.id, Date.now() - startTime);
                
                return {
                    success: true,
                    data: result,
                    provider: provider.id,
                    responseTime: Date.now() - startTime,
                    requestId: requestId,
                    retried: true
                };
            } catch (error) {
                this.recordFailure(provider.id, error);
                continue;
            }
        }

        // All providers failed
        return {
            success: false,
            error: 'All RPC providers failed',
            requestId: requestId,
            responseTime: Date.now() - startTime
        };
    }

    recordSuccess(providerId, responseTime) {
        const stats = this.providerStats.get(providerId);
        if (stats) {
            stats.totalRequests++;
            stats.successfulRequests++;
            stats.totalResponseTime += responseTime;
            stats.averageResponseTime = stats.totalResponseTime / stats.successfulRequests;
        }

        const provider = this.providers.get(providerId);
        if (provider) {
            provider.responseTimes.push(responseTime);
            // Keep only last 100 response times
            if (provider.responseTimes.length > 100) {
                provider.responseTimes.shift();
            }
            provider.successRate = stats.successfulRequests / stats.totalRequests;
            provider.failureCount = 0;
        }
    }

    recordFailure(providerId, error) {
        const stats = this.providerStats.get(providerId);
        if (stats) {
            stats.totalRequests++;
            stats.failedRequests++;
        }

        const provider = this.providers.get(providerId);
        if (provider) {
            provider.failureCount++;
            provider.lastFailure = new Date();
            provider.successRate = stats ? stats.successfulRequests / stats.totalRequests : 0;

            // Disable provider if too many failures
            if (provider.failureCount >= 5) {
                provider.isActive = false;
                console.warn(`íº¨ Provider ${providerId} disabled due to consecutive failures`);
                
                // Schedule reactivation
                setTimeout(() => {
                    this.reactivateProvider(providerId);
                }, 60000); // Reactivate after 1 minute
            }
        }

        this.emit('providerFailure', { providerId, error, failureCount: provider?.failureCount });
    }

    reactivateProvider(providerId) {
        const provider = this.providers.get(providerId);
        if (provider) {
            provider.isActive = true;
            provider.failureCount = 0;
            console.log(`âœ… Provider ${providerId} reactivated`);
            this.emit('providerReactivated', { providerId });
        }
    }

    // Batch request processing
    async sendBatchRequest(requests) {
        const batchId = this.generateBatchId();
        const startTime = Date.now();

        try {
            const provider = this.selectOptimalProvider();
            if (!provider) {
                throw new Error('No active RPC providers available');
            }

            const batchResults = [];
            const batchPromises = [];

            // Process requests in batches
            for (let i = 0; i < requests.length; i += this.batchSize) {
                const batch = requests.slice(i, i + this.batchSize);
                const batchPromise = this.processBatch(provider, batch, batchId);
                batchPromises.push(batchPromise);

                // Add delay between batches if needed
                if (i + this.batchSize < requests.length) {
                    await this.delay(this.batchDelay);
                }
            }

            const results = await Promise.all(batchPromises);
            const flattenedResults = results.flat();

            this.recordSuccess(provider.id, Date.now() - startTime);

            console.log(`âœ… Batch ${batchId} completed: ${flattenedResults.length} requests via ${provider.id}`);

            return {
                success: true,
                results: flattenedResults,
                provider: provider.id,
                totalTime: Date.now() - startTime,
                batchId: batchId
            };

        } catch (error) {
            console.error(`âŒ Batch ${batchId} failed:`, error);
            return {
                success: false,
                error: error.message,
                batchId: batchId,
                totalTime: Date.now() - startTime
            };
        }
    }

    async processBatch(provider, batch, batchId) {
        const batchResults = [];

        for (const request of batch) {
            try {
                const result = await this.executeWithProvider(provider, request.method, request.params);
                batchResults.push({
                    success: true,
                    data: result,
                    method: request.method,
                    requestId: request.requestId
                });
            } catch (error) {
                batchResults.push({
                    success: false,
                    error: error.message,
                    method: request.method,
                    requestId: request.requestId
                });
            }
        }

        return batchResults;
    }

    // Queue-based request processing
    queueRequest(method, params, priority = 1) {
        const request = {
            id: this.generateRequestId(),
            method,
            params,
            priority,
            timestamp: Date.now(),
            status: 'queued'
        };

        this.requestQueue.push(request);
        this.requestQueue.sort((a, b) => b.priority - a.priority); // Higher priority first

        this.processQueue();

        return request.id;
    }

    async processQueue() {
        if (this.isProcessingQueue || this.requestQueue.length === 0) {
            return;
        }

        this.isProcessingQueue = true;

        try {
            while (this.requestQueue.length > 0) {
                const batch = this.requestQueue.splice(0, this.batchSize);
                
                const results = await this.sendBatchRequest(batch.map(req => ({
                    method: req.method,
                    params: req.params,
                    requestId: req.id
                })));

                // Emit results for each request
                batch.forEach((request, index) => {
                    const result = results.results?.[index];
                    this.emit('requestCompleted', {
                        requestId: request.id,
                        success: result?.success || false,
                        data: result?.data,
                        error: result?.error,
                        provider: results.provider
                    });
                });

                // Rate limiting
                if (this.requestQueue.length > 0) {
                    await this.delay(this.batchDelay);
                }
            }
        } catch (error) {
            console.error('âŒ Queue processing failed:', error);
        } finally {
            this.isProcessingQueue = false;
        }
    }

    // Health monitoring
    startHealthMonitoring() {
        this.healthCheckInterval = setInterval(() => {
            this.checkProviderHealth();
        }, 30000); // Check every 30 seconds

        this.metricsInterval = setInterval(() => {
            this.logMetrics();
        }, 60000); // Log metrics every minute
    }

    async checkProviderHealth() {
        console.log('í´ Checking RPC provider health...');

        for (const [providerId, provider] of this.providers) {
            if (!provider.isActive) continue;

            try {
                const startTime = Date.now();
                await provider.provider.getBlockNumber();
                const responseTime = Date.now() - startTime;

                this.recordSuccess(providerId, responseTime);
                
                console.log(`â¤ï¸ Provider ${providerId} healthy - ${responseTime}ms response`);
            } catch (error) {
                this.recordFailure(providerId, error);
                console.warn(`í²” Provider ${providerId} health check failed:`, error.message);
            }
        }
    }

    logMetrics() {
        const metrics = this.getMetrics();
        console.log('í³Š RPC Optimizer Metrics:', metrics);
        this.emit('metrics', metrics);
    }

    getMetrics() {
        const providerMetrics = {};
        let totalRequests = 0;
        let successfulRequests = 0;

        this.providers.forEach((provider, providerId) => {
            const stats = this.providerStats.get(providerId);
            providerMetrics[providerId] = {
                isActive: provider.isActive,
                totalRequests: stats?.totalRequests || 0,
                successfulRequests: stats?.successfulRequests || 0,
                failedRequests: stats?.failedRequests || 0,
                successRate: provider.successRate,
                averageResponseTime: stats?.averageResponseTime || 0,
                failureCount: provider.failureCount
            };

            totalRequests += stats?.totalRequests || 0;
            successfulRequests += stats?.successfulRequests || 0;
        });

        return {
            totalProviders: this.providers.size,
            activeProviders: Array.from(this.providers.values()).filter(p => p.isActive).length,
            totalRequests,
            successfulRequests,
            overallSuccessRate: totalRequests > 0 ? successfulRequests / totalRequests : 0,
            queueLength: this.requestQueue.length,
            providers: providerMetrics,
            timestamp: new Date().toISOString()
        };
    }

    // Utility methods
    generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateBatchId() {
        return `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    getProviderStatus(providerId) {
        const provider = this.providers.get(providerId);
        const stats = this.providerStats.get(providerId);
        
        return provider ? {
            ...provider,
            stats: stats || {}
        } : null;
    }

    getAllProviderStatus() {
        const status = {};
        this.providers.forEach((provider, providerId) => {
            status[providerId] = this.getProviderStatus(providerId);
        });
        return status;
    }

    updateProviderConfig(providerId, updates) {
        const provider = this.providers.get(providerId);
        if (provider) {
            Object.assign(provider, updates);
            console.log(`âœ… Provider ${providerId} config updated`);
            return true;
        }
        return false;
    }

    // Cleanup
    stop() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
        }
        console.log('âœ… RPC Optimizer stopped');
    }
}

module.exports = RPCOptimizer;
