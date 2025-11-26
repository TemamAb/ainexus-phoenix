// QUANTUMNEX v1.0 - MESSAGE BROKER
// High-Performance Inter-Bot Communication System

const Redis = require('ioredis');
const { EventEmitter } = require('events');
const config = require('../deployment/environment-config');

class MessageBroker extends EventEmitter {
    constructor() {
        super();
        this.redis = null;
        this.connected = false;
        this.subscribers = new Map();
        this.messageQueue = [];
        this.stats = {
            messagesPublished: 0,
            messagesReceived: 0,
            deliveryErrors: 0,
            avgDeliveryTime: 0
        };

        // Message channels
        this.channels = {
            OPPORTUNITIES: 'quantumnex:opportunities',
            EXECUTIONS: 'quantumnex:executions',
            ALERTS: 'quantumnex:alerts',
            SYSTEM: 'quantumnex:system',
            PERFORMANCE: 'quantumnex:performance'
        };
    }

    /**
     * Initialize Redis connection and message broker
     */
    async initialize() {
        try {
            this.redis = new Redis({
                host: config.database.redis.host,
                port: config.database.redis.port,
                password: config.database.redis.password,
                retryDelayOnFailover: 100,
                maxRetriesPerRequest: 3
            });

            // Test connection
            await this.redis.ping();
            this.connected = true;

            // Start message processing
            this.processMessageQueue();

            console.log('✅ Message broker initialized successfully');
            return true;

        } catch (error) {
            console.error('❌ Message broker initialization failed:', error);
            this.connected = false;
            return false;
        }
    }

    /**
     * Publish message to channel
     */
    async publish(channel, message, options = {}) {
        if (!this.connected) {
            this.queueMessage(channel, message, options);
            return false;
        }

        const messageId = this.generateMessageId();
        const messageEnvelope = {
            id: messageId,
            channel: channel,
            data: message,
            timestamp: Date.now(),
            ttl: options.ttl || 3600, // 1 hour default
            priority: options.priority || 'normal'
        };

        try {
            const startTime = Date.now();
            
            await this.redis.publish(
                channel, 
                JSON.stringify(messageEnvelope)
            );

            const deliveryTime = Date.now() - startTime;
            this.updateDeliveryStats(deliveryTime);

            this.stats.messagesPublished++;
            
            // Log high-priority messages
            if (options.priority === 'high') {
                console.log(`��� Published high-priority message to ${channel}: ${messageId}`);
            }

            return messageId;

        } catch (error) {
            console.error(`❌ Failed to publish message to ${channel}:`, error);
            this.stats.deliveryErrors++;
            
            // Queue for retry
            this.queueMessage(channel, message, options);
            return false;
        }
    }

    /**
     * Subscribe to channel
     */
    async subscribe(channel, callback, options = {}) {
        if (!this.connected) {
            console.error('Cannot subscribe - broker not connected');
            return false;
        }

        try {
            // Store subscriber
            if (!this.subscribers.has(channel)) {
                this.subscribers.set(channel, new Set());
            }
            this.subscribers.get(channel).add(callback);

            // Create Redis subscription
            await this.redis.subscribe(channel);
            
            // Listen for messages
            this.redis.on('message', (msgChannel, message) => {
                if (msgChannel === channel) {
                    this.handleIncomingMessage(msgChannel, message, callback);
                }
            });

            console.log(`✅ Subscribed to channel: ${channel}`);
            return true;

        } catch (error) {
            console.error(`❌ Failed to subscribe to ${channel}:`, error);
            return false;
        }
    }

    /**
     * Unsubscribe from channel
     */
    async unsubscribe(channel, callback = null) {
        if (!this.subscribers.has(channel)) {
            return true;
        }

        try {
            if (callback) {
                // Remove specific callback
                const channelSubscribers = this.subscribers.get(channel);
                channelSubscribers.delete(callback);
                
                if (channelSubscribers.size === 0) {
                    this.subscribers.delete(channel);
                    await this.redis.unsubscribe(channel);
                }
            } else {
                // Remove all subscribers for channel
                this.subscribers.delete(channel);
                await this.redis.unsubscribe(channel);
            }

            console.log(`✅ Unsubscribed from channel: ${channel}`);
            return true;

        } catch (error) {
            console.error(`❌ Failed to unsubscribe from ${channel}:`, error);
            return false;
        }
    }

