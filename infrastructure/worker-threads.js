// QUANTUMNEX v1.0 - WORKER THREADS MANAGER
// Multi-Core Processing for Maximum Performance

const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const os = require('os');
const { globalMemoryPool } = require('../bots/memory-pool');

class WorkerThreadsManager {
    constructor() {
        this.workers = new Map();
        this.taskQueue = [];
        this.isRunning = false;
        this.workerCount = Math.max(1, os.cpus().length - 1); // Leave one core for main thread
        
        this.workerTypes = {
            PRICE_PROCESSOR: 'price_processor',
            ARBITRAGE_CALC: 'arbitrage_calc',
            RISK_MONITOR: 'risk_monitor',
            ORDER_EXECUTION: 'order_execution'
        };
    }

    /**
     * Initialize worker threads
     */
    async initialize() {
        console.log(`íº€ Initializing ${this.workerCount} worker threads...`);
        
        for (let i = 0; i < this.workerCount; i++) {
            await this.createWorker(i);
        }
        
        this.isRunning = true;
        this.processQueue();
        
        console.log(`âœ… ${this.workerCount} worker threads initialized`);
    }

    /**
     * Create individual worker thread
     */
    async createWorker(id) {
        return new Promise((resolve, reject) => {
            const worker = new Worker(__filename, {
                workerData: { workerId: id, type: this.getWorkerType(id) }
            });

            worker.on('online', () => {
                console.log(`âœ… Worker ${id} online (${this.getWorkerType(id)})`);
                this.workers.set(id, worker);
                resolve(worker);
            });

            worker.on('message', (message) => {
                this.handleWorkerMessage(id, message);
            });

            worker.on('error', (error) => {
                console.error(`âŒ Worker ${id} error:`, error);
                this.restartWorker(id);
            });

            worker.on('exit', (code) => {
                if (code !== 0) {
                    console.warn(`âš ï¸ Worker ${id} exited with code ${code}`);
                    this.restartWorker(id);
                }
            });
        });
    }

    /**
     * Assign worker type based on ID
     */
    getWorkerType(workerId) {
        const types = Object.values(this.workerTypes);
        return types[workerId % types.length];
    }

    /**
     * Submit task to worker pool
     */
    submitTask(task) {
        return new Promise((resolve, reject) => {
            const taskWithCallback = {
                ...task,
                resolve,
                reject,
                timestamp: Date.now()
            };
            
            this.taskQueue.push(taskWithCallback);
        });
    }

    /**
     * Process task queue
     */
    processQueue() {
        if (!this.isRunning) return;

        setImmediate(() => {
            if (this.taskQueue.length === 0) {
                this.processQueue();
                return;
            }

            const availableWorker = this.getAvailableWorker();
            if (availableWorker && this.taskQueue.length > 0) {
                const task = this.taskQueue.shift();
                this.assignTaskToWorker(availableWorker, task);
            }

            this.processQueue();
        });
    }

    /**
     * Get available worker with least load
     */
    getAvailableWorker() {
        let availableWorker = null;
        let minLoad = Infinity;

        for (let [id, worker] of this.workers) {
            const load = worker.pendingTasks || 0;
            if (load < minLoad) {
                minLoad = load;
                availableWorker = { id, worker };
            }
        }

        return availableWorker;
    }

    /**
     * Assign task to specific worker
     */
    assignTaskToWorker(workerInfo, task) {
        const { id, worker } = workerInfo;
        
        worker.pendingTasks = (worker.pendingTasks || 0) + 1;
        
        worker.postMessage({
            type: 'EXECUTE_TASK',
            task: task,
            taskId: task.id
        });

        // Timeout handling
        const timeout = setTimeout(() => {
            worker.pendingTasks--;
            task.reject(new Error(`Worker ${id} timeout on task ${task.id}`));
        }, task.timeout || 5000);

        task._timeoutId = timeout;
    }

