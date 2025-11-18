// File: core_foundation/execution_engine/MessageBus.js
// 7P-PILLAR: BOT3-7P
// PURPOSE: Real-time messaging between 3-Tier Bot components

const { EventEmitter } = require('events');

class MessageBus extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.connections = new Map();
        this.messageQueue = [];
        this.isProcessing = false;
        this.metrics = {
            messagesSent: 0,
            messagesReceived: 0,
            deliveryErrors: 0,
            averageLatency: 0
        };
    }

    // Register component to message bus
    registerComponent(componentId, component) {
        this.connections.set(componentId, {
            component,
            lastSeen: Date.now(),
            health: 1.0
        });
        
        this.emit('component_registered', { componentId, timestamp: Date.now() });
    }

    // Send message between components
    async sendMessage(fromComponent, toComponent, messageType, payload) {
        const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const timestamp = Date.now();
        
        const message = {
            id: messageId,
            from: fromComponent,
            to: toComponent,
            type: messageType,
            payload: payload,
            timestamp: timestamp,
            priority: this.getMessagePriority(messageType)
        };
        
        // Add to queue and process
        this.messageQueue.push(message);
        this.metrics.messagesSent++;
        
        await this.processQueue();
        
        return messageId;
    }

    // Process message queue
    async processQueue() {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            await this.deliverMessage(message);
            
            // Small delay to prevent blocking
            await new Promise(resolve => setTimeout(resolve, 1));
        }
        
        this.isProcessing = false;
    }

    // Deliver message to target component
    async deliverMessage(message) {
        const targetConnection = this.connections.get(message.to);
        
        if (!targetConnection) {
            this.metrics.deliveryErrors++;
            this.emit('delivery_failed', {
                messageId: message.id,
                reason: 'Component not found',
                timestamp: Date.now()
            });
            return;
        }
        
        try {
            const startTime = Date.now();
            
            // Emit message to target component
            this.emit(`message:${message.to}`, message);
            
            // Update component health
            targetConnection.lastSeen = Date.now();
            targetConnection.health = Math.min(1.0, targetConnection.health + 0.05);
            
            // Calculate latency
            const latency = Date.now() - startTime;
            this.updateLatencyMetrics(latency);
            
            this.metrics.messagesReceived++;
            
            this.emit('message_delivered', {
                messageId: message.id,
                from: message.from,
                to: message.to,
                latency: latency,
                timestamp: Date.now()
            });
            
        } catch (error) {
            this.metrics.deliveryErrors++;
            targetConnection.health -= 0.1;
            
            this.emit('delivery_error', {
                messageId: message.id,
                error: error.message,
                timestamp: Date.now()
            });
        }
    }

    // Message priority for queue processing
    getMessagePriority(messageType) {
        const priorities = {
            // High priority - execution critical
            'EXECUTION_COMMAND': 1,
            'RISK_ALERT': 1,
            'OPPORTUNITY_EXPIRING': 1,
            
            // Medium priority - strategy decisions
            'STRATEGY_APPROVED': 2,
            'MARKET_DATA_UPDATE': 2,
            'RISK_ASSESSMENT': 2,
            
            // Low priority - monitoring and logging
            'HEALTH_CHECK': 3,
            'PERFORMANCE_METRICS': 3,
            'DEBUG_INFO': 4
        };
        
        return priorities[messageType] || 3;
    }

    // Update latency metrics
    updateLatencyMetrics(latency) {
        this.metrics.averageLatency = (
            (this.metrics.averageLatency * (this.metrics.messagesReceived - 1) + latency) 
            / this.metrics.messagesReceived
        );
    }

    // Broadcast message to all components
    async broadcast(fromComponent, messageType, payload) {
        const broadcastPromises = [];
        
        for (const [componentId] of this.connections) {
            if (componentId !== fromComponent) {
                broadcastPromises.push(
                    this.sendMessage(fromComponent, componentId, messageType, payload)
                );
            }
        }
        
        await Promise.allSettled(broadcastPromises);
    }

    // Get component health status
    getComponentHealth(componentId) {
        const connection = this.connections.get(componentId);
        if (!connection) return 0;
        
        // Calculate health based on last seen and error rate
        const timeSinceLastSeen = Date.now() - connection.lastSeen;
        const timeHealth = Math.max(0, 1 - (timeSinceLastSeen / 60000)); // 1 minute threshold
        
        return (connection.health + timeHealth) / 2;
    }

    // Get all components health
    getSystemHealth() {
        const healthStatus = {};
        let overallHealth = 0;
        let componentCount = 0;
        
        for (const [componentId] of this.connections) {
            const health = this.getComponentHealth(componentId);
            healthStatus[componentId] = health;
            overallHealth += health;
            componentCount++;
        }
        
        return {
            components: healthStatus,
            overall: componentCount > 0 ? overallHealth / componentCount : 0,
            timestamp: Date.now()
        };
    }

    // Message types for 3-Tier Bot System
    static get MESSAGE_TYPES() {
        return {
            // Detection Tier messages
            OPPORTUNITY_DETECTED: 'OPPORTUNITY_DETECTED',
            MARKET_DATA_UPDATE: 'MARKET_DATA_UPDATE',
            SCANNING_STARTED: 'SCANNING_STARTED',
            SCANNING_STOPPED: 'SCANNING_STOPPED',
            
            // Decision Tier messages  
            STRATEGY_RANKED: 'STRATEGY_RANKED',
            RISK_ASSESSED: 'RISK_ASSESSED',
            STRATEGY_APPROVED: 'STRATEGY_APPROVED',
            STRATEGY_REJECTED: 'STRATEGY_REJECTED',
            
            // Execution Tier messages
            EXECUTION_COMMAND: 'EXECUTION_COMMAND',
            EXECUTION_RESULT: 'EXECUTION_RESULT',
            EXECUTION_FAILED: 'EXECUTION_FAILED',
            GAS_OPTIMIZED: 'GAS_OPTIMIZED',
            
            // System messages
            HEALTH_CHECK: 'HEALTH_CHECK',
            PERFORMANCE_METRICS: 'PERFORMANCE_METRICS',
            RISK_ALERT: 'RISK_ALERT',
            SYSTEM_SHUTDOWN: 'SYSTEM_SHUTDOWN'
        };
    }
}

module.exports = MessageBus;
