/**
 * QUANTUMNEX WEBSOCKET MANAGER
 * Industry Standards: ws library, Socket.io, WebSocket standards
 * Validated Sources:
 * - ws library (WebSocket implementation)
 * - Socket.io (Real-time communication patterns)
 * - WebSocket standards (RFC 6455)
 */

const WebSocket = require('ws');
const EventEmitter = require('events');

class WebSocketManager extends EventEmitter {
    constructor(options = {}) {
        super();
        this.options = {
            port: options.port || 8080,
            pingInterval: options.pingInterval || 30000,
            maxPayload: options.maxPayload || 1048576, // 1MB
            ...options
        };
        
        this.server = null;
        this.clients = new Map();
        this.rooms = new Map();
        this.messageCount = 0;
        this.connectionStats = {
            totalConnections: 0,
            activeConnections: 0,
            messagesSent: 0,
            messagesReceived: 0
        };
        
        console.log('âœ… WebSocket Manager initialized with ws library');
    }

    start() {
        try {
            this.server = new WebSocket.Server({
                port: this.options.port,
                maxPayload: this.options.maxPayload
            });

            this.setupEventHandlers();
            this.startHealthChecks();
            
            console.log(`íº€ WebSocket server started on port ${this.options.port}`);
            return this.server;
        } catch (error) {
            console.error('âŒ WebSocket server failed to start:', error);
            throw error;
        }
    }

    setupEventHandlers() {
        this.server.on('connection', (ws, request) => {
            this.handleConnection(ws, request);
        });

        this.server.on('error', (error) => {
            console.error('âŒ WebSocket server error:', error);
            this.emit('serverError', error);
        });

        this.server.on('close', () => {
            console.log('í´Œ WebSocket server closed');
            this.emit('serverClose');
        });
    }

    handleConnection(ws, request) {
        const clientId = this.generateClientId();
        const clientInfo = {
            id: clientId,
            ws: ws,
            connectedAt: new Date(),
            ip: request.socket.remoteAddress,
            userAgent: request.headers['user-agent'],
            rooms: new Set(),
            isAlive: true
        };

        this.clients.set(clientId, clientInfo);
        this.updateConnectionStats('connect');
        
        console.log(`í´— Client connected: ${clientId} from ${clientInfo.ip}`);

        // Setup client event handlers
        this.setupClientHandlers(clientId, ws);

        // Send welcome message
        this.sendToClient(clientId, {
            type: 'welcome',
            clientId: clientId,
            timestamp: new Date().toISOString(),
            serverInfo: {
                version: '1.0.0',
                features: ['real-time', 'rooms', 'binary-messages']
            }
        });

        this.emit('clientConnected', clientInfo);
    }

    setupClientHandlers(clientId, ws) {
        ws.on('message', (data) => {
            this.handleMessage(clientId, data);
        });

        ws.on('close', (code, reason) => {
            this.handleDisconnect(clientId, code, reason);
        });

        ws.on('error', (error) => {
            this.handleClientError(clientId, error);
        });

        ws.on('pong', () => {
            const client = this.clients.get(clientId);
            if (client) {
                client.isAlive = true;
            }
        });
    }

    handleMessage(clientId, data) {
        try {
            this.connectionStats.messagesReceived++;
            
            let message;
            if (typeof data === 'string') {
                message = JSON.parse(data);
            } else if (Buffer.isBuffer(data)) {
                // Handle binary data
                message = this.parseBinaryMessage(data);
            } else {
                throw new Error('Unsupported message format');
            }

            this.validateMessage(message);
            
            console.log(`í³¨ Message from ${clientId}: ${message.type}`);
            
            // Update message count
            this.messageCount++;
            
            // Emit message event
            this.emit('message', {
                clientId,
                message,
                timestamp: new Date().toISOString()
            });

            // Handle different message types
            this.routeMessage(clientId, message);

        } catch (error) {
            console.error(`âŒ Message handling failed for ${clientId}:`, error);
            this.sendToClient(clientId, {
                type: 'error',
                error: 'Invalid message format',
                originalType: data.type
            });
        }
    }

    parseBinaryMessage(data) {
        // Simple binary message parsing
        // In production, use Protocol Buffers or similar
        return {
            type: 'binary',
            data: data.toString('base64'),
            size: data.length
        };
    }

    validateMessage(message) {
        if (!message || typeof message !== 'object') {
            throw new Error('Message must be an object');
        }

        if (!message.type || typeof message.type !== 'string') {
            throw new Error('Message must have a type string');
        }

        // Validate size
        const messageSize = JSON.stringify(message).length;
        if (messageSize > this.options.maxPayload) {
            throw new Error(`Message size ${messageSize} exceeds maximum ${this.options.maxPayload}`);
        }

        return true;
    }

