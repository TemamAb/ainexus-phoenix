// QUANTUMNEX v1.0 - MEMORY POOL MANAGER
// Zero Garbage Collection Memory Management for Low-Latency Trading

class MemoryPool {
    constructor() {
        this.pools = new Map();
        this.stats = {
            allocations: 0,
            reuses: 0,
            hits: 0,
            misses: 0
        };
    }

    /**
     * Create object pool for specific type
     */
    createPool(className, size = 1000) {
        if (this.pools.has(className)) {
            return this.pools.get(className);
        }

        const pool = {
            objects: new Array(size),
            index: 0,
            size: size,
            constructor: null
        };

        // Pre-allocate objects
        for (let i = 0; i < size; i++) {
            pool.objects[i] = {};
        }

        this.pools.set(className, pool);
        return pool;
    }

    /**
     * Get object from pool (zero allocation)
     */
    get(className) {
        const pool = this.pools.get(className);
        if (!pool) {
            this.stats.misses++;
            return this.createPool(className).objects[0];
        }

        if (pool.index >= pool.size) {
            pool.index = 0; // Reset pool
        }

        const obj = pool.objects[pool.index];
        pool.index++;
        
        this.stats.hits++;
        this.stats.reuses++;
        
        // Reset object for reuse
        for (let key in obj) {
            if (obj.hasOwnProperty(key)) {
                delete obj[key];
            }
        }
        
        return obj;
    }

    /**
     * Pre-allocate frequently used objects
     */
    preallocateCommonObjects() {
        // Trading data structures
        this.createPool('TradeOpportunity', 5000);
        this.createPool('PriceData', 10000);
        this.createPool('OrderBook', 2000);
        this.createPool('ArbitrageCalc', 3000);
        
        // Network objects
        this.createPool('WebSocketMessage', 5000);
        this.createPool('RPCRequest', 3000);
        this.createPool('RPCResponse', 3000);
    }

    /**
     * Get performance statistics
     */
    getStats() {
        const hitRate = this.stats.hits / (this.stats.hits + this.stats.misses);
        return {
            ...this.stats,
            hitRate: hitRate || 0,
            totalPools: this.pools.size,
            memoryEfficiency: (this.stats.reuses / (this.stats.allocations + this.stats.reuses)) || 0
        };
    }

    /**
     * Reset all pools
     */
    reset() {
        for (let [className, pool] of this.pools) {
            pool.index = 0;
            for (let i = 0; i < pool.size; i++) {
                const obj = pool.objects[i];
                for (let key in obj) {
                    if (obj.hasOwnProperty(key)) {
                        delete obj[key];
                    }
                }
            }
        }
        this.stats.hits = 0;
        this.stats.misses = 0;
    }
}

// Pre-configured object templates
const ObjectTemplates = {
    TradeOpportunity: {
        id: '',
        chain: '',
        dexA: '',
        dexB: '',
        tokenIn: '',
        tokenOut: '',
        amountIn: 0,
        expectedProfit: 0,
        timestamp: 0,
        confidence: 0
    },

    PriceData: {
        symbol: '',
        price: 0,
        volume: 0,
        timestamp: 0,
        exchange: '',
        liquidity: 0
    },

    OrderBook: {
        symbol: '',
        bids: [],
        asks: [],
        timestamp: 0,
        spread: 0
    }
};

// Global memory pool instance
const globalMemoryPool = new MemoryPool();
globalMemoryPool.preallocateCommonObjects();

module.exports = { MemoryPool, globalMemoryPool, ObjectTemplates };
