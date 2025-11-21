module.exports = {
    agentConfigs: {
        scanner: {
            maxConcurrentTasks: 3,
            taskTimeout: 30000,
            healthCheckInterval: 10000
        },
        executor: {
            maxConcurrentTasks: 2,
            taskTimeout: 60000,
            healthCheckInterval: 5000
        },
        controller: {
            maxConcurrentTasks: 5,
            taskTimeout: 15000,
            healthCheckInterval: 15000
        },
        analytics: {
            maxConcurrentTasks: 2,
            taskTimeout: 45000,
            healthCheckInterval: 20000
        }
    },
    teamConfigs: {
        FAST_RESPONSE: {
            maxMissionTime: 30000,
            minSuccessRate: 0.9,
            autoRebalance: true
        },
        CROSS_CHAIN_SPECIALISTS: {
            maxMissionTime: 90000,
            minSuccessRate: 0.85,
            autoRebalance: true
        }
    },
    coordination: {
        taskDistributionInterval: 1000,
        performanceMonitoringInterval: 10000,
        teamRebalanceInterval: 30000,
        maxQueueSize: 100,
        priorityWeights: {
            profit: 0.6,
            urgency: 0.3,
            complexity: 0.1
        }
    },
    thresholds: {
        minAgentPerformance: 0.7,
        maxAgentFailures: 5,
        maxInactiveTime: 60000,
        teamPerformanceAlert: 0.75
    }
};