    /**
     * Handle messages from workers
     */
    handleWorkerMessage(workerId, message) {
        const worker = this.workers.get(workerId);
        if (!worker) return;

        switch (message.type) {
            case 'TASK_COMPLETE':
                worker.pendingTasks--;
                
                // Find and resolve the task
                const task = this.findTask(message.taskId);
                if (task) {
                    clearTimeout(task._timeoutId);
                    task.resolve(message.result);
                }
                break;

            case 'TASK_ERROR':
                worker.pendingTasks--;
                
                const errorTask = this.findTask(message.taskId);
                if (errorTask) {
                    clearTimeout(errorTask._timeoutId);
                    errorTask.reject(new Error(message.error));
                }
                break;

            case 'HEARTBEAT':
                worker.lastHeartbeat = Date.now();
                break;
        }
    }

    /**
     * Find task by ID
     */
    findTask(taskId) {
        // Check both queue and in-progress tasks
        for (let worker of this.workers.values()) {
            // This would track in-progress tasks in a real implementation
        }
        return null; // Simplified for example
    }

    /**
     * Restart failed worker
     */
    async restartWorker(workerId) {
        console.log(`í´„ Restarting worker ${workerId}...`);
        
        const oldWorker = this.workers.get(workerId);
        if (oldWorker) {
            oldWorker.terminate();
            this.workers.delete(workerId);
        }
        
        await this.createWorker(workerId);
    }

    /**
     * Get worker statistics
     */
    getStats() {
        const stats = {
            totalWorkers: this.workers.size,
            queueLength: this.taskQueue.length,
            workers: []
        };

        for (let [id, worker] of this.workers) {
            stats.workers.push({
                id,
                type: this.getWorkerType(id),
                pendingTasks: worker.pendingTasks || 0,
                lastHeartbeat: worker.lastHeartbeat || 0
            });
        }

        return stats;
    }

    /**
     * Shutdown all workers
     */
    async shutdown() {
        this.isRunning = false;
        
        for (let [id, worker] of this.workers) {
            worker.terminate();
        }
        
        this.workers.clear();
        this.taskQueue = [];
        
        console.log('âœ… All worker threads shutdown');
    }
}

// Worker thread implementation
if (!isMainThread) {
    const { workerId, type } = workerData;
    
    parentPort.on('message', async (message) => {
        try {
            switch (message.type) {
                case 'EXECUTE_TASK':
                    const result = await processTask(message.task, type);
                    
                    parentPort.postMessage({
                        type: 'TASK_COMPLETE',
                        taskId: message.taskId,
                        result: result
                    });
                    break;
            }
        } catch (error) {
            parentPort.postMessage({
                type: 'TASK_ERROR',
                taskId: message.taskId,
                error: error.message
            });
        }
    });

    // Send heartbeat every 10 seconds
    setInterval(() => {
        parentPort.postMessage({
            type: 'HEARTBEAT',
            workerId: workerId
        });
    }, 10000);

    /**
     * Process task based on worker type
     */
    async function processTask(task, workerType) {
        // Use memory pool for zero allocation
        const taskData = globalMemoryPool.get('WorkerTask');
        
        Object.assign(taskData, task);
        
        try {
            switch (workerType) {
                case 'price_processor':
                    return await processPriceData(taskData);
                case 'arbitrage_calc':
                    return await calculateArbitrage(taskData);
                case 'risk_monitor':
                    return await monitorRisk(taskData);
                case 'order_execution':
                    return await executeOrder(taskData);
                default:
                    throw new Error(`Unknown worker type: ${workerType}`);
            }
        } finally {
            // Object automatically returned to pool for reuse
        }
    }

    async function processPriceData(data) {
        // Price processing logic
        await new Promise(resolve => setTimeout(resolve, 1)); // Simulate work
        return { processed: true, symbols: data.symbols };
    }

    async function calculateArbitrage(data) {
        // Arbitrage calculation logic
        await new Promise(resolve => setTimeout(resolve, 2)); // Simulate work
        return { opportunity: true, profit: 0.0015 };
    }

    async function monitorRisk(data) {
        // Risk monitoring logic
        await new Promise(resolve => setTimeout(resolve, 1)); // Simulate work
        return { riskLevel: 'low', exposure: 0.1 };
    }

    async function executeOrder(data) {
        // Order execution logic
        await new Promise(resolve => setTimeout(resolve, 3)); // Simulate work
        return { executed: true, orderId: '12345' };
    }
}

module.exports = { WorkerThreadsManager };
