const MultiAgentExecutionOrchestrator = require('./MultiAgentExecutionOrchestrator');

describe('MultiAgentExecutionOrchestrator', () => {
    let orchestrator;
    const config = {
        agentConfigs: {
            scanner: { maxConcurrentTasks: 3 },
            executor: { maxConcurrentTasks: 2 }
        }
    };

    beforeEach(() => {
        orchestrator = new MultiAgentExecutionOrchestrator(config);
    });

    test('should initialize successfully', async () => {
        const result = await orchestrator.initialize();
        expect(result.success).toBe(true);
        expect(result.agents).toBeGreaterThan(0);
    });

    test('should submit tasks to queue', async () => {
        await orchestrator.initialize();
        
        const task = {
            type: 'SIMPLE_ARBITRAGE',
            priority: 'HIGH',
            expectedProfit: 1.5,
            opportunity: { pair: 'ETH/USDC', profit: 1.5 }
        };
        
        const taskId = await orchestrator.submitTask(task);
        expect(taskId).toContain('TASK_');
        
        const status = orchestrator.getStatus();
        expect(status.queuedTasks).toBe(1);
    });

    test('should calculate agent scores', () => {
        const performance = { speed: 0.9, accuracy: 0.8, reliability: 0.95 };
        const score = orchestrator.calculateAgentScore(performance);
        expect(score).toBeCloseTo(0.883, 2);
    });

    test('should get agent status', async () => {
        await orchestrator.initialize();
        const status = orchestrator.getAgentStatus();
        expect(status).toHaveProperty('SCANNER_ALPHA');
        expect(status.SCANNER_ALPHA).toHaveProperty('type');
        expect(status.SCANNER_ALPHA).toHaveProperty('status');
    });
});