    /**
     * Handle incoming Redis messages
     */
    handleIncomingMessage(channel, message, callback) {
        try {
            const messageEnvelope = JSON.parse(message);
            
            // Validate message
            if (!this.validateMessage(messageEnvelope)) {
                console.warn(`⚠️ Invalid message received on ${channel}`);
                return;
            }

            // Update statistics
            this.stats.messagesReceived++;

            // Deliver to subscriber
            callback(messageEnvelope.data, {
                channel: channel,
                messageId: messageEnvelope.id,
                timestamp: messageEnvelope.timestamp
            });

            // Emit event for internal listeners
            this.emit('messageReceived', {
                channel: channel,
                message: messageEnvelope.data,
                envelope: messageEnvelope
            });

        } catch (error) {
            console.error(`❌ Error processing message on ${channel}:`, error);
        }
    }

    /**
     * Queue message for later delivery when offline
     */
    queueMessage(channel, message, options) {
        const queuedMessage = {
            channel: channel,
            message: message,
            options: options,
            queuedAt: Date.now(),
            attempts: 0
        };

        this.messageQueue.push(queuedMessage);
        
        // Limit queue size
        if (this.messageQueue.length > 1000) {
            this.messageQueue.shift();
        }
    }

    /**
     * Process queued messages when connection is restored
     */
    async processMessageQueue() {
        if (this.messageQueue.length === 0 || !this.connected) {
            setTimeout(() => this.processMessageQueue(), 1000);
            return;
        }

        const message = this.messageQueue.shift();
        
        try {
            await this.publish(message.channel, message.message, message.options);
            console.log(`✅ Delivered queued message to ${message.channel}`);
        } catch (error) {
            // Re-queue with backoff
            message.attempts++;
            if (message.attempts < 5) {
                this.messageQueue.push(message);
            } else {
                console.error(`❌ Failed to deliver queued message after ${message.attempts} attempts`);
            }
        }

        // Continue processing
        setImmediate(() => this.processMessageQueue());
    }

    /**
     * Generate unique message ID
     */
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Validate incoming message
     */
    validateMessage(messageEnvelope) {
        return (
            messageEnvelope &&
            messageEnvelope.id &&
            messageEnvelope.channel &&
            messageEnvelope.data !== undefined &&
            messageEnvelope.timestamp
        );
    }

    /**
     * Update delivery time statistics
     */
    updateDeliveryStats(deliveryTime) {
        this.stats.avgDeliveryTime = 
            (this.stats.avgDeliveryTime * (this.stats.messagesPublished - 1) + deliveryTime) / 
            this.stats.messagesPublished;
    }

    /**
     * Publish opportunity found message
     */
    async publishOpportunity(opportunity) {
        return await this.publish(
            this.channels.OPPORTUNITIES,
            opportunity,
            { priority: 'high', ttl: 300 } // 5 minute TTL
        );
    }

    /**
     * Publish execution result
     */
    async publishExecution(execution) {
        return await this.publish(
            this.channels.EXECUTIONS,
            execution,
            { priority: 'normal', ttl: 3600 } // 1 hour TTL
        );
    }

    /**
     * Publish system alert
     */
    async publishAlert(alert) {
        return await this.publish(
            this.channels.ALERTS,
            alert,
            { priority: 'high', ttl: 86400 } // 24 hour TTL
        );
    }

    /**
     * Publish performance metrics
     */
    async publishPerformance(metrics) {
        return await this.publish(
            this.channels.PERFORMANCE,
            metrics,
            { priority: 'low', ttl: 1800 } // 30 minute TTL
        );
    }

    /**
     * Get broker statistics
     */
    getStats() {
        return {
            ...this.stats,
            connected: this.connected,
            subscribers: this.subscribers.size,
            queuedMessages: this.messageQueue.length,
            channels: Object.keys(this.channels).length
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

    /**
     * Shutdown message broker
     */
    async shutdown() {
        try {
            // Unsubscribe from all channels
            for (const channel of this.subscribers.keys()) {
                await this.unsubscribe(channel);
            }
            
            if (this.redis) {
                await this.redis.quit();
            }
            
            this.connected = false;
            console.log('✅ Message broker shutdown complete');
        } catch (error) {
            console.error('Error shutting down message broker:', error);
        }
    }
}

// Create global message broker instance
const messageBroker = new MessageBroker();

module.exports = { MessageBroker, messageBroker };