    routeMessage(clientId, message) {
        switch (message.type) {
            case 'join':
                this.handleJoinRoom(clientId, message.room);
                break;
            case 'leave':
                this.handleLeaveRoom(clientId, message.room);
                break;
            case 'ping':
                this.handlePing(clientId);
                break;
            case 'subscribe':
                this.handleSubscribe(clientId, message.channels);
                break;
            case 'unsubscribe':
                this.handleUnsubscribe(clientId, message.channels);
                break;
            default:
                // Custom message types are passed through
                this.emit('customMessage', { clientId, message });
        }
    }

    handleJoinRoom(clientId, roomName) {
        try {
            if (!roomName || typeof roomName !== 'string') {
                throw new Error('Invalid room name');
            }

            const client = this.clients.get(clientId);
            if (!client) {
                throw new Error('Client not found');
            }

            // Initialize room if it doesn't exist
            if (!this.rooms.has(roomName)) {
                this.rooms.set(roomName, new Set());
            }

            const room = this.rooms.get(roomName);
            room.add(clientId);
            client.rooms.add(roomName);

            console.log(`íºª Client ${clientId} joined room: ${roomName}`);
            
            this.sendToClient(clientId, {
                type: 'room_joined',
                room: roomName,
                memberCount: room.size
            });

            this.emit('roomJoined', { clientId, roomName, memberCount: room.size });

        } catch (error) {
            console.error(`âŒ Join room failed for ${clientId}:`, error);
            this.sendToClient(clientId, {
                type: 'error',
                error: `Join room failed: ${error.message}`,
                room: roomName
            });
        }
    }

    handleLeaveRoom(clientId, roomName) {
        try {
            const client = this.clients.get(clientId);
            if (!client) {
                throw new Error('Client not found');
            }

            const room = this.rooms.get(roomName);
            if (room) {
                room.delete(clientId);
                client.rooms.delete(roomName);

                // Clean up empty rooms
                if (room.size === 0) {
                    this.rooms.delete(roomName);
                }

                console.log(`íºª Client ${clientId} left room: ${roomName}`);
                
                this.sendToClient(clientId, {
                    type: 'room_left',
                    room: roomName
                });

                this.emit('roomLeft', { clientId, roomName });
            }

        } catch (error) {
            console.error(`âŒ Leave room failed for ${clientId}:`, error);
        }
    }

    handlePing(clientId) {
        this.sendToClient(clientId, {
            type: 'pong',
            timestamp: new Date().toISOString(),
            serverTime: Date.now()
        });
    }

    handleSubscribe(clientId, channels) {
        const client = this.clients.get(clientId);
        if (!client) return;

        if (!Array.isArray(channels)) {
            channels = [channels];
        }

        channels.forEach(channel => {
            client.rooms.add(`channel:${channel}`);
        });

        this.sendToClient(clientId, {
            type: 'subscribed',
            channels: channels,
            timestamp: new Date().toISOString()
        });
    }

    handleUnsubscribe(clientId, channels) {
        const client = this.clients.get(clientId);
        if (!client) return;

        if (!Array.isArray(channels)) {
            channels = [channels];
        }

        channels.forEach(channel => {
            client.rooms.delete(`channel:${channel}`);
        });

        this.sendToClient(clientId, {
            type: 'unsubscribed',
            channels: channels,
            timestamp: new Date().toISOString()
        });
    }

    handleDisconnect(clientId, code, reason) {
        const client = this.clients.get(clientId);
        if (!client) return;

        // Remove from all rooms
        client.rooms.forEach(roomName => {
            const room = this.rooms.get(roomName);
            if (room) {
                room.delete(clientId);
                if (room.size === 0) {
                    this.rooms.delete(roomName);
                }
            }
        });

        this.clients.delete(clientId);
        this.updateConnectionStats('disconnect');

        console.log(`í´Œ Client disconnected: ${clientId} (code: ${code}, reason: ${reason})`);
        
        this.emit('clientDisconnected', {
            clientId,
            code,
            reason,
            duration: Date.now() - client.connectedAt.getTime()
        });
    }

    handleClientError(clientId, error) {
        console.error(`âŒ Client ${clientId} error:`, error);
        this.emit('clientError', { clientId, error });
    }

    // Message sending methods
    sendToClient(clientId, message) {
        try {
            const client = this.clients.get(clientId);
            if (!client || client.ws.readyState !== WebSocket.OPEN) {
                throw new Error('Client not connected');
            }

            const messageString = JSON.stringify(message);
            client.ws.send(messageString);
            
            this.connectionStats.messagesSent++;
            
            return true;
        } catch (error) {
            console.error(`âŒ Failed to send message to ${clientId}:`, error);
            return false;
        }
    }

    sendToRoom(roomName, message, excludeClientId = null) {
        try {
            const room = this.rooms.get(roomName);
            if (!room) {
                console.warn(`Room ${roomName} not found`);
                return 0;
            }

            let sentCount = 0;
            const messageString = JSON.stringify(message);

            room.forEach(clientId => {
                if (clientId !== excludeClientId) {
                    if (this.sendToClient(clientId, message)) {
                        sentCount++;
                    }
                }
            });

            console.log(`í³¤ Sent to room ${roomName}: ${sentCount} clients`);
            return sentCount;
        } catch (error) {
            console.error(`âŒ Failed to send to room ${roomName}:`, error);
            return 0;
        }
    }

