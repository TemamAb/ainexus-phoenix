// QUANTUMNEX v1.0 - SHARED CACHE MANAGER
// Redis Cluster for Sub-Millisecond Data Access

const Redis = require('ioredis');
const config = require('../deployment/environment-config');

class SharedCache {
    constructor() {
        this.clients = new Map();
        this.connected = false;
        this.stats = {
            hits: 0,
            misses: 0,
            sets: 0,
            deletes: 0
        };
    }

    /**
     * Initialize Redis cluster connection
     */
    async initialize() {
        try {
            this.redis = new Redis.Cluster([
                {
                    host: config.database.redis.host,
                    port: config.database.redis.port
                }
            ], {
                redisOptions: {
                    password: config.database.redis.password,
                    lazyConnect: true
                },
                clusterRetryDelay: 100,
                enableReadyCheck: true
            });

            await this.redis.connect();
            this.connected = true;
            
            console.log('✅ Redis cluster connected successfully');
            return true;
        } catch (error) {
            console.error('❌ Redis connection failed:', error);
            this.connected = false;
            return false;
        }
    }

    /**
     * Get value with sub-millisecond access
     */
    async get(key, useMemoryCache = true) {
        if (!this.connected) return null;

        try {
            const start = process.hrtime.bigint();
            const value = await this.redis.get(key);
            const end = process.hrtime.bigint();
            
            const latency = Number(end - start) / 1000000; // Convert to milliseconds
            
            if (value) {
                this.stats.hits++;
                
                // Log slow accesses (above 0.5ms)
                if (latency > 0.5) {
                    console.warn(`Slow cache access: ${latency.toFixed(3)}ms for key: ${key}`);
                }
                
                return JSON.parse(value);
            } else {
                this.stats.misses++;
                return null;
            }
        } catch (error) {
            console.error('Cache get error:', error);
            return null;
        }
    }

    /**
     * Set value with expiration
     */
    async set(key, value, ttlSeconds = 60) {
        if (!this.connected) return false;

        try {
            const serialized = JSON.stringify(value);
            if (ttlSeconds > 0) {
                await this.redis.setex(key, ttlSeconds, serialized);
            } else {
                await this.redis.set(key, serialized);
            }
            
            this.stats.sets++;
            return true;
        } catch (error) {
            console.error('Cache set error:', error);
            return false;
        }
    }

    /**
     * Batch get multiple keys
     */
    async mget(keys) {
        if (!this.connected) return {};

        try {
            const values = await this.redis.mget(keys);
            const result = {};
            
            keys.forEach((key, index) => {
                if (values[index]) {
                    result[key] = JSON.parse(values[index]);
                    this.stats.hits++;
                } else {
                    this.stats.misses++;
                }
            });
            
            return result;
        } catch (error) {
            console.error('Cache mget error:', error);
            return {};
        }
    }

    /**
     * Batch set multiple key-value pairs
     */
    async mset(keyValuePairs, ttlSeconds = 60) {
        if (!this.connected) return false;

        try {
            const pipeline = this.redis.pipeline();
            
            Object.entries(keyValuePairs).forEach(([key, value]) => {
                const serialized = JSON.stringify(value);
                if (ttlSeconds > 0) {
                    pipeline.setex(key, ttlSeconds, serialized);
                } else {
                    pipeline.set(key, serialized);
                }
            });
            
            await pipeline.exec();
            this.stats.sets += Object.keys(keyValuePairs).length;
            return true;
        } catch (error) {
            console.error('Cache mset error:', error);
            return false;
        }
    }

    /**
     * Cache order book data with high frequency
     */
    async cacheOrderBook(symbol, orderBook) {
        const key = `orderbook:${symbol}:${orderBook.timestamp}`;
        return await this.set(key, orderBook, 5); // 5 second TTL for order books
    }

    /**
     * Cache price data with medium frequency
     */
    async cachePrice(symbol, priceData) {
        const key = `price:${symbol}:${priceData.exchange}`;
        return await this.set(key, priceData, 30); // 30 second TTL for prices
    }

    /**
     * Cache arbitrage opportunities with short TTL
     */
    async cacheArbitrage(opportunity) {
        const key = `arb:${opportunity.id}`;
        return await this.set(key, opportunity, 2); // 2 second TTL for arb opportunities
    }

    /**
     * Get cache statistics
     */
    getStats() {
        const total = this.stats.hits + this.stats.misses;
        const hitRate = total > 0 ? (this.stats.hits / total) : 0;
        
        return {
            ...this.stats,
            hitRate: hitRate,
            connected: this.connected
        };
    }

    /**
     * Health check
     */
    async healthCheck() {
        if (!this.connected) return false;
        
        try {
            await this.redis.ping();
            return true;
        } catch (error) {
            this.connected = false;
            return false;
        }
    }
}

// Global cache instance
const sharedCache = new SharedCache();

module.exports = { SharedCache, sharedCache };
