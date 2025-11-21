module.exports = {
    healthCheckInterval: 30000, // Check every 30 seconds
    dockerComposeFile: './docker/docker-compose.yml',
    services: {
        core: {
            image: 'ainexus-phase1:latest',
            port: 3000,
            healthCheck: '/health'
        },
        redis: {
            image: 'redis:7-alpine',
            port: 6379
        }
    },
    deployment: {
        autoRestart: true,
        resourceLimits: {
            memory: '1g',
            cpus: '1.0'
        },
        logRetention: '30d'
    }
};