    broadcast(message, excludeClientId = null) {
        try {
            let sentCount = 0;
            const messageString = JSON.stringify(message);

            this.clients.forEach((client, clientId) => {
                if (clientId !== excludeClientId && client.ws.readyState === WebSocket.OPEN) {
                    client.ws.send(messageString);
                    sentCount++;
                    this.connectionStats.messagesSent++;
                }
            });

            console.log(`í³¢ Broadcast to ${sentCount} clients`);
            return sentCount;
        } catch (error) {
            console.error('âŒ Broadcast failed:', error);
            return 0;
        }
    }

    sendBinaryToClient(clientId, binaryData) {
        try {
            const client = this.clients.get(clientId);
            if (!client || client.ws.readyState !== WebSocket.OPEN) {
                throw new Error('Client not connected');
            }

            client.ws.send(binaryData);
            this.connectionStats.messagesSent++;
            
            return true;
        } catch (error) {
            console.error(`âŒ Failed to send binary to ${clientId}:`, error);
            return false;
        }
    }

    // Room management
    createRoom(roomName) {
        if (!this.rooms.has(roomName)) {
            this.rooms.set(roomName, new Set());
            console.log(`âœ… Room created: ${roomName}`);
            return true;
        }
        return false;
    }

    deleteRoom(roomName) {
        const room = this.rooms.get(roomName);
        if (room) {
            // Notify all clients in room
            this.sendToRoom(roomName, {
                type: 'room_deleted',
                room: roomName,
                timestamp: new Date().toISOString()
            });

            // Remove room from all clients
            room.forEach(clientId => {
                const client = this.clients.get(clientId);
                if (client) {
                    client.rooms.delete(roomName);
                }
            });

            this.rooms.delete(roomName);
            console.log(`í·‘ï¸ Room deleted: ${roomName}`);
            return true;
        }
        return false;
    }

    getRoomMembers(roomName) {
        const room = this.rooms.get(roomName);
        return room ? Array.from(room) : [];
    }

    getRoomCount(roomName) {
        const room = this.rooms.get(roomName);
        return room ? room.size : 0;
    }

    // Health checks and monitoring
    startHealthChecks() {
        // Ping clients periodically
        this.healthCheckInterval = setInterval(() => {
            this.checkClientHealth();
        }, this.options.pingInterval);

        // Log statistics periodically
        this.statsInterval = setInterval(() => {
            this.logStatistics();
        }, 60000); // Every minute
    }

    checkClientHealth() {
        let deadClients = [];

        this.clients.forEach((client, clientId) => {
            if (!client.isAlive) {
                deadClients.push(clientId);
                return;
            }

            client.isAlive = false;
            client.ws.ping();
        });

        // Clean up dead clients
        deadClients.forEach(clientId => {
            console.log(`í²€ Removing dead client: ${clientId}`);
            this.handleDisconnect(clientId, 1001, 'Health check failed');
        });
    }

    logStatistics() {
        const stats = this.getStats();
        console.log('í³Š WebSocket Statistics:', stats);
        this.emit('statistics', stats);
    }

    getStats() {
        return {
            ...this.connectionStats,
            activeRooms: this.rooms.size,
            totalMessages: this.messageCount,
            uptime: process.uptime(),
            timestamp: new Date().toISOString()
        };
    }

    updateConnectionStats(type) {
        switch (type) {
            case 'connect':
                this.connectionStats.totalConnections++;
                this.connectionStats.activeConnections++;
                break;
            case 'disconnect':
                this.connectionStats.activeConnections = Math.max(0, this.connectionStats.activeConnections - 1);
                break;
        }
    }

    // Utility methods
    generateClientId() {
        return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getClient(clientId) {
        return this.clients.get(clientId);
    }

    getAllClients() {
        return Array.from(this.clients.values());
    }

    getClientCount() {
        return this.clients.size;
    }

    isClientConnected(clientId) {
        const client = this.clients.get(clientId);
        return client && client.ws.readyState === WebSocket.OPEN;
    }

    // Cleanup
    stop() {
        console.log('í»‘ Stopping WebSocket server...');

        // Clear intervals
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        if (this.statsInterval) {
            clearInterval(this.statsInterval);
        }

        // Close all client connections
        this.clients.forEach((client, clientId) => {
            client.ws.close(1001, 'Server shutdown');
        });

        // Close server
        if (this.server) {
            this.server.close();
        }

        this.clients.clear();
        this.rooms.clear();
        
        console.log('âœ… WebSocket server stopped');
    }

    // Binary message utilities
    createBinaryMessage(type, data) {
        const message = {
            type,
            timestamp: Date.now(),
            ...data
        };
        
        return Buffer.from(JSON.stringify(message));
    }

    parseBinaryMessageData(binaryData) {
        try {
            const jsonString = binaryData.toString();
            return JSON.parse(jsonString);
        } catch (error) {
            throw new Error('Invalid binary message data');
        }
    }
}

module.exports = WebSocketManager;
